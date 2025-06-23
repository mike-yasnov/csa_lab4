"""Модель стекового процессора с векторными расширениями и системой прерываний."""

import struct
from typing import List, Dict, Optional, Any, Tuple, Union
from enum import Enum
import logging

from ..isa.opcodes import Opcode, INSTRUCTION_CYCLES, is_vector_operation
from ..isa.machine_code import Instruction, MachineCode


class ProcessorState(Enum):
    """Состояния процессора."""
    RUNNING = "running"
    HALTED = "halted"
    WAITING_FOR_INTERRUPT = "waiting"
    IN_INTERRUPT = "interrupt"


class InterruptType(Enum):
    """Типы прерываний."""
    INPUT_READY = 0
    OUTPUT_REQUEST = 1
    TIMER = 2
    SOFTWARE = 3


class ProcessorError(Exception):
    """Ошибка процессора."""
    pass


class StackUnderflowError(ProcessorError):
    """Ошибка: попытка взять элемент с пустого стека."""
    pass


class StackOverflowError(ProcessorError):
    """Ошибка: переполнение стека."""
    pass


class Memory:
    """Модель памяти (Гарвардская архитектура)."""
    
    def __init__(self, size: int = 65536) -> None:
        self.size = size
        self.data = bytearray(size)
        self.access_count = 0
    
    def read_word(self, address: int) -> int:
        """Читать 32-битное слово из памяти."""
        self.access_count += 1
        if address < 0 or address + 4 > self.size:
            raise ProcessorError(f"Неверный адрес памяти: {address}")
        
        return struct.unpack('<I', self.data[address:address+4])[0]
    
    def write_word(self, address: int, value: int) -> None:
        """Записать 32-битное слово в память."""
        self.access_count += 1
        if address < 0 or address + 4 > self.size:
            raise ProcessorError(f"Неверный адрес памяти: {address}")
        
        self.data[address:address+4] = struct.pack('<I', value)
    
    def read_byte(self, address: int) -> int:
        """Читать байт из памяти."""
        self.access_count += 1
        if address < 0 or address >= self.size:
            raise ProcessorError(f"Неверный адрес памяти: {address}")
        
        return self.data[address]
    
    def write_byte(self, address: int, value: int) -> None:
        """Записать байт в память."""
        self.access_count += 1
        if address < 0 or address >= self.size:
            raise ProcessorError(f"Неверный адрес памяти: {address}")
        
        self.data[address] = value & 0xFF
    
    def load_data(self, data: bytearray, offset: int = 0) -> None:
        """Загрузить данные в память."""
        if offset + len(data) > self.size:
            raise ProcessorError("Данные не помещаются в память")
        
        self.data[offset:offset+len(data)] = data


class IOController:
    """Контроллер ввода-вывода с поддержкой прерываний."""
    
    def __init__(self) -> None:
        self.input_buffer: List[int] = []
        self.output_buffer: List[int] = []
        self.interrupt_schedule: List[Tuple[int, int, int]] = []  # (cycle, type, data)
        self.current_cycle = 0
        
        # Порты
        self.ports: Dict[int, int] = {}
    
    def schedule_input(self, cycle: int, data: int) -> None:
        """Запланировать ввод данных на определенном такте."""
        self.interrupt_schedule.append((cycle, InterruptType.INPUT_READY.value, data))
        self.interrupt_schedule.sort()
    
    def update(self, cycle: int) -> List[Tuple[InterruptType, int]]:
        """Обновить состояние на такте и вернуть список прерываний."""
        self.current_cycle = cycle
        interrupts = []
        
        # Проверяем запланированные прерывания
        while (self.interrupt_schedule and 
               self.interrupt_schedule[0][0] <= cycle):
            scheduled_cycle, int_type, data = self.interrupt_schedule.pop(0)
            
            if int_type == InterruptType.INPUT_READY.value:
                self.input_buffer.append(data)
                interrupts.append((InterruptType.INPUT_READY, data))
        
        return interrupts
    
    def read_port(self, port: int) -> int:
        """Читать из порта."""
        if port == 0:  # Порт ввода
            if self.input_buffer:
                return self.input_buffer.pop(0)
            return 0
        elif port in self.ports:
            return self.ports[port]
        
        return 0
    
    def write_port(self, port: int, value: int) -> None:
        """Записать в порт."""
        if port == 1:  # Порт вывода
            self.output_buffer.append(value)
        else:
            self.ports[port] = value


