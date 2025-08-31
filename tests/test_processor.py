"""Тесты для стекового процессора."""

import pytest
from comp.processor import StackProcessor, ProcessorError
from isa.machine_code import Instruction
from isa.opcodes import Opcode

# Constants to avoid magic numbers in assertions
PUSH_VALUE = 42
SUM_5_3 = 8
MUL_RESULT = 16
EXEC_COUNT_FIVE = 5
EXEC_COUNT_FOUR = 4
FINAL_PC_AFTER_HALT = 3


def test_basic_stack_operations() -> None:
    """Тест основных стековых операций."""
    processor = StackProcessor()
    
    # PUSH value
    processor.push(PUSH_VALUE)
    assert len(processor.stack) == 1
    assert processor.stack[0] == PUSH_VALUE
    
    # POP
    value = processor.pop()
    assert value == PUSH_VALUE
    assert len(processor.stack) == 0


def test_arithmetic_operations() -> None:
    """Тест арифметических операций."""
    processor = StackProcessor()
    
    # Тест сложения: 5 + 3 = 8
    instructions = [
        Instruction(Opcode.PUSH, 5),
        Instruction(Opcode.PUSH, 3),
        Instruction(Opcode.ADD),
        Instruction(Opcode.HALT),
    ]
    
    processor.load_program(instructions)
    result = processor.run()
    
    assert result['state'] == 'halted'
    assert len(processor.stack) == 1
    assert processor.stack[0] == SUM_5_3


def test_memory_operations() -> None:
    """Тест операций с памятью."""
    processor = StackProcessor()
    
    # Записываем значение 42 по адресу 0
    instructions = [
        Instruction(Opcode.PUSH, PUSH_VALUE),  # value
        Instruction(Opcode.PUSH, 0),   # address
        Instruction(Opcode.STORE),     # store
        Instruction(Opcode.PUSH, 0),   # address
        Instruction(Opcode.LOAD),      # load
        Instruction(Opcode.HALT),
    ]
    
    processor.load_program(instructions)
    result = processor.run()
    
    assert result['state'] == 'halted'
    assert len(processor.stack) == 1
    assert processor.stack[0] == PUSH_VALUE


def test_stack_underflow() -> None:
    """Тест переполнения стека снизу."""
    processor = StackProcessor()
    
    with pytest.raises(ProcessorError):
        processor.pop()


def test_output() -> None:
    """Тест вывода."""
    processor = StackProcessor()
    
    instructions = [
        Instruction(Opcode.PUSH, 65),  # ASCII 'A'
        Instruction(Opcode.OUT, 1),    # output to port 1
        Instruction(Opcode.HALT),
    ]
    
    processor.load_program(instructions)
    result = processor.run()
    
    assert result['state'] == 'halted'
    assert result['output'] == [65]


def test_complex_calculation() -> None:
    """Тест сложного вычисления: (5 + 3) * 2 = 16."""
    processor = StackProcessor()
    
    instructions = [
        Instruction(Opcode.PUSH, 5),
        Instruction(Opcode.PUSH, 3),
        Instruction(Opcode.ADD),       # 8 on stack
        Instruction(Opcode.PUSH, 2),
        Instruction(Opcode.MUL),       # 16 on stack
        Instruction(Opcode.HALT),
    ]
    
    processor.load_program(instructions)
    result = processor.run()
    
    assert result['state'] == 'halted'
    assert len(processor.stack) == 1
    assert processor.stack[0] == MUL_RESULT
    assert result['instructions_executed'] == EXEC_COUNT_FIVE


def test_execution_stats() -> None:
    """Тест статистики выполнения."""
    processor = StackProcessor()
    
    instructions = [
        Instruction(Opcode.PUSH, 1),
        Instruction(Opcode.PUSH, 2),
        Instruction(Opcode.ADD),
        Instruction(Opcode.HALT),
    ]
    
    processor.load_program(instructions)
    result = processor.run()
    
    assert result['instructions_executed'] == EXEC_COUNT_FOUR
    assert result['cycles_executed'] >= EXEC_COUNT_FOUR  # Минимум по одному такту на инструкцию
    assert result['final_pc'] == FINAL_PC_AFTER_HALT  # PC после HALT