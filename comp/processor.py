"""Модель стекового процессора с векторными расширениями и системой прерываний."""

import struct
from typing import List, Dict, Optional, Any, Tuple, Union
from enum import Enum
import logging

from isa.opcodes import Opcode, INSTRUCTION_CYCLES, is_vector_operation
from isa.machine_code import Instruction, MachineCode


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


class VectorProcessor:
    """Векторный блок процессора."""
    
    def __init__(self) -> None:
        # 8 векторных регистров
        self.vector_registers: List[List[int]] = [[] for _ in range(8)]
        self.max_vector_length = 16  # Максимальная длина вектора
    
    def load_vector(self, reg_id: int, elements: List[int]) -> None:
        """Загрузить вектор в регистр."""
        if 0 <= reg_id < len(self.vector_registers):
            self.vector_registers[reg_id] = elements[:self.max_vector_length]
    
    def get_vector(self, reg_id: int) -> List[int]:
        """Получить вектор из регистра."""
        if 0 <= reg_id < len(self.vector_registers):
            return self.vector_registers[reg_id].copy()
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
    
    def vector_norm(self, reg: int) -> int:
        """Вычислить норму (длину) вектора."""
        vec = self.get_vector(reg)
        sum_squares = sum(x * x for x in vec)
        return int(sum_squares ** 0.5) & 0xFFFFFFFF
    
    def vector_max(self, reg: int) -> int:
        """Найти максимальный элемент вектора."""
        vec = self.get_vector(reg)
        return max(vec) if vec else 0
    
    def vector_min(self, reg: int) -> int:
        """Найти минимальный элемент вектора."""
        vec = self.get_vector(reg)
        return min(vec) if vec else 0
    
    def vector_sum(self, reg: int) -> int:
        """Сумма элементов вектора."""
        vec = self.get_vector(reg)
        return sum(vec) & 0xFFFFFFFF
    
    def vector_avg(self, reg: int) -> int:
        """Среднее арифметическое элементов вектора."""
        vec = self.get_vector(reg)
        if not vec:
            return 0
        return (sum(vec) // len(vec)) & 0xFFFFFFFF
    
    def vector_scale(self, reg: int, scalar: int, result_reg: int) -> None:
        """Умножение вектора на скаляр."""
        vec = self.get_vector(reg)
        result = [(x * scalar) & 0xFFFFFFFF for x in vec]
        self.load_vector(result_reg, result)
    
    def vector_copy(self, src_reg: int, dst_reg: int) -> None:
        """Копирование вектора."""
        vec = self.get_vector(src_reg)
        self.load_vector(dst_reg, vec)
    
    def vector_set(self, reg: int, index: int, value: int) -> None:
        """Установить элемент вектора."""
        if 0 <= reg < len(self.vector_registers):
            vec = self.vector_registers[reg]
            if 0 <= index < len(vec):
                vec[index] = value & 0xFFFFFFFF
    
    def vector_get(self, reg: int, index: int) -> int:
        """Получить элемент вектора."""
        if 0 <= reg < len(self.vector_registers):
            vec = self.vector_registers[reg]
            if 0 <= index < len(vec):
                return vec[index]
        return 0


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
        
        # Векторный процессор
        self.vector_unit = VectorProcessor()
        
        # Логгер
        self.execution_log: List[str] = []

        # Потактовая модель
        self.current_instruction: Optional[Instruction] = None
        self.remaining_cycles: int = 0

        # Контроллер ввода-вывода (для расписания ввода)
        self.io_controller = IOController()

        # Состояние системы прерываний
        self.interrupts_enabled: bool = False
        self.in_interrupt: bool = False
        self.interrupt_handlers: Dict[int, int] = {}
        self.pending_interrupts: List[Tuple[int, int]] = []  # (vector, data)
    
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
        
        # Логирование факта завершения инструкции (перед выполнением семантики на последнем такте)
        self.log_execution(instruction)
        
        try:
            if opcode == Opcode.HALT:
                self.state = ProcessorState.HALTED
                return False
            
            elif opcode == Opcode.PUSH:
                self.push(operand)
            
            elif opcode == Opcode.POP:
                self.pop()
            
            elif opcode == Opcode.DUP:
                if self.stack:
                    value = self.stack[-1]
                    self.push(value)
                else:
                    raise ProcessorError("Стек пуст для DUP")
            
            elif opcode == Opcode.SWAP:
                if len(self.stack) >= 2:
                    a = self.pop()
                    b = self.pop()
                    self.push(a)
                    self.push(b)
                else:
                    raise ProcessorError("Недостаточно элементов для SWAP")
            
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
            
            elif opcode == Opcode.DIV:
                b = self.pop()
                a = self.pop()
                if b == 0:
                    raise ProcessorError("Деление на ноль")
                result = (a // b) & 0xFFFFFFFF
                self.push(result)
            
            elif opcode == Opcode.MOD:
                b = self.pop()
                a = self.pop()
                if b == 0:
                    raise ProcessorError("Деление на ноль")
                result = (a % b) & 0xFFFFFFFF
                self.push(result)
            
            # Логические операции
            elif opcode == Opcode.AND:
                b = self.pop()
                a = self.pop()
                result = a & b
                self.push(result)
            
            elif opcode == Opcode.OR:
                b = self.pop()
                a = self.pop()
                result = a | b
                self.push(result)
            
            elif opcode == Opcode.NOT:
                a = self.pop()
                result = (~a) & 0xFFFFFFFF
                self.push(result)
            
            # Операции сравнения
            elif opcode == Opcode.EQ:
                b = self.pop()
                a = self.pop()
                result = 1 if a == b else 0
                self.push(result)
            
            elif opcode == Opcode.NE:
                b = self.pop()
                a = self.pop()
                result = 1 if a != b else 0
                self.push(result)
            
            elif opcode == Opcode.LT:
                b = self.pop()
                a = self.pop()
                result = 1 if a < b else 0
                self.push(result)
            
            elif opcode == Opcode.LE:
                b = self.pop()
                a = self.pop()
                result = 1 if a <= b else 0
                self.push(result)
            
            elif opcode == Opcode.GT:
                b = self.pop()
                a = self.pop()
                result = 1 if a > b else 0
                self.push(result)
            
            elif opcode == Opcode.GE:
                b = self.pop()
                a = self.pop()
                result = 1 if a >= b else 0
                self.push(result)
            
            # Переходы
            elif opcode == Opcode.JMP:
                self.pc = operand
                return True
            
            elif opcode == Opcode.JZ:
                condition = self.pop()
                if condition == 0:
                    self.pc = operand
                    return True
            
            elif opcode == Opcode.JNZ:
                condition = self.pop()
                if condition != 0:
                    self.pc = operand
                    return True
            
            # Функции
            elif opcode == Opcode.CALL:
                self.call_stack.append(self.pc + 1)
                self.pc = operand
                return True
            
            elif opcode == Opcode.RET:
                if self.call_stack:
                    self.pc = self.call_stack.pop()
                    return True
                else:
                    # Если стек вызовов пуст, завершаем программу
                    self.state = ProcessorState.HALTED
                    return False
            
            # Операции с памятью
            elif opcode == Opcode.LOAD:
                address = self.pop()
                value = self.read_memory_word(address)
                self.push(value)
            elif opcode == Opcode.LOADB:
                address = self.pop()
                if address < 0 or address >= len(self.data_memory):
                    raise ProcessorError(f"Неверный адрес памяти: {address}")
                self.push(self.data_memory[address])
            
            elif opcode == Opcode.STORE:
                address = self.pop()
                value = self.pop()
                self.write_memory_word(address, value)
            elif opcode == Opcode.STOREB:
                address = self.pop()
                value = self.pop() & 0xFF
                if address < 0 or address >= len(self.data_memory):
                    raise ProcessorError(f"Неверный адрес памяти: {address}")
                self.data_memory[address] = value
            
            # Портовый I/O с прерываниями
            elif opcode == Opcode.IN:
                # Читаем из входного буфера
                if self.input_buffer:
                    value = self.input_buffer.pop(0)
                    self.push(value)
                else:
                    # Если нет данных, ждем прерывание или возвращаем 0
                    self.push(0)
            
            elif opcode == Opcode.OUT:
                value = self.pop()
                # Порт 1: вывод C-строки по адресу
                if operand == 1:
                    if 0 <= value < len(self.data_memory):
                        string_bytes: List[int] = []
                        addr = value
                        while addr < len(self.data_memory) and self.data_memory[addr] != 0:
                            string_bytes.append(self.data_memory[addr])
                            addr += 1
                        self.output_buffer.extend(string_bytes)
                    else:
                        # Если адрес вне памяти, выводим само значение как число
                        for ch in str(value):
                            self.output_buffer.append(ord(ch))
                # Порт 0: вывод числа в ASCII (Digit)
                elif operand == 0:
                    for ch in str(value):
                        self.output_buffer.append(ord(ch))
                # Порт 2: одиночный символ (char)
                elif operand == 2:
                    self.output_buffer.append(value & 0xFF)
                else:
                    # По умолчанию выводим сырое значение (как байт)
                    self.output_buffer.append(value)
            
            # Прерывания
            elif opcode == Opcode.INT:
                # Программное прерывание
                self.handle_software_interrupt(operand)
            
            elif opcode == Opcode.IRET:
                # Возврат из прерывания
                if self.call_stack:
                    self.pc = self.call_stack.pop()
                    self.in_interrupt = False
                    return True
                else:
                    raise ProcessorError("Стек вызовов пуст при IRET")
            
            # Векторные операции
            elif opcode == Opcode.V_ADD:
                # Ожидаем 3 регистра на стеке: reg1, reg2, result_reg
                if len(self.stack) >= 3:
                    result_reg = self.pop()
                    reg2 = self.pop()
                    reg1 = self.pop()
                    self.vector_unit.vector_add(reg1, reg2, result_reg)
                else:
                    raise ProcessorError("Недостаточно параметров для V_ADD")
            
            elif opcode == Opcode.V_SUB:
                if len(self.stack) >= 3:
                    result_reg = self.pop()
                    reg2 = self.pop()
                    reg1 = self.pop()
                    self.vector_unit.vector_sub(reg1, reg2, result_reg)
                else:
                    raise ProcessorError("Недостаточно параметров для V_SUB")
            
            elif opcode == Opcode.V_MUL:
                if len(self.stack) >= 3:
                    result_reg = self.pop()
                    reg2 = self.pop()
                    reg1 = self.pop()
                    self.vector_unit.vector_mul(reg1, reg2, result_reg)
                else:
                    raise ProcessorError("Недостаточно параметров для V_MUL")
            
            elif opcode == Opcode.V_DOT:
                if len(self.stack) >= 2:
                    reg2 = self.pop()
                    reg1 = self.pop()
                    result = self.vector_unit.vector_dot(reg1, reg2)
                    self.push(result)
                else:
                    raise ProcessorError("Недостаточно параметров для V_DOT")
            
            elif opcode == Opcode.V_NORM:
                if len(self.stack) >= 1:
                    reg = self.pop()
                    result = self.vector_unit.vector_norm(reg)
                    self.push(result)
                else:
                    raise ProcessorError("Недостаточно параметров для V_NORM")
            
            elif opcode == Opcode.V_MAX:
                if len(self.stack) >= 1:
                    reg = self.pop()
                    result = self.vector_unit.vector_max(reg)
                    self.push(result)
                else:
                    raise ProcessorError("Недостаточно параметров для V_MAX")
            
            elif opcode == Opcode.V_MIN:
                if len(self.stack) >= 1:
                    reg = self.pop()
                    result = self.vector_unit.vector_min(reg)
                    self.push(result)
                else:
                    raise ProcessorError("Недостаточно параметров для V_MIN")
            
            elif opcode == Opcode.V_SUM:
                if len(self.stack) >= 1:
                    reg = self.pop()
                    result = self.vector_unit.vector_sum(reg)
                    self.push(result)
                else:
                    raise ProcessorError("Недостаточно параметров для V_SUM")
            
            elif opcode == Opcode.V_AVG:
                if len(self.stack) >= 1:
                    reg = self.pop()
                    result = self.vector_unit.vector_avg(reg)
                    self.push(result)
                else:
                    raise ProcessorError("Недостаточно параметров для V_AVG")
            
            elif opcode == Opcode.V_SCALE:
                if len(self.stack) >= 3:
                    result_reg = self.pop()
                    scalar = self.pop()
                    reg = self.pop()
                    self.vector_unit.vector_scale(reg, scalar, result_reg)
                else:
                    raise ProcessorError("Недостаточно параметров для V_SCALE")
            
            elif opcode == Opcode.V_COPY:
                if len(self.stack) >= 2:
                    dst_reg = self.pop()
                    src_reg = self.pop()
                    self.vector_unit.vector_copy(src_reg, dst_reg)
                else:
                    raise ProcessorError("Недостаточно параметров для V_COPY")
            
            elif opcode == Opcode.V_SET:
                # index в operand, value и reg на стеке
                if len(self.stack) >= 2:
                    value = self.pop()
                    reg = self.pop()
                    self.vector_unit.vector_set(reg, operand, value)
                else:
                    raise ProcessorError("Недостаточно параметров для V_SET")
            
            elif opcode == Opcode.V_LOAD:
                # Загрузить вектор из памяти данных
                if len(self.stack) >= 3:
                    reg = self.pop()
                    length = self.pop()
                    address = self.pop()
                    
                    elements = []
                    # Память векторов хранится как [size][elem0][elem1]..., пропускаем заголовок size (4 байта)
                    base = address + 4
                    for i in range(min(length, self.vector_unit.max_vector_length)):
                        if base + i * 4 + 3 < len(self.data_memory):
                            word = self.read_memory_word(base + i * 4)
                            elements.append(word)
                        else:
                            break
                    
                    self.vector_unit.load_vector(reg, elements)
                else:
                    raise ProcessorError("Недостаточно параметров для V_LOAD")
            
            elif opcode == Opcode.V_STORE:
                # Сохранить вектор в память данных
                if len(self.stack) >= 2:
                    reg = self.pop()
                    address = self.pop()
                    
                    vec = self.vector_unit.get_vector(reg)
                    for i, value in enumerate(vec):
                        if address + i * 4 + 3 < len(self.data_memory):
                            self.write_memory_word(address + i * 4, value)
                        else:
                            break
                else:
                    raise ProcessorError("Недостаточно параметров для V_STORE")
            
            else:
                raise ProcessorError(f"Неизвестная инструкция: {opcode}")
        
        except ProcessorError as e:
            self.state = ProcessorState.HALTED
            return False
        
        # Увеличиваем PC
        self.pc += 1
        return True
    
    def handle_software_interrupt(self, vector: int) -> None:
        """Обработать программное прерывание."""
        # Управление прерываниями / системные вызовы
        if vector == 0x80:
            # set_interrupt_handler(irq, handler_addr)
            if len(self.stack) >= 2:
                handler_addr = self.pop()
                irq_vec = self.pop()
                self.interrupt_handlers[int(irq_vec)] = int(handler_addr)
            else:
                raise ProcessorError("Недостаточно параметров для установки обработчика")
        elif vector == 0x81:
            self.interrupts_enabled = True
        elif vector == 0x82:
            self.interrupts_enabled = False
        elif vector == 0:
            # Печать строки по адресу на стеке через порт 1
            if self.stack:
                _ = self.pop()
                self.execute_instruction(Instruction(Opcode.OUT, 1))
        elif vector == 1:
            # Возвратить 0 
            self.push(0)
    
    def step(self) -> bool:
        """Выполнить один такт. Возвращает True если нужно продолжать."""
        if self.state == ProcessorState.HALTED:
            return False

        # Обновляем контроллер ввода-вывода и принимаем события ввода
        for int_type, data in self.io_controller.update(self.cycle_count):
            if int_type == InterruptType.INPUT_READY:
                self.input_buffer.append(data)
                # Формируем запрос прерывания на вектор 0 (ввод готов)
                self.pending_interrupts.append((InterruptType.INPUT_READY.value, data))

        # Если программа закончилась и нет активной инструкции — останавливаемся
        if self.current_instruction is None and self.pc >= len(self.instruction_memory):
            self.state = ProcessorState.HALTED
            return False

        # Если нет активной инструкции — обработать прерывание и выбрать следующую
        if self.current_instruction is None:
            # Вход в прерывание между инструкциями
            if self.interrupts_enabled and (not self.in_interrupt) and self.pending_interrupts:
                vector, _ = self.pending_interrupts.pop(0)
                handler = self.interrupt_handlers.get(vector)
                if handler is not None:
                    self.call_stack.append(self.pc)
                    self.pc = handler
                    self.in_interrupt = True
                    self.execution_log.append(
                        f"Cycle {self.cycle_count:06d}: ENTER_IRQ vec={vector} -> PC={self.pc:04X}"
                    )

            self.current_instruction = self.instruction_memory[self.pc]
            self.remaining_cycles = INSTRUCTION_CYCLES.get(Opcode(self.current_instruction.opcode), 1)

        # Тик
        self.remaining_cycles -= 1
        self.cycle_count += 1

        # Если это последний такт — выполняем семантику инструкции
        if self.remaining_cycles == 0 and self.current_instruction is not None:
            instruction = self.current_instruction
            self.current_instruction = None
            self.remaining_cycles = 0
            continue_execution = self.execute_instruction(instruction)
            self.instruction_count += 1
            return continue_execution

        # Продолжаем выполнение (инструкция ещё не завершена)
        return True
    
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

    def schedule_input_event(self, cycle: int, data: int) -> None:
        """Запланировать поступление байта ввода на указанном такте."""
        self.io_controller.schedule_input(cycle, data)