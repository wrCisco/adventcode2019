#!/usr/bin/env python
# -*- coding: utf-8 -*-


from typing import Any, Sequence, Mapping, Set, List


class Wire:

    def __init__(self, path: Sequence[str]) -> None:
        self.path = path
        self.length = 0
        self.coordinates = self.compute_path()

    def compute_path(self) -> Mapping[tuple, int]:
        coords = {}
        pos = [0, 0]
        for direction, length in self.path:
            for step in range(length):
                if direction == 'U':
                    pos[0] += 1
                elif direction == 'D':
                    pos[0] -= 1
                elif direction == 'R':
                    pos[1] += 1
                elif direction == 'L':
                    pos[1] -= 1
                self.length += 1
                try:
                    coords[tuple(pos)]
                except KeyError:
                    coords[tuple(pos)] = self.length
        return coords

    def compare_paths(self, other: Set[tuple]) -> List:
        intersections = []
        for pos in self.coordinates:
            if pos in other.keys():
                intersections.append(
                    (pos, self.coordinates[pos] + other[pos])
                )
        return intersections


def run():
    wires = []
    with open('input.txt', encoding='utf-8') as fh:
        for line in fh:
            path = [(step[0], int(step[1:])) for step in line.split(',') if step]
            wires.append(Wire(path))
    wires[0].compute_path()
    wires[1].compute_path()
    intersections = wires[0].compare_paths(wires[1].coordinates)

    min_distance = min(intersections, key=lambda elem: elem[0][0] + elem[0][1])
    print("Lowest distance:", min_distance[0][0] + min_distance[0][1])

    min_steps = min(intersections, key=lambda elem: elem[1])
    print("Minimum number of steps:", min_steps[1])


if __name__ == '__main__':
    run()
