# Routing data

Station rows stay compact. Routing uses separate common CSV tables:

- `data/japanese-ic/edges.csv` and `data/t-union/edges/<city>.csv`:
  `line_code,from_code,to_code,distance_km,vertices`.
- `data/t-union/line-stops.csv` and `data/u-money/line-stops.csv`:
  `line_code,code,sequence`. Only known positive sequences are included.

Japanese `from_code`/`to_code` are physical station codes, not FeliCa codes.
Chinese endpoints are complete city-prefixed card station keys. Connections are
undirected; geometry is stored in the from-to direction. Reverse the decoded
vertices when drawing the reverse edge. A blank `vertices` cell means fallback,
not a surveyed straight rail alignment. Line membership alone does not create
connections.

## Geohash paths

`vertices` begins with the precision digit (`9`). Each following vertex consists
of one shared-prefix-length digit, followed by the remaining base32 geohash
characters. The first prefix length must be zero. Successive duplicate cells are
omitted. Coordinates decode to geohash cell centres, in longitude/latitude order.
Nine characters keep quantization error below four metres across Japan.

`routing/geohash.py` contains the reference encoder and decoder. Python and
Swift implementations are cross-checked in CardBal. Prefix compression avoids
repeating the same city-level prefix for each rail vertex; no decimal coordinate
arrays are repeated in the CSVs.

## Import

```sh
python3 scripts/import_routing.py \
  --station-db /path/to/station_database \
  --routing-db /path/to/previous-cardbal-routing.sqlite
```

The importer uses continuous rail geometry from the pinned `extra/polyline`
files. Station projections must lie within 200 metres, share a connected source
component, and pass a detour sanity check. Missing or disconnected geometry is
left blank. Distances for matched edges follow the clipped path. Provenance,
file checksums, and coverage are in `reference/japan-routing.json`.

Two mixed historical/current segments are explicitly left as fallbacks in
`reference/routing-fallbacks.json`; no common geometry epoch is declared for
them. Source-specific origins, including historical-source overrides, are
retained in the provenance manifest rather than attributed generically to MLIT.
