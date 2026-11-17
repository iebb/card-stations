# Card Stations

[English](README.md) · [Español](README.es.md) · **Français** · [简体中文](README.zh-CN.md) · [繁體中文（台灣）](README.zh-TW.md) · [繁體中文（香港）](README.zh-HK.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

Card Stations est un catalogue ouvert qui associe les codes de station
enregistrés sur les cartes de transport à des noms de station, des lignes, des
coordonnées et des références OpenStreetMap. Les sources sont de simples CSV, ce
qui rend les contributions faciles à relire. Un petit compilateur Python valide
les CSV et génère les fichiers que chargent les applications.

## Couverture

| Famille de cartes | Fichiers de stations |
| --- | --- |
| Cartes IC japonaises (Suica, PASMO, ICOCA, …) | `data/japanese-ic/stations/all.csv` |
| T-Union (Chine) | `data/t-union/stations/<code-ville>.csv` |
| Cartes de transport coréennes | `data/korean/stations/<société-ou-mode>.csv` |
| U-money (Mongolie) | `data/u-money/stations/ulaanbaatar.csv` |

Chaque ligne identifie un code de carte :

```csv
code,name,line_code,line,latitude,longitude,osm_ref
602000020201,东莞火车站,60200002,2号线,23.0914394,113.8557158,node/7942711901
```

Les noms de colonnes ont le même sens dans toutes les familles de cartes. Une
cellule vide signifie que la valeur est inconnue. Les colonnes de traduction
n'apparaissent que lorsqu'une source les fournit. Le chemin du fichier indique
la ville ou la société. Les noms des modes coréens sont stockés une seule fois
dans [`data/korean/modes.csv`](data/korean/modes.csv), car les quatre derniers
chiffres hexadécimaux de chaque code coréen identifient le mode.
[SCHEMA.md](SCHEMA.md) est la référence complète du format.

## Itinéraires

Les liaisons entre stations sont stockées à part, dans `edges.csv` et `edges/`.
L'ordre connu des arrêts se trouve dans `line-stops.csv`. Les liaisons
japonaises comprennent le tracé détaillé des voies, encodé en chemins geohash
compressés par préfixe, précis à quelques mètres près. Une géométrie vide
signifie qu'il n'existe aucun tracé continu vérifié : les applications tracent
alors une ligne droite entre les stations. Voir
[routing/README.md](routing/README.md).

## Compilation

Seuls Python 3 et sa bibliothèque standard sont nécessaires.

```sh
python3 build.py --check                    # valide toutes les sources
python3 -m unittest discover -s tests -v    # lance les tests
python3 build.py --output dist              # génère les fichiers SQLite, TSV et JSON
```

Les fichiers générés vont dans `dist/` et ne sont pas versionnés. Les
applications épinglent un commit de ce dépôt. Pour tester une modification
locale dans CardBal, compilez-la avec `--csv-source /chemin/vers/card-stations`.

## Contribuer

Modifiez un CSV, citez votre source et ouvrez une pull request vers `master`.
Les codes sont du texte : conservez leurs zéros initiaux. Ne devinez jamais des
coordonnées ni des identités OSM. En cas de doute, laissez la cellule vide.
[CONTRIBUTING.md](CONTRIBUTING.md) liste les règles et [AGENTS.md](AGENTS.md)
décrit la méthode de recherche appliquée aux données actuelles.

## Licence

Le code et les contributions originales sont sous licence
[BSD 3-Clause](LICENSE). Les données importées conservent leur licence
d'origine, notamment ODbL, CC BY-SA 4.0 et CC BY 4.0.
[DATA_SOURCES.md](DATA_SOURCES.md) recense chaque source et
[`licenses/`](licenses/README.md) indique la licence de chaque chemin ainsi que
l'attribution à conserver.
