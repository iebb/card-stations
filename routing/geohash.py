"""Geohash vertices with shared-prefix compression; longitude/latitude input."""
from __future__ import annotations

import math

ALPHABET = '0123456789bcdefghjkmnpqrstuvwxyz'


def encode(longitude, latitude, precision=9):
    if not 1 <= precision <= 9 or not math.isfinite(longitude) or not math.isfinite(latitude) or not -180 <= longitude <= 180 or not -90 <= latitude <= 90:
        raise ValueError('Invalid coordinate or precision')
    bounds = [[-180.0, 180.0], [-90.0, 90.0]]
    output, value = [], 0
    for bit in range(precision * 5):
        axis = bit % 2
        mid = sum(bounds[axis]) / 2
        high = (longitude, latitude)[axis] >= mid
        value = (value << 1) | int(high)
        bounds[axis][0 if high else 1] = mid
        if bit % 5 == 4:
            output.append(ALPHABET[value]); value = 0
    return ''.join(output)


def decode(value):
    if not value or len(value) > 9 or any(c not in ALPHABET for c in value):
        raise ValueError('Invalid geohash')
    bounds = [[-180.0, 180.0], [-90.0, 90.0]]
    bit = 0
    for c in value:
        number = ALPHABET.index(c)
        for shift in range(4, -1, -1):
            axis = bit % 2
            mid = sum(bounds[axis]) / 2
            bounds[axis][0 if number & (1 << shift) else 1] = mid
            bit += 1
    return (sum(bounds[0]) / 2, sum(bounds[1]) / 2)


def encode_path(vertices, precision=9):
    previous, output = '', [str(precision)]
    for longitude, latitude in vertices:
        current = encode(longitude, latitude, precision)
        if current == previous:
            continue
        shared = 0
        while shared < len(previous) and previous[shared] == current[shared]:
            shared += 1
        output.extend((str(shared), current[shared:]))
        previous = current
    return ''.join(output) if previous else ''


def decode_path(value):
    if not value or value[0] not in '123456789':
        raise ValueError('Invalid geohash path precision')
    precision, offset, previous, output = int(value[0]), 1, '', []
    while offset < len(value):
        if value[offset] not in '0123456789':
            raise ValueError('Invalid geohash prefix length')
        shared = int(value[offset]); offset += 1
        if shared > min(len(previous), precision) or offset + precision - shared > len(value):
            raise ValueError('Truncated geohash path')
        current = previous[:shared] + value[offset:offset + precision - shared]
        offset += precision - shared
        output.append(decode(current)); previous = current
    if len(output) < 2:
        raise ValueError('A path needs at least two distinct vertices')
    return output
