"""Work with machine code in binary format."""

import struct
from pathlib import Path
from typing import List

from .opcodes import Opcode, get_opcode_name, INSTRUCTION_SIZES


class Instruction:
    """Представление инструкции машинного кода."""
    
    def __init__(self, opcode: int, operand: int = 0) -> None:
        self.opcode = opcode
        self.operand = operand
    
    def __repr__(self) -> str:
        if self.operand != 0:
            return f"Instruction({get_opcode_name(self.opcode)}, {self.operand})"
        return f"Instruction({get_opcode_name(self.opcode)})"
    
    def to_bytes(self) -> bytes:
        """Конвертировать инструкцию в байты (little-endian, 32-bit)."""
        # Опкод в младших 8 битах, операнд в старших 24 битах
        word = (self.operand << 8) | self.opcode
        return struct.pack('<I', word)
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'Instruction':
        """Создать инструкцию из байтов."""
        word = struct.unpack('<I', data)[0]
        opcode = word & 0xFF
        operand = (word >> 8) & 0xFFFFFF
        return cls(opcode, operand)
    
    def size_in_words(self) -> int:
        """Размер инструкции в словах."""
        return INSTRUCTION_SIZES.get(Opcode(self.opcode), 1)


class MachineCode:
    """Класс для работы с машинным кодом."""
    
    def __init__(self) -> None:
        self.instructions: List[Instruction] = []
        self.data_memory: bytearray = bytearray()
    
    def add_instruction(self, opcode: int, operand: int = 0) -> None:
        """Добавить инструкцию."""
        self.instructions.append(Instruction(opcode, operand))
    
    def add_data(self, data: bytes) -> int:
        """Добавить данные в память данных. Возвращает адрес."""
        addr = len(self.data_memory)
        self.data_memory.extend(data)
        return addr
    
    def add_word(self, value: int) -> int:
        """Добавить 32-битное слово в память данных."""
        return self.add_data(struct.pack('<I', value))
    
    def add_cstring(self, text: str) -> int:
        """Добавить C-строку (null-terminated) в память данных."""
        return self.add_data(text.encode('utf-8') + b'\0')
    
    def save_instruction_memory(self, file_path: str) -> None:
        """Save instruction memory to a binary file."""
        path = Path(file_path)
        with path.open('wb') as f:
            for instr in self.instructions:
                f.write(instr.to_bytes())
    
    def save_data_memory(self, file_path: str) -> None:
        """Save data memory to a binary file."""
        path = Path(file_path)
        with path.open('wb') as f:
            f.write(self.data_memory)
    
    def save_debug_listing(self, file_path: str) -> None:
        """Save debug listing to a text file."""
        path = Path(file_path)
        with path.open('w', encoding='utf-8') as f:
            f.write("INSTRUCTION MEMORY:\n")
            f.write("Address - Hex Code - Mnemonic\n")
            f.write("-" * 40 + "\n")
            
            addr = 0
            for _i, instr in enumerate(self.instructions):
                hex_code = instr.to_bytes().hex().upper()
                if instr.operand != 0:
                    mnemonic = f"{get_opcode_name(instr.opcode)} {instr.operand}"
                else:
                    mnemonic = get_opcode_name(instr.opcode)
                
                f.write(f"{addr:04X} - {hex_code} - {mnemonic}\n")
                addr += instr.size_in_words()
            
            f.write("\nDATA MEMORY:\n")
            f.write("Address - Hex Dump - ASCII\n")
            f.write("-" * 40 + "\n")
            
            # Dump data in 16-byte rows
            for i in range(0, len(self.data_memory), 16):
                chunk = self.data_memory[i:i+16]
                hex_dump = ' '.join(f"{b:02X}" for b in chunk)
                ascii_min = 32
                ascii_max = 126
                ascii_dump = ''.join(chr(b) if ascii_min <= b <= ascii_max else '.' for b in chunk)
                f.write(f"{i:04X} - {hex_dump:<48} - {ascii_dump}\n")
    
    @classmethod
    def load_instruction_memory(cls, file_path: str) -> List[Instruction]:
        """Load instruction memory from a binary file."""
        word_size = 4
        instructions: List[Instruction] = []
        path = Path(file_path)
        with path.open('rb') as f:
            while True:
                data = f.read(word_size)
                if len(data) < word_size:
                    break
                instructions.append(Instruction.from_bytes(data))
        return instructions
    
    @classmethod
    def load_data_memory(cls, file_path: str) -> bytearray:
        """Load data memory from a binary file."""
        path = Path(file_path)
        with path.open('rb') as f:
            return bytearray(f.read())


def format_instruction_trace(pc: int, instruction: Instruction) -> str:
    """Format instruction for execution trace output."""
    if instruction.operand != 0:
        return f"PC={pc:04X}: {get_opcode_name(instruction.opcode)} {instruction.operand}"
    return f"PC={pc:04X}: {get_opcode_name(instruction.opcode)}"