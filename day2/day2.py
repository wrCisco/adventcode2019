#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Sequence, Optional, Callable


class InvalidInstruction(Exception):
    pass


class Instruction:

    def __init__(
            self,
            opcode: int,
            size: int,
            func: Callable
    ) -> None:
        self.opcode = opcode
        self.size = size  # offset for next instr in program
        self.func = func

    def __call__(self, *args, **kwargs):
        self.func(*args, **kwargs)


class IntcodeComputer:

    def __init__(self) -> None:
        self.memory = []
        self.instruction_pointer = 0
        self.instructions = {
            1: Instruction(opcode=1, size=4, func=self.add),
            2: Instruction(opcode=2, size=4, func=self.mul),
            99: Instruction(opcode=99, size=1, func=self.halt)
        }

    def load_program(self, program: Sequence[int]) -> None:
        self.memory = program[:]

    def run_program(self, program: Optional[Sequence[int]] = None) -> int:
        if program:
            self.load_program(program)
        self.instruction_pointer = 0
        while self.memory[self.instruction_pointer] != 99:
            self.instruction_pointer += self.compute()
        return self.memory[0]

    def dump_memory(self) -> None:
        print(', '.join((str(code) for code in self.memory)))

    def _binary_instruction(self):
        first_operand = self.memory[self.memory[self.instruction_pointer+1]]
        second_operand = self.memory[self.memory[self.instruction_pointer+2]]
        result_pointer = self.memory[self.instruction_pointer+3]
        return (first_operand, second_operand, result_pointer)

    def add(self):
        first_operand, second_operand, result_pointer = self._binary_instruction()
        self.memory[result_pointer] = first_operand + second_operand

    def mul(self):
        first_operand, second_operand, result_pointer = self._binary_instruction()
        self.memory[result_pointer] = first_operand * second_operand

    def halt(self):
        return

    def compute(self) -> int:
        opcode = self.memory[self.instruction_pointer]
        try:
            self.instructions[opcode]()
        except KeyError:
            raise InvalidInstruction(
                'Found invalid instruction at position '
                f'{self.instruction_pointer}: {self.memory[self.instruction_pointer]}'
            )
        return self.instructions[opcode].size


def run():
    with open('input.txt', encoding='utf-8') as fh:
        program = [int(code) for code in fh.read().split(',') if code]
    computer = IntcodeComputer()

    # examples:
    # computer.run_program([1, 0, 0, 0, 99])
    # computer.run_program([2, 3, 0, 3, 99])
    # computer.run_program([2, 4, 4, 5, 99, 0])
    # computer.run_program([1, 1, 1, 4, 99, 5, 6, 0, 99])

    # first question:
    program[1] = 12
    program[2] = 2
    computer.run_program(program)
    print(f'1. The answer is {computer.memory[0]}')
    
    # second question:
    original_program = program[:]
    for noun in range(100):
        for verb in range(100):
            program[1] = noun
            program[2] = verb
            try:
                result = computer.run_program(program)
            except InvalidInstruction as e:
                print(e.args[0])
            else:
                if result == 19690720:
                    print("2. The answer is", 100 * noun + verb)
                    return
            program = original_program[:]


if __name__ == '__main__':
    run()
