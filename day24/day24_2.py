#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from typing import Tuple, MutableMapping, Optional, List
from collections import defaultdict


class GameOfBugs:

    neighbours = (-1j, 1j, -1, 1)
    
    def __init__(
            self,
            data: str,
            inner: Optional['GameOfBugs'] = None,
            outer: Optional['GameOfBugs'] = None
    ) -> None:
        self.map, self.width, self.height = self._build_map(data)
        self.map[(2 + 2j)] = '?'
        self.inner: Optional['GameOfBugs'] = inner
        self.outer: Optional['GameOfBugs'] = outer
        self.new_map = { 2 + 2j: '?' }

    def _build_map(self, data: str) -> Tuple[MutableMapping[complex, str], int, int]:
        coords = 0j
        map_ = {}
        for c in data:
            if c == '\n':
                width = int(coords.real)
                coords -= coords.real - 1j
            else:
                map_[coords] = c
                coords += 1
        return map_, width, int(coords.imag)

    def render_map(self):
        return (
            '\n'.join(
                ''.join(
                    c for x in range(self.width) for c in self.map[complex(x, y)]
                ) for y in range(self.height)
            )
        )

    def neighbour_bugs(self, pos: complex) -> int:
        neighbours = (pos + n for n in self.neighbours)
        bugs = 0
        for n in neighbours:
            neighbour_type = self.map.get(n)
            if not neighbour_type:
                if self.outer:
                    outer_coords: List[complex] = []
                    if n.imag < 0:
                        outer_coords.append(2 + 1j)
                    elif n.imag > 4:
                        outer_coords.append(2 + 3j)
                    if n.real < 0:
                        outer_coords.append(1 + 2j)
                    elif n.real > 4:
                        outer_coords.append(3 + 2j)
                    bugs += sum(1 for c in outer_coords if self.outer.map[c] == '#')
            elif neighbour_type == '?':
                if self.inner:
                    inner_coords: List[complex] = []
                    if pos == 2 + 1j:
                        inner_coords.extend((0j, 1 + 0j, 2 + 0j, 3 + 0j, 4 + 0j))
                    elif pos == 1 + 2j:
                        inner_coords.extend((0j, 1j, 2j, 3j, 4j))
                    elif pos == 3 + 2j:
                        inner_coords.extend((4 + 0j, 4 + 1j, 4 + 2j, 4 + 3j, 4 + 4j))
                    elif pos == 2 + 3j:
                        inner_coords.extend((4j, 1 + 4j, 2 + 4j, 3 + 4j, 4 + 4j))
                    bugs += sum(1 for c in inner_coords if self.inner.map[c] == '#')
            elif neighbour_type == '#':
                bugs += 1
        return bugs

    def compute_next_step(self) -> None:
        for pos, c in self.map.items():
            nigh_bugs = self.neighbour_bugs(pos)
            if c == '#':
                self.new_map[pos] = '#' if nigh_bugs == 1 else '.'
            elif c == '.':
                self.new_map[pos] = '#' if nigh_bugs in (1, 2) else '.'
    
    def step(self) -> None:
        self.map = self.new_map.copy()

    def bugs(self) -> int:
        return list(self.map.values()).count('#')


def make_empty_gob():
    return GameOfBugs('.....\n' * 5)



def run():
    with open('input.txt', encoding='utf8') as fh:
        gob = GameOfBugs(fh.read(), make_empty_gob(), make_empty_gob())
    gob.inner = make_empty_gob()
    gob.inner.outer = gob
    gob.outer = make_empty_gob()
    gob.outer.inner = gob

    start = gob
    for minute in range(200):
        gob = start
        gob.compute_next_step()
        while gob.inner:
            gob = gob.inner
            gob.compute_next_step()
        gob = start
        while gob.outer:
            gob = gob.outer
            gob.compute_next_step()
        gob = start
        gob.step()
        while gob.inner:
            gob = gob.inner
            gob.step()
        if not minute % 2:
            gob.inner = make_empty_gob()
            gob.inner.outer = gob
        gob = start
        while gob.outer:
            gob = gob.outer
            gob.step()
        if not minute % 2:
            gob.outer = make_empty_gob()
            gob.outer.inner = gob

    gob = start
    bugs = 0
    while gob:
        bugs += gob.bugs()
        gob = gob.inner
    gob = start.outer
    while gob:
        bugs += gob.bugs()
        gob = gob.outer
    print(bugs)

if __name__ == '__main__':
    run()