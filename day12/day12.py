#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import re
from typing import List, Sequence


class Moon:

    def __init__(self, x: int, y: int, z: int) -> None:
        self._pos = [x, y, z]
        self._velocity = [0, 0, 0]

    @property
    def x(self) -> int:
        return self.pos[0]

    @x.setter
    def x(self, value: int) -> None:
        self.pos[0] = value

    @property
    def y(self) -> int:
        return self.pos[1]

    @y.setter
    def y(self, value: int) -> None:
        self.pos[1] = value

    @property
    def z(self) -> int:
        return self.pos[2]

    @z.setter
    def z(self, value: int) -> None:
        self.pos[2] = value

    @property
    def pos(self) -> List[int]:
        return self._pos
    
    @pos.setter
    def pos(self, value: List[int]) -> None:
        self._pos = value

    @property
    def dx(self) -> int:
        return self._velocity[0]

    @dx.setter
    def dx(self, value: int) -> None:
        self.velocity[0] = value

    @property
    def dy(self) -> int:
        return self._velocity[1]

    @dy.setter
    def dy(self, value: int) -> None:
        self.velocity[1] = value

    @property
    def dz(self) -> int:
        return self._velocity[2]

    @dz.setter
    def dz(self, value: int) -> None:
        self.velocity[2] = value

    @property
    def velocity(self) -> List[int]:
        return self._velocity
    
    @velocity.setter
    def velocity(self, value: List[int]) -> None:
        self._velocity = value

    def update_velocity(self, others: Sequence['Moon']) -> None:
        dvel = [0, 0, 0]
        for moon in others:
            if moon is self:
                continue
            for i in range(len(self.pos)):
                if self.pos[i] > moon.pos[i]:
                    dvel[i] -= 1
                elif self.pos[i] < moon.pos[i]:
                    dvel[i] += 1
        self.velocity = [self._velocity[i] + dvel[i] for i in range(3)]

    def update_pos(self) -> None:
        self.pos = [self._pos[i] + self._velocity[i] for i in range(3)]

    def potential_energy(self) -> int:
        return sum(abs(x) for x in self.pos)

    def kinetic_energy(self) -> int:
        return sum(abs(x) for x in self.velocity)

    def dump_posvel(self) -> None:
        print(f'pos: x={self.x} y={self.y} z={self.z}   vel: x={self.dx} y={self.dy} z={self.dz}')


def gcd(a: int, b: int) -> int:
    if not a or not b:
        raise ValueError
    while b:
        a, b = b, a % b
    return a


def lcm(a: int, b: int) -> int:
    if not a or not b:
        return 0
    return (a * b) // gcd(a, b)


def run():
    with open('input.txt', encoding='utf-8') as fh:
        moons = [
            Moon(int(x), int(y), int(z)) for line in fh.readlines() if line
            for x, y, z in re.findall(r'x=(-?\d+), y=(-?\d+), z=(-?\d+)', line)
        ]

    prev_x, prev_y, prev_z = {}, {}, {}  # dictionaries of previous configurations
    p_x, p_y, p_z = 0, 0, 0  # periods of single dimensions
    step = 0
    while not p_x or not p_y or not p_z:
        xs = tuple((moon.x, moon.dx) for moon in moons)
        ys = tuple((moon.y, moon.dy) for moon in moons)
        zs = tuple((moon.z, moon.dz) for moon in moons)
        if prev_x.get(xs) and not p_x:
            print(f'found x period: from step {prev_x[xs]} to step {step}')
            print(xs)
            p_x = step - prev_x[xs]
        elif not prev_x.get(xs):
            prev_x[xs] = step
        if prev_y.get(ys) and not p_y:
            print(f'found y period: from step {prev_y[ys]} to step {step}')
            print(ys)
            p_y = step - prev_y[ys]
        elif not prev_y.get(ys):
            prev_y[ys] = step
        if prev_z.get(zs) and not p_z:
            print(f'found z period: from step {prev_z[zs]} to step {step}')
            print(zs)
            p_z = step - prev_z[zs]
        elif not prev_z.get(zs):
            prev_z[zs] = step

        # print(step)
        # for moon in moons:
        #     moon.dump_posvel()
        # input()

        for moon in moons:
            moon.update_velocity(moons)
        for moon in moons:
            moon.update_pos()

        if step == 999:
            total = sum(moon.potential_energy() * moon.kinetic_energy() for moon in moons)
            print('total power after 1000 steps:', total)
            # for moon in moons:
            #     moon.dump_posvel()
        step += 1

    print('number of steps before first period:', lcm(lcm(p_x, p_y), p_z))

if __name__ == '__main__':
    run()
