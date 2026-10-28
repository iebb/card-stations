# Independent Korean collected-candidate review — 2026-10-28

All **407 proposed exact location-code/native-name rows are cleared** for additive station-only import; **none require deferral** after the checks below. The [machine-readable clearance](../research/korean-collected-candidates-review-2026-10-28.json) lists every cleared key, an empty deferred set, source hashes, and the dated identity bridges. This review does not authorize inferred coordinates, OSM references, translations, or operator/line labels.

## Exact join and preservation

The independent implementation reconstructed every proposal directly from [MOLIT’s settlement-station CSV](https://www.data.go.kr/data/15128614/fileData.do), then reproduced the generator at revision `5f9f9392e2c6e3312bba1dd6e445b2c5edbd4bf6`. A fresh official download matched SHA-256 `10d25ec17b6cb4258e3f071ea2c465a2fa3a41d490d5db25b865cc47f9aa164e`. The downloaded file contains 134,442 data rows, all dated 2026-07-03; the portal’s displayed row count is stale.

Each accepted key has a literal seven-decimal-digit official settlement ID followed by a zero nibble, then its four-hex-digit mode. Every selected mode belongs to the primary [official KOTRIS bus class B catalog](https://www.data.go.kr/data/15121099/fileData.do). The official ID must be globally bus-only and have one complete, consistent native name and province/district identity. Normal entry or exit (`00`/`01`) must be present in the reviewed [public station aggregate](https://korean-trip-crowdsourcing.ieb.app/research/station-observations) snapshot. Its SHA-256 is `58d7b47b10aa4615d5f4410ac3636750128f5bc184ad4eb9f0781e829a36ff8a`. The independent client received HTTP 403 when attempting a fresh aggregate fetch; the supplied snapshot was schema-validated and checked directly.

For example, `2800107001F0` is settlement ID `2800107`, mode 496, and the official **bus** stop 선바위역 in 경기도 과천시. A name ending 역 does not make it a rail match, and a token prefix or bus-mode label does not determine administrative location. No rail crosswalk is extrapolated.

The selection has no collision with existing location keys, including event-specific aliases, and contains no guarded override token. A simulated additive merge preserves all 2,119 existing alias rows and event restrictions exactly. All six collection-match regression tests pass.

## Three exact dated Seoul name bridges

Three substantive differences from older aliases were checked through explicit MOLIT mobile IDs and the official Seoul ARS fields. Both the **2026-08-04** [physical stop inventory](https://data.seoul.go.kr/dataList/OA-15067/S/1/datasetView.do?tab=A) and [route-stop inventory](https://data.seoul.go.kr/dataList/OA-1095/S/1/datasetView.do) agree on the same node, name, and position. The **2025-02** [official multilingual inventory](https://data.seoul.go.kr/dataList/OA-12830/A/1/datasetView.do) supplies the older names at those exact ARS IDs.

| New location key | Settlement ID | ARS ID | TOPIS node ID | Current official name | Older official name |
| --- | --- | --- | --- | --- | --- |
| 400156300073 | 4001563 | 02507 | 101900006 | 시청역1호선.서울시청 | 프레스센터 |
| 900212900078 | 9002129 | 03161 | 102000067 | 서울시기술교육원중부.블루스퀘어 | 서울시중부기술교육원.블루스퀘어 |
| 900646100082 | 9006461 | 02001 | 101000001 | 명동성당.남대문세무서(중) | 남대문세무서 |

The 중앙차로 qualifier `(중)` is present in the MOLIT 02001 label and omitted from the current Seoul name; its exact ARS/node identity agrees. The node IDs above are official TOPIS identifiers, not OSM references. This supports current names for the new keys while leaving every older alias unchanged. Source-file hashes and exact dates are recorded in the clearance; these Seoul physical/route files are August snapshots, not July.

## Administrative and formatting differences

Six same-token comparisons differ only because older rows use 화성시 code 41590 and the July 2026 official file uses 화성시 만세구 code 41591. The [Ministry of the Interior and Safety’s notice](https://www.mois.go.kr/frt/bbs/type001/commonSelectBoardArticle.do?bbsId=BBSMSTR_000000000052&nttId=122595) documents Hwaseong’s district creation effective 2026-02-01. Exact settlement IDs and native stop names agree; the six keys and evidence are recorded in the clearance. Four other comparisons differ only in period/underscore punctuation, with exact IDs and administrative fields agreeing. Existing labels remain unchanged.

Twenty-seven proposed rows have official districts absent from the pinned map-district table. The official station identity remains usable; map references and translations stay unknown without independent evidence. Do not inherit geometry from a same-name or same-token peer merely to fill a cell.

## Public-data boundary

The proposed artifact passed an exact station-field allowlist check. The review publishes station keys, official station/admin facts, source hashes and citations only. It includes no card identifiers, raw card bytes, histories, timestamps, per-observation counts, or private paths. No CSVs, upstream source files, or repository history were changed by this independent review.
