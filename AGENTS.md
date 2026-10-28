Use `master` as the default branch.

CSV files under `data/` are the authoritative station sources. Preserve text
identifiers and leading zeroes. Never add personal card identifiers, histories,
raw captures, credentials, or APK binaries. Document upstream sources and terms
in DATA_SOURCES.md. Run `python3 build.py --check` and
`python3 -m unittest discover -s tests -v` before committing data or compiler changes.
