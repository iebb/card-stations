#!/usr/bin/env python3
"""Import station codes, names, lines, coordinates, and real OSM references."""
from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from collections import defaultdict
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATION_COLUMNS = ["code", "station_code", "name", "name_en", "name_ja", "name_hanja", "name_zh_hans", "name_zh_hant", "line_code", "line", "latitude", "longitude", "osm_ref"]


def write_csv(path, rows, columns=STATION_COLUMNS, required=("code", "name")):
    rows = [{key: ("" if key.startswith("name_") and value == row["name"] else value)
             for key, value in row.items()} for row in rows]
    rows = sorted(rows, key=lambda r: r["code"])
    columns = [c for c in columns if c in required or any(r.get(c) not in (None, "") for r in rows)]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({c: "" if row.get(c) is None else row.get(c, "") for c in columns})


def load_table(path, table):
    with closing(sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)) as db:
        db.row_factory = sqlite3.Row
        return [dict(r) for r in db.execute(f'SELECT * FROM "{table}"')]


def migrate(resources: Path, portable: Path, destination: Path):
    if (destination / "data").exists():
        raise ValueError("Import into a new directory, then review the CSV diff")
    jp = load_table(portable / "jp_stations.sqlite", "jp_stations")
    write_csv(destination / "data/japanese-ic/stations/all.csv", [
        {"code": r["hex_code"], "station_code": r["station_code"], "name": r["station_name"],
         "line_code": "|".join(map(str, json.loads(r["line_codes_json"]))),
         "latitude": r["latitude"], "longitude": r["longitude"]} for r in jp])
    with (portable / "JPBusCodes.csv").open(encoding="utf-8", newline="") as handle:
        write_csv(destination / "data/japanese-ic/bus-companies.csv", [{"code": c, "name": n} for c, n in csv.reader(handle)])

    cn = load_table(portable / "tunion_stations.sqlite", "tunion_stations")
    grouped = defaultdict(list)
    for r in cn:
        grouped[r["city_id"]].append({
            "code": r["station_key"], "name": r["station_name"],
            "name_en": r["osm_name_en"], "name_ja": r["osm_name_ja"],
            "name_zh_hans": r["osm_name_zh"] if r["osm_name_zh"] != r["station_name"] else "",
            "line_code": r["line_key"], "line": r["source_line_name"],
            "latitude": r["latitude"], "longitude": r["longitude"],
            "osm_ref": f"{r['osm_type']}/{r['osm_id']}" if r["osm_type"] in ("node", "way", "relation") and str(r["osm_id"]).isdigit() else "",
        })
    for city, rows in grouped.items():
        write_csv(destination / f"data/t-union/stations/{city}.csv", rows)
    stations = {r["station_key"]: r for r in cn}
    for table, folder in (("tunion_terminal_stations", "terminals"), ("cityunion_terminal_prefixes", "cityunion")):
        grouped = defaultdict(list)
        for r in load_table(portable / "tunion_stations.sqlite", table):
            group = f"{r['record_kind']}/{r['city_id']}" if folder == "terminals" else r["city_id"]
            grouped[group].append({"code": r.get("terminal_code", r.get("terminal_prefix")),
                "station_code": r["station_key"],
                "name": "" if r["station_key"] and stations[r["station_key"]]["station_name"] == r["station_name"] else r["station_name"],
                "line": "" if r["station_key"] and stations[r["station_key"]]["source_line_name"] == r["line_name"] else r["line_name"]})
        for group, rows in grouped.items():
            write_csv(destination / f"data/t-union/{folder}/{group}.csv", rows)
    for original, name in (("TUnionCityCodes.json", "cities.csv"), ("TUnionCardNames.json", "card-names.csv")):
        rows = json.loads((portable / original).read_text(encoding="utf-8"))
        write_csv(destination / f"data/t-union/{name}", [{"code": c, "name": n} for c, n in rows.items()])

    modes_payload = json.loads((portable / "KOTRISTransportModes.json").read_text(encoding="utf-8"))
    modes = {str(r["code"]): {"code": str(r["code"]), "name": r["nameKo"], "class": r["transportClass"]} for r in modes_payload["modes"]}
    for r in modes_payload.get("supplementaryModes", []):
        modes.setdefault(str(r["code"]), {"code": str(r["code"]), "name": r["nameKo"], "class": r["transportClass"]})
    grouped = defaultdict(list)
    with (resources / "korean_stations.tsv").open(encoding="utf-8", newline="") as handle:
        for r in csv.DictReader(handle, delimiter="\t"):
            modes[r["transport_mode_code"]] = {"code": r["transport_mode_code"], "name": r["transport_mode_name_ko"],
                **{f"name_{lang}": r[f"transport_mode_name_{lang}"] for lang in ("en", "ja", "hanja", "zh_hans", "zh_hant")}, "class": r["transport_class"]}
            company = r["operator_name"].replace("/", "-") or f"mode-{int(r['transport_mode_code']):04d}"
            grouped[company].append({"code": r["location_code"], "name": r["canonical_name_ko"],
                **{f"name_{lang}": r[f"station_name_{lang}"] for lang in ("en", "ja", "hanja", "zh_hans", "zh_hant")},
                "line": r["line_name"], "latitude": r["latitude"], "longitude": r["longitude"]})
    for company, rows in grouped.items():
        write_csv(destination / f"data/korean/stations/{company}.csv", rows)
    write_csv(destination / "data/korean/modes.csv", list(modes.values()), ["code", "name", "name_en", "name_ja", "name_hanja", "name_zh_hans", "name_zh_hant", "class"])

    mn_path = portable / "ulaanbaatar_transit.sqlite"
    memberships = defaultdict(set)
    for r in load_table(mn_path, "route_stations"):
        memberships[r["station_id"]].add(str(r["route_id"]))
    write_csv(destination / "data/u-money/stations/ulaanbaatar.csv", [
        {"code": str(r["station_id"]), "name": r["station_name_mn"], "name_en": r["station_name_en"],
         "line_code": "|".join(sorted(memberships[r["station_id"]])), "latitude": r["latitude"], "longitude": r["longitude"]}
        for r in load_table(mn_path, "stations")])
    write_csv(destination / "data/u-money/lines.csv", [
        {"code": str(r["route_id"]), "name": r["route_name_mn"], "name_en": r["route_name_en"]} for r in load_table(mn_path, "routes")])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resources", type=Path, required=True)
    parser.add_argument("--portable", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    migrate(args.resources, args.portable, args.output)
