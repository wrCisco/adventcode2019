#!/usr/bin/env python
# -*- coding: utf-8 -*-


def run():
    with open('input.txt', encoding='utf-8') as fh:
        psw_range = [int(limit) for limit in fh.read().split('-')]
    num = psw_range[0]
    passwords_first_part = set()
    passwords_second_part = set()
    for num in range(psw_range[0], psw_range[1]+1):
        digits = str(num)
        is_monotonic = True
        doubles = set()
        more_than_doubles = set()
        previous = digits[0]
        for i, digit in enumerate(digits[1:], 1):
            if previous == digit:
                doubles.add(digit)
                row = 2
                for d in digits[i-2::-1]:
                    if d == digit:
                        row += 1
                    else:
                        break
                for d in digits[i+1:]:
                    if d == digit:
                        row += 1
                    else:
                        break
                if row > 2:
                    more_than_doubles.add(digit)
            if int(digit) < int(previous):
                is_monotonic = False
            previous = digit
        if doubles and is_monotonic:
            passwords_first_part.add(num)
            if (doubles - more_than_doubles) and is_monotonic:
                passwords_second_part.add(num)
    print(len(passwords_first_part))
    print(len(passwords_second_part))


if __name__ == '__main__':
    run()
