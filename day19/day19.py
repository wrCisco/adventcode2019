#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Sequence, Optional, Callable, List, Union, Any, MutableMapping, Set
from collections import defaultdict
from copy import deepcopy


class InvalidInstruction(Exception):
    pass

class EndProgram(Exception):
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
            inputs: Optional[Sequence[int]] = None,
            rel_base: int = 0,
            output_recipient: Optional[Any] = None,
            input_source: Optional[Any] = None
    ) -> None:
        '''
        output_recipient must have a 'process' method
        which takes as argument the output of the program
        and is called every time an output instruction is executed
        (if there is an output_recipient).
        input_source must have a 'send' method, which must return
        the values (as a list) to extend the 'inputs' list
        of the program. The send method is called every time an
        input instruction is executed and the inputs list of the
        program is empty (and input_source is not None).
        '''
        self.memory = defaultdict(int)
        for i, code in enumerate(memory):
            self.memory[i] = code
        self.instruction_pointer = instr_ptr
        self.inputs = inputs or []
        self.relative_base = rel_base
        self.output_recipient = output_recipient
        self.input_source = input_source

    def dump_program(self):
        print(
            'MEMORY:',
            f'{", ".join(str(self.memory[num]) for num in sorted(self.memory))}',
            f'INSTRUCTION POINTER: {self.instruction_pointer}',
            f'RELATIVE BASE: {self.relative_base}',
            f'INPUTS: {self.inputs}',
            sep='\n',
            end='\n\n'
        )


class DroidControl:

    def __init__(self):
        self.map: MutableMapping[Tuple[int, int], int] = defaultdict(int)
        self.width = 50
        self.height = 50
        self.last_coords: Tuple[int, int] = ()
        self.regions_affected = 0
        self.offset_x = 0
        self.offset_y = 0

    def reset(self):
        self.width = 0
        self.height = 0
        self.last_coords = ()
        self.regions_affected = 0
        self.offset_x = 0
        self.offset_y = 0

    def process(self, program_output: int):
        self.map[self.last_coords] = program_output
        if program_output == 1:
            self.regions_affected += 1

    def send(self) -> List[int]:
        if not self.last_coords:
            self.last_coords = (self.offset_x, self.offset_y)
        elif self.last_coords[0] == self.offset_x + self.width - 1:
            self.last_coords = (self.offset_x, self.last_coords[1] + 1)
        else:
            self.last_coords = (self.last_coords[0] + 1, self.last_coords[1])
        #print('returning', self.last_coords)
        return self.last_coords

    def render_map(self):
        for y in range(self.offset_y, self.offset_y + self.height):
            print(
                y,
                ''.join(
                    str(self.map[(x, y)]) for x in range(self.offset_x, self.offset_x + self.width)
                ).replace('0', '.').replace('1', '#')
            )

