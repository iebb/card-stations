#!/usr/bin/env python3
"""Enrich T-Union station CSVs from cached, city-scoped OSM snapshots.

Codes and native names are never changed. Existing non-empty fields are kept,
except unreferenced approximate coordinates once a unique exact identity is
found. Snapshots are public OSM data and are not stored in the repository.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

COLUMNS = ["code", "station_code", "name", "name_en", "name_ja", "name_hanja", "name_zh_hans",
           "name_zh_hant", "line_code", "line", "latitude", "longitude", "osm_ref"]
LANGUAGES = {
    "name_en": ("name:en",),
    "name_ja": ("name:ja",),
    "name_zh_hans": ("name:zh-Hans", "name:zh"),
    "name_zh_hant": ("name:zh-Hant",),
}
RAIL_KINDS = ("地铁", "单轨", "轻轨", "有轨")
BUS_KINDS = ("BRT", "公交", "自行车")


def normalized(value):
    return "".join(unicodedata.normalize("NFKC", value or "").split()).translate(str.maketrans("", "", "()（）"))


def chinese_component(tags):
    """Return the Han prefix of a Chinese + Uyghur label whose suffix is the exact name:ug tag."""
    def clean(value):
        return "".join(c for c in value if unicodedata.category(c) != "Cf").strip()

    name, uyghur = clean(tags.get("name", "")), clean(tags.get("name:ug", ""))
    if not uyghur or not name.endswith(uyghur):
        return ""
    prefix = name[:-len(uyghur)]
    if not prefix or not prefix[-1].isspace():
        return ""
    chinese = prefix.strip()
    return chinese if re.fullmatch(r"[㐀-鿿]+", chinese) else ""


def native_names(tags):
    result = set()
    for key in ("name", "name:zh", "name:zh-Hans"):
        result.update(normalized(part) for part in tags.get(key, "").split(";") if normalized(part))
    component = chinese_component(tags)
    if component:
        result.add(normalized(component))
    return result


def point(element):
    center = element.get("center", {})
    lat = element.get("lat", center.get("lat"))
    lon = element.get("lon", center.get("lon"))
    return (float(lon), float(lat)) if lat is not None and lon is not None else None


def metres(a, b):
    return math.hypot((a[0] - b[0]) * math.cos(math.radians((a[1] + b[1]) / 2)), a[1] - b[1]) * 111195.08


def station_rank(element, kind=""):
    """Score how well an OSM element represents a station of this kind; 0 means incompatible."""
    tags = element.get("tags", {})
    if tags.get("railway") == "subway_entrance" or "entrance" in tags:
        return 0
    bus = (tags.get("highway") == "bus_stop" or tags.get("amenity") == "bus_station"
           or (tags.get("bus") == "yes" and tags.get("public_transport") in ("station", "platform")))
    rail = (tags.get("railway") in ("station", "halt", "tram_stop") or tags.get("station") in ("subway", "light_rail")
            or (tags.get("public_transport") in ("station", "stop_area") and not bus))
    if kind in BUS_KINDS:
        if not bus:
            return 0
        brt_text = " ".join(tags.get(k, "") for k in ("network", "operator", "ref", "route_ref"))
        if kind == "BRT" and tags.get("brt") != "yes" and not re.search(r"brt|快速公交", brt_text, re.I):
            return 0
    elif not rail:
        return 0
    node = element["type"] == "node"
    if tags.get("railway") == "station" or tags.get("station") == "subway":
        return 10 if node else 8
    if tags.get("public_transport") == "station":
        return 9 if node else 7
    if tags.get("railway") == "tram_stop":
        return 8
    if bus:
        return 6 if node else 4
    return 3


def osm_key(element):
    return f"{element['type']}/{element['id']}"


def line_label(tags):
    ref = tags.get("ref", "").strip()
    if re.fullmatch("[0-9]+", ref):
        return ref + "号线"
    if re.fullmatch("[Ss][0-9]+", ref):
        return ref.upper() + "号线"
    for key in ("name:zh", "name"):
        match = re.search(r"([0-9一二三四五六七八九十]+号线)", tags.get(key, ""))
        if match:
            return match.group(1)
    if ref and len(ref) <= 24 and not any(c in ref for c in ";|/"):
        return ref
    return ""


def build_route_memberships(elements):
    """Map each station object (and its stop-area peers) to the line labels of routes that stop there."""
    areas = defaultdict(set)
    known_stops = set()
    for e in elements:
        tags = e.get("tags", {})
        if (tags.get("railway") in ("station", "halt", "tram_stop", "stop") or tags.get("station") in ("subway", "light_rail")
                or tags.get("public_transport") in ("station", "platform", "stop_position")):
            known_stops.add(osm_key(e))
    for e in elements:
        if e["type"] == "relation" and e.get("tags", {}).get("public_transport") == "stop_area":
            members = {f"{m['type']}/{m['ref']}" for m in e.get("members", []) if m["type"] in ("node", "way")}
            members.add(osm_key(e))
            for m in e.get("members", []):
                role = m.get("role", "")
                if role in ("station", "stop", "platform", "stop_position") or "stop" in role or "platform" in role:
                    known_stops.add(f"{m['type']}/{m['ref']}")
            for key in members:
                areas[key].update(members)
    membership, refs = defaultdict(set), defaultdict(set)
    for e in elements:
        tags = e.get("tags", {})
        if e["type"] != "relation" or tags.get("type") != "route" or tags.get("route") not in ("subway", "light_rail", "monorail", "tram"):
            continue
        label = line_label(tags)
        if not label:
            continue
        for m in e.get("members", []):
            if m["type"] not in ("node", "way"):
                continue
            key = f"{m['type']}/{m['ref']}"
            role = m.get("role", "")
            # An empty role only counts for a known stop; otherwise it may be plain track.
            if role and "stop" not in role and "platform" not in role and role != "station":
                continue
            if not role and key not in known_stops:
                continue
            for joined in {key} | areas.get(key, set()):
                membership[joined].add(label)
                refs[(joined, label)].add(e["id"])
    return membership, refs


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def write_csv(path, rows):
    columns = [c for c in COLUMNS if c in ("code", "name") or any(r.get(c) for r in rows)]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        for row in sorted(rows, key=lambda r: r["code"]):
            writer.writerow({c: row.get(c, "") for c in columns})


def load_snapshot(cache, city):
    snapshot = cache / f"{city}.json"
    raw = snapshot.read_bytes()
    payload = json.loads(raw)
    elements = payload["elements"]
    info = {"sha256": hashlib.sha256(raw).hexdigest(), "osm_base": payload.get("osm3s", {}).get("timestamp_osm_base"),
            "elements": len(elements)}
    supplement = cache / f"{city}-supplement.json"
    supplement_info = None
    if supplement.exists():
        extra = supplement.read_bytes()
        extra_payload = json.loads(extra)
        joined = {osm_key(e): e for e in elements}
        joined.update({osm_key(e): e for e in extra_payload["elements"]})
        elements = list(joined.values())
        supplement_info = {"sha256": hashlib.sha256(extra).hexdigest(),
                           "osm_base": extra_payload.get("osm3s", {}).get("timestamp_osm_base"),
                           "elements": len(extra_payload["elements"])}
    return elements, info, supplement_info


def check_equivalence(row, equivalence, candidate):
    code = row["code"]
    if normalized(row["name"]) != normalized(equivalence["native_name"]):
        raise ValueError(f"Reviewed equivalence native label changed: {code}")
    if row.get("osm_ref") and row["osm_ref"] != equivalence["osm_ref"]:
        raise ValueError(f"Reviewed equivalence conflicts with an existing reference: {code}")
    if not candidate or normalized(equivalence["current_osm_name"]) not in native_names(candidate.get("tags", {})):
        raise ValueError(f"Reviewed equivalence missing or its OSM name changed: {code}")
    if not station_rank(candidate) or not point(candidate):
        raise ValueError(f"Reviewed equivalence is not a positioned rail station: {code}")


def enrich_city(path, cache, source_types, reviewed_coordinates, reference_cities, equivalences):
    city = path.stem
    _, rows = read_csv(path)
    audit = {"city_code": city, "records": len(rows), "snapshot": None, "changes": Counter(), "unresolved": [],
             "rejected_matches": [], "line_evidence": [], "bilingual_name_evidence": []}
    if not (cache / f"{city}.json").exists():
        audit["unresolved"] = [{"code": r["code"], "name": r["name"], "reason": "city snapshot unavailable"} for r in rows]
        return audit, []
    elements, audit["snapshot"], audit["supplement"] = load_snapshot(cache, city)
    by_ref = {osm_key(e): e for e in elements}
    by_name = defaultdict(list)
    for e in elements:
        if point(e) and (station_rank(e) or station_rank(e, "公交")):
            for name in native_names(e.get("tags", {})):
                by_name[name].append(e)
    memberships, relations = build_route_memberships(elements)
    ledger = []

    for row in rows:
        code, name, old_ref = row["code"], normalized(row["name"]), row.get("osm_ref", "")
        equivalence = equivalences.get(code)
        element = by_ref.get(old_ref)
        if element and not equivalence and name not in native_names(element.get("tags", {})):
            audit["rejected_matches"].append({"code": code, "osm_ref": old_ref,
                                              "reason": "referenced object native name differs; no enrichment"})
            element = None
        if equivalence:
            element = by_ref.get(equivalence["osm_ref"])
            check_equivalence(row, equivalence, element)
        elif not old_ref:
            element = match_station(row, name, source_types.get(code, ""), by_name, memberships,
                                    reference_cities, city, audit)
        if not element:
            if not old_ref:
                audit["unresolved"].append({"code": code, "name": row["name"],
                                            "reason": "no unique compatible exact OSM station identity"})
            continue

        key = osm_key(element)
        changes = {}
        if not old_ref:
            changes["osm_ref"] = {"before": "", "after": key}
            row["osm_ref"] = key
            position = reviewed_coordinates.setdefault(key, point(element))
            reference_cities.setdefault(key, set()).add(city)
            for field, value in (("longitude", position[0]), ("latitude", position[1])):
                text = str(value)
                if row.get(field, "") != text:
                    changes[field] = {"before": row.get(field, ""), "after": text}
                    row[field] = text
        elif not row.get("latitude") and point(element):
            position = reviewed_coordinates.setdefault(key, point(element))
            for field, value in (("longitude", position[0]), ("latitude", position[1])):
                changes[field] = {"before": "", "after": str(value)}
                row[field] = str(value)
        tags = element.get("tags", {})
        if name == normalized(chinese_component(tags)):
            audit["bilingual_name_evidence"].append({"code": code, "osm_ref": key, "name": tags["name"],
                                                     "name:ug": tags["name:ug"], "chinese_component": chinese_component(tags)})
        for field, keys in LANGUAGES.items():
            if row.get(field):
                continue
            value = next((tags[k].strip() for k in keys if tags.get(k, "")), "")
            if value and normalized(value) != name:
                changes[field] = {"before": "", "after": value}
                row[field] = value
        if changes:
            audit["changes"].update(changes.keys())
            ledger.append({"city_code": city, "code": code, "name": row["name"], "osm_ref": key,
                           "source_url": "https://www.openstreetmap.org/" + key, "fields": changes,
                           **({"equivalence_sources": equivalence["sources"]} if equivalence else {})})

    fill_line_labels(rows, memberships, relations, city, audit, ledger)
    audit["changes"] = dict(audit["changes"])
    audit["unmatched_after"] = sum(not r.get("osm_ref") for r in rows)
    write_csv(path, rows)
    return audit, ledger


def match_station(row, name, kind, by_name, memberships, reference_cities, city, audit):
    code = row["code"]
    candidates = [e for e in by_name[name] if station_rank(e, kind)
                  and (e.get("tags", {}).get("public_transport") != "stop_area" or memberships.get(osm_key(e)) or kind == "BRT")]
    if any(k in kind for k in RAIL_KINDS):
        candidates = [e for e in candidates
                      if e.get("tags", {}).get("station") in ("subway", "light_rail") or e.get("tags", {}).get("subway") == "yes"
                      or e.get("tags", {}).get("railway") == "tram_stop" or memberships.get(osm_key(e))]
    # A unique top-ranked station can coexist with lower-ranked footprint geometry.
    if candidates:
        best = max(station_rank(e, kind) for e in candidates)
        candidates = [e for e in candidates if station_rank(e, kind) == best]
    if len(candidates) > 1:
        audit["rejected_matches"].append({"code": code, "reason": "multiple exact station objects",
                                          "candidates": [osm_key(e) for e in candidates]})
        return None
    if not candidates:
        return None
    candidate = candidates[0]
    key = osm_key(candidate)
    if row.get("latitude") and metres((float(row["longitude"]), float(row["latitude"])), point(candidate)) > 700:
        audit["rejected_matches"].append({"code": code, "osm_ref": key, "reason": "candidate is over 700 m from prior approximate point"})
        return None
    owners = reference_cities.get(key, set())
    if owners and owners != {city}:
        audit["rejected_matches"].append({"code": code, "osm_ref": key, "reason": "OSM identity belongs to another city-code group"})
        return None
    return candidate


def fill_line_labels(rows, memberships, relations, city, audit, ledger):
    """Fill empty line names only when route memberships clearly agree across several stations."""
    grouped = defaultdict(list)
    for row in rows:
        if row.get("line_code"):
            grouped[row["line_code"]].append(row)
    for line_code, group in grouped.items():
        votes, seen_refs, evidence = Counter(), set(), defaultdict(set)
        for row in group:
            ref = row.get("osm_ref", "")
            labels = memberships.get(ref, set())
            if ref in seen_refs or not labels:
                continue
            seen_refs.add(ref)
            votes.update(labels)
            for label in labels:
                evidence[label].update(relations[(ref, label)])
        if not votes:
            continue
        label, count = votes.most_common(1)[0]
        second = max((v for k, v in votes.items() if k != label), default=0)
        if count < 3 or count < len(seen_refs) * .7 or second > count * .5:
            continue
        existing = {normalized(r["line"]) for r in group if r.get("line")}
        if existing and existing != {normalized(label)}:
            continue
        changed = []
        for row in group:
            if row.get("line"):
                continue
            row["line"] = label
            changed.append(row["code"])
            audit["changes"]["line"] += 1
            ledger.append({"city_code": city, "code": row["code"], "name": row["name"], "osm_ref": row.get("osm_ref", ""),
                           "source_urls": [f"https://www.openstreetmap.org/relation/{k}" for k in sorted(evidence[label])],
                           "fields": {"line": {"before": "", "after": label}}})
        if changed:
            audit["line_evidence"].append({"line_code": line_code, "label": label, "supporting_station_identities": count,
                                           "mapped_station_identities": len(seen_refs), "next_candidate_support": second,
                                           "relation_ids": sorted(evidence[label]), "rows_filled": len(changed)})


def load_baseline(stations):
    reviewed_coordinates, reference_cities = {}, defaultdict(set)
    for path in sorted(stations.glob("*.csv")):
        for row in read_csv(path)[1]:
            ref = row.get("osm_ref")
            if not ref:
                continue
            reference_cities[ref].add(path.stem)
            if row.get("latitude"):
                position = (float(row["longitude"]), float(row["latitude"]))
                if reviewed_coordinates.get(ref, position) != position:
                    raise ValueError(f"Baseline coordinates disagree for {ref}")
                reviewed_coordinates[ref] = position
    return reviewed_coordinates, reference_cities


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--source-types", type=Path)
    parser.add_argument("--city-relations", type=Path)
    parser.add_argument("--equivalences", type=Path)
    parser.add_argument("--audit", type=Path, help="Local diagnostics (default: dist/china-enrichment.json)")
    args = parser.parse_args()
    types = {}
    if args.source_types:
        source = json.loads(args.source_types.read_text())
        types = {code: r.get("type", "") for code, r in source.get("stations", {}).items()}
    equivalences = {r["code"]: r for r in json.loads(args.equivalences.read_text())["entries"]} if args.equivalences else {}
    stations = args.root / "data/t-union/stations"
    reviewed_coordinates, reference_cities = load_baseline(stations)
    results, ledger = [], []
    for path in sorted(stations.glob("*.csv")):
        result, changes = enrich_city(path, args.cache, types, reviewed_coordinates, reference_cities, equivalences)
        results.append(result)
        ledger.extend(changes)
    if args.city_relations:
        registry = args.root / "data/t-union/cities.csv"
        _, rows = read_csv(registry)
        verified = {r["code"]: r for r in json.loads(args.city_relations.read_text())["verified"]}
        for row in rows:
            source = verified.get(row["code"], {})
            for key in ("osm_ref", "name_en", "name_ja", "name_zh_hant"):
                if not row.get(key) and source.get(key) and normalized(source[key]) != normalized(row["name"]):
                    row[key] = source[key]
        write_csv(registry, rows)
    output = {"policy": "Exact city-scoped OSM identities with whitespace/parenthesis equivalence or a Chinese component "
                        "followed by the exact explicit name:ug suffix; preserve primary names/codes; no inferred card codes; "
                        "line labels require explicit relation membership at multiple station identities.",
              "cities": results, "changes": ledger}
    audit_path = args.audit or args.root / "dist/china-enrichment.json"
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"cities": len(results), "snapshot_cities": sum(bool(r["snapshot"]) for r in results),
                      "changed_fields": dict(sum((Counter(r["changes"]) for r in results), Counter())),
                      "rows_with_changes": len({r["code"] for r in ledger})}, ensure_ascii=False))


if __name__ == "__main__":
    main()
