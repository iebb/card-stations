# Data sources and attribution

Every correction or new mapping must cite its evidence in the pull request.
Station CSVs hold no timestamps, matching scores, or per-row source payloads.
Source revisions, checksums, and per-code evidence live in
[`reference/`](reference/README.md). [`licenses/`](licenses/README.md) maps each
path to its license.

| Data | Source | Terms |
| --- | --- | --- |
| Japanese physical stations and route graph | [Seo-4d696b75/station_database](https://github.com/Seo-4d696b75/station_database), revision `76d4d4dbf15aa1ef967fc137b4ddf892abe3f3f8` | [CC BY-SA 4.0](licenses/CC-BY-SA-4.0.txt); see [`licenses/station_database.md`](licenses/station_database.md) |
| Japanese FeliCa and bus code/name registries | Existing CardBal code tables | No upstream grant recorded |
| T-Union stations, lines, gates, and Shanghai/Shenzhen CU prefixes | Domosekai Limited and Trip Reader data contributors, [domosekai/tripreader-data](https://github.com/domosekai/tripreader-data), revision `c5584d6b8d9a39d7162b7b9781134be52db66186` | [CC BY 4.0](licenses/CC-BY-4.0.txt) |
| Additional T-Union station codes (including Wuhan), station renames, Hangzhou Metro CU terminals, and Lingnan Pass metro terminals | Domosekai Limited and Trip Reader data contributors, [HaoTian22/tripreader-data](https://github.com/HaoTian22/tripreader-data) (maintained fork), revision `3b54dbb90607826c4ab7bfa697fa255c4480971e` | [CC BY 4.0](licenses/CC-BY-4.0.txt) |
| Chinese coordinates and OSM names | [OpenStreetMap contributors](https://www.openstreetmap.org/copyright) | [ODbL 1.0](licenses/ODbL-1.0.txt) |
| Three Taizhou station codes and reviewed terminal-to-station links | Domosekai Limited, Trip Reader 读卡识途 1.7.17-cn | APK data terms not specified; not relicensed |
| Base Korean location aliases | [iebb/korean-stations](https://github.com/iebb/korean-stations), revision `f63c4050f862f4b64a530bf923d5f21cd2698847`, SHA-256 `a8b3076d10bd19a18f00fff650b4c96ddfa26d2f7fc458fa801911c4e10e86c0` | Korean public-sector datasets (KORAIL KOTRIS, MOLIT, Seoul Metropolitan Government, Busan BIMS, KRIC, Daegu Transportation Corporation), each under its publisher's terms; Seoul data is [KOGL Type 1](https://www.kogl.or.kr/info/licenseType1.do) |
| Additional Korean aliases and official station fields | [MOLIT settlement inventory, 2026-07-03](https://www.data.go.kr/data/15128614/fileData.do), station-only source revision `5f9f9392e2c6e3312bba1dd6e445b2c5edbd4bf6`, and Seoul stop IDs | Publisher terms; Seoul data is [KOGL Type 1](https://www.kogl.or.kr/info/licenseType1.do) |
| Korean map references and supplementary names | [OpenStreetMap contributors](https://www.openstreetmap.org/copyright) (Geofabrik South Korea extract, 2026-07-28) and [Wikidata labels](https://www.wikidata.org/wiki/Wikidata:Licensing) | OSM-derived data is an [ODbL 1.0](licenses/ODbL-1.0.txt) Derived Database; Wikidata labels are [CC0 1.0](licenses/CC0-1.0.txt) |
| Korean transport modes | [KORAIL KOTRIS, 2023-08-25 dataset](https://www.data.go.kr/data/15121099/fileData.do) | Recorded as “No restrictions on permitted use”; supplementary modes cite their own sources |
| Ulaanbaatar stops, routes, and sequences | Ulaanbaatar Smart Card LLC, UB Smart Bus service | No redistribution license recorded |

## Japan

Decoder names and coordinates come from the same station rows. Synthetic
line-approximation IDs are never presented as OSM references.

Routing geometry uses the `extra` rail polylines from
[station_database](https://github.com/Seo-4d696b75/station_database), revision
`66ba36b937ab40fb53afafb4d0ec10ba652b876a`. Those polylines come from
several origins, including MLIT National Land Numerical Information
(2008/2017) and historical sources such as rail-history.org.
`reference/japan-routing.json` keeps each declared origin, the input hashes,
and coverage. See [routing/README.md](routing/README.md) for the method.

## China (T-Union)

Shenzhen's 284 station-level terminal prefixes come from public
`Guangdong/Shenzhen/cu.csv` at the revision above. The 30 broader line/operator
prefixes are excluded. Names and line labels have no inferred TU station links
or coordinates; file checksums are in `reference/tripreader-provenance.json`.

`reference/tripreader-provenance.json` pins the Trip Reader source-file checksums
and the separate APK supplement. The APK supplies three station codes, `34503113`
(仙居南), `34503116` (临海南), and `34503119` (台州西), plus exact terminal links.
No APK, decompiled code, card identifiers, or travel histories are distributed.

The OSM source snapshots are dated 2026-10-28:

- [China OSM provenance](reference/china-osm.json) records source and query
  hashes, explicit line memberships, and bilingual source tags.
- [Chinese station evidence](reference/china-stations.json) records accepted
  station identities, field sources, and line-specific station bodies.
- [Name equivalences](reference/name-equivalences.json) records former and
  short/full names with Wikipedia and OSM citations.
- [Exact T-Union aliases](reference/tunion-aliases.json) records complete
  observed keys and their independently established station identities.

Cited Wikipedia articles, operator publications, and government naming records
establish historical names. Their coordinates and station numbers are not
imported.

## Korea

The [public station-observations aggregate](https://korean-trip-crowdsourcing.ieb.app/research/station-observations)
identifies observed lookup keys; the accepted codes are listed in
[Korean station provenance](reference/korean-stations.json). MOLIT station facts
come from its 2026-07-03 snapshot. Seoul stop and route joins use
the 2026-08-04 files, and Seoul multilingual labels come from February 2025.

The same reference records input hashes, accepted OSM object versions, ARS IDs,
field sources, and historical Seoul name bridges. `data/korean/modes.csv` holds
mode names once. `reference/korean-mode-metadata.json` keeps the official catalog
metadata and the citations for supplementary modes.

No card identifiers, histories, raw captures, or observation timestamps are
included.

## License scope

The [BSD 3-Clause License](LICENSE) covers the compiler, tooling, and original
contributions. It does not replace upstream data licenses, and it grants nothing
for datasets with no recorded upstream grant. When you redistribute the data, keep
its attribution and share-alike notices.
