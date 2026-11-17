# Card Stations

**English** · [Español](README.es.md) · [Français](README.fr.md) · [简体中文](README.zh-CN.md) · [繁體中文（台灣）](README.zh-TW.md) · [繁體中文（香港）](README.zh-HK.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

Card Stations is an open catalog that maps the station codes stored on transit
cards to station names, lines, coordinates, and OpenStreetMap references. The
source is plain CSV, so contributions are easy to review. A small Python compiler
validates the CSVs and generates the files that apps load.

## Coverage

| Card family | Station files |
| --- | --- |
| Japanese IC (Suica, PASMO, ICOCA, …) | `data/japanese-ic/stations/all.csv` |
| China T-Union | `data/t-union/stations/<city-code>.csv` |
| Korean transit cards | `data/korean/stations/<company-or-mode>.csv` |
| Mongolia U-money | `data/u-money/stations/ulaanbaatar.csv` |

Each row identifies one card code:

```csv
code,name,line_code,line,latitude,longitude,osm_ref
602000020201,东莞火车站,60200002,2号线,23.0914394,113.8557158,node/7942711901
```

Column names mean the same thing in every card family. An empty cell means the
value is unknown. Translation columns appear only when a source supplies them.
The file path gives the city or company. Korean mode names are stored once in
[`data/korean/modes.csv`](data/korean/modes.csv), because the last four hex
digits of each Korean code identify the mode. [SCHEMA.md](SCHEMA.md) is the full
format reference.

## Routing

Station-to-station edges are stored separately, in `edges.csv` and `edges/`.
Known stop order is in `line-stops.csv`. Japanese edges include detailed rail
geometry, encoded as prefix-compressed geohash paths that are accurate to a few
metres. A blank geometry means that no verified continuous path exists, so apps
draw a straight station-to-station line instead. See
[routing/README.md](routing/README.md).

## Build

You need only Python 3 and its standard library.

```sh
python3 build.py --check                    # validate all sources
python3 -m unittest discover -s tests -v    # run the test suite
python3 build.py --output dist              # generate SQLite, TSV, and JSON assets
```

Generated files go in `dist/` and are not committed. Apps pin a commit of this
repository. To test a local change in CardBal, build it with
`--csv-source /path/to/card-stations`.

## Contributing

Edit a CSV, cite your source, and open a pull request against `master`. Codes are
text, so keep their leading zeroes. Never guess coordinates or OSM identities.
Leave a cell empty when you are unsure. [CONTRIBUTING.md](CONTRIBUTING.md) lists
the rules, and [AGENTS.md](AGENTS.md) describes the research method behind the
current data.

## License

The code and original contributions use the [BSD 3-Clause](LICENSE) license.
Imported data keeps its upstream license, which includes ODbL, CC BY-SA 4.0, and
CC BY 4.0. [DATA_SOURCES.md](DATA_SOURCES.md) records every source, and
[`licenses/`](licenses/README.md) gives the license for each path and the
attribution you must keep.
