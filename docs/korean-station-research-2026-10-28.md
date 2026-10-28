# Korean station research, 2026-10-28

All 1,142 existing card-code rows were checked against the reviewed station-only
export at revision `5f9f9392e2c6e3312bba1dd6e445b2c5edbd4bf6`. This pass also
adds its 977 exact bus aliases and 407 independently cleared current aliases.
All 1,384 occur in the current aggregate observations.
Each was independently reproduced from the official MOLIT settlement inventory
using its already reviewed code and source-ID join. The catalog now has 2,526
codes. Another 2,826 observed codes lack a reviewed source mapping and remain
outside the station CSVs. No code was invented from a station name or OSM ID.

The changes add 773 OSM references across 684 distinct objects: 336 references
on existing codes and 437 on new codes. A further 137 existing rows gain coordinates;
766 new rows have coordinates from an exact official bridge or an accepted OSM
identity. Existing native names and all populated fields are preserved. Empty
operator and line fields remain empty when the source does not establish them.
Modes remain in `data/korean/modes.csv`; all new aliases already have cataloged
modes.
Three added coordinate pairs reuse the same verified TOPIS stops' existing
reviewed points; the official snapshot differences were under nine millimetres.

The additional 407 codes received an independent [official-ID and dated-name
review](korean-collected-candidates-review-2026-10-28.md). Three historical Seoul
name variants were resolved through exact dated ARS/TOPIS links, and six
Hwaseong district changes were checked against the current official inventory.
Both new-code groups are listed separately in the audit.

## Evidence and matching

The compact [audit](../research/korean-osm-audit-2026-10-28.json) records the exact
new codes, export/input hashes, accepted OSM object versions, official ARS stop
IDs, added-field sources and withheld matches. It contains station data only.
Source-internal identity keys, raw observations, event counts and personal data
are excluded. Field-source abbreviations have one shared legend; exact
TOPIS node IDs are evidence for official coordinates, never OSM references.

- [MOLIT, 국토교통부_정류장 현황_20260703](https://www.data.go.kr/data/15128614/fileData.do):
  134,442 rows, SHA-256
  `10d25ec17b6cb4258e3f071ea2c465a2fa3a41d490d5db25b865cc47f9aa164e`.
  Each new alias retains the exact reviewed seven-digit settlement ID and mode.
  The official name, bus classification, province and district must agree.
  The `모바일아이디` column also supplies an explicit ARS ID where its exact
  station-ID/name/administrative state agrees. Missing or conflicting IDs stay
  unresolved.
- Seoul Metropolitan Government [stop locations](https://data.seoul.go.kr/dataList/OA-15067/S/1/datasetView.do?tab=A)
  and [multilingual stop names](https://data.seoul.go.kr/dataList/OA-12830/A/1/datasetView.do):
  the collected 2026-08-04 location and February 2025 translation snapshots,
  joined through reviewed current CardBal-to-TOPIS IDs or exact guarded
  MOLIT-ARS-to-TOPIS links. Official English, Japanese and Simplified Chinese
  labels are retained; Traditional Chinese is the source's deterministic
  OpenCC conversion of the accepted official Simplified Chinese label. These files are
  provided under KOGL Type 1 and attributed to Seoul Metropolitan Government.
  Export and bridge checksums, exact dataset dates and primary download URLs
  are pinned in the audit. New complete-inventory joins require a unique ARS ID,
  equal full Korean identity and equal official district. A dated historical
  name exception requires its separately reviewed exact ID bridge.
- [Geofabrik South Korea](https://download.geofabrik.de/asia/south-korea.html):
  `south-korea-260728.osm.pbf`, SHA-256
  `335ed4c16754d13b23284b2cfc662ad261cfedf6d6b8b1205338ee32f97f2895`.
  The accepted objects were checked through the primary OSM API on 2026-10-28,
  including their current names, stop IDs, transit tags, geometry and versions.
  Missing coordinates use the accepted live object point or platform-way
  center, unless an existing coordinate already represents that same ref.
- Explicit OSM multilingual names and Korean-identity-checked linked Wikidata
  labels fill empty cells only. The collected Wikidata label cache has SHA-256
  `e26a7e06414bb3cc19f5f864b4368fd3f005be5eab51f02d593921a3cf1239ef`.
  Deterministic OpenCC conversion completes a missing Chinese script from a
  present official Chinese label; it does not translate a Korean station name.

Rail matches require an equal Korean station identity and a source point within
150 metres, with explicit source refs or operator identity resolving competing
features. The recorded feature may be a station or an identified rail stop
position. Bus matches require equal Korean identity and the same explicit
official ARS ID. A single platform can be selected over its matching on-road
stop position; two competing platform features stay unresolved. The source
province and available official coordinates must also agree.

For example, `917562300215` (이천역), official ARS `32514`, matches
[OSM node 7573622836](https://www.openstreetmap.org/node/7573622836), while
`2802601001F0` (송도더샵퍼스트월드(동문)), ARS `38013`, matches
[node 11379636156](https://www.openstreetmap.org/node/11379636156).
`0000010000C9` (시청) matches
[node 9467463479](https://www.openstreetmap.org/node/9467463479), whose rail ref
is `201`.

## Unresolved cases and preservation

Name-only global clusters and name-plus-distance bus candidates were rejected:
the opposite stop can be the only mapped feature. `2803231001E3` (배다리), ARS
`35186`, has two competing bus-stop features,
[436873979](https://www.openstreetmap.org/node/436873979) and
[4903334643](https://www.openstreetmap.org/node/4903334643), so no ref was added.
The deleted live objects `node/9322069255` and `node/9322069253` were also rejected.

Twelve rail rows share a physical OSM station candidate with another row but
retain different official line-specific coordinates. Their coordinates were
preserved and the conflicting refs withheld. Every ref actually present in the
CSV now has one identical numeric coordinate pair across its aliases. Exact
rows and retained points are listed in the audit.

© OpenStreetMap contributors. The OSM-derived Korean station data is an
[ODbL 1.0 Derived Database](https://www.openstreetmap.org/copyright).
[Wikidata structured labels are CC0](https://www.wikidata.org/wiki/Wikidata:Licensing).
The official source-specific terms remain applicable; this research does not
relicense the official inputs under the compiler's MIT license.
