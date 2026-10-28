from __future__ import annotations

import csv
import json
import shutil
import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temporary.name)
        cls.output = cls.root / "baseline"
        cls.manifest = build.build(build.ROOT, cls.output)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def setUp(self):
        self.case = tempfile.TemporaryDirectory()
        self.addCleanup(self.case.cleanup)
        self.source = Path(self.case.name) / "source"
        self.source.mkdir()
        for folder in ("data", "reference", "adapters", "routing"):
            shutil.copytree(build.ROOT / folder, self.source / folder)
        for filename in ("schema.json", "build.py"):
            shutil.copyfile(build.ROOT / filename, self.source / filename)
        self.target = Path(self.case.name) / "dist"

    def edit(self, pattern, mutate):
        path = next(self.source.glob(pattern))
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            names, rows = reader.fieldnames, list(reader)
        mutate(rows)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=names, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        return path

    def test_deterministic_output(self):
        manifest = build.build(self.source, self.target)
        self.assertEqual(manifest, self.manifest)
        for name in manifest["outputs"]:
            self.assertEqual((self.output / name).read_bytes(), (self.target / name).read_bytes())

    def test_station_correction_reaches_database_and_decoder(self):
        self.edit("data/t-union/stations/1000.csv", lambda rows: rows[0].update(name="Reviewed station name"))
        build.build(self.source, self.target)
        with closing(sqlite3.connect(self.target / "tunion_stations.sqlite")) as db:
            self.assertEqual(db.execute("SELECT station_name FROM tunion_stations WHERE station_key='1000010001'").fetchone()[0], "Reviewed station name")
        self.assertEqual(json.loads((self.target / "TUnionLineStations.json").read_text())["1000010001"], "Reviewed station name")

    def test_mode_correction_is_joined_into_all_consumers(self):
        def correct(rows):
            next(r for r in rows if r["code"] == "105")["name_en"] = "Reviewed bus mode"
        self.edit("data/korean/modes.csv", correct)
        build.build(self.source, self.target)
        with (self.target / "korean_stations.tsv").open() as handle:
            rows = [r for r in csv.DictReader(handle, delimiter="\t") if r["transport_mode_code"] == "105"]
        self.assertTrue(rows)
        self.assertTrue(all(r["transport_mode_name_en"] == "Reviewed bus mode" for r in rows))

    def test_linked_terminal_inherits_corrected_station_name(self):
        data, _ = build.load_data(self.source)
        terminal = next(r for r in data["terminals"] if r["station_code"] and not r["name"])
        code = terminal["station_code"]
        def correct(rows):
            next(r for r in rows if r["code"] == code)["name"] = "Corrected linked station"
        self.edit(f"data/t-union/stations/{code[:4]}.csv", correct)
        build.build(self.source, self.target)
        with closing(sqlite3.connect(self.target / "tunion_stations.sqlite")) as db:
            self.assertEqual(db.execute("SELECT station_name FROM tunion_terminal_stations WHERE record_kind=? AND city_id=? AND terminal_code=?",
                (terminal["_kind"], terminal["_group"], terminal["code"])).fetchone(), ("Corrected linked station",))

    def test_station_sources_have_no_mode_or_importer_columns(self):
        for path in (self.source / "data").glob("*/stations/**/*.csv"):
            with path.open() as handle:
                columns = next(csv.reader(handle))
            self.assertFalse(any(c.startswith("transport_mode") or c.endswith("_json") or c in ("city_id", "last_updated_at", "match_status", "source_code") for c in columns), path)

    def test_duplicate_code_across_company_files_rejected(self):
        original = next((self.source / "data/korean/stations").glob("*.csv"))
        shutil.copyfile(original, original.with_name("duplicate.csv"))
        with self.assertRaisesRegex(build.ValidationError, "duplicate code"):
            build.build(self.source, self.target)

    def test_nested_company_file_discovered(self):
        original = next((self.source / "data/korean/stations").glob("mode-*.csv"))
        nested = original.parent / "reviewed" / original.name
        nested.parent.mkdir()
        original.rename(nested)
        manifest = build.build(self.source, self.target)
        self.assertIn(nested.relative_to(self.source).as_posix(), manifest["inputs"])
        self.assertEqual(manifest["outputs"]["korean_stations.tsv"], self.manifest["outputs"]["korean_stations.tsv"])

    def test_lost_leading_zero_rejected(self):
        self.edit("data/korean/stations/mode-*.csv", lambda rows: rows[0].update(code="123"))
        with self.assertRaisesRegex(build.ValidationError, "12 uppercase hexadecimal"):
            build.build(self.source, self.target)

    def test_invalid_coordinates_leave_existing_output_untouched(self):
        self.target.mkdir()
        sentinel = self.target / "jp_stations.sqlite"
        sentinel.write_bytes(b"previous validated database")
        self.edit("data/japanese-ic/stations/all.csv", lambda rows: rows[0].update(latitude="NaN"))
        with self.assertRaisesRegex(build.ValidationError, "finite"):
            build.build(self.source, self.target)
        self.assertEqual(sentinel.read_bytes(), b"previous validated database")

    def test_unrecognized_csv_rejected(self):
        (self.source / "data/misplaced.csv").write_text("code,name\n1,Station\n")
        with self.assertRaisesRegex(build.ValidationError, "do not match"):
            build.build(self.source, self.target)

    def test_orphan_terminal_link_rejected(self):
        self.edit("data/t-union/cityunion/*.csv", lambda rows: rows[0].update(station_code="2900FFFFFF"))
        with self.assertRaisesRegex(build.ValidationError, "orphan station link"):
            build.build(self.source, self.target)

    def test_fabricated_osm_reference_rejected(self):
        self.edit("data/t-union/stations/6020.csv", lambda rows: rows[0].update(osm_ref="line-approx/123"))
        with self.assertRaisesRegex(build.ValidationError, "osm_ref"):
            build.build(self.source, self.target)

    def test_korean_unknown_mode_rejected(self):
        self.edit("data/korean/stations/mode-*.csv", lambda rows: rows[0].update(code=rows[0]["code"][:8]+"FFFF"))
        with self.assertRaisesRegex(build.ValidationError, "missing mode"):
            build.build(self.source, self.target)

    def test_routing_edges_and_geometry_are_exported(self):
        with closing(sqlite3.connect(self.output / "jp_stations.sqlite")) as db:
            self.assertGreater(db.execute("SELECT COUNT(*) FROM station_edges").fetchone()[0], 13000)
            self.assertGreater(db.execute("SELECT COUNT(*) FROM station_edge_paths").fetchone()[0], 12000)

    def test_geometry_must_match_known_edge_endpoints(self):
        from routing.geohash import encode_path
        data, _ = build.load_data(self.source)
        known = {r["station_code"] for r in data["japanese-ic"] if r["latitude"]}
        def corrupt(rows):
            row = next(r for r in rows if r["from_code"] in known and r["vertices"])
            row["vertices"] = encode_path([(0, 0), (.1, .1)])
        self.edit("data/japanese-ic/edges.csv", corrupt)
        with self.assertRaisesRegex(build.ValidationError, "geometry endpoint does not match"):
            build.build(self.source, self.target)


if __name__ == "__main__":
    unittest.main()
