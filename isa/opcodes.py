"""Определение опкодов для стековой архитектуры."""

from enum import IntEnum


class Opcode(IntEnum):
    """Опкоды инструкций для стековой архитектуры с векторными расширениями."""
    
    # Основные стековые операции
    PUSH = 0x00     # Положить значение на стек
    POP = 0x01      # Снять значение со стека
    DUP = 0x02      # Дублировать верхний элемент стека
    SWAP = 0x03     # Поменять местами два верхних элемента
    DROP = 0x04     # Удалить верхний элемент стека
    
    # Арифметические операции
    ADD = 0x10      # Сложение двух верхних элементов
    SUB = 0x11      # Вычитание
    MUL = 0x12      # Умножение
    DIV = 0x13      # Деление
    MOD = 0x14      # Остаток от деления
    NEG = 0x15      # Отрицание
    
    # Логические операции
    AND = 0x20      # Логическое И
    OR = 0x21       # Логическое ИЛИ
    XOR = 0x22      # Исключающее ИЛИ
    NOT = 0x23      # Логическое отрицание
    
    # Операции сравнения
    EQ = 0x30       # Равенство
    NE = 0x31       # Неравенство
    LT = 0x32       # Меньше
    LE = 0x33       # Меньше или равно
    GT = 0x34       # Больше
    GE = 0x35       # Больше или равно
    
    # Операции перехода
    JMP = 0x40      # Безусловный переход
    JZ = 0x41       # Переход если ноль
    JNZ = 0x42      # Переход если не ноль
    CALL = 0x43     # Вызов функции
    RET = 0x44      # Возврат из функции
    
    # Операции с памятью
    LOAD = 0x50     # Загрузить из памяти данных по адресу TOS
    STORE = 0x51    # Сохранить в память данных
    LOAD_I = 0x52   # Загрузить из памяти команд
    
    # Портовый ввод-вывод
    IN = 0x60       # Ввод из порта
    OUT = 0x61      # Вывод в порт
    
    # Системные операции
    HALT = 0x70     # Остановка процессора
    NOP = 0x71      # Нет операции
    INT = 0x72      # Программное прерывание
    IRET = 0x73     # Возврат из прерывания
    
    # Векторные операции (vector extension)
    V_LOAD = 0x80   # Загрузить вектор
    V_STORE = 0x81  # Сохранить вектор
    V_ADD = 0x82    # Векторное сложение
    V_SUB = 0x83    # Векторное вычитание
    V_MUL = 0x84    # Векторное умножение
    V_DIV = 0x85    # Векторное деление
    V_CMP = 0x86    # Векторное сравнение
    V_DOT = 0x87    # Скалярное произведение векторов


# Размеры инструкций в словах
INSTRUCTION_SIZES = {
    # Инструкции без операндов
    Opcode.POP: 1,
    Opcode.DUP: 1,
    Opcode.SWAP: 1,
    Opcode.DROP: 1,
    Opcode.ADD: 1,
    Opcode.SUB: 1,
    Opcode.MUL: 1,
    Opcode.DIV: 1,
    Opcode.MOD: 1,
    Opcode.NEG: 1,
    Opcode.AND: 1,
    Opcode.OR: 1,
    Opcode.XOR: 1,
    Opcode.NOT: 1,
    Opcode.EQ: 1,
    Opcode.NE: 1,
    Opcode.LT: 1,
    Opcode.LE: 1,
    Opcode.GT: 1,
    Opcode.GE: 1,
    Opcode.LOAD: 1,
    Opcode.STORE: 1,
    Opcode.LOAD_I: 1,
    Opcode.RET: 1,
    Opcode.HALT: 1,
    Opcode.NOP: 1,
    Opcode.IRET: 1,
    
    # Инструкции с одним операндом
    Opcode.PUSH: 2,
    Opcode.JMP: 2,
    Opcode.JZ: 2,
    Opcode.JNZ: 2,
    Opcode.CALL: 2,
    Opcode.IN: 2,
    Opcode.OUT: 2,
    Opcode.INT: 2,
    
    # Векторные инструкции с операндами
    Opcode.V_LOAD: 2,
    Opcode.V_STORE: 2,
    Opcode.V_ADD: 1,
    Opcode.V_SUB: 1,
    Opcode.V_MUL: 1,
    Opcode.V_DIV: 1,
    Opcode.V_CMP: 1,
    Opcode.V_DOT: 1,
}


# Количество тактов для выполнения инструкций
INSTRUCTION_CYCLES = {
    Opcode.NOP: 1,
    Opcode.PUSH: 2,
    Opcode.POP: 1,
    Opcode.DUP: 2,
    Opcode.SWAP: 2,
    Opcode.DROP: 1,
    Opcode.ADD: 3,
    Opcode.SUB: 3,
    Opcode.MUL: 4,
    Opcode.DIV: 6,
    Opcode.MOD: 6,
    Opcode.NEG: 2,
    Opcode.AND: 2,
    Opcode.OR: 2,
    Opcode.XOR: 2,
    Opcode.NOT: 2,
    Opcode.EQ: 3,
    Opcode.NE: 3,
    Opcode.LT: 3,
    Opcode.LE: 3,
    Opcode.GT: 3,
    Opcode.GE: 3,
    Opcode.JMP: 2,
    Opcode.JZ: 3,
    Opcode.JNZ: 3,
    Opcode.CALL: 4,
    Opcode.RET: 3,
    Opcode.LOAD: 4,
    Opcode.STORE: 4,
    Opcode.LOAD_I: 4,
    Opcode.IN: 5,
    Opcode.OUT: 5,
    Opcode.HALT: 1,
    Opcode.INT: 8,
    Opcode.IRET: 6,
    # Векторные операции (более медленные)
    Opcode.V_LOAD: 8,
    Opcode.V_STORE: 8,
    Opcode.V_ADD: 4,
    Opcode.V_SUB: 4,
    Opcode.V_MUL: 6,
    Opcode.V_DIV: 12,
    Opcode.V_CMP: 4,
    Opcode.V_DOT: 8,
}


def get_opcode_name(opcode: int) -> str:
    """Получить имя опкода по его значению."""
    try:
        return Opcode(opcode).name
    except ValueError:
        return f"UNKNOWN_{opcode:02X}"


def is_vector_operation(opcode: int) -> bool:
    """Проверить, является ли операция векторной."""
    return opcode >= 0x80 