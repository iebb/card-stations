# Licenses

The compiler, adapters, routing code, scripts, tests, schema, documentation, and
original contributions are licensed under the [BSD 3-Clause License](../LICENSE).

Third-party data keeps its upstream license. When a file combines sources, each
field remains under the license of the source it came from. Where an upstream
license is share-alike, adapted files are shared under that license. The BSD
license does not apply to imported data or replace a missing upstream grant.
[DATA_SOURCES.md](../DATA_SOURCES.md) records revisions, checksums, and evidence.

| Path | Upstream | License |
| --- | --- | --- |
| `data/japanese-ic/stations/`, `data/japanese-ic/edges.csv`, `reference/japan-routing.json` | [station_database](https://github.com/Seo-4d696b75/station_database) by Seo-4d696b75: physical stations, lines, route graph, and rail polylines | [CC BY-SA 4.0](CC-BY-SA-4.0.txt); [source terms](station_database.md) |
| Japanese FeliCa station codes and `data/japanese-ic/bus-companies.csv` | Existing CardBal code registries | No upstream grant recorded; not relicensed |
| `data/t-union/` station, line, gate, and `cityunion/` rows | Domosekai Limited and the [Trip Reader data](https://github.com/domosekai/tripreader-data) contributors | [CC BY 4.0](CC-BY-4.0.txt) |
| `data/t-union/` coordinates, OSM names, and `osm_ref` values; China audits under `research/` | [© OpenStreetMap contributors](https://www.openstreetmap.org/copyright) | [ODbL 1.0](ODbL-1.0.txt) Derived Database |
| Three Taizhou station codes and the APK terminal-to-station links in `data/t-union/` | Domosekai Limited, Trip Reader 读卡识途 1.7.17-cn | No terms specified; not relicensed |
| `data/korean/stations/` codes, names, and official fields | Korean public-sector datasets: KORAIL KOTRIS, MOLIT, Seoul Metropolitan Government, Busan BIMS, KRIC, and Daegu Transportation Corporation | Each publisher's terms; Seoul data is [KOGL Type 1](https://www.kogl.or.kr/info/licenseType1.do) |
| `data/korean/stations/` coordinates and OSM references; Korean audits under `research/` | [© OpenStreetMap contributors](https://www.openstreetmap.org/copyright), Geofabrik South Korea extract of 2026-07-28 | [ODbL 1.0](ODbL-1.0.txt) Derived Database |
| Supplementary Korean names | [Wikidata](https://www.wikidata.org/wiki/Wikidata:Licensing) | [CC0 1.0](CC0-1.0.txt) |
| `data/korean/modes.csv`, `reference/korean-mode-metadata.json` | [KORAIL KOTRIS, 2023-08-25 dataset](https://www.data.go.kr/data/15121099/fileData.do) | Recorded as “No restrictions on permitted use” |
| `data/u-money/` | Ulaanbaatar Smart Card LLC, UB Smart Bus service | No redistribution license recorded; not relicensed |

## Attribution

Products that redistribute these files must keep the notices that apply:

- © OpenStreetMap contributors, ODbL 1.0
- Japanese station data: station_database by Seo-4d696b75, CC BY-SA 4.0
- T-Union data: Domosekai Limited and the Trip Reader data contributors, CC BY 4.0
- Contains Seoul Metropolitan Government public data, KOGL Type 1

## License texts

`CC-BY-SA-4.0.txt`, `CC-BY-4.0.txt`, `ODbL-1.0.txt`, and `CC0-1.0.txt` are the
canonical texts from SPDX license-list-data v3.27.0. `station_database.md`
reproduces station_database's own terms and disclaimer.
