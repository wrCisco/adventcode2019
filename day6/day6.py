#!/usr/bin/env python
# -*- coding: utf-8 -*-


def find_santa(orbits: dict, orbitants: dict, start: str, finish: str):
    paths = [[start]]
    orbitants[start].remove('YOU')
    dead_paths = set()
    new_paths = []

    while True:
        for i, path in enumerate(paths):
            pos = path[-1]
            next_steps = orbitants.get(pos, [])[:]
            try:
                next_steps.append(orbits[pos])
            except KeyError:
                pass
            for s in next_steps:
                if s == 'SAN':
                    return len(path) - 1                
            for step in next_steps:
                try:
                    if step == path[-2]:
                        next_steps.remove(step)
                except IndexError:
                    pass
            if not next_steps:
                dead_paths.add(i)
            else:
                for step in next_steps[1:]:
                    new_paths.append(path.copy())
                    new_paths[-1].append(step)
                path.append(next_steps[0])
        
        paths.extend(new_paths)
        new_paths = []

        offset = 0
        for n, path in enumerate(paths):
            if n in dead_paths:
                del paths[n + offset]
                offset -= 1
        dead_paths = set()


def run():
    with open('input.txt', encoding='utf-8') as fh:
        orbits = {
        line.split(')')[1].strip('\n'): line.split(')')[0] for line in fh.readlines() if line
    }
    # first question
    total_orbits = 0
    for corp in orbits:
        rcom = orbits[corp]
        orbit_number = 1
        while True:
            try:
                rcom = orbits[rcom]
                print
                orbit_number += 1
            except KeyError:
                break
        total_orbits += orbit_number
    print(total_orbits)

    # second question
    orbitants = {}
    for orbitant, r_com in orbits.items():
        try:
            orbitants[r_com].append(orbitant)
        except KeyError:
            orbitants[r_com] = [orbitant]
    print(find_santa(orbits, orbitants, orbits['YOU'], orbits['SAN']))

if __name__ == '__main__':
    run()
