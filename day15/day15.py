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


class RepairDroid:

    movements = {
        1:  0 - 1j,  # north
        2:  0 + 1j,  # south
        3: -1 + 0j,  # west
        4:  1 + 0j   # east
    }
    instructions = {
        v: k for k, v in movements.items()
    }
    directions = {
        1: 'North',
        2: 'South',
        3: 'West',
        4: 'East'
    }

    def __init__(self):
        self.map: MutableMapping[complex, str] = defaultdict(lambda: ' ')  # ' ': unexplored space
        self.pos = 0j
        self.map[self.pos] = '.'
        self.last_instruction = None
        self.oxygen_system = 0j
        self.path_to_unexplored = []
        
    def process(self, program_output: int) -> None:
        movement = RepairDroid.movements[self.last_instruction]
        if program_output == 0:  # hit a wall
            self.map[self.pos + movement] = '#'
            self.path_to_unexplored.clear()
        elif program_output == 1:  # empty space
            self.pos += movement
            self.map[self.pos] = '.'
        elif program_output == 2:  # found oxygen system
            self.pos += movement
            self.map[self.pos] = '.'
            self.oxygen_system = self.pos

    def send(self) -> Sequence[int]:
        if not self.path_to_unexplored:
            self.path_to_unexplored = self.next_path()
        if not self.path_to_unexplored:
            raise EndProgram
        self.last_instruction = RepairDroid.instructions[self.path_to_unexplored[0] - self.pos]
        del self.path_to_unexplored[0]
        #print(f'moving {RepairDroid.directions[self.last_instruction]} from {self.pos} to {self.pos + self.movements[self.last_instruction]}')
        return [self.last_instruction]

    def next_path(self):
        '''
        Find the closest unexplored region and return
        the path toward that space.
        '''
        paths = [[self.pos]]
        new_paths = []
        dead_paths = []
        while paths:
            for i, path in enumerate(paths):
                pos = path[-1]
                walkable_paths = self.walkable_neighbours(pos) - set(path)
                if not walkable_paths:
                    dead_paths.append(i)
                new_path = path.copy()
                for index, walkable in enumerate(walkable_paths):
                    if index:
                        new_paths.append(new_path.copy())
                        p = new_paths[-1]
                    else:
                        p = path
                    p.append(walkable)
                    if self.map[walkable] == ' ':
                        return p[1:]
            for index in reversed(dead_paths):
                del paths[index]
            paths.extend(new_paths)
            dead_paths.clear()
            new_paths.clear()

    def walkable_neighbours(self, pos: complex) -> Set[complex]:
        return set(pos + move for move in RepairDroid.movements.values() if self.map[pos + move] != '#')

    def render_map(self):
        offset_x = min(int(x.real) for x in self.map)
        offset_y = min(int(y.imag) for y in self.map)
        width = max(int(x.real) for x in self.map) - offset_x
        height = max(int(y.imag) for y in self.map) - offset_y
        if self.oxygen_system:
            self.map[self.oxygen_system] = 'X'
        if self.oxygen_system != self.pos:
            self.map[self.pos] = 'D'
        self.map[0j] = 'O'
        for y in range(height+1):
            print(''.join(pos for x in range(width+1) for pos in self.map[complex(x + offset_x, y + offset_y)]))
        self.map[0j] = '.'
        if self.oxygen_system != self.pos:
            self.map[self.pos] = '.'
        if self.oxygen_system:
            self.map[self.oxygen_system] = '.'


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

def bfs(graph: MutableMapping[complex, str], start: complex, end: complex):
    if end is not None:
        condition = lambda: graph[end] != 'O'
    else:
        condition = lambda: any(pos == '.' for pos in graph.values())
    paths = [[start]]
    new_paths = []
    dead_paths = []
    steps = 0
    movements = [ 0 - 1j, 0 + 1j, -1 + 0j, 1 + 0j ]
    while condition():
        steps += 1
        for i, path in enumerate(paths):
            pos = path[-1]
            neighbours = [pos + movement for movement in movements if graph[pos + movement] == '.']
            if not neighbours:
                dead_paths.append(i)
            for index, neighbour in enumerate(neighbours):
                if not index:
                    p = path
                else:
                    new_paths.append(path[:-1])
                    p = new_paths[-1]
                p.append(neighbour)
                graph[neighbour] = 'O'
        for i in reversed(dead_paths):
            del paths[i]
        dead_paths.clear()
        paths.extend(new_paths)
        new_paths.clear()
    return steps

def run():
    with open('input.txt', encoding='utf-8') as fh:
        program = [int(code) for code in fh.read().split(',') if code]
    computer = IntcodeComputer()

    droid = RepairDroid()
    moves = Program(program, 0, [], 0, droid, droid)
    try:
        computer.run_program(moves)
    except EndProgram:
        pass
    droid.render_map()
    print(f'Steps from origin to oxygen system: {bfs(deepcopy(droid.map), 0j, droid.oxygen_system)}')
    print(f'Minutes to fill the space with oxygen: {bfs(deepcopy(droid.map), droid.oxygen_system, None)}')

if __name__ == '__main__':
    run()
