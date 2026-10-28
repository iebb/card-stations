import importlib.util
import math
import random
import unittest
from pathlib import Path
from routing.geohash import encode, decode, encode_path, decode_path

spec = importlib.util.spec_from_file_location('import_routing', Path(__file__).resolve().parents[1] / 'scripts/import_routing.py')
routing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(routing)


class GeohashTests(unittest.TestCase):
    def test_standard_geohash_vector(self):
        self.assertEqual(encode(-5.6, 42.6, 5), 'ezs42')

    def test_japanese_vertices_round_trip_within_four_metres(self):
        rng = random.Random(20261028)
        points = [(rng.uniform(128, 145), rng.uniform(26, 46)) for _ in range(500)]
        restored = decode_path(encode_path(points))
        self.assertEqual(len(points), len(restored))
        self.assertLess(max(routing.distance(a, b) for a, b in zip(points, restored)), 4)

    def test_shared_prefix_saves_space_and_preserves_reverse_order(self):
        points = [(139.7 + i * .0001, 35.6 + i * .0001) for i in range(100)]
        encoded = encode_path(points)
        self.assertLess(len(encoded), 9 * len(points) / 2)
        decoded = decode_path(encode_path(list(reversed(points))))
        self.assertLess(routing.distance(decoded[0], points[-1]), 4)
        self.assertLess(routing.distance(decoded[-1], points[0]), 4)

    def test_invalid_or_truncated_paths_fail(self):
        for bad in ['', '0', '9', '91abc', '90!!!!!!!!!', '90xn76urx66x']:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                decode_path(bad)

    def test_curve_follows_source_vertices(self):
        feature = {'geometry': {'type':'LineString','coordinates':[[139,35],[139.01,35],[139.01,35.01]]}}
        graph = routing.RailGeometry([feature])
        result = graph.path((139,35),(139.01,35.01))
        self.assertIsNotNone(result)
        distance, packed = result
        points = decode_path(packed)
        self.assertGreater(len(points), 2)
        self.assertTrue(any(routing.distance(p,(139.01,35)) < 4 for p in points))
        self.assertGreater(distance * 1000, routing.distance((139,35),(139.01,35.01)))

    def test_disconnected_rail_segments_are_not_fabricated(self):
        features = [{'geometry':{'type':'LineString','coordinates':[[139,35],[139.001,35]]}},
                    {'geometry':{'type':'LineString','coordinates':[[139.1,35],[139.101,35]]}}]
        self.assertIsNone(routing.RailGeometry(features).path((139,35),(139.101,35)))


if __name__ == '__main__':
    unittest.main()
