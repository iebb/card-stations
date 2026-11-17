# Card Stations

[English](README.md) · [Español](README.es.md) · [Français](README.fr.md) · [简体中文](README.zh-CN.md) · [繁體中文（台灣）](README.zh-TW.md) · [繁體中文（香港）](README.zh-HK.md) · [日本語](README.ja.md) · **한국어**

Card Stations는 교통카드에 기록된 역 코드를 역 이름, 노선, 좌표, OpenStreetMap
참조와 연결하는 공개 카탈로그입니다. 원본 데이터는 일반 CSV라서 기여 내용을 쉽게
검토할 수 있습니다. 작은 Python 컴파일러가 CSV를 검증하고 앱이 불러오는 파일을
생성합니다.

## 지원 범위

| 카드 종류 | 역 파일 |
| --- | --- |
| 일본 IC 카드 (Suica, PASMO, ICOCA 등) | `data/japanese-ic/stations/all.csv` |
| 중국 T-Union | `data/t-union/stations/<도시-코드>.csv` |
| 한국 교통카드 | `data/korean/stations/<회사-또는-수단>.csv` |
| 몽골 U-money | `data/u-money/stations/ulaanbaatar.csv` |

각 행은 카드 코드 하나에 대응합니다.

```csv
code,name,line_code,line,latitude,longitude,osm_ref
602000020201,东莞火车站,60200002,2号线,23.0914394,113.8557158,node/7942711901
```

열 이름의 의미는 모든 카드 종류에서 같습니다. 빈 칸은 값을 모른다는 뜻입니다. 번역
열은 출처에 번역명이 있을 때만 나타납니다. 도시나 회사는 파일 경로로 나타냅니다. 한국
코드는 마지막 16진수 네 자리가 교통수단을 나타내므로 교통수단 이름은
[`data/korean/modes.csv`](data/korean/modes.csv)에 한 번만 저장합니다. 전체 형식은
[SCHEMA.md](SCHEMA.md)를 참고하세요.

## 경로

역 사이의 연결은 `edges.csv`와 `edges/`에 따로 저장하고, 알려진 정차 순서는
`line-stops.csv`에 있습니다. 일본 연결에는 선로의 상세 형상이 포함되며, 접두사를
압축한 geohash 경로로 몇 미터 이내의 정밀도로 인코딩됩니다. 형상이 비어 있으면 검증된
연속 경로가 없다는 뜻이며, 앱은 역 사이를 직선으로 그립니다.
[routing/README.md](routing/README.md)를 참고하세요.

## 빌드

Python 3와 표준 라이브러리만 있으면 됩니다.

```sh
python3 build.py --check                    # 모든 원본 검증
python3 -m unittest discover -s tests -v    # 테스트 실행
python3 build.py --output dist              # SQLite, TSV, JSON 파일 생성
```

생성된 파일은 `dist/`에 저장되며 Git에 커밋하지 않습니다. 앱은 이 저장소의 특정
커밋을 고정해서 사용합니다. 로컬 변경 사항을 CardBal에서 시험하려면
`--csv-source /path/to/card-stations`로 빌드하세요.

## 기여하기

CSV를 수정하고 출처를 밝힌 뒤 `master`로 풀 리퀘스트를 보내 주세요. 코드는 텍스트이므로
앞자리의 0을 지우지 마세요. 좌표나 OSM 객체를 추측해서 채우지 말고, 확실하지 않으면 빈
칸으로 두세요. 규칙은 [CONTRIBUTING.md](CONTRIBUTING.md)에, 데이터의 출처는
[reference/](reference/README.md)에 정리되어 있습니다.

## 라이선스

코드와 원본 기여물은 [BSD 3-Clause](LICENSE) 라이선스를 따릅니다. 가져온 데이터는
ODbL, CC BY-SA 4.0, CC BY 4.0 등 원래의 라이선스를 유지합니다.
[DATA_SOURCES.md](DATA_SOURCES.md)에 모든 출처를 기록했으며, 경로별 라이선스와
유지해야 할 저작자 표시는 [`licenses/`](licenses/README.md)에서 확인할 수 있습니다.
