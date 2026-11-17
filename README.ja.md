# Card Stations

[English](README.md) · [Español](README.es.md) · [Français](README.fr.md) · [简体中文](README.zh-CN.md) · [繁體中文（台灣）](README.zh-TW.md) · [繁體中文（香港）](README.zh-HK.md) · **日本語** · [한국어](README.ko.md)

Card Stations は、交通系 IC カードに記録された駅コードを、駅名・路線・座標・
OpenStreetMap 参照に対応付けるオープンなカタログです。元データはプレーンな CSV なので、
変更内容を簡単にレビューできます。小さな Python 製コンパイラが CSV を検証し、アプリが
読み込むファイルを生成します。

## 対象

| カードの種類 | 駅ファイル |
| --- | --- |
| 日本の交通系 IC（Suica・PASMO・ICOCA など） | `data/japanese-ic/stations/all.csv` |
| 中国 交通聯合（T-Union） | `data/t-union/stations/<都市コード>.csv` |
| 韓国の交通カード | `data/korean/stations/<事業者またはモード>.csv` |
| モンゴル U-money | `data/u-money/stations/ulaanbaatar.csv` |

1 行が 1 つのカードコードに対応します。

```csv
code,name,line_code,line,latitude,longitude,osm_ref
602000020201,东莞火车站,60200002,2号线,23.0914394,113.8557158,node/7942711901
```

列名の意味はどのカードでも共通です。空欄は「不明」を表します。翻訳列は、出典に訳名が
ある場合にだけ現れます。都市や事業者はファイルのパスで表します。韓国のコードは末尾
4 桁の 16 進数が交通モードを表すため、モード名は
[`data/korean/modes.csv`](data/korean/modes.csv) に一度だけ記録しています。形式の
詳細は [SCHEMA.md](SCHEMA.md) を参照してください。

## 経路

駅間の接続は `edges.csv` と `edges/` に分けて格納しています。判明している停車順は
`line-stops.csv` にあります。日本の接続には線路の詳細な形状が含まれ、プレフィックス
圧縮した geohash 経路として数メートル程度の精度で符号化しています。形状が空欄の場合は
検証済みの連続した経路がないことを表し、アプリは駅間を直線で描きます。詳しくは
[routing/README.md](routing/README.md) を参照してください。

## ビルド

必要なのは Python 3 と標準ライブラリだけです。

```sh
python3 build.py --check                    # すべての元データを検証
python3 -m unittest discover -s tests -v    # テストを実行
python3 build.py --output dist              # SQLite・TSV・JSON を生成
```

生成ファイルは `dist/` に出力され、Git にはコミットしません。アプリはこのリポジトリの
特定のコミットを固定して使います。ローカルの変更を CardBal で試すには、
`--csv-source /path/to/card-stations` を指定してビルドしてください。

## コントリビュート

CSV を編集し、出典を明記して `master` 宛てにプルリクエストを送ってください。コードは
文字列なので、先頭のゼロを消さないでください。座標や OSM の対象を推測で埋めず、確信が
なければ空欄のままにしてください。ルールは [CONTRIBUTING.md](CONTRIBUTING.md) に、
データの出典は [reference/](reference/README.md) にまとめています。

## ライセンス

コードとオリジナルの貢献は [BSD 3-Clause](LICENSE) ライセンスです。取り込んだデータは
ODbL、CC BY-SA 4.0、CC BY 4.0 などの元のライセンスに従います。すべての出典は
[DATA_SOURCES.md](DATA_SOURCES.md) に記録しています。パスごとのライセンスと必要な
クレジット表記は [`licenses/`](licenses/README.md) を参照してください。
