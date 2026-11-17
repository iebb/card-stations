# Card Stations

[English](README.md) · **Español** · [Français](README.fr.md) · [简体中文](README.zh-CN.md) · [繁體中文（台灣）](README.zh-TW.md) · [繁體中文（香港）](README.zh-HK.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

Card Stations es un catálogo abierto que relaciona los códigos de estación
guardados en las tarjetas de transporte con nombres de estación, líneas,
coordenadas y referencias de OpenStreetMap. Las fuentes son CSV planos, así que
las contribuciones son fáciles de revisar. Un pequeño compilador en Python valida
los CSV y genera los archivos que cargan las aplicaciones.

## Cobertura

| Familia de tarjetas | Archivos de estaciones |
| --- | --- |
| IC japonesas (Suica, PASMO, ICOCA, …) | `data/japanese-ic/stations/all.csv` |
| T-Union (China) | `data/t-union/stations/<código-de-ciudad>.csv` |
| Tarjetas de transporte coreanas | `data/korean/stations/<empresa-o-modo>.csv` |
| U-money (Mongolia) | `data/u-money/stations/ulaanbaatar.csv` |

Cada fila identifica un código de tarjeta:

```csv
code,name,line_code,line,latitude,longitude,osm_ref
602000020201,东莞火车站,60200002,2号线,23.0914394,113.8557158,node/7942711901
```

Los nombres de columna significan lo mismo en todas las familias de tarjetas.
Una celda vacía indica que el valor se desconoce. Las columnas de traducción
solo aparecen cuando una fuente las proporciona. La ruta del archivo indica la
ciudad o la empresa. Los nombres de los modos coreanos se guardan una sola vez
en [`data/korean/modes.csv`](data/korean/modes.csv), porque los cuatro últimos
dígitos hexadecimales de cada código coreano identifican el modo.
[SCHEMA.md](SCHEMA.md) es la referencia completa del formato.

## Rutas

Las conexiones entre estaciones se guardan aparte, en `edges.csv` y `edges/`. El
orden conocido de las paradas está en `line-stops.csv`. Las conexiones
japonesas incluyen la geometría detallada de la vía, codificada como trayectos
geohash con compresión de prefijos y una precisión de pocos metros. Una
geometría vacía significa que no existe un trayecto continuo verificado, así que
las aplicaciones trazan una línea recta entre estaciones. Consulta
[routing/README.md](routing/README.md).

## Compilación

Solo necesitas Python 3 y su biblioteca estándar.

```sh
python3 build.py --check                    # valida todas las fuentes
python3 -m unittest discover -s tests -v    # ejecuta las pruebas
python3 build.py --output dist              # genera los recursos SQLite, TSV y JSON
```

Los archivos generados van a `dist/` y no se confirman en Git. Las aplicaciones
fijan un commit de este repositorio. Para probar un cambio local en CardBal,
compílalo con `--csv-source /ruta/a/card-stations`.

## Contribuir

Edita un CSV, cita la fuente y abre un pull request contra `master`. Los códigos
son texto, así que conserva sus ceros iniciales. Nunca adivines coordenadas ni
identidades de OSM. Deja la celda vacía si tienes dudas.
[CONTRIBUTING.md](CONTRIBUTING.md) recoge las reglas y [AGENTS.md](AGENTS.md)
describe el método de investigación de los datos actuales.

## Licencia

El código y las contribuciones originales usan la licencia
[BSD 3-Clause](LICENSE). Los datos importados conservan su licencia de origen,
entre ellas ODbL, CC BY-SA 4.0 y CC BY 4.0. [DATA_SOURCES.md](DATA_SOURCES.md)
registra todas las fuentes y [`licenses/`](licenses/README.md) indica la licencia
de cada ruta y la atribución que debes mantener.
