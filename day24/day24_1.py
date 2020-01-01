#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from typing import Tuple, MutableMapping
from collections import defaultdict


class GameOfBugs:

    neighbours = (-1j, 1j, -1, 1)
    twos_powers = { complex(n % 5, n // 5): 2 ** n for n in range(25) }
    
    def __init__(self, data: str) -> None:
        self.map, self.width, self.height = self._build_map(data)

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
        return sum(1 for n in self.neighbours if self.map.get(pos + n) == '#')

    def next_step(self) -> None:
        new_map = {}
        for pos, c in self.map.items():
            neighbours = self.neighbour_bugs(pos)
            if c == '#':
                new_map[pos] = '#' if neighbours == 1 else '.'
            else:
                new_map[pos] = '#' if neighbours in (1, 2) else '.'
        self.map = new_map

    def biodiversity_rating(self):
        return sum(self.twos_powers[coords] for coords in self.map if self.map[coords] == '#')


def run():
    with open('input.txt', encoding='utf8') as fh:
        gob = GameOfBugs(fh.read())

    layouts = set()
    n = 0
    while True:
        print(f'After {n} minutes:')
        print(gob.render_map(), end='\n\n')
        rating = gob.biodiversity_rating()
        if rating in layouts:
            print(rating)
            break
        layouts.add(rating)
        gob.next_step()
        n += 1

if __name__ == '__main__':
    run()