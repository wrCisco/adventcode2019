#!/usr/bin/env python
# -*- coding: utf-8 -*-

with open('input.txt', encoding='utf-8') as fh:
    data = [int(mass) for mass in fh.readlines() if mass]

fuel = 0

modules = len(data)
for i, mass in enumerate(data):
    if i == modules:
        print(fuel)  # first answer
    fuel_for_module = mass // 3 - 2
    if fuel_for_module >= 9:
        data.append(fuel_for_module)
    fuel += fuel_for_module

print(fuel)  # second answer
