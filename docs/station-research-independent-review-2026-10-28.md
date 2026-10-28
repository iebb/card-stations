# Independent station identity review — 2026-10-28

The integration review checked ten higher-risk Chinese proposals against the
live primary OSM API, separately from the two research agents. Wikipedia
corroborated former names, station layouts, and line context. This is a targeted
review of identity decisions, not independent verification of every map object.

- **Separate station bodies:** Foshan Line 2's Guangzhou South is
  [node/9372157614](https://www.openstreetmap.org/node/9372157614), explicitly
  tagged with the Foshan operator and `F227`. The
  [station article](https://zh.wikipedia.org/wiki/广州南站_(地铁)) distinguishes
  its west-square station from Guangzhou Lines 2/7 and 22. Hanghai's
  [node/9439672136](https://www.openstreetmap.org/node/9439672136) is west of the
  nearby Hangzhou Line 9 node, consistent with the
  [Hanghai layout](https://zh.wikipedia.org/wiki/杭海城际).
- **Rail versus metro:** Xianyang West
  [node/11207125789](https://www.openstreetmap.org/node/11207125789) is explicitly
  a subway station, distinct from the national-rail station. The
  [metro article](https://zh.wikipedia.org/wiki/咸阳西站_(地铁)) corroborates the
  Line 1 identity. The misspelled OSM English label was flagged for exclusion.
- **Historical names:** Dongxinyuan
  [node/9852293351](https://www.openstreetmap.org/node/9852293351) has the exact
  `old_name=香积寺路`; the [station history](https://zh.wikipedia.org/wiki/东新园站)
  records the January 2022 rename. Xiamen
  [stop area/2334368](https://www.openstreetmap.org/relation/2334368) still uses
  the old 文灶 label, while the [Jinbang Park article](https://zh.wikipedia.org/wiki/金榜公园站)
  identifies that old physical site and the 2019 rename. Existing card lookup
  names are retained; a current name alone does not prove that an older code
  should move to another station.
- **Station groups and status:** Songdong Road
  [stop area/19059548](https://www.openstreetmap.org/relation/19059548) explicitly
  groups two tram stops and two platforms. A group centre represents that
  station, without claiming a particular directional platform. Chongqing
  [Xinqiao node/9436112295](https://www.openstreetmap.org/node/9436112295) is tagged
  as a subway station under construction with `ref=9/01`; adding its physical
  reference does not assert that it is operating. The
  [Line 9 article](https://zh.wikipedia.org/wiki/重庆轨道交通9号线) lists it as unopened.

The remaining sampled nodes were Shanghai Line 11's
[Huaqiao](https://www.openstreetmap.org/node/3506766921),
[Guniangqiao](https://www.openstreetmap.org/node/9471678351), and
[Sifanghe](https://www.openstreetmap.org/node/11434854460). Their explicit station
identities support the reviewed line or qualified-name decisions.

Card-city prefixes describe lookup namespaces, not administrative containment.
An intercity service can therefore reuse the same verified OSM identity across
city CSVs. Such aliases must share a consistent physical coordinate.

## Korean samples

Live primary OSM checks corroborated the exact stop IDs for
[Icheon Station bus stop/7573622836](https://www.openstreetmap.org/node/7573622836)
(`ref=32514`) and
[Songdo The Sharp First World east entrance/11379636156](https://www.openstreetmap.org/node/11379636156)
(`ref=38013`). A station's name and proximity alone cannot establish a
particular directional bus stop. Name-and-distance-only bus candidates were
excluded from the accepted map-reference set.

[Baedari/436873979](https://www.openstreetmap.org/node/436873979) and
[Baedari/4903334643](https://www.openstreetmap.org/node/4903334643) both carry
`ref=35186` and the same Korean name. This unresolved duplicate shows why even
an exact stop ID must identify one supported physical object; a nearest-node
choice was rejected.

Rail samples
[Gayang/9181579793](https://www.openstreetmap.org/node/9181579793) and
[City Hall/9467463479](https://www.openstreetmap.org/node/9467463479) have explicit
station/subway tags and the reviewed operator or line reference. Exact names,
line/operator context, and source station identity distinguish them from
homonyms and other line-specific station nodes.

Two spelling-only Chinese proposals were also cross-reviewed by both agents:
蒌葑 versus 娄葑 and 卢葭 versus 芦葭. Public sources establish the real stations,
but do not document those lookup spellings as aliases. Both physical-reference
mappings are deferred under the same standard.

## Related station-body corrections

Reviewing shared city namespaces exposed two pre-existing line-specific
reference errors. The [correction ledger](../research/station-body-corrections-2026-10-28.json)
records the old and new references, coordinates and exact public evidence.
Both changes were independently checked against live primary OSM relations.

- Suzhou Line 11 key `305000110067` now uses
  [node/8992739373](https://www.openstreetmap.org/node/8992739373) and
  [stop area/16025192](https://www.openstreetmap.org/relation/16025192).
  [Suzhou Line 11](https://www.openstreetmap.org/relation/16025193) explicitly
  serves its stop members. The previous node belongs to Shanghai Line 11.
  [The station layout](https://zh.wikipedia.org/wiki/花桥站_(昆山市地铁车站)) distinguishes
  Shanghai's elevated station from Suzhou's underground station.
- Nanhai Tram key `588000610001` now uses
  [node/9016807913](https://www.openstreetmap.org/node/9016807913), explicitly
  tagged light rail with `TNH101`, and
  [stop area/13124234](https://www.openstreetmap.org/relation/13124234).
  [The tram route](https://www.openstreetmap.org/relation/13103097) serves its
  stops. The previous reference is Guangfo subway station `GF13`.
  [The tram station article](https://zh.wikipedia.org/wiki/𧒽岗站_(有轨电车))
  distinguishes its platforms from the connecting subway platforms.

These two corrections retain every code, native name and other populated field.
They are additional to the 157 references added for the original 190 gaps.
Beijiao Park, Dongping and Guniangqiao still legitimately share one OSM station
across card-city namespaces; explicit multi-line references support those shared
identities. The app generator must accept such aliases without assigning an
arbitrary single lookup city to the physical station.