class IntcodeComputer:

    def __init__(self) -> None:
        self.memory = defaultdict(int)
        self.instruction_pointer = 0
        self.relative_base = 0
        self.instructions = {
            1: Instruction(size=4, func=self.add),
            2: Instruction(size=4, func=self.mul),
            3: Instruction(size=2, func=self.input_),
            4: Instruction(size=2, func=self.output),
            5: Instruction(size=0, func=self.jump_if_true),
            6: Instruction(size=0, func=self.jump_if_false),
            7: Instruction(size=4, func=self.lt),
            8: Instruction(size=4, func=self.eq),
            9: Instruction(size=2, func=self.adjust_base),
            99: Instruction(size=1, func=self.halt)
        }
        self.last_output = 0
        self.programs: List[Program] = []
        self.running_program: int
        self.program_to_freeze: List[int] = []
        self.output_recipient = None
        self.input_source = None

    def add_program(self, program: Program):
        self.programs.append(program)

    def load_program(self, program_index: int) -> None:
        self.memory = self.programs[program_index].memory.copy()
        self.instruction_pointer = self.programs[program_index].instruction_pointer
        self.relative_base = self.programs[program_index].relative_base
        self.running_program = program_index
        self.output_recipient = self.programs[program_index].output_recipient
        self.input_source = self.programs[program_index].input_source

    def freeze_running_program(self):
        program = self.programs[self.running_program]
        program.memory = self.memory.copy()
        program.instruction_pointer = self.instruction_pointer
        program.relative_base = self.relative_base
        program.output_recipient = self.output_recipient
        program.input_source = self.input_source

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
        print(', '.join((str(self.memory[code]) for code in sorted(self.memory))))

    def parameters(self, modes: str) -> List[int]:
        '''
        mode 2 - relative mode: like position mode, but offset with the
        self.relative_base
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
            if mode == '0':
                parameters.append(self.memory[ptr])
            elif mode == '1':
                parameters.append(ptr)
            elif mode == '2':
                parameters.append(self.memory[ptr+self.relative_base])
            else:
                raise InvalidInstruction
        # last parameter: result pointer
        if modes[-1] == '0':
            parameters.append(self.memory[self.instruction_pointer + len(modes)])
        elif modes[-1] == '2':
            parameters.append(
                self.memory[self.instruction_pointer + len(modes)] + self.relative_base
            )
        else:
            raise InvalidInstruction
        return parameters

    def add(self, modes: str) -> None:
        first_operand, second_operand, result_pointer = self.parameters(modes)
        self.memory[result_pointer] = first_operand + second_operand

    def mul(self, modes: str) -> None:
        first_operand, second_operand, result_pointer = self.parameters(modes)
        self.memory[result_pointer] = first_operand * second_operand

    def input_(self, modes: str) -> None:
        #operand = input('> ')
        program = self.programs[self.running_program]
        if not program.inputs and self.input_source:
            program.inputs.extend(self.input_source.send())
        try:
            operand = self.programs[self.running_program].inputs[0]
            del self.programs[self.running_program].inputs[0]
        except IndexError:
            self.program_to_freeze.append(self.running_program)
            return
        write_to = self.parameters(modes[:1])[0]
        self.memory[write_to] = int(operand)

    def output(self, modes: str) -> None:
        out, _ = self.parameters(modes[:2])
        self.last_output = out
        if self.output_recipient:
            self.output_recipient.process(out)
        else:
            self.programs[self.next_program()].inputs.append(out)
            print(out)

    def jump_if_true(self, modes: str) -> None:
        first_parameter, second_parameter = self.parameters(modes)[:-1]
        if first_parameter:
            self.instruction_pointer = second_parameter
        else:
            self.instruction_pointer += 3

    def jump_if_false(self, modes: str) -> None:
        first_parameter, second_parameter = self.parameters(modes)[:-1]
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

    def adjust_base(self, modes: str) -> None:
        parameter = self.parameters(modes[:2])[0]
        self.relative_base += parameter

    def halt(self) -> None:
        return

    def compute(self) -> int:
        opcode = self.memory[self.instruction_pointer]
        instruction = opcode % 100
        parameter_modes = str(opcode)[:-2].zfill(3)[::-1]
        try:
            self.instructions[instruction](parameter_modes)
        except (InvalidInstruction, KeyError):
            raise InvalidInstruction(
                'Found invalid instruction at position '
                f'{self.instruction_pointer}: {self.memory[self.instruction_pointer]}'
            )
        return self.instructions[instruction].size


def run():
    with open('input.txt', encoding='utf-8') as fh:
        program = [int(code) for code in fh.read().split(',') if code]
    computer = IntcodeComputer()

    control = DroidControl()
    for i in range(50*50):
        computer.run_program(Program(program, 0, [], 0, control, control))
    print(control.regions_affected)  # first answer
    control.render_map()

    control.map.clear()
    control.offset_x = 0
    control.offset_y = 0
    control.last_coords = ()
    found = False
    while not found:
        offset_x = control.offset_x
        offset_y = control.offset_y
        control.last_coords = ()
        control.offset_x += 99
        computer.run_program(Program(program, 0, [], 0, control, control))
        if control.map[control.last_coords] == 1:
            control.last_coords = ()
            control.offset_x -= 99
            control.offset_y += 99
            computer.run_program(Program(program, 0, [], 0, control, control))
            if control.map[control.last_coords] == 1:
                found = True
                print(f'{offset_x * 10000 + offset_y}')  # second answer
            else:
                offset_x += 1
        else:
            offset_y += 1
        control.offset_x = offset_x
        control.offset_y = offset_y


if __name__ == '__main__':
    run()
