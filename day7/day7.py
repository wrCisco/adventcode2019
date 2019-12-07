#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Sequence, Optional, Callable, List, Union
from itertools import permutations


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


class Program:

    def __init__(
            self,
            memory: Sequence[int],
            instr_ptr: int = 0,
            inputs: Optional[Sequence[int]] = None
    ) -> None:
        self.memory = memory[:]
        self.instruction_pointer = instr_ptr
        self.inputs = inputs or []

    def dump_program(self):
        print(
            'MEMORY:',
            f'{", ".join(str(num) for num in self.memory)}',
            f'INSTRUCTION POINTER: {self.instruction_pointer}',
            f'INPUTS: {self.inputs}',
            sep='\n',
            end='\n\n'
        )


class IntcodeComputer:

    def __init__(self) -> None:
        self.memory: List[int] = []
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
        self.last_output = 0
        self.programs: List[Program] = []
        self.running_program: int
        self.program_to_freeze: List[int] = []

    def add_program(self, program: Program):
        self.programs.append(program)

    def load_program(self, program_index: int) -> None:
        self.memory = self.programs[program_index].memory[:]
        self.instruction_pointer = self.programs[program_index].instruction_pointer
        self.running_program = program_index

    def freeze_running_program(self):
        program = self.programs[self.running_program]
        program.memory = self.memory[:]
        program.instruction_pointer = self.instruction_pointer

    def next_program(self):
        return (self.running_program + 1) % len(self.programs)

    def load_next_program(self):
        if self.programs:
            self.freeze_running_program()
            self.load_program(self.next_program())

    def run_program(self, program: Union[int, Program]) -> int:
        if isinstance(program, Program):
            self.add_program(program)
            program = len(self.programs) - 1
        self.load_program(program)
        while self.memory[self.instruction_pointer] != 99:
            # print(f'BEFORE\nrunning program index {self.running_program}')
            # self.programs[self.running_program].dump_program()
            offset = self.compute()
            if offset and not self.program_to_freeze:
                self.instruction_pointer += offset
            # print(f'AFTER\nrunning program index {self.running_program}')
            # self.freeze_running_program()
            # self.programs[self.running_program].dump_program()
            # input()
            while self.program_to_freeze:
                self.load_next_program()
                del self.program_to_freeze[0]
        self.programs.remove(self.programs[self.running_program])
        return self.memory[0]

    def run_programs(self, start_index: Optional[int] = 0) -> int:
        self.running_program = start_index
        while self.programs:
            try:
                result = self.run_program(self.running_program)
            except IndexError:
                self.next_program()
        return result

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
        #operand = input('> ')
        try:
            operand = self.programs[self.running_program].inputs[0]
            del self.programs[self.running_program].inputs[0]
        except IndexError:
            self.program_to_freeze.append(self.running_program)
            return
        self.memory[self.memory[self.instruction_pointer+1]] = int(operand)

    def output(self, modes: str) -> None:
        out, _ = self.parameters(modes[:2])
        #print(out)
        self.last_output = out
        self.programs[self.next_program()].inputs.append(out)

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

    outputs = []
    for phase_settings in permutations([0, 1, 2, 3, 4]):
        computer.last_output = 0
        for i in range(5):
            inputs = [phase_settings[i], computer.last_output]
            computer.run_program(Program(program, 0, inputs))
        outputs.append(computer.last_output)
    print(max(outputs))  # first answer

    outputs = []
    for phase_settings in permutations([5, 6, 7, 8, 9]):
        computer.last_output = 0
        for i in range(5):
            inputs = [phase_settings[i]]
            if not i:
                inputs.append(0)
            computer.add_program(Program(program, 0, inputs))
        computer.run_programs()
        outputs.append(computer.last_output)
    print(max(outputs))  # second answer


if __name__ == '__main__':
    run()
