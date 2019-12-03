#!/usr/bin/env python
# -*- coding: utf-8 -*-

with open('input.txt', encoding='utf-8') as fh:
    data = [int(mass) for mass in fh.readlines() if mass]

fuel = 0

for mass in data:
    fuel_for_module = mass // 3 - 2
    if fuel_for_module >= 9:
        data.append(fuel_for_module)
    fuel += fuel_for_module

print(fuel)
