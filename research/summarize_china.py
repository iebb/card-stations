#!/usr/bin/env python3
"""Write the public China OSM audit from a local enrichment ledger."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def file_sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def summarize_city(item, ledger, registry, cache):
    city = item["city_code"]
    return {
        "city_code": city,
        "name": registry[city]["name"],
        "lookup_rows": item["records"],
        "snapshot": item["snapshot"],
        "query_sha256": file_sha256(cache / f"{city}.overpass"),
        "supplement": item.get("supplement"),
        "supplement_query_sha256": file_sha256(cache / f"{city}-supplement.overpass") if item.get("supplement") else None,
        "lookup_rows_changed": len({c["code"] for c in ledger}),
        "fields_filled": dict(item["changes"]),
        "new_reference_lookup_rows": sum("osm_ref" in c["fields"] for c in ledger),
        "coordinate_pairs_added_or_replaced": len({c["code"] for c in ledger if {"latitude", "longitude"} & c["fields"].keys()}),
        "new_physical_osm_references": sorted({c["osm_ref"] for c in ledger if "osm_ref" in c["fields"]}),
        "unreferenced_lookup_rows_remaining": item.get("unmatched_after", len(item["unresolved"])),
        "unresolved": item["unresolved"],
        "rejected_matches": item["rejected_matches"],
        "line_evidence": item["line_evidence"],
        "bilingual_name_evidence": item.get("bilingual_name_evidence", []),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    args = parser.parse_args()
    full = json.loads(args.ledger.read_text())
    with (args.root / "data/t-union/cities.csv").open(encoding="utf-8") as handle:
        registry = {r["code"]: r for r in csv.DictReader(handle)}
    changes = defaultdict(list)
    for item in full["changes"]:
        changes[item["city_code"]].append(item)
    summaries = [summarize_city(item, changes[item["city_code"]], registry, args.cache) for item in full["cities"]]
    output = {
        "checked_date": "2026-10-28",
        "status": "complete" if all(c["snapshot"] for c in summaries) else "partial",
        "policy": full["policy"],
        "city_registry": {"rows": len(registry), "verified_administrative_osm_references": sum(bool(r.get("osm_ref")) for r in registry.values())},
        "totals": {
            "station_cities_researched": sum(bool(c["snapshot"]) for c in summaries),
            "station_cities": len(summaries),
            "lookup_rows_changed": len({c["code"] for c in full["changes"]}),
            "fields_filled": dict(sum((Counter(c["fields_filled"]) for c in summaries), Counter())),
            "new_reference_lookup_rows": sum(c["new_reference_lookup_rows"] for c in summaries),
            "coordinate_pairs_added_or_replaced": sum(c["coordinate_pairs_added_or_replaced"] for c in summaries),
        },
        "cities": summaries,
    }
    target = args.root / "research/china-osm-audit-2026-10-28.json"
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(output["totals"], ensure_ascii=False))


if __name__ == "__main__":
    main()
