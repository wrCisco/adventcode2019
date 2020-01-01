#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from typing import Sequence, List, Tuple, Set, Deque, Optional
from collections import deque
import string

import networkx as nx


def get_neighbours(pos: Sequence[int]) -> List[Tuple[int, int]]:
    return [
        (pos[0], pos[1] - 1),
        (pos[0], pos[1] + 1),
        (pos[0] - 1, pos[1]),
        (pos[0] + 1, pos[1])
    ]


def find_shortest_path(
        graph: nx.Graph,
        start: Tuple[int, int],
        end: Tuple[int, int],
        upward: Set[Tuple[int, int]],
        downward: Set[Tuple[int, int]],
        limits: Tuple[int, int] = (0, 1000)
) -> Optional[List]:
    '''
    Find shortest path on a multiple level labyrinth.
    Returns a list of two elements: the last one is a Tuple[int, Tuple[int, int]],
    representing the level and the coordinates of the last step to reach the 'end'
    (which is, the end itself); the first one is a list of two elements: the second
    is a tuple representing the level and the coordinates of the step preceding 
    the last one, while the first one is a list of two elements, and so on...
    '''
    graphs = { 0: graph }
    dist = {(0, start): [[], (0, start)]}
    q: Deque[Tuple[int, Tuple[int, int]]] = deque()
    q.append((0, start))
    while len(q):
        at = q.popleft()
        for next_ in graphs[at[0]][at[1]]:
            level = at[0]
            if at[1] in downward and next_ in upward:
                if level <= limits[0]:
                    continue
                level -= 1
            elif at[1] in upward and next_ in downward:
                if level >= limits[1]:
                    continue
                level += 1
            if not graphs.get(level):
                graphs[level] = graph.copy()
            if (level, next_) not in dist:
                dist[(level, next_)] = [dist[at], (level, next_)]
                q.append((level, next_))
        try:
            return dist[(0, end)]
        except KeyError:
            pass
    return None


def run():
    lab = set()
    label_parts = {}
    with open('input.txt', encoding='utf-8') as fh:
        for y, row in enumerate(fh):
            for x, char in enumerate(row):
                if char == '.':
                    lab.add((x, y))
                elif char in string.ascii_uppercase:
                    label_parts[(x, y)] = char

    labels = {}
    for coords, char in label_parts.items():
        neighbours = get_neighbours(coords)[1::2]
        for n in neighbours:
            try:
                label = char + label_parts[n]
                possible_dots = set(get_neighbours(coords))
                possible_dots.update(get_neighbours(n))
                for d in possible_dots:
                    if d in lab:
                        try:
                            labels[label].append(d)
                        except KeyError:
                            labels[label] = [d]
                break
            except KeyError:
                pass

    start = labels.pop('AA')[0]
    end = labels.pop('ZZ')[0]

    labyrinth = nx.Graph()
    labyrinth.add_edges_from(((p, n) for p in lab for n in get_neighbours(p) if n in lab))
    # for p in lab:
    #     for n in get_neighbours(p):
    #         if n in lab:
    #             labyrinth.add_edge(p, n)
    labyrinth.add_edges_from(labels.values())
    # for label, coords in labels.items():
    #     labyrinth.add_edge(coords[0], coords[1])

    path = nx.shortest_path(labyrinth, start, end)
    print(len(path) - 1)  # first answer

    min_x = min(n[0] for coords in labels.values() for n in coords)
    max_x = max(n[0] for coords in labels.values() for n in coords)
    min_y = min(n[1] for coords in labels.values() for n in coords)
    max_y = max(n[1] for coords in labels.values() for n in coords)

    outer_portals = set()
    inner_portals = set()
    for coords in labels.values():
        for coord in coords:
            if coord[0] in (min_x, max_x) or coord[1] in (min_y, max_y):
                outer_portals.add(coord)
            else:
                inner_portals.add(coord)

    path = find_shortest_path(labyrinth, start, end, inner_portals, outer_portals)
    if not path:
        print("There is no path to ZZ within limits")
    else:
        length = 0
        elem = path[0]
        # rpath = [path[-1]]
        while elem:
            length += 1
            elem = elem[0]
            # rpath.append(elem[-1])
        print(length)  # second answer


if __name__ == '__main__':
    run()
