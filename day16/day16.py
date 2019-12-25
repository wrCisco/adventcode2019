#!/usr/bin/env python3

import operator


def run():
    with open('input.txt', encoding='utf-8') as fh:
        signal = [int(c) for c in fh.read().strip('\n')]
    base_pattern = [0, 1, 0, -1]

    input_list = signal
    output_list = []
    for phase in range(100):
        prev_num = 0
        for i in range(len(input_list)):
            if i <= len(input_list) // 2:
                pattern = [d for d in base_pattern for _ in range(i+1)]
                pattern *= len(input_list) // len(pattern) + 2
                new_num = abs(sum(map(operator.mul, input_list[i:], pattern[i+1:])))
            else:
                new_num = prev_num - input_list[i - 1]
            output_list.append(new_num % 10)
            prev_num = new_num
        input_list = output_list[:]
        output_list.clear()
    print(''.join(str(d) for d in input_list[:8]))  # first answer


    input_list = signal * 5000
    message_offset = int(''.join(str(d) for d in signal[:7])) - len(input_list)
    for phase in range(100):
        new_num = sum(input_list)
        output_list.append(new_num % 10)
        prev_num = new_num
        for i in range(1, len(input_list)):
            new_num = prev_num - input_list[i - 1]
            output_list.append(new_num % 10)
            prev_num = new_num
        input_list = output_list[:]
        output_list.clear()
    print('message:', ''.join(str(d) for d in input_list[message_offset:message_offset+8]))  # second answer


if __name__ == '__main__':
    run()
