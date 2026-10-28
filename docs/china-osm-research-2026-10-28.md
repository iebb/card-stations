# Chinese station research — 2026-10-28

All 368 city-code registry entries were checked against current primary OSM administrative relations. Their exact Chinese names or explicit Chinese-language names matched the reviewed relation identities; two bilingual default names were checked using `name:zh`. Registry English, Japanese, and Traditional Chinese labels are retained only when supplied by OSM. No city coordinates were invented.

This pass researched 39 of 39 existing station-city CSVs, preserving every card lookup code and native primary name. It changed 3,068 lookup rows, adding 101 verified OSM links and 1,304 supported line labels. Counts describe lookup rows, not unique physical stations.

## Method

- City-scoped OSM snapshots include referenced objects, railway stations, metro/light-rail/monorail/tram routes, and relevant stop areas. Targeted supplements look for omitted tram/platform/BRT identities.
- New identity matches require a unique compatible exact native name after whitespace/parenthesis normalization. A bilingual Chinese/Uyghur label may supply its Chinese component only when the remaining suffix exactly matches its explicit `name:ug` tag, ignoring bidirectional format marks. BRT records require explicit BRT network evidence. A named rail stop area is accepted only with explicit compatible route membership; separate station nodes take precedence.
- Existing nonempty station fields remain, except unreferenced approximate coordinates replaced by a verified identity. New aliases reuse an existing OSM group's reviewed coordinates; objects already owned by another city code are rejected.
- Missing line names require explicit route/stop-area memberships across at least three distinct station references, at least 70% support, and a clear margin over the next label. Empty-role track ways cannot create a vote. Existing conflicting labels block fills. No line label is inferred from card-code digits.
- 9 reviewed former-name or short/full-name equivalences use [Wikipedia and OSM corroboration](../research/reviewed-name-equivalences.json). Their native card labels and codes stay unchanged.
- Translations come from exact OSM tags; no transliteration or synthetic translations are generated. The primary OSM data is [ODbL licensed](https://www.openstreetmap.org/copyright).

## City results

| City code | City | Rows | Changed | New OSM links | New line labels | Remaining without OSM ref |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1000 | 北京市 | 648 | 560 | 14 | 0 | 14 |
| 1121 | 天津市 | 241 | 63 | 1 | 57 | 6 |
| 2210 | 沈阳市 | 136 | 37 | 0 | 37 | 0 |
| 2220 | 大连市 | 109 | 20 | 0 | 18 | 5 |
| 2610 | 哈尔滨市 | 78 | 71 | 0 | 0 | 1 |
| 2900 | 上海市 | 612 | 528 | 16 | 0 | 34 |
| 3010 | 南京市 | 234 | 172 | 5 | 36 | 5 |
| 3020 | 无锡市 | 98 | 10 | 0 | 10 | 2 |
| 3030 | 徐州市 | 54 | 0 | 0 | 0 | 0 |
| 3040 | 常州市 | 44 | 0 | 0 | 0 | 0 |
| 3050 | 苏州市 | 277 | 104 | 3 | 56 | 2 |
| 3060 | 南通市 | 28 | 28 | 0 | 28 | 0 |
| 3310 | 杭州市 | 311 | 311 | 1 | 311 | 2 |
| 3320 | 宁波市 | 217 | 1 | 1 | 0 | 2 |
| 3330 | 温州市 | 41 | 41 | 0 | 41 | 3 |
| 3350 | 嘉兴市 | 13 | 13 | 0 | 13 | 3 |
| 3370 | 绍兴市 | 47 | 9 | 0 | 9 | 3 |
| 3380 | 金华市 | 27 | 0 | 0 | 0 | 0 |
| 3450 | 台州市 | 18 | 18 | 3 | 15 | 0 |
| 3610 | 合肥市 | 80 | 76 | 1 | 0 | 0 |
| 3620 | 芜湖市 | 36 | 19 | 0 | 0 | 0 |
| 3750 | 滁州市 | 14 | 6 | 0 | 0 | 0 |
| 3910 | 福州市 | 22 | 0 | 0 | 0 | 0 |
| 3930 | 厦门市 | 122 | 100 | 25 | 0 | 21 |
| 4210 | 南昌市 | 57 | 54 | 0 | 0 | 1 |
| 4510 | 济南市 | 48 | 1 | 0 | 0 | 1 |
| 4520 | 青岛市 | 179 | 75 | 4 | 46 | 12 |
| 4930 | 洛阳市 | 19 | 1 | 0 | 0 | 2 |
| 5510 | 长沙市 | 208 | 11 | 2 | 9 | 4 |
| 5810 | 广州市 | 350 | 40 | 2 | 31 | 25 |
| 5880 | 佛山市 | 50 | 49 | 2 | 23 | 1 |
| 6020 | 东莞市 | 15 | 14 | 0 | 0 | 1 |
| 6510 | 成都市 | 398 | 398 | 0 | 398 | 4 |
| 6900 | 重庆市 | 333 | 56 | 1 | 43 | 1 |
| 7010 | 贵阳市 | 99 | 48 | 0 | 42 | 3 |
| 7310 | 昆明市 | 114 | 13 | 0 | 0 | 0 |
| 7910 | 西安市 | 295 | 81 | 0 | 81 | 32 |
| 8210 | 兰州市 | 20 | 20 | 2 | 0 | 0 |
| 8810 | 乌鲁木齐市 | 21 | 20 | 18 | 0 | 0 |

Remaining gaps include ambiguous directional platforms, planned/unmapped stops, and historical names lacking enough identity evidence. A blank field is retained instead of inventing a card-code crosswalk, translation, station position, or route relation.

Snapshot timestamps, exact content/query SHA-256 values, candidate rejections, and line-relation evidence are in the [compact audit](../research/china-osm-audit-2026-10-28.json). Each station row retains its inspectable OSM reference. The full before/after ledger is a local review artifact rather than another authoritative data table.

The enrichment uses only public station and OSM/Wikipedia evidence. It contains no card hashes, device IDs, submission IDs, private notes, or report location pins.
