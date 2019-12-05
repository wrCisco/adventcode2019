#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Sequence, Optional, Callable, List


class InvalidInstruction(Exception):
    pass


class Instruction:

    def __init__(
            self,
            size: int,
            func: Callable
    ) -> None:
        self.size = size  # offset for next instr in program
        self.func = func

    def __call__(self, *args, **kwargs):
        self.func(*args, **kwargs)


class IntcodeComputer:

    def __init__(self) -> None:
        self.memory = []
        self.instruction_pointer = 0
        self.instructions = {
            1: Instruction(size=4, func=self.add),
            2: Instruction(size=4, func=self.mul),
            3: Instruction(size=2, func=self.input_),
            4: Instruction(size=2, func=self.output),
            5: Instruction(size=0, func=self.jump_if_true),
            6: Instruction(size=0, func=self.jump_if_false),
            7: Instruction(size=4, func=self.lt),
            8: Instruction(size=4, func=self.eq),
            99: Instruction(size=1, func=self.halt)
        }

    def load_program(self, program: Sequence[int]) -> None:
        self.memory = program[:]

    def run_program(self, program: Optional[Sequence[int]] = None) -> int:
        if program:
            self.load_program(program)
        self.instruction_pointer = 0
        while self.memory[self.instruction_pointer] != 99:
            offset = self.compute()
            if offset:
                self.instruction_pointer += offset
        return self.memory[0]

    def dump_memory(self) -> None:
        print(', '.join((str(code) for code in self.memory)))

    def parameters(self, modes: str) -> List[int]:
        '''
        mode 1 - immediate mode: parameter is the value pointed to by the
        self.instruction_pointer + i
        mode 0 - position mode: parameter is the value pointed to by the
        value pointed to by the self.instruction_pointer + i
        The last parameter is always a pointer to the position where the
        result, if any, will have to be written.
        '''
        parameters = []
        for i, mode in enumerate(modes[:-1], 1):
            ptr = self.memory[self.instruction_pointer + i]
            parameters.append(ptr if mode == '1' else self.memory[ptr])
        # last parameter: result pointer
        parameters.append(self.memory[self.instruction_pointer + i + 1])
        return parameters

    def add(self, modes: str) -> None:
        first_operand, second_operand, result_pointer = self.parameters(modes)
        self.memory[result_pointer] = first_operand + second_operand

    def mul(self, modes: str) -> None:
        first_operand, second_operand, result_pointer = self.parameters(modes)
        self.memory[result_pointer] = first_operand * second_operand

    def input_(self, modes: str) -> None:
        operand = input('> ')
        self.memory[self.memory[self.instruction_pointer+1]] = int(operand)

    def output(self, modes: str) -> None:
        out, _ = self.parameters(modes[:2])
        print(out)

    def jump_if_true(self, modes: str) -> None:
        first_parameter, second_parameter, _ = self.parameters(modes)
        if first_parameter:
            self.instruction_pointer = second_parameter
        else:
            self.instruction_pointer += 3

    def jump_if_false(self, modes: str) -> None:
        first_parameter, second_parameter, _ = self.parameters(modes)
        if not first_parameter:
            self.instruction_pointer = second_parameter
        else:
            self.instruction_pointer += 3

    def lt(self, modes: str) -> None:
        first_parameter, second_parameter, result_pointer = self.parameters(modes)
        if first_parameter < second_parameter:
            self.memory[result_pointer] = 1
        else:
            self.memory[result_pointer] = 0

    def eq(self, modes: str) -> None:
        first_parameter, second_parameter, result_pointer = self.parameters(modes)
        if first_parameter == second_parameter:
            self.memory[result_pointer] = 1
        else:
            self.memory[result_pointer] = 0

    def halt(self) -> None:
        return

    def compute(self) -> int:
        opcode = self.memory[self.instruction_pointer]
        instruction = opcode % 100
        parameter_modes = str(opcode)[:-2].zfill(3)[::-1]
        try:
            self.instructions[instruction](parameter_modes)
        except KeyError:
            raise InvalidInstruction(
                'Found invalid instruction at position '
                f'{self.instruction_pointer}: {self.memory[self.instruction_pointer]}'
            )
        return self.instructions[instruction].size


def run():
    with open('input.txt', encoding='utf-8') as fh:
        program = [int(code) for code in fh.read().split(',') if code]
    computer = IntcodeComputer()

    computer.run_program(program)  # to get first answer: manual input 1
    computer.run_program(program)  # to get second answer: manual input 5


if __name__ == '__main__':
    run()
