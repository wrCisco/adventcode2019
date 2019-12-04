#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re


def run():
    with open('input.txt', encoding='utf-8') as fh:
        psw_range = [int(limit) for limit in fh.read().split('-')]
    num = psw_range[0]
    passwords_first_part = set()
    passwords_second_part = set()
    for num in range(psw_range[0], psw_range[1]+1):
        digits = str(num)
        has_double = False
        has_same_digit_sequence = False
        matches = re.findall(r'([0-9])(\1+)', digits)
        for m in matches:
            sequence = ''.join(m)
            if len(sequence):
                has_same_digit_sequence = True
            if len(sequence) == 2:
                has_double = True
                break
        is_monotonic = True
        previous = digits[0]
        for i, digit in enumerate(digits[1:], 1):
            if int(digit) < int(previous):
                is_monotonic = False
            previous = digit
        if has_same_digit_sequence and is_monotonic:
            passwords_first_part.add(num)
            if has_double:
                passwords_second_part.add(num)
    print(len(passwords_first_part))
    print(len(passwords_second_part))


if __name__ == '__main__':
    run()
