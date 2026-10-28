# Data sources and attribution

The migration changes the storage format, grouping, and output generation.
Upstream lookup identifiers, station names, coordinates, and real OSM references
are retained. Source citations and licenses live here and in `reference/`;
timestamps, matching scores, and per-row source payloads are omitted.
Corrections and added mappings must include evidence in their pull request.

| Data | Source | Recorded terms |
| --- | --- | --- |
| Japanese physical stations and route graph | [Seo-4d696b75/station_database](https://github.com/Seo-4d696b75/station_database), revision `76d4d4dbf15aa1ef967fc137b4ddf892abe3f3f8` | CC BY-SA 4.0; see [`licenses/station_database.md`](licenses/station_database.md) |
| Japanese FeliCa and bus code/name registries | Existing CardBal code tables | Separate upstream grant not recorded in the imported assets |
| Published T-Union station, line, gate, and Shanghai CU data | Domosekai Limited and Trip Reader data contributors, [domosekai/tripreader-data](https://github.com/domosekai/tripreader-data), revision `c5584d6b8d9a39d7162b7b9781134be52db66186` | CC BY 4.0 |
| China coordinates and OSM names | [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), retained OSM element type/ID | ODbL 1.0 |
| Three Taizhou station codes and reviewed exact terminal-to-station links | Domosekai Limited, Trip Reader 读卡识途 1.7.17-cn | APK data terms not specified; the public CSV license is not asserted for these mappings |
| Korean exact location aliases | [iebb/korean-stations](https://github.com/iebb/korean-stations), consumer export revision `f63c4050f862f4b64a530bf923d5f21cd2698847`, SHA-256 `a8b3076d10bd19a18f00fff650b4c96ddfa26d2f7fc458fa801911c4e10e86c0` | Retains the upstream source-specific terms; consult its DATA_SOURCES.md and pinned sources |
| Korean transport-mode catalog | [KORAIL KOTRIS, 2023-08-25 dataset](https://www.data.go.kr/data/15121099/fileData.do) | Imported source records “No restrictions on permitted use”; supplementary entries retain separate citations |
| Ulaanbaatar stops, routes, and sequences | Ulaanbaatar Smart Card LLC, UB Smart Bus service | A separate redistribution license was not recorded in the imported snapshot |

Full pinned Trip Reader source-file checksums and the separately identified APK
supplement remain in [`reference/tripreader-provenance.json`](reference/tripreader-provenance.json).
The three APK station codes are `34503113` (仙居南), `34503116` (临海南), and
`34503119` (台州西). These and exact terminal links have distinct provenance.
No APK, decompiled application code, card identifiers, or travel histories are
distributed here.

Korean names come from the pinned station-only consumer export, not later
collection observations or the separate ODbL research export. Missing operator
names remain unknown. Mode names, translations, and classes are normalized into
one `data/korean/modes.csv`, joined by the mode embedded in each location code.
`reference/korean-mode-metadata.json` preserves the
official catalog metadata and supplementary-mode citations.

Japanese decoder names now come from the same station rows as coordinates;
empty unnamed registry entries and duplicate spelling tables are not carried
forward. Terminal names inherit from linked stations when identical. Synthetic
line-approximation IDs are not presented as OSM references. Matching diagnostics and administrative lookup metadata are outside the station
CSVs. Routing tables are separate. These format changes do not add new station mappings.

The MIT license covers this repository's compiler and contribution tooling.
It does not replace upstream data licenses or supply missing permission for
datasets whose grant was not recorded. Consumers must retain applicable
attribution and share-alike notices for the data they redistribute.

Japanese routing geometry uses the `extra` rail polylines in
[station_database](https://github.com/Seo-4d696b75/station_database), revision
`66ba36b937ab40fb53afafb4d0ec10ba652b876a`. The project publishes rail polylines from source-specific origins, including
MLIT National Land Numerical Information 2008/2017 and historical sources such
as rail-history.org; declared origins are retained in the routing provenance. We clip
continuous source paths between verified station positions, then quantize
vertices to nine-character geohashes with shared-prefix compression. Exact
input hashes and coverage are in `reference/japan-routing.json`. The source
license notice is retained in `licenses/station_database.md`. Unmatched edges
retain their prior distance and have no claimed detailed geometry.
