#!/usr/bin/env python3
"""Import topology and snap Japanese edges to pinned station_database rail polylines."""
from __future__ import annotations

import argparse
import csv
import hashlib
import heapq
import json
import math
import sqlite3
import subprocess
import sys
from collections import defaultdict
from contextlib import closing
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from routing.geohash import encode_path, decode_path

ROOT = Path(__file__).resolve().parents[1]


def distance(a, b):
    lat = math.radians((a[1] + b[1]) / 2)
    return math.hypot((a[0] - b[0]) * math.cos(lat), a[1] - b[1]) * 111195.08


def projection(point, a, b):
    scale = math.cos(math.radians(point[1]))
    dx, dy = (b[0] - a[0]) * scale, b[1] - a[1]
    length = dx * dx + dy * dy
    t = max(0, min(1, (((point[0] - a[0]) * scale * dx + (point[1] - a[1]) * dy) / length))) if length else 0
    p = (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
    return distance(point, p), p, t


class RailGeometry:
    def __init__(self, features):
        self.graph = defaultdict(dict)
        self.segments = []
        for feature in features:
            if feature['geometry']['type'] != 'LineString':
                continue
            points = [tuple(p[:2]) for p in feature['geometry']['coordinates']]
            for a, b in zip(points, points[1:]):
                if a == b:
                    continue
                self.graph[a][b] = self.graph[b][a] = distance(a, b)
                self.segments.append((a, b))
        self.components = {}
        for node in self.graph:
            if node in self.components:
                continue
            component = len(self.components)
            stack = [node]
            self.components[node] = component
            while stack:
                for adjacent in self.graph[stack.pop()]:
                    if adjacent not in self.components:
                        self.components[adjacent] = component
                        stack.append(adjacent)
        self.snaps = {}

    def snap(self, point):
        if point in self.snaps:
            return self.snaps[point]
        best = {}
        for a, b in self.segments:
            if abs(a[1] - point[1]) > .06 and abs(b[1] - point[1]) > .06:
                continue
            gap, projected, t = projection(point, a, b)
            component = self.components[a]
            if gap <= 200 and (component not in best or gap < best[component][0]):
                best[component] = (gap, projected, t, a, b)
        self.snaps[point] = best
        return best

    def path(self, start, end):
        starts, ends = self.snap(start), self.snap(end)
        common = sorted(starts.keys() & ends.keys(), key=lambda c: starts[c][0] + ends[c][0])
        for component in common:
            left, right = starts[component], ends[component]
            _, p, _, a, b = left
            _, q, _, c, d = right
            if {a, b} == {c, d}:
                points = [start, p, q, end]
            else:
                distances, previous = {}, {}
                heap = []
                for node in (a, b):
                    cost = distance(p, node)
                    distances[node] = cost
                    heapq.heappush(heap, (cost, node))
                best, reached = math.inf, None
                while heap:
                    cost, node = heapq.heappop(heap)
                    if cost != distances[node] or cost >= best:
                        continue
                    if node in (c, d):
                        candidate = cost + distance(node, q)
                        if candidate < best:
                            best, reached = candidate, node
                    for adjacent, weight in self.graph[node].items():
                        candidate = cost + weight
                        if candidate < distances.get(adjacent, math.inf) and candidate < best:
                            distances[adjacent] = candidate
                            previous[adjacent] = node
                            heapq.heappush(heap, (candidate, adjacent))
                if reached is None:
                    continue
                nodes = [reached]
                while nodes[-1] in previous:
                    nodes.append(previous[nodes[-1]])
                points = [start, p, *reversed(nodes), q, end]
            points = [p for i, p in enumerate(points) if not i or p != points[i - 1]]
            length = sum(distance(a, b) for a, b in zip(points, points[1:]))
            if len(points) >= 2 and length <= distance(start, end) * 4 + 1000:
                encoded = encode_path(points)
                try:
                    decode_path(encoded)
                except ValueError:
                    continue
                return round(length / 1000, 6), encoded
        return None


def write_rows(path, columns, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle, lineterminator='\n')
        writer.writerow(columns); writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--station-db', type=Path, required=True)
    parser.add_argument('--routing-db', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=ROOT)
    args = parser.parse_args()
    station_root = args.station_db / 'out/extra'
    coordinates = {}
    with (args.output / 'data/japanese-ic/stations/all.csv').open() as handle:
        for r in csv.DictReader(handle):
            if r.get('station_code') and r.get('latitude'):
                coordinates[r['station_code']] = (float(r['longitude']), float(r['latitude']))
    # Rail-only intermediary stations keep their source positions for clipping.
    source_stations = json.loads((station_root / 'station.json').read_text())
    for r in source_stations:
        coordinates.setdefault(str(r['code']), (r['lng'], r['lat']))
    used, detailed, vertices, origins = {}, 0, 0, {}
    fallbacks = json.loads((args.output / 'reference/routing-fallbacks.json').read_text())
    with closing(sqlite3.connect(args.routing_db)) as db:
        grouped = defaultdict(list)
        for row in db.execute('SELECT line_code,from_code,to_code,distance_km FROM connections WHERE family=? ORDER BY line_code,from_code,to_code', ('japanese-ic',)):
            grouped[row[0]].append(row)
        output = []
        for line, edges in grouped.items():
            path = station_root / f'polyline/{line}.json'
            rail = RailGeometry(json.loads(path.read_text())['features']) if path.is_file() else None
            if rail:
                used[path.relative_to(args.station_db).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
                definition = args.station_db / f'src/polyline/{line}.json'
                if definition.is_file():
                    source = json.loads(definition.read_text())
                    relative = definition.relative_to(args.station_db).as_posix()
                    used[relative] = hashlib.sha256(definition.read_bytes()).hexdigest()
                    if source.get('origin'):
                        origins[line] = source['origin']
            for line, start, end, old_distance in edges:
                result = rail.path(coordinates[start], coordinates[end]) if rail and start in coordinates and end in coordinates else None
                if f'{line}|{start}|{end}' in fallbacks:
                    result = None
                if result:
                    length, encoded = result
                    detailed += 1; vertices += len(decode_path(encoded))
                else:
                    length, encoded = old_distance, ''
                output.append((line, start, end, length, encoded))
        write_rows(args.output / 'data/japanese-ic/edges.csv', ['line_code','from_code','to_code','distance_km','vertices'], output)
        china = defaultdict(list)
        for row in db.execute("SELECT line_code,from_code,to_code,distance_km FROM connections WHERE family='t-union' ORDER BY line_code,from_code,to_code"):
            china[row[1][:4]].append((*row, ''))
        for city, rows in china.items():
            write_rows(args.output / f'data/t-union/edges/{city}.csv', ['line_code','from_code','to_code','distance_km','vertices'], rows)
        for family in ('t-union', 'u-money'):
            rows = db.execute('SELECT line_code,code,sequence FROM line_stops WHERE family=? AND sequence>0 ORDER BY line_code,sequence,code', (family,)).fetchall()
            write_rows(args.output / f'data/{family}/line-stops.csv', ['line_code','code','sequence'], rows)
    revision = subprocess.run(['git','-C',str(args.station_db),'rev-parse','HEAD'], capture_output=True, text=True, check=True).stdout.strip()
    metadata = {'repository':'https://github.com/Seo-4d696b75/station_database','revision':revision,'dataset':'extra',
        'geometry':'station_database-published rail polylines; source-specific origins retained when provided',
        'encoding':'geohash shared-prefix path v1, precision 9', 'max_station_snap_metres':200,
        'files':used,'source_origins':origins,'reviewed_fallbacks':fallbacks,
        'edge_count':len(output),'detailed_edge_count':detailed,'detailed_vertices':vertices}
    (args.output / 'reference/japan-routing.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:metadata[k] for k in ('edge_count','detailed_edge_count','detailed_vertices')}))


if __name__ == '__main__':
    main()
