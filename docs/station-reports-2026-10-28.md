# Incoming station report review — 2026-10-28

The 16 pending submissions reduce to 12 distinct station/line/code groups
covering 11 station names. Four submissions repeat an existing group. Three
groups contain an exact code; nine groups have no code.

Only independently verified OSM station coordinates are used. Report location
pins are not station coordinates. Private report metadata and notes are omitted.
No report status was changed.

## Proposed exact aliases

| City | Station | Exact observed code | Mapping and primary evidence |
| --- | --- | --- | --- |
| Chengdu | 西南交大 | `651000060638000000` | Same physical station as existing `65100638`; [station node](https://www.openstreetmap.org/node/8242507064), [Line 6 stop area](https://www.openstreetmap.org/relation/12038792), [Line 6 route](https://www.openstreetmap.org/relation/9627850). |
| Chengdu | 春熙路 | `651000030330000000` | Same physical station as existing `65100330`; [station node](https://www.openstreetmap.org/node/5617074686), [stop area](https://www.openstreetmap.org/relation/8297270), [Line 3 route](https://www.openstreetmap.org/relation/6517083). |
| Shenzhen | 后瑞 | `584000000000000016` | [Station node 12054570025](https://www.openstreetmap.org/node/12054570025), [stop area 7713272](https://www.openstreetmap.org/relation/7713272), and both [Line 1 directions](https://www.openstreetmap.org/relation/2287554), [reverse](https://www.openstreetmap.org/relation/7913935). No internal card line code is inferred. |

The app's travel decoder treats the seven-byte station field separately from
the eight-byte terminal field. When unresolved, it displays the city code plus
the entire station field. These three report strings fit that form. The proposed
rows preserve each complete observed code; they do not strip zeroes, create a
shorter prefix, or treat an OSM element ID or terminal number as a card code.
OSM verifies physical identity and geography; the report supplies the observed
card key. This is evidence for the listed exact aliases, not a universal claim
about every card using that station.

HouRui's station node is distinct from railway building way `242945735` and its
two directional stop positions. Stop area `7713272` contains the station and
stop positions `1888314914` / `6498615472`; those stop positions are members of
Line 1 routes `2287554` / `7913935`. The proposed point is the station node's
WGS84 coordinate, `22.6317812, 113.830368`.

## Name-only groups

| City | Station / line | Submissions | Existing station-code coverage | Outcome |
| --- | --- | ---: | --- | --- |
| Ningbo | 鼓楼 / Line 2 | 1 | `332000020042`, `33200242`; [OSM](https://www.openstreetmap.org/node/5325681131) | No reported code; no new alias. |
| Chongqing | 观音桥 / Line 3 | 2 | `69000321`; [OSM](https://www.openstreetmap.org/node/1856754755) | No reported code; no new alias. |
| Chongqing | 两路口 / Line 3 | 2 | `69000318`; [OSM](https://www.openstreetmap.org/node/5619893122) | No reported code; no new alias. |
| Chongqing | 观音桥 / Line 9 | 3 | `69000912`; [OSM](https://www.openstreetmap.org/node/1856754755) | No reported code; no new alias. |
| Chongqing | 李家坪 / Line 9 | 1 | `69000910`; [OSM](https://www.openstreetmap.org/node/9436112302) | No reported code; no new alias. |
| Chengdu | 省体育馆 / Line 1 | 1 | `65100129`; [OSM](https://www.openstreetmap.org/node/7213434056) | No reported code; no new alias. |
| Chengdu | 天府广场 / Line 1 | 1 | `65100126`; [OSM](https://www.openstreetmap.org/node/7417454927) | No reported code; no new alias. |
| Chengdu | 西华大道 / Line 6 | 1 | `65100635`; [OSM](https://www.openstreetmap.org/node/8242507061) | No reported code; no new alias. |
| Nanping | 高铁南平市站 / K2 | 1 | No established card-code mapping | Needs the card key and a bus-stop-specific identity. A railway station destination is not automatically the settlement bus stop. |

A matching name in the catalog does not prove that a name-only report has been
resolved: the report may refer to another identifier or record format. No mapping
is inferred from station names, public line numbers, or the city registry alone.
