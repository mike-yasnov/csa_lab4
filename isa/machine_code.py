"""Работа с машинным кодом в бинарном формате."""

import struct
from typing import BinaryIO, List, Tuple

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
        """Сохранить память команд в бинарный файл."""
        with open(file_path, 'wb') as f:
            for instr in self.instructions:
                f.write(instr.to_bytes())
    
    def save_data_memory(self, file_path: str) -> None:
        """Сохранить память данных в бинарный файл."""
        with open(file_path, 'wb') as f:
            f.write(self.data_memory)
    
    def save_debug_listing(self, file_path: str) -> None:
        """Сохранить отладочную информацию в текстовый файл."""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("INSTRUCTION MEMORY:\n")
            f.write("Address - Hex Code - Mnemonic\n")
            f.write("-" * 40 + "\n")
            
            addr = 0
            for i, instr in enumerate(self.instructions):
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
            
            # Вывод данных по 16 байт в строке
            for i in range(0, len(self.data_memory), 16):
                chunk = self.data_memory[i:i+16]
                hex_dump = ' '.join(f"{b:02X}" for b in chunk)
                ascii_dump = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
                f.write(f"{i:04X} - {hex_dump:<48} - {ascii_dump}\n")
    
    @classmethod
    def load_instruction_memory(cls, file_path: str) -> List[Instruction]:
        """Загрузить память команд из бинарного файла."""
        instructions = []
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(4)  # 4 байта на инструкцию
                if len(data) < 4:
                    break
                instructions.append(Instruction.from_bytes(data))
        return instructions
    
    @classmethod
    def load_data_memory(cls, file_path: str) -> bytearray:
        """Загрузить память данных из бинарного файла."""
        with open(file_path, 'rb') as f:
            return bytearray(f.read())


def format_instruction_trace(pc: int, instruction: Instruction) -> str:
    """Форматировать инструкцию для вывода в трассировке."""
    if instruction.operand != 0:
        return f"PC={pc:04X}: {get_opcode_name(instruction.opcode)} {instruction.operand}"
    return f"PC={pc:04X}: {get_opcode_name(instruction.opcode)}" 