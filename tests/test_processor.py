"""Тесты для стекового процессора."""

import pytest
from comp.processor import StackProcessor, ProcessorError
from isa.machine_code import Instruction
from isa.opcodes import Opcode


def test_basic_stack_operations() -> None:
    """Тест основных стековых операций."""
    processor = StackProcessor()
    
    # PUSH 42
    processor.push(42)
    assert len(processor.stack) == 1
    assert processor.stack[0] == 42
    
    # POP
    value = processor.pop()
    assert value == 42
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
    assert processor.stack[0] == 8


def test_memory_operations() -> None:
    """Тест операций с памятью."""
    processor = StackProcessor()
    
    # Записываем значение 42 по адресу 0
    instructions = [
        Instruction(Opcode.PUSH, 42),  # value
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
    assert processor.stack[0] == 42


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
    assert processor.stack[0] == 16
    assert result['instructions_executed'] == 5


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
    
    assert result['instructions_executed'] == 4
    assert result['cycles_executed'] >= 4  # Минимум по одному такту на инструкцию
    assert result['final_pc'] == 3  # PC после HALT 