#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from typing import Sequence, List
import sys


def shuffle1(deck: List[int], instructions: Sequence[str]) -> List[int]:
    for instruction in instructions:
        if instruction == 'deal into new stack':
            deck.reverse()
        elif instruction.startswith('deal with increment '):
            n = int(instruction[len('deal with increment '):])
            new_deck = deck[:]
            pos = 0
            for card in deck:
                new_deck[pos] = card
                pos = (pos + n) % len(deck)
            deck = new_deck
        elif instruction.startswith('cut '):
            n = int(instruction[len('cut '):])
            deck = deck[n:] + deck[:n]
    return deck


def shuffle2(cards: int, instructions: Sequence[str], pos: int) -> int:
    for instruction in instructions:
        if instruction == 'deal into new stack':
            pos = cards - 1 - pos
        elif instruction.startswith('deal with increment '):
            n = int(instruction[len('deal with increment '):])
            offset = 0
            offset_increment = n - cards % n
            used = 0
            while True:
                if (pos - offset) % n == 0:
                    pos = used + ((pos - offset) // n)
                    break
                cycle, r = divmod(cards - offset, n)
                used += cycle
                if r != 0:
                    used += 1
                offset = (offset + offset_increment) % n
        elif instruction.startswith('cut '):
            n = -int(instruction[len('cut '):])
            if n < 0:
                n = cards + n
            if pos > n:
                pos -= n
            else:
                pos = cards - (n - pos)
    return pos


def shuffle3(cards: int, instructions: Sequence[str], pos: int) -> int:
    for instruction in instructions:
        if instruction == 'deal into new stack':
            pos = cards - 1 - pos
        elif instruction.startswith('deal with increment '):
            n = int(instruction[len('deal with increment '):])
            pos = (n * pos) % cards
        elif instruction.startswith('cut '):
            n = int(instruction[len('cut '):])
            if n < 0:
                n = cards + n
            if pos > n:
                pos -= n
            else:
                pos = cards - (n - pos)
    return pos


def run():
    with open('input.txt', encoding='utf-8') as fh:
        instructions = [instr for instr in fh.read().splitlines()]

    result = shuffle1([n for n in range(10007)], instructions).index(2019)
    print(result)  # first answer

    control = shuffle2(10007, reversed(instructions), result)
    assert control == 2019

    control2 = shuffle3(10007, instructions, 2019)
    assert control2 == result


if __name__ == '__main__':
    run()
