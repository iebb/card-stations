# Card Stations

[English](README.md) · [Español](README.es.md) · [Français](README.fr.md) · **简体中文** · [繁體中文（台灣）](README.zh-TW.md) · [繁體中文（香港）](README.zh-HK.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

Card Stations 是一个开放的站点目录，把交通卡中记录的站点代码对应到站名、线路、坐标和
OpenStreetMap 引用。源数据是纯 CSV，方便审阅贡献。一个小型 Python 编译器负责校验这些
CSV，并生成应用加载的文件。

## 覆盖范围

| 卡种 | 站点文件 |
| --- | --- |
| 日本 IC 卡（Suica、PASMO、ICOCA 等） | `data/japanese-ic/stations/all.csv` |
| 交通联合（T-Union） | `data/t-union/stations/<城市代码>.csv` |
| 韩国交通卡 | `data/korean/stations/<公司或交通方式>.csv` |
| 蒙古 U-money | `data/u-money/stations/ulaanbaatar.csv` |

每一行对应一个卡内代码：

```csv
code,name,line_code,line,latitude,longitude,osm_ref
602000020201,东莞火车站,60200002,2号线,23.0914394,113.8557158,node/7942711901
```

各卡种的列名含义一致。空单元格表示未知。只有来源提供译名时才会出现翻译列。城市或公司
由文件路径表示。韩国代码的最后四位十六进制数字标识交通方式，所以交通方式名称只在
[`data/korean/modes.csv`](data/korean/modes.csv) 中保存一次。完整格式说明见
[SCHEMA.md](SCHEMA.md)。

## 路线

站间连接单独存放在 `edges.csv` 和 `edges/` 中，已知的停靠顺序在 `line-stops.csv` 中。
日本的连接包含详细的轨道几何，编码为前缀压缩的 geohash 路径，误差在几米以内。几何为空
表示没有经过验证的连续路径，应用会改为在站点之间画直线。详见
[routing/README.md](routing/README.md)。

## 构建

只需要 Python 3 及其标准库。

```sh
python3 build.py --check                    # 校验所有源文件
python3 -m unittest discover -s tests -v    # 运行测试
python3 build.py --output dist              # 生成 SQLite、TSV 和 JSON 文件
```

生成的文件放在 `dist/`，不提交到 Git。应用会固定引用本仓库的某个提交。要在 CardBal
中测试本地修改，用 `--csv-source /path/to/card-stations` 构建。

## 参与贡献

修改 CSV，注明来源，然后向 `master` 提交 pull request。代码是文本，请保留前导零。
不要猜测坐标或 OSM 对象；不确定时请留空。规则见 [CONTRIBUTING.md](CONTRIBUTING.md)，
数据来源依据见 [reference/](reference/README.md)。

## 许可

代码和原创贡献采用 [BSD 3-Clause](LICENSE) 许可。导入的数据沿用其上游许可，包括
ODbL、CC BY-SA 4.0 和 CC BY 4.0。[DATA_SOURCES.md](DATA_SOURCES.md) 记录了全部来源，
[`licenses/`](licenses/README.md) 列出了每个路径的许可以及必须保留的署名。
