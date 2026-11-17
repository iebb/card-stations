# Card Stations

[English](README.md) · [Español](README.es.md) · [Français](README.fr.md) · [简体中文](README.zh-CN.md) · **繁體中文（台灣）** · [繁體中文（香港）](README.zh-HK.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

Card Stations 是一個開放的車站目錄，把交通票卡中記錄的車站代碼對應到站名、路線、座標和
OpenStreetMap 參照。原始資料是純 CSV，方便審閱貢獻。一個小型 Python 編譯器負責驗證這些
CSV，並產生應用程式載入的檔案。

## 涵蓋範圍

| 票卡類型 | 車站檔案 |
| --- | --- |
| 日本 IC 卡（Suica、PASMO、ICOCA 等） | `data/japanese-ic/stations/all.csv` |
| 中國交通聯合（T-Union） | `data/t-union/stations/<城市代碼>.csv` |
| 韓國交通卡 | `data/korean/stations/<公司或運具>.csv` |
| 蒙古 U-money | `data/u-money/stations/ulaanbaatar.csv` |

每一列對應一個卡片代碼：

```csv
code,name,line_code,line,latitude,longitude,osm_ref
602000020201,东莞火车站,60200002,2号线,23.0914394,113.8557158,node/7942711901
```

各票卡類型的欄位名稱意義一致。空白儲存格表示未知。只有來源提供譯名時才會出現翻譯欄位。
城市或公司由檔案路徑表示。韓國代碼的最後四位十六進位數字代表運具，所以運具名稱只在
[`data/korean/modes.csv`](data/korean/modes.csv) 中儲存一次。完整格式說明請見
[SCHEMA.md](SCHEMA.md)。

## 路線

站間連線另外存放在 `edges.csv` 和 `edges/` 中，已知的停靠順序在 `line-stops.csv` 中。
日本的連線包含詳細的軌道幾何，編碼為前綴壓縮的 geohash 路徑，誤差在幾公尺以內。幾何
空白表示沒有經過驗證的連續路徑，應用程式會改為在車站之間畫直線。詳見
[routing/README.md](routing/README.md)。

## 建置

只需要 Python 3 與其標準函式庫。

```sh
python3 build.py --check                    # 驗證所有原始檔案
python3 -m unittest discover -s tests -v    # 執行測試
python3 build.py --output dist              # 產生 SQLite、TSV 與 JSON 檔案
```

產生的檔案放在 `dist/`，不提交到 Git。應用程式會固定使用本儲存庫的某個提交。若要在
CardBal 中測試本機修改，請用 `--csv-source /path/to/card-stations` 建置。

## 參與貢獻

修改 CSV、註明來源，然後向 `master` 提出 pull request。代碼是文字，請保留開頭的零。
不要猜測座標或 OSM 物件；不確定時請留空。規則請見 [CONTRIBUTING.md](CONTRIBUTING.md)，
現有資料的研究方法請見 [AGENTS.md](AGENTS.md)。

## 授權

程式碼與原創貢獻採用 [BSD 3-Clause](LICENSE) 授權。匯入的資料沿用其上游授權，包括
ODbL、CC BY-SA 4.0 與 CC BY 4.0。[DATA_SOURCES.md](DATA_SOURCES.md) 記錄了所有來源，
[`licenses/`](licenses/README.md) 列出每個路徑的授權，以及必須保留的姓名標示。
