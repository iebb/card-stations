"""Application compatibility formats, derived from the compact contributor CSVs."""
from __future__ import annotations

import csv
import json
import sqlite3
from contextlib import closing


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path, columns, rows, delimiter=",", header=True):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter=delimiter, lineterminator="\n")
        if header:
            writer.writerow(columns)
        writer.writerows([[row.get(c, "") for c in columns] for row in rows])


def export_assets(root, output, data):
    schema = json.loads((root / "adapters/legacy-schema.json").read_text(encoding="utf-8"))
    rows = {name: {t: [] for t in spec["tables"]} for name, spec in schema["databases"].items()}
    jp = rows["jp_stations.sqlite"]["jp_stations"]
    for r in data["japanese-ic"]:
        if not r["station_code"] or not r["latitude"]:
            continue  # Name-only codes remain in the decoder registry.
        pseudo = r["station_code"] == "0"
        jp.append({"hex_code": r["code"], "code_integer": int(r["code"], 16),
            "csv_names_json": json.dumps([r["name"]], ensure_ascii=False), "csv_primary_name": r["name"],
            "station_name": r["name"], "station_original_name": r["name"], "station_source": "csv",
            "station_code": r["station_code"], "latitude": float(r["latitude"]), "longitude": float(r["longitude"]),
            "line_codes_json": json.dumps(r["line_code"].split("|") if r["line_code"] else []),
            "match_method": "pseudo" if pseudo else "csv", "is_pseudo": int(pseudo),
            "pseudo_id": f"pseudo:{r['code']}" if pseudo else None})
    cities = {r["code"]: r["name"] for r in data["cities"]}
    cn = rows["tunion_stations.sqlite"]["tunion_stations"]
    cn_by_code = {r["code"]: r for r in data["t-union"]}
    for r in data["t-union"]:
        osm_type, osm_id = r["osm_ref"].split("/") if r["osm_ref"] else (None, None)
        cn.append({"station_key": r["code"], "city_id": r["_group"], "city_name": cities.get(r["_group"], ""),
            "line_key": r["line_code"] or f"{r['_group']}:unassigned", "sequence": 0,
            "station_name": r["name"], "normalized_station_name": r["name"], "display_name": r["name"],
            "match_status": "csv" if r["latitude"] else "unmatched", "match_quality": "", "match_source": "csv",
            "latitude": float(r["latitude"]) if r["latitude"] else None, "longitude": float(r["longitude"]) if r["longitude"] else None,
            "osm_type": osm_type, "osm_id": osm_id, "osm_name_en": r["name_en"] or None,
            "osm_name_ja": r["name_ja"] or None, "osm_name_zh": r["name_zh_hans"] or None,
            "source_code": r["code"][4:], "source_line_name": r["line"]})
    for table, key, name in (("tunion_terminal_stations", "terminal_code", "terminals"), ("cityunion_terminal_prefixes", "terminal_prefix", "cityunion")):
        for r in data[name]:
            linked = cn_by_code.get(r["station_code"])
            row = {key: r["code"], "city_id": r["_group"], "station_name": r["name"] or linked["name"],
                "line_name": r["line"] or (linked["line"] if linked else ""), "station_key": r["station_code"] or None, "source_json": "{}"}
            if name == "terminals":
                row["record_kind"] = r["_kind"]
            rows["tunion_stations.sqlite"][table].append(row)
    mn = rows["ulaanbaatar_transit.sqlite"]
    mn["stations"] = [{"station_id": int(r["code"]), "station_name_mn": r["name"], "station_name_en": r["name_en"],
        "latitude": float(r["latitude"]), "longitude": float(r["longitude"])} for r in data["u-money"]]
    mn["routes"] = [{"route_id": int(r["code"]), "route_name_mn": r["name"], "route_name_en": r["name_en"]} for r in data["u-money-lines"]]
    for edge in data["edges"]:
        filename = {"japanese-ic": "jp_stations.sqlite", "t-union": "tunion_stations.sqlite"}[edge["_family"]]
        row = {"line_code": edge["line_code"], "from_station_code": edge["from_code"],
               "to_station_code": edge["to_code"], "distance_km": float(edge["distance_km"])}
        rows[filename]["station_edges"].append(row)
        if edge["vertices"]:
            rows[filename]["station_edge_paths"].append({**row, "geohash_path": edge["vertices"]})
    cn_lookup = {r["station_key"]: r for r in cn}
    for stop in data["line-stops"]:
        if stop["_family"] == "t-union":
            cn_lookup[stop["code"]]["sequence"] = int(stop["sequence"])
        elif stop["_family"] == "u-money":
            mn["route_stations"].append({"route_id": int(stop["line_code"]), "station_sequence": int(stop["sequence"]), "station_id": int(stop["code"])})
    for filename, database in schema["databases"].items():
        with closing(sqlite3.connect(output / filename)) as db:
            db.executescript("\n".join(database["schema"]))
            db.execute("PRAGMA foreign_keys=ON")
            db.execute("PRAGMA defer_foreign_keys=ON")
            for table, columns in database["tables"].items():
                info = list(db.execute(f'PRAGMA table_info("{table}")'))
                def values(row):
                    return [row.get(c[1], None if not c[3] and not c[5] else (0 if c[2] in ("REAL", "INTEGER") else "")) for c in info]
                db.executemany(f'INSERT INTO "{table}" VALUES ({",".join("?" for _ in columns)})', [values(r) for r in rows[filename][table]])
            if db.execute("PRAGMA foreign_key_check").fetchall():
                raise ValueError(f"{filename}: invalid foreign key")
            db.commit()
            if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise ValueError(f"{filename}: invalid database")
            db.execute("VACUUM")
    modes = {int(r["code"]): r for r in data["modes"]}
    kr = []
    for r in data["korean"]:
        mode_code = int(r["code"][8:], 16)
        mode = modes[mode_code]
        company = "" if r["_group"].startswith("mode-") else r["_group"]
        kr.append({"location_code": r["code"], "station_id": r["code"][:8], "transport_mode_code": str(mode_code),
            "transport_mode_name_ko": mode["name"],
            **{f"transport_mode_name_{lang}": mode[f"name_{lang}"] or mode["name"] for lang in ("en", "ja", "hanja", "zh_hans", "zh_hant")},
            "transport_class": mode["class"], "station_name_ko": r["name"], "canonical_name_ko": r["name"],
            **{f"station_name_{lang}": r[f"name_{lang}"] for lang in ("en", "ja", "hanja", "zh_hans", "zh_hant")},
            "operator_name": company, "line_name": r["line"], "latitude": r["latitude"], "longitude": r["longitude"]})
    kr.sort(key=lambda r: (int(r["transport_mode_code"]), r["station_id"]))
    write_csv(output / "korean_stations.tsv", schema["korean_columns"], kr, "\t")
    write_csv(output / "JPStationCodes.csv", ["code", "name"], data["japanese-ic"], header=False)
    write_csv(output / "JPBusCodes.csv", ["code", "name"], data["bus-companies"], header=False)
    write_json(output / "JPStationCodes.json", {str(int(r["code"], 16)): r["name"] for r in data["japanese-ic"]})
    write_json(output / "TUnionLineStations.json", {r["code"]: r["name"] for r in data["t-union"]})
    write_json(output / "TUnionCityCodes.json", cities)
    write_json(output / "TUnionCardNames.json", {r["code"]: r["name"] for r in data["card-names"]})
    write_json(output / "jp_stations_coverage.json", {"csv_rows": len(data["japanese-ic"]), "output_rows": len(jp),
        "pseudo_row_count": sum(r["is_pseudo"] for r in jp), "real_station_row_count": sum(not r["is_pseudo"] for r in jp)})
    mode_meta = json.loads((root / "reference/korean-mode-metadata.json").read_text(encoding="utf-8"))
    mode_rows = [{"code": int(r["code"]), "nameKo": r["name"], "transportClass": r["class"]} for r in data["modes"]]
    supplementary_codes = {int(r["code"]) for r in mode_meta.get("supplementaryModes", [])}
    mode_meta["modes"] = sorted((r for r in mode_rows if r["code"] not in supplementary_codes), key=lambda r: r["code"])
    mode_meta["supplementaryModes"] = [{**r, "nameKo": modes[int(r["code"])]["name"], "transportClass": modes[int(r["code"])]["class"]} for r in mode_meta.get("supplementaryModes", [])]
    write_json(output / "KOTRISTransportModes.json", mode_meta)
    write_json(output / "tunion_tripreader_source.json", json.loads((root / "reference/tripreader-provenance.json").read_text(encoding="utf-8")))
    for table, name in (("stations", "ulaanbaatar_stations.tsv"), ("routes", "ulaanbaatar_routes.tsv"), ("route_stations", "ulaanbaatar_route_stations.tsv")):
        write_csv(output / name, schema["databases"]["ulaanbaatar_transit.sqlite"]["tables"][table], mn[table], "\t")
