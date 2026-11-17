# Contributing

Target `master`. Edit the appropriate CSV and cite the source in your pull request.
New city/company files are discovered automatically through `schema.json`.

- Keep only codes, names, lines, coordinates, and OSM references in station rows.
- Use the shared names in [SCHEMA.md](SCHEMA.md). Do not add timestamps, scores,
  duplicated identifiers, JSON payloads, or importer bookkeeping.
- Keep codes as text. Spreadsheet editors must preserve leading zeroes.
- Use empty cells for unknown values. Never guess coordinates or OSM identities.
- Do not duplicate a native name in a translation column.
- Change Korean mode labels in `data/korean/modes.csv`, not individual stations.
- A linked terminal can inherit its station name; do not copy it into both rows.
- Do not infer line order or connections from station-code order.
- Do not include personal card numbers, histories, captures, credentials, or APKs.

Run:

```sh
python3 build.py --check
python3 -m unittest discover -s tests -v
```

For maintenance, `scripts/import_cardbal.py --resources /path/to/CardBal/Resources
--portable /path/to/StationAssets --output /temporary/new-catalog` extracts the
compact station fields from finalized app assets. Review the resulting CSV diff
and attribution before replacing source files. Normal builds contact no station
services. Generated compatibility assets belong in `dist/`, not in Git.

## OSM maintenance

[AGENTS.md](AGENTS.md) defines the identity and matching rules.
[Reference formats](reference/README.md) describes the verified source evidence
kept alongside the CSVs.

To enrich Chinese stations from cached Overpass JSON:

```sh
python3 scripts/enrich_china.py --root . --cache /path/to/cached-osm \
  --equivalences reference/name-equivalences.json
```

The cache uses `<city>.json` and optional `<city>-supplement.json` files, each
containing an Overpass `elements` array. The tool reads local snapshots, updates
station CSVs, and writes diagnostics to ignored `dist/china-enrichment.json`.
`--source-types` can supply a JSON `stations` object keyed by code with a `type`
field; `--city-relations` can supply a `verified` array of city registry fields.
`--audit` overrides the diagnostic output path.

Review the CSV diff and source hashes before committing. Keep only independently
supported facts and their public sources in `reference/`, using the existing
formats; leave progress summaries and unresolved candidates in local diagnostics.
