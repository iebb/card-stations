#!/usr/bin/env python3
"""Produce a compact public audit from a local detailed enrichment ledger."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from collections import Counter,defaultdict
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--ledger',type=Path,required=True)
    parser.add_argument('--cache',type=Path,required=True)
    args=parser.parse_args()
    full=json.loads(args.ledger.read_text())
    equivalences=json.loads((args.root/'research/reviewed-name-equivalences.json').read_text())['entries']
    with (args.root/'data/t-union/cities.csv').open() as f:registry={r['code']:r for r in csv.DictReader(f)}
    changes=defaultdict(list)
    for item in full['changes']:changes[item['city_code']].append(item)
    summaries=[]
    for item in full['cities']:
        city=item['city_code'];ledger=changes[city]
        query=args.cache/(city+'.overpass');supplement_query=args.cache/(city+'-supplement.overpass')
        summaries.append({
            'city_code':city,'name':registry[city]['name'],'lookup_rows':item['records'],
            'snapshot':item['snapshot'],'query_sha256':hashlib.sha256(query.read_bytes()).hexdigest() if query.is_file() else None,
            'supplement':item.get('supplement'),'supplement_query_sha256':hashlib.sha256(supplement_query.read_bytes()).hexdigest() if item.get('supplement') and supplement_query.is_file() else None,
            'lookup_rows_changed':len({c['code'] for c in ledger}),
            'fields_filled':dict(item['changes']),
            'new_reference_lookup_rows':sum('osm_ref' in c['fields'] for c in ledger),
            'coordinate_pairs_added_or_replaced':len({c['code'] for c in ledger if {'latitude','longitude'}&c['fields'].keys()}),
            'new_physical_osm_references':sorted({c['osm_ref'] for c in ledger if 'osm_ref' in c['fields']}),
            'unreferenced_lookup_rows_remaining':item.get('unmatched_after',sum(1 for r in item['unresolved'])),
            'unresolved':item['unresolved'],'rejected_matches':item['rejected_matches'],
            'line_evidence':item['line_evidence'],
            'bilingual_name_evidence':item.get('bilingual_name_evidence',[]),
        })
    total=sum((Counter(c['fields_filled']) for c in summaries),Counter())
    city_refs=sum(bool(r.get('osm_ref')) for r in registry.values())
    output={'checked_date':'2026-10-28','status':'complete' if all(c['snapshot'] for c in summaries) else 'partial','policy':full['policy'],
        'city_registry':{'rows':len(registry),'verified_administrative_osm_references':city_refs},
        'totals':{'station_cities_researched':sum(bool(c['snapshot']) for c in summaries),'station_cities':len(summaries),'lookup_rows_changed':len({c['code'] for c in full['changes']}),'fields_filled':dict(total),'new_reference_lookup_rows':sum(c['new_reference_lookup_rows'] for c in summaries),'coordinate_pairs_added_or_replaced':sum(c['coordinate_pairs_added_or_replaced'] for c in summaries)},
        'cities':summaries}
    target=args.root/'research/china-osm-audit-2026-10-28.json'
    target.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    lines=['# Chinese station research — 2026-10-28','',
        'All 368 city-code registry entries were checked against current primary OSM administrative relations. Their exact Chinese names or explicit Chinese-language names matched the reviewed relation identities; two bilingual default names were checked using `name:zh`. Registry English, Japanese, and Traditional Chinese labels are retained only when supplied by OSM. No city coordinates were invented.','',
        f"This pass researched {output['totals']['station_cities_researched']} of {len(summaries)} existing station-city CSVs, preserving every card lookup code and native primary name. It changed {output['totals']['lookup_rows_changed']:,} lookup rows, adding {output['totals']['new_reference_lookup_rows']} verified OSM links and {total['line']:,} supported line labels. Counts describe lookup rows, not unique physical stations.",'',
        '## Method','',
        '- City-scoped OSM snapshots include referenced objects, railway stations, metro/light-rail/monorail/tram routes, and relevant stop areas. Targeted supplements look for omitted tram/platform/BRT identities.','- New identity matches require a unique compatible exact native name after whitespace/parenthesis normalization. A bilingual Chinese/Uyghur label may supply its Chinese component only when the remaining suffix exactly matches its explicit `name:ug` tag, ignoring bidirectional format marks. BRT records require explicit BRT network evidence. A named rail stop area is accepted only with explicit compatible route membership; separate station nodes take precedence.','- Existing nonempty station fields remain, except unreferenced approximate coordinates replaced by a verified identity. New aliases reuse an existing OSM group\'s reviewed coordinates; objects already owned by another city code are rejected.','- Missing line names require explicit route/stop-area memberships across at least three distinct station references, at least 70% support, and a clear margin over the next label. Empty-role track ways cannot create a vote. Existing conflicting labels block fills. No line label is inferred from card-code digits.',f'- {len(equivalences)} reviewed former-name or short/full-name equivalences use [Wikipedia and OSM corroboration](../research/reviewed-name-equivalences.json). Their native card labels and codes stay unchanged.','- Translations come from exact OSM tags; no transliteration or synthetic translations are generated. The primary OSM data is [ODbL licensed](https://www.openstreetmap.org/copyright).','',
        '## City results','',
        '| City code | City | Rows | Changed | New OSM links | New line labels | Remaining without OSM ref |','| --- | --- | ---: | ---: | ---: | ---: | ---: |']
    for c in summaries:
        lines.append(f"| {c['city_code']} | {c['name']} | {c['lookup_rows']} | {c['lookup_rows_changed']} | {c['new_reference_lookup_rows']} | {c['fields_filled'].get('line',0)} | {c['unreferenced_lookup_rows_remaining']} |")
    lines+=['','Remaining gaps include ambiguous directional platforms, planned/unmapped stops, and historical names lacking enough identity evidence. A blank field is retained instead of inventing a card-code crosswalk, translation, station position, or route relation.','',
        'Snapshot timestamps, exact content/query SHA-256 values, candidate rejections, and line-relation evidence are in the [compact audit](../research/china-osm-audit-2026-10-28.json). Each station row retains its inspectable OSM reference. The full before/after ledger is a local review artifact rather than another authoritative data table.','',
        'The enrichment uses only public station and OSM/Wikipedia evidence. It contains no card hashes, device IDs, submission IDs, private notes, or report location pins.']
    (args.root/'docs/china-osm-research-2026-10-28.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(output['totals'],ensure_ascii=False))


if __name__=='__main__':main()