class VectorUnit:
    """Векторный блок процессора."""
    
    def __init__(self) -> None:
        self.vector_registers: List[List[int]] = [[] for _ in range(8)]  # 8 векторных регистров
        self.vector_length = 4  # Длина вектора по умолчанию
    
    def load_vector(self, reg: int, data: List[int]) -> None:
        """Загрузить вектор в регистр."""
        if 0 <= reg < len(self.vector_registers):
            self.vector_registers[reg] = data[:self.vector_length]
    
    def get_vector(self, reg: int) -> List[int]:
        """Получить вектор из регистра."""
        if 0 <= reg < len(self.vector_registers):
            return self.vector_registers[reg]
        return []
    
    def vector_add(self, reg1: int, reg2: int, result_reg: int) -> None:
        """Векторное сложение."""
        vec1 = self.get_vector(reg1)
        vec2 = self.get_vector(reg2)
        
        result = []
        for i in range(min(len(vec1), len(vec2))):
            result.append((vec1[i] + vec2[i]) & 0xFFFFFFFF)
        
        self.load_vector(result_reg, result)
    
    def vector_sub(self, reg1: int, reg2: int, result_reg: int) -> None:
        """Векторное вычитание."""
        vec1 = self.get_vector(reg1)
        vec2 = self.get_vector(reg2)
        
        result = []
        for i in range(min(len(vec1), len(vec2))):
            result.append((vec1[i] - vec2[i]) & 0xFFFFFFFF)
        
        self.load_vector(result_reg, result)
    
    def vector_mul(self, reg1: int, reg2: int, result_reg: int) -> None:
        """Векторное умножение."""
        vec1 = self.get_vector(reg1)
        vec2 = self.get_vector(reg2)
        
        result = []
        for i in range(min(len(vec1), len(vec2))):
            result.append((vec1[i] * vec2[i]) & 0xFFFFFFFF)
        
        self.load_vector(result_reg, result)
    
    def vector_dot(self, reg1: int, reg2: int) -> int:
        """Скалярное произведение векторов."""
        vec1 = self.get_vector(reg1)
        vec2 = self.get_vector(reg2)
        
        result = 0
        for i in range(min(len(vec1), len(vec2))):
            result += vec1[i] * vec2[i]
        
        return result & 0xFFFFFFFF


