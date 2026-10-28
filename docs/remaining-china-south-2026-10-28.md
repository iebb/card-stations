# Remaining southern/western Chinese station research — 2026-10-28

All **93** originally missing OSM rows in these ten city files were reviewed: **85** references added; **8** remain unresolved. The compact [per-code evidence ledger](../research/remaining-china-south-2026-10-28.json) records every decision, source URL, selected object, coordinates, and added fields.

| Catalog city code | Reviewed | Added | Unresolved |
| --- | ---: | ---: | ---: |
| 3930 | 21 | 18 | 3 |
| 4210 | 1 | 1 | 0 |
| 5510 | 4 | 3 | 1 |
| 5810 | 25 | 25 | 0 |
| 5880 | 1 | 1 | 0 |
| 6020 | 1 | 1 | 0 |
| 6510 | 4 | 1 | 3 |
| 6900 | 1 | 1 | 0 |
| 7010 | 3 | 3 | 0 |
| 7910 | 32 | 31 | 1 |

## Identity and coordinate rules

Codes and native names are unchanged. Public route/stop-area memberships, station tags, operators, and cited station history establish identity; card-code order or numeric suffixes do not establish a line. The card city identifies the service catalog, so verified stations can lie outside its administrative boundary: Guangzhou services reach Foshan/Qingyuan, Foshan Line 2 reaches Guangzhou South, Changsha Line 3 reaches Xiangtan, Chengdu S3 reaches Ziyang, and Xi’an metro reaches Xianyang.

Coordinates come from primary OSM station nodes or the representative bounding-box centre of a supported stop group/footprint. Existing coordinates are reused for objects already referenced elsewhere. Wikipedia corroborates identity/history; its coordinates and public station numbers are not imported. Detailed geometry and travel histories are outside this review.

## Higher-risk decisions

- Guangzhou South for the Foshan lookup uses [node/9372157614](https://www.openstreetmap.org/node/9372157614), whose operator/ref identify Foshan Line 2; Guangzhou Lines 2/7 and 22 have different OSM nodes. [Station context](https://zh.wikipedia.org/wiki/广州南站_(地铁)).
- 金榜公园 uses [the old BRT 文灶 stop area](https://www.openstreetmap.org/relation/2334368) at the documented old-station location. [The station history](https://zh.wikipedia.org/wiki/金榜公园站) records the 2019 rename and the separate new 文灶 station. OSM’s label remains stale. The pre-existing 文灶 lookup is untouched because its historical semantics are not proven by the current name.
- 新桥 uses [node/9436112295](https://www.openstreetmap.org/node/9436112295), explicitly tagged as a subway station under construction. [The Line 9 article](https://zh.wikipedia.org/wiki/重庆轨道交通9号线) lists it as unopened. Adding the physical identity does not assert current passenger service.
- 馬王/马王村 is supported by the OSM node’s explicit `alt_name=马王站;马王火车站;Mawang Railway Station` and the [Xihu project report](https://www.cnr.cn/sxpd/sx/20220722/t20220722_525927020.shtml). The lookup gains the source-supported line name 西户线; no passenger-opening claim is made.

## Unresolved rows

| Code | Native name | Reason and evidence |
| --- | --- | --- |
| 39302126 | 产业研究院 | Only a platform with defective/truncated OSM name 产业研究研究 Institution ... (BRT) was found in the expected BRT corridor. Operator announcement confirms the station exists, but no exact grouped station identity or reliable name equivalence was established; do not turn a fuzzy match into a lookup mapping. [source 1](https://www.openstreetmap.org/node/4406288790) [source 2](https://www.sina.cn/news/detail/5159356387563925.html) |
| 39302128 | 东宅 | Two directional BRT stops exist without a station/stop-area grouping. Do not choose one direction without lookup-direction evidence. The exact-name metro 东宅 station is a different physical station and is rejected. [source 1](https://www.openstreetmap.org/node/12089955453) [source 2](https://www.openstreetmap.org/node/12089967511) [source 3](https://www.openstreetmap.org/way/765488976) [source 4](https://zh.wikipedia.org/wiki/厦门快速公交) |
| 39302129 | 田厝 | Two BRT boarding points and ordinary-bus homonyms exist without a station/stop-area grouping. Keep the physical mapping unknown rather than choose an arbitrary direction. [source 1](https://www.openstreetmap.org/node/3902785853) [source 2](https://www.openstreetmap.org/node/12089949096) [source 3](https://zh.wikipedia.org/wiki/厦门快速公交) |
| 5510060035 | 黄花机场T3 | The documented Line 6 extension station is distinct from T1/T2. Regional rail/construction queries and the T3 vicinity map supplied the airport terminal building but no verified metro station object; the terminal building is rejected as a station reference. [source 1](https://www.openstreetmap.org/way/1292584043) [source 2](https://zh.wikipedia.org/wiki/黄花机场T1T2站) [source 3](https://static.sse.com.cn/disclosure/bond/announcement/company/c/new/2026-03-25/244942_20260325_CM0R.pdf) |
| 65101831 | 天府机场3号4号航站楼 | Reserved/unopened terminal station is documented. OSM has several directional named stop_position nodes but no verified station centre/group; their placement also differs materially from the article coordinates. Keep the mapping unknown rather than select a direction or borrow the T1/T2 station. [source 1](https://www.openstreetmap.org/node/6669929054) [source 2](https://www.openstreetmap.org/node/8867473140) [source 3](https://www.openstreetmap.org/node/9164861769) [source 4](https://zh.wikipedia.org/wiki/天府机场3号4号航站楼站) |
| 65101941 | 天府机场3号4号航站楼 | Same reserved terminal-station ambiguity as the Line 18 lookup: directional stop_position nodes are insufficient to select a stable station identity; no T1/T2 substitution or operating-status inference. [source 1](https://www.openstreetmap.org/node/6669929054) [source 2](https://www.openstreetmap.org/node/9164861769) [source 3](https://zh.wikipedia.org/wiki/天府机场3号4号航站楼站) |
| 65107322 | 卢葭 | A real reserved S3 station is mapped as 芦葭站 and documented as 芦葭. No public source found establishes the different lookup spelling 卢葭 as an alias; similarity alone is insufficient. Preserve the native lookup name and defer the OSM link. [source 1](https://www.openstreetmap.org/way/1530966031) [source 2](https://zh.wikipedia.org/wiki/芦葭站) |
| 7910240017 | 昆明池 | The Xihu railway project and line article identify this planned/new passenger station. No named, verified station object was found in the corridor query; the lake/scenic site and future metro station must not be substituted. No coordinate is invented. [source 1](https://zh.wikipedia.org/wiki/西户铁路) [source 2](https://www.cnr.cn/sxpd/sx/20220722/t20220722_525927020.shtml) |

## Source quality and validation

Obvious source English defects are omitted: `Raliway`, `Lingtong`, `BaoquanRoad`, stale `WenZao` for 金榜公园, and `BinHui … Juction`. No corrected translation is invented. Source formatting controls are removed from otherwise unchanged English labels.

All 83 selected OSM objects were rechecked using the primary OSM API. The supplied ledger includes route URLs where the cached explicit membership evidence is available. No raw OSM payloads, local caches, private captures, or personal report fields are included.

Validation: `python3 build.py --check` passed; all 29 tests passed with `python3 -m unittest discover -s tests -v`. Independent coverage checks confirm all 93 original gaps are represented, every existing code/native name is unchanged, pre-existing mapped rows are untouched, shared-reference coordinates agree, and public artifacts contain no private report fields.
