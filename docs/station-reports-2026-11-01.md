# Station report follow-up: Chinese cards, 2026-11-01

Read-only review covered 21 pending reports. No report status was changed.
Only aggregate outcomes and station lookup keys are recorded here; private
identifiers, notes, raw histories, and report location pins are omitted.

## Shenzhen: retract the station-field alias

The key `584000000000000016` was reported for both 后瑞 (Line 1) and 岗厦
(Line 10), from independent submissions. Another report supplied
`584000000000000015` for 会展中心 (Line 1). These are the TU city code
followed by the seven-byte travel station field. The conflict invalidates
the earlier 后瑞 alias; it is removed. The field must not supply a station
name in Shenzhen without independent format evidence.

The public [Shenzhen format notes](https://github.com/domosekai/tripreader-data/blob/c5584d6b8d9a39d7162b7b9781134be52db66186/Guangdong/Shenzhen/README.md)
say that metro uses the terminal number in file `18` for CU, and the terminal
number in `1E`, in the same format, for TU.
[cu.csv](https://github.com/domosekai/tripreader-data/blob/c5584d6b8d9a39d7162b7b9781134be52db66186/Guangdong/Shenzhen/cu.csv)
contains 284 station rows with five-digit terminal prefixes and 30 broader
line/operator rows. Only station rows are imported to `cityunion/5180.csv`,
under the original CU city code `5180`; Shenzhen's TU city is `5840`.

Examples, with the CU city prefix:

| Prefix | Station | Line |
| --- | --- | --- |
| `518068035` | 后瑞 | 1号线 |
| `518068007` | 岗厦 | 1号线 |
| `518040013` | 岗厦 | 10号线 |
| `518068008` | 会展中心 | 1号线 |

Trip Reader 1.7.17 was examined as format evidence only. Its Shenzhen TU
travel discriminator is city `5840` and an eight-byte terminal starting
`00000002`; the remaining four bytes are looked up as `5180` plus those
eight hex characters, using the longest published prefix. A CU PBOC
terminal beginning `5180` can use the same station table directly. No APK
code or APK-derived station data is copied.

These names identify terminal prefixes, not new physical station positions.
The source has no coordinates and there is no established TU station-code
link. Both stay empty. Public line/operator-only rows are excluded so a
line label cannot be displayed as a station.

## Hong Kong

One report labels 铜锣湾 on 港铁 with city `0344`, followed by the seven-byte
field `00010200000100`. The [UN M49 list](https://unstats.un.org/unsd/methodology/m49/overview/)
identifies Hong Kong with numeric code `344`.
[Chongqing's government reported T-Union acceptance from 22 March 2025](https://cq.gov.cn/ywdt/bmts/202503/t20250331_14468183.html).
This supports an observed city-level alias `0344` to Hong Kong's existing
`9101` boundary and the name 香港. It does not establish an MTR station
numbering scheme. No Causeway Bay station mapping is added.

## Already covered and still unresolved

Two name-only Xiamen reports for 马青路 / Line 2 match an existing catalog
name (`39300209`); there is no reported card code to add.
City Union-family submissions for Chengdu and Ningbo also lack lookup
codes. They remain unresolved rather than being matched by name alone.
The two previously reviewed Chengdu exact aliases remain in the catalog.

City Union `2000` is Shanghai, separately from TU `2900`. Its existing 614
terminal mappings and the Shanghai city boundary alias are retained.

## Provenance and validation

Public station names, codes, and line labels are by Domosekai Limited and
Trip Reader data contributors, CC BY 4.0, revision
`c5584d6b8d9a39d7162b7b9781134be52db66186`. Full source-file hashes are in
`reference/tripreader-provenance.json`. Format evidence uses the separately
identified APK already documented there; its public CSV license is not
asserted for APK contents.

Run `python3 build.py --check` and
`python3 -m unittest discover -s tests -v` before publishing these changes.
