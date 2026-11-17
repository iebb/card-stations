# Card Stations

[English](README.md) · [Español](README.es.md) · [Français](README.fr.md) · [简体中文](README.zh-CN.md) · [繁體中文（台灣）](README.zh-TW.md) · **繁體中文（香港）** · [日本語](README.ja.md) · [한국어](README.ko.md)

Card Stations 是一個開放的車站目錄，把交通卡內記錄的車站編號對應到站名、路綫、坐標和
OpenStreetMap 參照。源數據是純 CSV，方便審閱貢獻。一個小型 Python 編譯器負責驗證這些
CSV，並生成應用程式載入的檔案。

## 覆蓋範圍

| 卡種 | 車站檔案 |
| --- | --- |
| 日本 IC 卡（Suica、PASMO、ICOCA 等） | `data/japanese-ic/stations/all.csv` |
| 內地交通聯合（T-Union） | `data/t-union/stations/<城市編號>.csv` |
| 韓國交通卡 | `data/korean/stations/<公司或交通模式>.csv` |
| 蒙古 U-money | `data/u-money/stations/ulaanbaatar.csv` |

每一行對應一個卡內編號：

```csv
code,name,line_code,line,latitude,longitude,osm_ref
602000020201,东莞火车站,60200002,2号线,23.0914394,113.8557158,node/7942711901
```

各卡種的欄位名稱意思一致。空白欄表示未知。只有來源提供譯名時才會出現翻譯欄位。城市或
公司由檔案路徑表示。韓國編號的最後四位十六進制數字代表交通模式，所以交通模式名稱只在
[`data/korean/modes.csv`](data/korean/modes.csv) 中儲存一次。完整格式說明見
[SCHEMA.md](SCHEMA.md)。

## 路綫

站與站之間的連接另行存放在 `edges.csv` 和 `edges/` 中，已知的停站次序在
`line-stops.csv` 中。日本的連接包含詳細的路軌幾何，以前綴壓縮的 geohash 路徑編碼，
誤差在幾米以內。幾何留空表示沒有經核實的連續路徑，應用程式會改為在車站之間畫直綫。詳見
[routing/README.md](routing/README.md)。

## 建構

只需要 Python 3 及其標準程式庫。

```sh
python3 build.py --check                    # 驗證所有源檔案
python3 -m unittest discover -s tests -v    # 執行測試
python3 build.py --output dist              # 生成 SQLite、TSV 和 JSON 檔案
```

生成的檔案放在 `dist/`，不會提交到 Git。應用程式會鎖定本儲存庫的某個提交。如要在
CardBal 中測試本機修改，請用 `--csv-source /path/to/card-stations` 建構。

## 參與貢獻

修改 CSV、註明來源，然後向 `master` 提交 pull request。編號是文字，請保留前置零。
切勿估算坐標或 OSM 物件；如有疑問請留空。規則見 [CONTRIBUTING.md](CONTRIBUTING.md)，
數據來源依據見 [reference/](reference/README.md)。

## 授權

程式碼和原創貢獻採用 [BSD 3-Clause](LICENSE) 授權。匯入的數據沿用其上游授權，包括
ODbL、CC BY-SA 4.0 和 CC BY 4.0。[DATA_SOURCES.md](DATA_SOURCES.md) 記錄了所有來源，
[`licenses/`](licenses/README.md) 列出每個路徑的授權，以及必須保留的署名。
