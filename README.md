# Card Stations

Contribution-friendly transit-card station CSVs. Each row contains only codes,
names, lines, coordinates, and OSM references.

| Cards | Station files |
| --- | --- |
| Japanese IC | `data/japanese-ic/stations/all.csv` — one shared network |
| T-Union | `data/t-union/stations/<city-code>.csv` |
| Korean cards | `data/korean/stations/<company-or-mode>.csv` |
| U-money | `data/u-money/stations/ulaanbaatar.csv` |

For example, Dongguan uses:

```csv
code,name,line_code,line,latitude,longitude,osm_ref
602000020201,东莞火车站,60200002,2号线,23.0914394,113.8557158,node/7942711901
```

All families use the same column names. Optional translations and separate
physical-station codes appear only where useful. Empty cells mean unknown.
There are no JSON cells, matching scores, timestamps, or duplicated source fields.

Korean mode names, translations, and classes live once in
[`data/korean/modes.csv`](data/korean/modes.csv). The station's 12-hex `code`
already contains its mode in the final four characters, so station CSVs have no
transport-mode columns.

Terminal mappings use the same compact columns. A linked terminal inherits its
station name when its own name is empty. City codes and record kind come from
file paths. See [SCHEMA.md](SCHEMA.md) for the short format reference.

## Contribute and build

Edit a CSV and open a pull request against `master`, with a source for the change.
Python's standard library is sufficient:

```sh
python3 build.py --check
python3 -m unittest discover -s tests -v
python3 build.py --output dist
```

The compiler generates the SQLite, TSV, and JSON formats required by existing
apps. Generated files stay out of Git. CardBal pins a commit of this repository;
`--csv-source /path/to/card-stations` tests a local contribution.

Routing CSVs are separate from station rows: `edges.csv`/`edges/` contain line,
endpoint codes, distance, and optional geometry; `line-stops.csv` records known
stop order. Japanese edges use station_database's detailed rail polylines.
Vertices are geohash encoded and prefix compressed, reducing storage while
retaining metre-scale detail. A blank geometry means the source did not provide
a continuous match; applications retain their station-to-station fallback.

See [routing/README.md](routing/README.md) for the format and provenance.

See [CONTRIBUTING.md](CONTRIBUTING.md) and [DATA_SOURCES.md](DATA_SOURCES.md).
Code is MIT licensed; imported data retains its upstream terms.
