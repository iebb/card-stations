#!/usr/bin/env python3
"""Validate the common CSV format and generate application compatibility assets."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import re
import sqlite3
import tempfile
from pathlib import Path

from adapters.legacy import export_assets
from routing.geohash import decode_path

ROOT = Path(__file__).resolve().parent


class ValidationError(ValueError):
    pass


def fail(label, message):
    raise ValidationError(f"{label}: {message}")


def require_hex(value, length, label):
    if not re.fullmatch(rf"[0-9A-F]{{{length}}}", value):
        fail(label, f"expected {length} uppercase hexadecimal characters")


def load_data(root):
    schema = json.loads((root / "schema.json").read_text(encoding="utf-8"))
    if schema["version"] != 2:
        fail("schema.json", "unsupported version")
    tables, consumed = {}, set()
    for spec in schema["tables"]:
        rows, seen = [], set()
        paths = sorted(root.glob(spec["glob"]))
        if not paths:
            fail(spec["glob"], "no CSV files found")
        for path in paths:
            relative = path.relative_to(root).as_posix()
            consumed.add(relative)
            with path.open(encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle, strict=True)
                header = reader.fieldnames or []
                if len(set(header)) != len(header) or not {"code", "name"}.issubset(header) or set(header) - set(spec["columns"]):
                    fail(relative, "header must contain code,name and only documented columns")
                for source_row in reader:
                    label = f"{relative}:{reader.line_num}"
                    if None in source_row or None in source_row.values():
                        fail(label, "incorrect number of cells")
                    if any(value == "\\N" for value in source_row.values()):
                        fail(label, "use an empty cell for missing values")
                    row = {c: source_row.get(c, "") for c in spec["columns"]}
                    row["_group"] = path.stem
                    if spec["name"] == "terminals":
                        row["_kind"] = path.parent.name
                    code = row["code"]
                    key = (row.get("_kind", ""), path.stem, code) if spec["name"] in ("terminals", "cityunion") else code
                    if not code or key in seen:
                        fail(label, f"empty or duplicate code {code!r} across CSV files")
                    seen.add(key)
                    if not row["name"] and not (spec["name"] in ("terminals", "cityunion") and row["station_code"]):
                        fail(label, "name is required")
                    if spec["name"] == "japanese-ic":
                        require_hex(code, 5, label)
                    elif spec["name"] == "korean":
                        require_hex(code, 12, label)
                    elif spec["name"] == "t-union":
                        require_hex(path.stem, 4, label)
                        if not re.fullmatch(r"[0-9A-F]+", code) or not code.startswith(path.stem):
                            fail(label, "code must be uppercase hexadecimal beginning with the city code")
                        if row["line_code"] and not row["line_code"].startswith(path.stem):
                            fail(label, "line_code must begin with the city code")
                    elif spec["name"] == "terminals":
                        if row["_kind"] not in ("18", "1e"):
                            fail(label, "terminal folder must be 18 or 1e")
                        require_hex(code, 12 if row["_kind"] == "18" else 16, label)
                        require_hex(path.stem, 4, label)
                    elif spec["name"] == "cityunion":
                        if path.stem != "2000" or not re.fullmatch(r"2000[0-9A-F]+", code) or len(code) not in (8, 10, 12):
                            fail(label, "invalid Shanghai City Union prefix")
                    elif spec["name"] in ("u-money", "u-money-lines", "modes"):
                        if not re.fullmatch(r"[1-9][0-9]*", code):
                            fail(label, "code must be a positive decimal identifier")
                    lat, lon = row.get("latitude", ""), row.get("longitude", "")
                    if bool(lat) != bool(lon):
                        fail(label, "latitude and longitude must appear together")
                    if lat:
                        try:
                            valid = math.isfinite(float(lat)) and math.isfinite(float(lon)) and -90 <= float(lat) <= 90 and -180 <= float(lon) <= 180
                        except ValueError:
                            valid = False
                        if not valid:
                            fail(label, "coordinates must be finite WGS84 degrees")
                    if row.get("osm_ref") and not re.fullmatch(r"(node|way|relation)/[1-9][0-9]*", row["osm_ref"]):
                        fail(label, "osm_ref must be node/ID, way/ID, or relation/ID")
                    if row.get("line_code") and any(not value for value in row["line_code"].split("|")):
                        fail(label, "empty line code in membership list")
                    rows.append(row)
        tables[spec["name"]] = sorted(rows, key=lambda r: (r.get("_kind", ""), r["code"], r["_group"]))
    stations = {r["code"]: r for r in tables["t-union"]}
    for table in ("terminals", "cityunion"):
        for row in tables[table]:
            linked = row["station_code"]
            if linked:
                if linked not in stations:
                    fail(table, f"orphan station link {linked}")
                expected_city = row["_group"] if table == "terminals" else "2900"
                if not linked.startswith(expected_city) or (row["name"] and row["name"] != stations[linked]["name"]):
                    fail(table, f"station link disagrees with city or name: {linked}")
    modes = {int(r["code"]): r for r in tables["modes"]}
    for row in tables["korean"]:
        mode = int(row["code"][8:], 16)
        if mode not in modes:
            fail("korean", f"code {row['code']} references missing mode {mode}")
    lines = {r["code"] for r in tables["u-money-lines"]}
    for row in tables["u-money"]:
        if row["line_code"] and set(row["line_code"].split("|")) - lines:
            fail("u-money", f"unknown line in {row['code']}")
    for family, key_column in (("japanese-ic", "station_code"), ("t-union", "osm_ref")):
        positions = {}
        for row in tables[family]:
            key = row[key_column]
            if not key or key == "0" or not row["latitude"]:
                continue
            point = (float(row["latitude"]), float(row["longitude"]))
            if key in positions and positions[key] != point:
                fail(family, f"aliases for {key} have conflicting coordinates")
            positions[key] = point
    routing_edges, routing_stops = [], []
    edge_keys, stop_keys = set(), set()
    endpoint_positions = {
        "japanese-ic": {r["station_code"]: (float(r["longitude"]), float(r["latitude"]))
                        for r in tables["japanese-ic"] if r["station_code"] and r["latitude"]},
        "t-union": {r["code"]: (float(r["longitude"]), float(r["latitude"]))
                    for r in tables["t-union"] if r["latitude"]},
    }
    paths = sorted(root.glob("data/*/edges.csv")) + sorted(root.glob("data/*/edges/**/*.csv"))
    for path in paths:
        family = path.relative_to(root).parts[1]
        if family not in endpoint_positions:
            fail(path, "unsupported routing family")
        consumed.add(path.relative_to(root).as_posix())
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, strict=True)
            if reader.fieldnames != ["line_code", "from_code", "to_code", "distance_km", "vertices"]:
                fail(path, "invalid edge header")
            for row in reader:
                key = (family, row["line_code"], row["from_code"], row["to_code"])
                if key in edge_keys or not all(key) or row["from_code"] == row["to_code"]:
                    fail(path, f"invalid or duplicate edge {key}")
                edge_keys.add(key)
                try:
                    distance = float(row["distance_km"])
                    if not math.isfinite(distance) or distance < 0:
                        raise ValueError("invalid distance")
                    if row["vertices"]:
                        vertices = decode_path(row["vertices"])
                        for key, point in ((row["from_code"], vertices[0]), (row["to_code"], vertices[-1])):
                            expected = endpoint_positions[family].get(key)
                            if expected:
                                latitude = math.radians((point[1] + expected[1]) / 2)
                                gap = math.hypot((point[0] - expected[0]) * math.cos(latitude), point[1] - expected[1]) * 111195.08
                                if gap > 10:
                                    raise ValueError(f"geometry endpoint does not match station {key}")
                except ValueError as error:
                    fail(path, str(error))
                row["_family"] = family
                routing_edges.append(row)
    mongolian_codes = {r["code"] for r in tables["u-money"]}
    for path in sorted(root.glob("data/*/line-stops.csv")):
        family = path.relative_to(root).parts[1]
        if family not in ("t-union", "u-money"):
            fail(path, "unsupported ordered-stop family")
        consumed.add(path.relative_to(root).as_posix())
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, strict=True)
            if reader.fieldnames != ["line_code", "code", "sequence"]:
                fail(path, "invalid line-stop header")
            for row in reader:
                try:
                    sequence = int(row["sequence"])
                    if sequence < 1:
                        raise ValueError()
                except ValueError:
                    fail(path, "invalid stop sequence")
                key = (family, row["line_code"], row["code"], sequence)
                if key in stop_keys:
                    fail(path, "duplicate line stop")
                stop_keys.add(key)
                if family == "t-union" and (row["code"] not in stations or stations[row["code"]]["line_code"] != row["line_code"]):
                    fail(path, "line stop references an unknown station or line")
                if family == "u-money" and (row["line_code"] not in lines or row["code"] not in mongolian_codes):
                    fail(path, "line stop references an unknown station or line")
                row["_family"] = family
                routing_stops.append(row)
    tables["edges"], tables["line-stops"] = routing_edges, routing_stops
    unused = {p.relative_to(root).as_posix() for p in (root / "data").rglob("*.csv")} - consumed
    if unused:
        fail("data", f"CSV files do not match a schema glob: {sorted(unused)}")
    return tables, consumed


def compile_sources(root, output):
    tables, consumed = load_data(root)
    export_assets(root, output, tables)
    inputs = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in sorted(consumed)}
    for folder in ("reference", "adapters", "routing"):
        for path in sorted((root / folder).rglob("*")):
            if path.is_file() and path.suffix in (".json", ".py"):
                inputs[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    for name in ("schema.json", "build.py"):
        inputs[name] = hashlib.sha256((root / name).read_bytes()).hexdigest()
    digest = hashlib.sha256(json.dumps(inputs, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    manifest = {"format": "card-stations-v3", "source_sha256": digest,
        "toolchain": {"python": platform.python_version(), "sqlite": sqlite3.sqlite_version},
        "inputs": dict(sorted(inputs.items())), "counts": {name: len(rows) for name, rows in tables.items()},
        "outputs": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir())}}
    (output / "card-stations-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def build(root: Path, output: Path):
    root, output = root.resolve(), output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".card-stations-", dir=output.parent) as directory:
        staging = Path(directory)
        manifest = compile_sources(root, staging)
        output.mkdir(parents=True, exist_ok=True)
        for path in sorted(staging.iterdir()):
            if not (output / path.name).is_file() or (output / path.name).read_bytes() != path.read_bytes():
                os.replace(path, output / path.name)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.check:
            with tempfile.TemporaryDirectory(prefix="card-stations-check-") as directory:
                manifest = build(args.source, Path(directory) / "dist")
        else:
            manifest = build(args.source, args.output)
    except (ValidationError, sqlite3.Error, csv.Error) as error:
        parser.exit(1, f"error: {error}\n")
    print(json.dumps({"source_sha256": manifest["source_sha256"], "counts": manifest["counts"]}, indent=2))


if __name__ == "__main__":
    main()
