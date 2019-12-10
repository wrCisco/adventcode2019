#!/usr/bin/env python
# -*- coding: utf-8 -*-


import math


def factors(x):
    f = []
    while abs(x) > 1:
        for i in range(2, abs(x)+1):
            if abs(x) % i == 0:
                f.append(i)
                x //= i
                break
    return f


def common_factors(x, y):
    x, y = factors(x), factors(y)
    common = []
    for f1 in x:
        if f1 in y:
            common.append(f1)
            y.remove(f1)
    return common


def minimal(x, y):
    denominator = 1
    for f in common_factors(x, y):
        denominator *= f
    # if x % denominator != 0 or y % denominator != 0:
    #     return (x, y)
    # else:
    return (x // denominator, y // denominator)


def directions_clockwise(direction):
    offset = math.atan2(0, -1)
    d = offset - math.atan2(direction[1], direction[0])
    if d > 4.71238898038469:
        d -= math.pi + offset
    return d


def run():
    region = []
    with open('input.txt', encoding='utf-8') as fh:
        for line in fh:
            region.append([pos for pos in line])
    width, height = len(region[0]), len(region)
    asteroids = {}
    max_directions = []
    max_vaporized = []
    for x in range(width):
        for y in range(height):
            if region[y][x] == '#':
                asteroid = (x, y)
                in_sight = set()

                directions = {(1, 0), (0, 1), (-1, 0), (0, -1)}
                # bottom-right
                for deltaY in range(1, height - y):
                    for deltaX in range(1, width - x):
                        directions.add(minimal(deltaX, deltaY))
                # top-left
                for deltaY in range(-1, -(y+1), -1):
                    for deltaX in range(-1, -(x+1), -1):
                        directions.add(minimal(deltaX, deltaY))
                # top-right
                for deltaY in range(-1, -(y+1), -1):
                    for deltaX in range(1, width - x):
                        directions.add(minimal(deltaX, deltaY))
                # bottom-left
                for deltaY in range(1, height - y):
                    for deltaX in range(-1, -(x+1), -1):
                        directions.add(minimal(deltaX, deltaY))

                directions = sorted(
                    list(directions),
                    key=lambda d: directions_clockwise(d),
                    reverse=True
                )
                
                vaporized = []
                for dX, dY in directions:
                    pos = [x + dX, y + dY]
                    while 0 <= pos[0] < width and 0 <= pos[1] < height:
                        if region[pos[1]][pos[0]] == '#':
                            vaporized.append(pos)
                            if len(vaporized) > len(max_vaporized):
                                max_vaporized = vaporized[:]
                                max_directions = directions[:]
                            in_sight.add((pos[0], pos[1]))
                            break
                        pos[0] += dX
                        pos[1] += dY

                asteroids[asteroid] = in_sight

    better_point_of_view = max(asteroids, key=lambda x: len(asteroids[x]))
    print(better_point_of_view, len(asteroids[better_point_of_view]))
    print(max_vaporized[199])


if __name__ == '__main__':
    run()