class StackProcessor:
    """Стековый процессор с векторными расширениями."""
    
    def __init__(self, data_memory_size: int = 65536, stack_size: int = 1024) -> None:
        # Память (Гарвардская архитектура)
        self.instruction_memory: List[Instruction] = []
        self.data_memory: bytearray = bytearray(data_memory_size)
        
        # Стек данных
        self.stack: List[int] = []
        self.stack_size = stack_size
        
        # Стек вызовов (для функций)
        self.call_stack: List[int] = []
        
        # Регистры
        self.pc = 0  # Программный счетчик
        
        # Состояние процессора
        self.state = ProcessorState.RUNNING
        self.cycle_count = 0
        self.instruction_count = 0
        
        # IO буферы
        self.input_buffer: List[int] = []
        self.output_buffer: List[int] = []
        
        # Логгер
        self.execution_log: List[str] = []
    
    def load_program(self, instructions: List[Instruction]) -> None:
        """Загрузить программу в память команд."""
        self.instruction_memory = instructions
        self.pc = 0
    
    def load_data(self, data: bytearray, offset: int = 0) -> None:
        """Загрузить данные в память данных."""
        if offset + len(data) > len(self.data_memory):
            raise ProcessorError("Данные не помещаются в память")
        
        self.data_memory[offset:offset+len(data)] = data
    
    def push(self, value: int) -> None:
        """Положить значение на стек."""
        if len(self.stack) >= self.stack_size:
            raise ProcessorError("Переполнение стека")
        
        self.stack.append(value & 0xFFFFFFFF)
    
    def pop(self) -> int:
        """Снять значение со стека."""
        if not self.stack:
            raise ProcessorError("Стек пуст")
        
        return self.stack.pop()
    
    def read_memory_word(self, address: int) -> int:
        """Читать 32-битное слово из памяти данных."""
        if address < 0 or address + 4 > len(self.data_memory):
            raise ProcessorError(f"Неверный адрес памяти: {address}")
        
        return struct.unpack('<I', self.data_memory[address:address+4])[0]
    
    def write_memory_word(self, address: int, value: int) -> None:
        """Записать 32-битное слово в память данных."""
        if address < 0 or address + 4 > len(self.data_memory):
            raise ProcessorError(f"Неверный адрес памяти: {address}")
        
        self.data_memory[address:address+4] = struct.pack('<I', value)
    
    def execute_instruction(self, instruction: Instruction) -> bool:
        """Выполнить инструкцию. Возвращает True если нужно продолжать."""
        opcode = instruction.opcode
        operand = instruction.operand
        
        # Логируем выполнение
        self.log_execution(instruction)
        
        try:
            if opcode == Opcode.HALT:
                self.state = ProcessorState.HALTED
                return False
            
            elif opcode == Opcode.PUSH:
                self.push(operand)
            
            elif opcode == Opcode.POP:
                self.pop()
            
            elif opcode == Opcode.ADD:
                b = self.pop()
                a = self.pop()
                result = (a + b) & 0xFFFFFFFF
                self.push(result)
            
            elif opcode == Opcode.SUB:
                b = self.pop()
                a = self.pop()
                result = (a - b) & 0xFFFFFFFF
                self.push(result)
            
            elif opcode == Opcode.MUL:
                b = self.pop()
                a = self.pop()
                result = (a * b) & 0xFFFFFFFF
                self.push(result)
            
            elif opcode == Opcode.LOAD:
                address = self.pop()
                value = self.read_memory_word(address)
                self.push(value)
            
            elif opcode == Opcode.STORE:
                address = self.pop()
                value = self.pop()
                self.write_memory_word(address, value)
            
            elif opcode == Opcode.OUT:
                value = self.pop()
                self.output_buffer.append(value)
            
            else:
                raise ProcessorError(f"Неизвестная инструкция: {opcode}")
        
        except ProcessorError as e:
            self.state = ProcessorState.HALTED
            return False
        
        # Увеличиваем PC
        self.pc += 1
        return True
    
    def step(self) -> bool:
        """Выполнить один шаг. Возвращает True если нужно продолжать."""
        if self.state == ProcessorState.HALTED or self.pc >= len(self.instruction_memory):
            return False
        
        instruction = self.instruction_memory[self.pc]
        cycles = INSTRUCTION_CYCLES.get(Opcode(instruction.opcode), 1)
        
        continue_execution = self.execute_instruction(instruction)
        
        self.cycle_count += cycles
        self.instruction_count += 1
        
        return continue_execution
    
    def run(self, max_cycles: int = 1000000) -> Dict[str, Any]:
        """Запустить выполнение программы."""
        start_cycle = self.cycle_count
        
        while self.cycle_count - start_cycle < max_cycles:
            if not self.step():
                break
        
        return {
            'state': self.state.value,
            'instructions_executed': self.instruction_count,
            'cycles_executed': self.cycle_count - start_cycle,
            'final_pc': self.pc,
            'stack_size': len(self.stack),
            'output': self.output_buffer.copy(),
            'execution_log': self.execution_log.copy()
        }
    
    def log_execution(self, instruction: Instruction) -> None:
        """Логировать выполнение инструкции."""
        stack_top = f"TOS={self.stack[-1]}" if self.stack else "TOS=empty"
        log_entry = (f"Cycle {self.cycle_count:06d}: PC={self.pc:04X} "
                    f"{instruction.opcode:02X}({instruction.operand:06X}) "
                    f"Stack[{len(self.stack)}] {stack_top}")
        
        self.execution_log.append(log_entry)
        
        # Ограничиваем размер лога
        if len(self.execution_log) > 1000:
            self.execution_log = self.execution_log[-500:] 