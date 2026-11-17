Use `master` as the default branch.

CSV files under `data/` are the authoritative station sources. Preserve text
identifiers and leading zeroes. Never add personal card identifiers, histories,
raw captures, credentials, or APK binaries. Document upstream sources and terms
in DATA_SOURCES.md. Run `python3 build.py --check` and
`python3 -m unittest discover -s tests -v` before committing data or compiler changes.

# Station evidence rules

Follow these rules when adding OSM references, coordinates, names, or new codes.
Record verified per-code facts and their public sources under `reference/`.
Keep documentation focused on formats, source evidence, and maintenance guides.
Do not add dated reports, work logs, progress summaries, or candidate inventories.

## Always

- Never change an existing card code. Change a native primary name only for an
  official rename documented upstream or in `reference/`, and keep the former
  name in that evidence. Add identity, coordinates, references, and translations
  around them.
- Never derive a code from a station name, an OSM ID, a terminal number, or a
  public station number. Never infer a line or physical station from the digits
  or order of card codes.
- Fill empty cells only. Keep existing non-empty fields. The one exception is an
  unreferenced, interpolated coordinate, which can be replaced once a verified
  identity is established.
- Leave a cell empty when the evidence is ambiguous. Do not pick one of several
  candidates, guess a direction, or use the nearest node.
- Every alias that shares an `osm_ref` must have identical coordinates. Reuse the
  coordinates already reviewed for that reference.
- Translations come only from exact source tags or official multilingual data.
  Do not transliterate or machine-translate. OpenCC may convert between Chinese
  scripts only when an official Chinese label exists. Omit source labels with
  obvious defects; do not invent a corrected version.
- Wikipedia can confirm identity, history, and published names. Do not import its
  coordinates or station numbers.
- A physical identity says nothing about service. Do not claim that a reserved,
  unopened, or under-construction station is operating.
- Use only public station facts. Leave out card hashes, device or submission IDs,
  private notes, report location pins, observation timestamps, and raw payloads.
  Pin source revisions and SHA-256 checksums in the reference data.

## Chinese (T-Union) stations

- A new match needs a unique, compatible OSM object with the exact native name,
  after only NFKC, whitespace, and parenthesis normalization. Rail rows need rail
  tags; BRT rows need explicit BRT network evidence. Entrances never match.
- Prefer a station node. Use a stop area only with explicit compatible route
  membership. When a station has separate directional platforms, use the stop
  area's bounding-box centre to represent the station group.
- A Chinese/Uyghur bilingual `name` can supply its all-Han prefix only when the
  rest of it exactly equals the explicit `name:ug` tag, ignoring Unicode format
  controls.
- Former, engineering, or short/full names need a documented source, such as an
  OSM `old_name`/`alt_name`, a Wikipedia station history, an operator naming
  table, or a government approval. List each one individually in
  `reference/name-equivalences.json`. Spelling-only variants, such as
  蒌葑/娄葑 and 卢葭/芦葭, stay unresolved without a published alias.
- A card city is a lookup namespace, not administrative containment. Intercity
  and cross-boundary lines can reference stations in another city, and several
  city CSVs can share one OSM identity. Otherwise, reject an object that another
  city code already owns. Check line-specific station bodies: two operators at
  one interchange usually have separate nodes.
- Reject a candidate that lies more than 700 m from an existing approximate
  point.
- Fill an empty `line` only when the line group has at least three distinct
  station references with explicit route or stop-area membership, at least 70%
  of them agree, and the runner-up has at most half the winner's support. A route
  member with an empty role counts only if it is a known station, stop, or
  platform. An existing label that conflicts blocks the fill.
- `scripts/enrich_china.py` implements these rules over cached city-scoped
  Overpass snapshots. Keep generated diagnostics in ignored `dist/`; commit only
  independently supported facts and their source evidence.

## Korean stations

- A new code must come from a reviewed source mapping. For bus aliases, use the
  official MOLIT settlement ID (seven decimal digits and a zero nibble) followed
  by the four-hex mode. The mode must be in the KOTRIS bus class. The ID must be
  bus-only, with one consistent native name and province/district. The code must
  have a normal entry or exit in the public station-observations aggregate.
- Do not let a name ending in 역 turn a bus stop into a rail station.
- A rail OSM match needs an equal Korean station identity within 150 m, and
  explicit refs or operator identity must resolve competing features.
- A bus OSM match needs an equal Korean identity and the same official ARS ID.
  Prefer a single platform over its on-road stop position. When two features
  share an ARS ID, add no reference. Name-plus-distance alone never qualifies.
- Join Seoul data through a unique ARS ID with equal full Korean name and equal
  district. A dated historical name needs its own reviewed ID bridge. TOPIS node
  IDs are official identifiers, not OSM references.
- Treat administrative recodes, such as Hwaseong's 2026 district split, and
  punctuation-only differences as the same identity. Keep existing labels.
- When rail rows share an OSM candidate but have different official
  line-specific coordinates, keep their coordinates and withhold the reference.

## Station reports

An incoming report can add an alias only when it shows the complete card key
exactly as decoded and an independent OSM station identity backs it. Keep the
full observed string. Do not strip zeroes or shorten it. Report location pins
are not coordinates. A name-only report creates no mapping, even when the
catalog already has a station with that name.
