#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from typing import Tuple, List
from copy import deepcopy
import math


class Material:

    def __init__(self, name: str, production_unit: int, reagents: List[Tuple[int, str]]) -> None:
        self.name = name
        self.production_unit = production_unit
        self.reagents = reagents

        self.stashed = 0
        self.tot_prod = 0

    def dump(self) -> str:
        return (
            f'Name: {self.name}\nProduction unit: {self.production_unit}\n'
            f'Reagents: {self.reagents}\nStashed: {self.stashed}\n'
            f'Total production: {self.tot_prod}'
        )


def get_reagents(reactions: dict, product: Material, qty: int) -> int:
    needed_qty = qty - product.stashed  # quantity we'll have to produce = quantity requested - quantity stashed
    if needed_qty <= 0:
        production_qty = 0
        product.stashed -= qty
    else:
        production_qty = needed_qty
        if production_qty % product.production_unit:
            production_qty += product.production_unit - (production_qty % product.production_unit)
        product.stashed = production_qty - needed_qty
    product.tot_prod += production_qty
    # print(f'{product.dump()}\nproduction_qty: {production_qty}\nqty: {qty}\n')
    if product.reagents[0][1] == 'ORE':
        ore = math.ceil(product.reagents[0][0] * production_qty / product.production_unit)
        return ore
    else:
        return sum(
            get_reagents(
                reactions=reactions,
                product=reactions[reagent_name],
                qty=math.ceil(reagent_qty * production_qty / product.production_unit)
            ) for reagent_qty, reagent_name in reactions[product.name].reagents
        )

def run():
    reactions = {} # product_name: Material(product_name, production_unit, reagents)
    with open('input.txt', encoding='utf-8') as fh:
        for reaction in fh:
            elems = reaction.strip('\n').split(' => ')
            reagents = elems[0].split(', ')
            product = elems[1].split(' ')
            rs = [(int(r.split(' ')[0]), r.split(' ')[1]) for r in reagents]
            reactions[product[1]] = Material(product[1], int(product[0]), rs)
    orig_reactions = deepcopy(reactions)

    ore_per_fuel = get_reagents(reactions, reactions['FUEL'], 1)
    print(ore_per_fuel)  # first answer

    # print(f'\nTOTALS:')
    # for i, (name, material) in enumerate(reactions.items(), 1):
    #     print(f'{i: >2}. {material.name: <5} - {material.tot_prod: >5} (stashed: {material.stashed}) (unit: {material.production_unit})')

    collected_ore = 1000000000000
    fuel_bottom = collected_ore // ore_per_fuel
    fuel_top = collected_ore // ore_per_fuel * 100  # reasonably higher than the produced fuel
    fuel = (fuel_top + fuel_bottom) // 2
    while fuel_top != fuel_bottom + 1:
        ore = get_reagents(deepcopy(orig_reactions), reactions['FUEL'], fuel)
        if ore > collected_ore:
            fuel_top = fuel
        else:
            fuel_bottom = fuel
        fuel = (fuel_top + fuel_bottom) // 2
    print(fuel)  # second answer


if __name__ == '__main__':
    run()
