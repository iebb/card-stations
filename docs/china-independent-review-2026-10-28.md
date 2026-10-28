# Independent enrichment review — 2026-10-28

This review sampled the city's new-identity ledger and route-label evidence; it
is separate from the enrichment algorithm's own checks. No source CSV was edited
by the reviewer.

## Identity samples

The higher-interest matches were checked against current primary OSM API data:

- Tianjin [瑞景新苑 relation 19886973](https://www.openstreetmap.org/relation/19886973)
  and Shanghai [莲溪路 relation 19631195](https://www.openstreetmap.org/relation/19631195)
  are explicitly tagged subway stations, not unrelated area features. A
  multipolygon's centre is used when no single station node supplies the record.
- Suzhou [华元路东](https://www.openstreetmap.org/node/7099222614),
  [洋泾](https://www.openstreetmap.org/node/7099222610), and
  [虎北路](https://www.openstreetmap.org/node/7099206592) have exact native-name
  matches and subway-station tags. The latter two also retain distinct old-name
  tags, which are not substituted as new card codes.
- Ningbo [镇海大道(慈海)](https://www.openstreetmap.org/node/12520995759) matches the
  existing full-width-parenthesis label after punctuation normalization. The
  qualifier 慈海 remains present; it is not stripped to force a match.
- Nanjing [方州广场](https://www.openstreetmap.org/node/7998534650), Hefei
  [省博物院](https://www.openstreetmap.org/node/3473112202), and Taizhou
  [仙居南](https://www.openstreetmap.org/node/8541577162),
  [临海南](https://www.openstreetmap.org/node/8566213144), and
  [台州西](https://www.openstreetmap.org/node/7714110156) also match the existing
  names and compatible rail-station types.

No incorrect physical identity was found in these samples. This does not assert
that every unreviewed name match is correct. Existing reference-coordinate reuse
and the city-ownership guard avoid introducing contradictory coordinates or a
second city owner for an already known OSM object.

## Route labels

The inspected ledger derives labels from route/stop-area memberships, not from
the numeric card line code. For example, card group `3010000D` is supported as
Nanjing Line 7 by route relations `15336345` / `15336347`, even though the card
code suffix is not the public line number. Evidence thresholds require multiple
unique station references and a clear majority, with conflicts blocking a fill.

The initial membership helper accepted empty-role track ways despite its
explicit-stop comment. This was fixed before the final pass: an empty role now
requires known station/stop/platform tags or an explicit stop-area stop/platform
member. The final helper was independently inspected, and the enrichment
author's eight passing tests include this regression. A route merely passing
along track cannot create a station vote.

## Nine reviewed name equivalences

These are explicit exceptions for existing lookup rows, not a fuzzy-name rule.
[The reviewed equivalences](../research/reviewed-name-equivalences.json) contain the exact code-to-node assignments,
available line-specific stop areas, source routes, and citations. The two
Lanzhou entries below use live station-node tags and cited name history; the
station query did not supply stop-area/route evidence for those two entries.

- Shanghai's 黄陂南路 / 新天地 labels are recorded as former names in
  [一大会址·黄陂南路站](https://zh.wikipedia.org/wiki/一大会址·黄陂南路站) and
  [一大会址·新天地站](https://zh.wikipedia.org/wiki/一大会址·新天地站).
  OSM also retains exact `alt_name:zh` values. Separate Line 1 / 14 nodes and
  Line 10 / 13 nodes must be kept; choosing the first same-named node would be
  wrong for a line-specific row.
- Nanjing [草场门站](https://zh.wikipedia.org/wiki/草场门站) identifies the full
  草场门·南艺·二师 name, the shortened lookup name, and the name/hint change.
  Primary OSM stop areas independently link node `9164951625` to both Lines 4
  and 7. The two existing card rows can share this physical node.
- [徐庄站](https://zh.wikipedia.org/wiki/徐庄站) identifies 徐庄·苏宁总部 as
  the full name and explains its name/hint change. Node `9164951632` is linked
  to explicit Line 4 stop memberships.

Native card lookup names and card codes remain unchanged. Wikipedia's public
station numbers are not card-code evidence. Only the reviewed physical identity,
OSM coordinates, references, and source-provided translations are added.

## Public-data boundary

The ledger uses station fields and public OSM/Wikipedia sources. It contains no
card hashes, device identifiers, submission identifiers, private notes, or report
location pins. The separate report audit recommends only exact publicly shown
station-code strings, with all name-only reports left unresolved as mappings.

## Final station identity checks

The final review inspected all seven requested lower-priority stop-area relations: Beijing 1596678/1652652, Shanghai 19059550/19059554/19083809, Nanjing 3955385, and Hangzhou 11076850. Each has an exact native area label and explicit compatible rail/tram stop or platform members on route relations. No false station identity was found. Stop-area centres are grouped representative points; the mixed bus/rail Terminal 2 area is supported specifically by Airport Line subway routes 2062998/2062999. The source lookup names and codes remain unchanged.

All 18 new Urumqi references were inspected. The bilingual rule extracts only an all-Han prefix separated by whitespace from the exact explicitly tagged name:ug suffix, after removing Unicode format controls. It does not transliterate or perform fuzzy matching. All matched objects have explicit railway=station and subway tags; some older OSM nodes additionally have public_transport=stop_position. This tag inconsistency does not alter the independently supported station identity.

Two final Lanzhou exceptions are documented in reviewed-name-equivalences.json: 821000010021 深安大桥南 matches [node/6563923252](https://www.openstreetmap.org/node/6563923252), whose live old_name is exact; [the station article](https://zh.wikipedia.org/wiki/奥体中心站_(兰州市)) records the 2023-11-22 rename to 奥体中心. 821000010022 兰州城市学院 matches [node/6563941615](https://www.openstreetmap.org/node/6563941615) 兰州城市学院（省科技馆）; [the station article](https://zh.wikipedia.org/wiki/兰州城市学院（省科技馆）站) and [the Line 1 article](https://zh.wikipedia.org/wiki/兰州轨道交通1号线) corroborate the full and short names. The latter is a short/full-name equivalence, not an official former-name claim. Only live OSM coordinates are proposed; Wikipedia station numbers and coordinates are not imported.

The final preview covers all 39 existing station cities and 5,713 lookup rows,
with 101 new OSM references and 3,068 rows enriched. Independent checks found
no changed existing lookup codes/native names and no inconsistent coordinate pairs for shared OSM references. Public city research/audit artifacts contain no private report identifiers or card-family fields. No unresolved blocker was found in the reviewed samples; this is a targeted identity audit, not independent verification of every OSM object.
