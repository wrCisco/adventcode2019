#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from typing import (
    Sequence, Optional, Callable, List, Union, Any,
    MutableSequence, DefaultDict, Deque, Dict
)
from collections import defaultdict, deque
from copy import deepcopy
import threading, time, os


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
            inputs: Optional[MutableSequence[int]] = None,
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
        self.memory: DefaultDict[int, int] = defaultdict(int)
        for i, code in enumerate(memory):
            self.memory[i] = code
        self.instruction_pointer = instr_ptr
        self.inputs = deque(inputs or [])
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


class AsciiPrinter:

    def process(self, output: int) -> None:
        if output > 128:
            print(output)
        else:
            print(chr(output), end='')


class IntcodeComputer:

    def __init__(self) -> None:
        self.memory: DefaultDict[int, int] = defaultdict(int)
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

    def add_program(self, program: Program) -> None:
        self.programs.append(program)

    def load_program(self, program_index: int) -> None:
        self.memory = self.programs[program_index].memory.copy()
        self.instruction_pointer = self.programs[program_index].instruction_pointer
        self.relative_base = self.programs[program_index].relative_base
        self.running_program = program_index
        self.output_recipient = self.programs[program_index].output_recipient
        self.input_source = self.programs[program_index].input_source

    def freeze_running_program(self) -> None:
        program = self.programs[self.running_program]
        program.memory = self.memory.copy()
        program.instruction_pointer = self.instruction_pointer
        program.relative_base = self.relative_base
        program.output_recipient = self.output_recipient
        program.input_source = self.input_source

    def next_program(self) -> int:
        return (self.running_program + 1) % len(self.programs)

    def load_next_program(self) -> None:
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

    def run_programs(self, start_index: int = 0) -> int:
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
            operand = self.programs[self.running_program].inputs.popleft()
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
        except (InvalidInstruction, KeyError) as e:
            raise InvalidInstruction(
                'Found invalid instruction at position '
                f'{self.instruction_pointer}: {self.memory[self.instruction_pointer]}'
            ) from e
        return self.instructions[instruction].size


class NetworkInterfaceController:

    def __init__(self) -> None:
        '''
        Packets are received one bit at a time in self.packets.
        When they are complete, they are moved to self.sender,
        and then sent to clients on demand.
        '''
        self.packets: Dict[int, List[List[int]]] = { dest: [] for dest in range(50) }
        self.sender: Dict[int, Deque[List[int]]] = { dest: deque() for dest in range(50) }
        self.NAT: List[int] = []
        self.prev_NATY: Optional[int] = None
        self.last_packet: Dict[int, List[int]] = { dest: [] for dest in range(50) }
        self.first_255: Optional[int] = None
        self.lock = threading.RLock()

    def restart_if_idle(self) -> None:
        with self.lock:
            if self._is_idle() and self.NAT:
                try:
                    if self.prev_NATY == self.NAT[1]:
                        print(f'First Y value sent by the NAT twice in a row: {self.NAT[1]}')  # second answer
                        os._exit(0)  # quick and dirty exit
                except IndexError:
                    pass
                self.sender[0].append([0] + self.NAT)
                self.prev_NATY = self.NAT[1]
                self.NAT.clear()

    def update_NAT(self, packet: List[int]) -> None:
        with self.lock:
            if self.first_255 is None:
                print(f'First Y value sent to 255: {packet[1]}')  # first answer
                self.first_255 = packet[1]
            self.NAT = packet[:]

    def update_sender(self, packet: List[int]) -> None:
        with self.lock:
            self.sender[packet[0]].append(packet[:])

    def retrieve_packet(self, ip: int) -> List[int]:
        with self.lock:
            try:
                packet = self.sender[ip].popleft()[1:]
            except IndexError:
                packet = [-1]
            self.last_packet[ip] = packet
            return packet

    def _is_idle(self) -> bool:
        with self.lock:
            if any(self.sender.values()) or any(self.packets.values()) \
                    or not all((packet == [-1] for packet in self.last_packet.values())):
                return False
            return True

    def check_idle(self) -> None:
        while True:
            time.sleep(0.1)
            self.restart_if_idle()


class Client:

    def __init__(self, ip: int, net: NetworkInterfaceController) -> None:
        self.ip = ip
        self.net = net

    def process(self, output: int) -> None:
        #print(f'{self.ip} is sending {output}')
        if not self.net.packets.get(self.ip):
            self.net.packets[self.ip].append([])
        packet = self.net.packets[self.ip][-1]
        packet.append(output)
        if len(packet) == 3:
            if packet[0] == 255:
                self.net.update_NAT(packet[1:])
            else:
                self.net.update_sender(packet)
            del self.net.packets[self.ip][-1]

    def send(self) -> List[int]:
        return self.net.retrieve_packet(self.ip)


def run():
    with open('input.txt', encoding='utf-8') as fh:
        program = [int(code) for code in fh.read().split(',')]

    NIC = NetworkInterfaceController()

    for t in range(50):
        c = IntcodeComputer()
        client = Client(t, NIC)
        p = Program(program[:], 0, [t], 0, client, client)
        threading.Thread(target=c.run_program, args=(p,)).start()
    
    threading.Thread(target=NIC.check_idle).start()


if __name__ == '__main__':
    run()
