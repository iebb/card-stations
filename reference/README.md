# Reference formats and source evidence

The CSVs under [`data/`](../data/) are authoritative. These reference files
explain source identity, revisions, checksums, and verified mappings.
[SCHEMA.md](../SCHEMA.md) defines CSV fields and terminal lookup rules;
[DATA_SOURCES.md](../DATA_SOURCES.md) and
[licenses/](../licenses/README.md) record attribution and license scope.

Codes are strings with leading zeroes intact. `osm_ref` is an actual OSM
`node/ID`, `way/ID`, or `relation/ID`. Dates identify source snapshots or
historical names. Source-relative paths in checksum maps belong to the pinned
upstream repository, rather than this repository.

## Chinese stations

| File | Format and contents |
| --- | --- |
| [china-osm.json](china-osm.json) | `card-stations-china-osm-provenance-v1`: `source_snapshots` records city-scoped OSM payload and query hashes; `line_memberships` cites route relation IDs; `bilingual_names` preserves source tags. |
| [china-stations.json](china-stations.json) | `card-stations-china-station-evidence-v1`: `entries` joins exact `code` values to current CSV identity fields and an `evidence` array of public sources, field sources, and historical names. `excluded_osm_ref` distinguishes an incorrect station body from the accepted identity. |
| [name-equivalences.json](name-equivalences.json) | `card-stations-name-equivalences-v1`: `entries` identifies each exact code, retained native name, documented equivalent name, OSM identity, route memberships, and source citations. |
| [tunion-aliases.json](tunion-aliases.json) | `card-stations-tunion-aliases-v1`: `aliases` maps complete observed keys to an existing `station_code`, with independent OSM identity and public station sources. Keys are exact matches, never prefixes. |
| [tripreader-provenance.json](tripreader-provenance.json) | `sources` pins the upstream repository revision and individual file hashes, and identifies the separate APK supplement and its terms. |

OSM establishes physical identity; it does not establish a card lookup code.
An observed alias establishes only that exact key. Preserve the full string,
including trailing zeroes. See the [matching rules](../AGENTS.md) and
[maintenance guide](../CONTRIBUTING.md#osm-maintenance).

## Korean stations

[korean-stations.json](korean-stations.json) uses
`card-stations-korean-station-provenance-v1`:

- `sources` pins official data revisions, hashes, OSM object-version URL
  templates, and public source locations.
- `observed_alias_codes` lists accepted complete lookup keys.
- `official_seoul_stations` records official station ID and name bridges.
- `osm_matches` records accepted OSM identities, object versions, and matching
  rules for the listed codes.
- `field_sources`, `field_source_legend`, and `ars_source_legend` identify the
  origin of station fields and ARS identifiers.
- `seoul_name_bridges` and `administrative_names` document historical names and
  administrative recodes without changing the catalog's primary names.
- `coordinate_identities` records shared official station identities and their
  consistent coordinates.

[korean-mode-metadata.json](korean-mode-metadata.json) records official transport
mode metadata and supplementary mode citations.

## Routing

[japan-routing.json](japan-routing.json) pins geometry sources and hashes.
[routing-fallbacks.json](routing-fallbacks.json) documents why specific edges
retain fallback geometry. Graph fields and geometry encoding are defined in the
[routing format](../routing/README.md).
