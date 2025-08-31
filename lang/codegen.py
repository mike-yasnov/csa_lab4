"""Генератор кода для стековой архитектуры с векторными расширениями."""

from typing import Dict, List, Any
import struct

from .ast_nodes import (
    ASTVisitor,
    Program,
    FunctionDeclaration,
    VarDeclaration,
    IfStatement,
    WhileStatement,
    ForStatement,
    ReturnStatement,
    Block,
    Identifier,
    Assignment,
    ExpressionStatement,
    Expression,
    BinaryOperation,
    UnaryOperation,
    ArrayAccess,
    FunctionCall,
    BooleanLiteral,
    NullLiteral,
    NumberLiteral,
    StringLiteral,
    VectorLiteral,
)
from isa.opcodes import Opcode
from isa.machine_code import MachineCode

# Argument count constants (to avoid magic numbers in checks)
ARGS_2 = 2
ARGS_3 = 3


class CodeGenError(Exception):
    """Ошибка генерации кода."""
    pass


class SymbolTable:
    """Таблица символов для переменных и функций."""
    
    def __init__(self) -> None:
        self.scopes: List[Dict[str, Any]] = [{}]  # Стек областей видимости
        self.functions: Dict[str, int] = {}  # Функции -> адрес
        self.strings: Dict[str, int] = {}   # Строки -> адрес в памяти данных
        self.next_temp_id = 0
    
    def enter_scope(self) -> None:
        """Войти в новую область видимости."""
        self.scopes.append({})
    
    def exit_scope(self) -> None:
        """Выйти из области видимости."""
        if len(self.scopes) > 1:
            self.scopes.pop()
    
    def define(self, name: str, value: Any) -> None:
        """Определить переменную в текущей области видимости."""
        self.scopes[-1][name] = value
    
    def get(self, name: str) -> Any:
        """Получить переменную."""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise CodeGenError(f"Неопределенная переменная: {name}")
    
    def exists(self, name: str) -> bool:
        """Проверить, существует ли переменная."""
        return any(name in scope for scope in reversed(self.scopes))
    
    def get_temp_var(self) -> str:
        """Получить имя временной переменной."""
        name = f"__temp_{self.next_temp_id}"
        self.next_temp_id += 1
        return name


class CodeGenerator(ASTVisitor):
    """Генератор кода для стековой архитектуры."""
    
    def __init__(self) -> None:
        self.machine_code = MachineCode()
        self.symbols = SymbolTable()
        self.current_address = 0
        self.loop_stack: List[Dict[str, int]] = []  # Для break/continue
        self.call_stack_depth = 0
        
        # Предопределенные адреса портов
        self.INPUT_PORT = 0
        self.OUTPUT_PORT = 1
        
        # Встроенные функции
        self.builtin_functions = {
            'print': self._generate_print,
            'print_number': self._generate_print_number,
            'readLine': self._generate_read_line,
            'alloc': self._generate_alloc,
            'readLineBuf': self._generate_read_line_buf,
            'read': self._generate_read,
            'readInt': self._generate_read_int,
            'len': self._generate_len,
            'chr': self._generate_chr,
            'putc': self._generate_putc,
            'v_load': self._generate_v_load,
            'v_add': self._generate_v_add,
            'v_dot': self._generate_v_dot,
            'v_store': self._generate_v_store,
            'v_sum': self._generate_v_sum,
            'set_interrupt_handler': self._generate_set_interrupt_handler,
            'enable_interrupts': self._generate_enable_interrupts,
            'disable_interrupts': self._generate_disable_interrupts,
        }
    
    def generate(self, program: Program) -> MachineCode:
        """Главная функция генерации кода."""
        # Генерируем код программы
        program.accept(self)
        
        # Добавляем halt в конец программы
        self._emit(Opcode.HALT)
        
        return self.machine_code
    

    
    def _emit(self, opcode: int, operand: int = 0) -> int:
        """Генерировать инструкцию и вернуть её адрес."""
        address = len(self.machine_code.instructions)
        self.machine_code.add_instruction(opcode, operand)
        return address
    
    def _patch_address(self, instruction_addr: int, target_addr: int) -> None:
        """Исправить адрес в инструкции."""
        self.machine_code.instructions[instruction_addr].operand = target_addr
    
    def _get_string_address(self, text: str) -> int:
        """Получить адрес строки в памяти данных."""
        if text not in self.symbols.strings:
            self.symbols.strings[text] = self.machine_code.add_cstring(text)
        return self.symbols.strings[text]
    
    # Методы посетителя
    def visit_program(self, node: Program) -> Any:
        """Посетить программу."""
        for statement in node.statements:
            statement.accept(self)
    
    def visit_number_literal(self, node: NumberLiteral) -> Any:
        """Посетить числовой литерал."""
        if isinstance(node.value, float):
            # Для float сохраняем в памяти данных
            addr = self.machine_code.add_data(struct.pack('<f', node.value))
            self._emit(Opcode.PUSH, addr)
            self._emit(Opcode.LOAD)
        else:
            # Целые числа помещаем напрямую
            self._emit(Opcode.PUSH, int(node.value))
    
    def visit_string_literal(self, node: StringLiteral) -> Any:
        """Посетить строковый литерал."""
        addr = self._get_string_address(node.value)
        self._emit(Opcode.PUSH, addr)
    
    def visit_boolean_literal(self, node: BooleanLiteral) -> Any:
        """Посетить булев литерал."""
        self._emit(Opcode.PUSH, 1 if node.value else 0)
    
    def visit_null_literal(self, _node: NullLiteral) -> Any:
        """Посетить null литерал."""
        self._emit(Opcode.PUSH, 0)
    
    def visit_identifier(self, node: Identifier) -> Any:
        """Посетить идентификатор."""
        # Сначала проверяем, не является ли это именем функции (для передачи адреса функции)
        if node.name in self.symbols.functions:
            self._emit(Opcode.PUSH, self.symbols.functions[node.name])
            return

        if not self.symbols.exists(node.name):
            raise CodeGenError(f"Неопределенная переменная: {node.name}")
        
        var_info = self.symbols.get(node.name)
        if isinstance(var_info, dict) and 'address' in var_info:
            # Переменная в памяти
            self._emit(Opcode.PUSH, var_info['address'])
            self._emit(Opcode.LOAD)
        else:
            # Константа
            self._emit(Opcode.PUSH, var_info)
    
    def visit_binary_operation(self, node: BinaryOperation) -> Any:
        """Посетить бинарную операцию."""
        # Генерируем код для операндов (стековая машина)
        node.left.accept(self)
        node.right.accept(self)
        
        # Генерируем операцию
        op_map = {
            '+': Opcode.ADD,
            '-': Opcode.SUB,
            '*': Opcode.MUL,
            '/': Opcode.DIV,
            '%': Opcode.MOD,
            '==': Opcode.EQ,
            '!=': Opcode.NE,
            '<': Opcode.LT,
            '<=': Opcode.LE,
            '>': Opcode.GT,
            '>=': Opcode.GE,
            '&&': Opcode.AND,
            '||': Opcode.OR,
            'and': Opcode.AND,
            'or': Opcode.OR,
        }
        
        if node.operator in op_map:
            self._emit(op_map[node.operator])
        else:
            raise CodeGenError(f"Неизвестная бинарная операция: {node.operator}")
    
    def visit_unary_operation(self, node: UnaryOperation) -> Any:
        """Посетить унарную операцию."""
        node.operand.accept(self)
        
        if node.operator == '-':
            self._emit(Opcode.NEG)
        elif node.operator in {'!', 'not'}:
            self._emit(Opcode.NOT)
        else:
            raise CodeGenError(f"Неизвестная унарная операция: {node.operator}")
    
    def visit_function_call(self, node: FunctionCall) -> Any:
        """Посетить вызов функции."""
        if node.name in self.builtin_functions:
            # Встроенная функция
            self.builtin_functions[node.name](node.arguments)
        elif node.name in self.symbols.functions:
            # Пользовательская функция
            # Помещаем аргументы на стек
            for arg in node.arguments:
                arg.accept(self)
            
            # Вызываем функцию
            self._emit(Opcode.CALL, self.symbols.functions[node.name])
        else:
            raise CodeGenError(f"Неопределенная функция: {node.name}")
    
    def visit_vector_literal(self, node: VectorLiteral) -> Any:
        """Посетить векторный литерал."""
        # Векторы сохраняем в памяти данных
        vector_data = bytearray()
        
        # Сначала записываем размер вектора
        vector_data.extend(struct.pack('<I', len(node.elements)))
        
        # Затем элементы (предполагаем 32-битные числа)
        for element in node.elements:
            if isinstance(element, NumberLiteral):
                if isinstance(element.value, float):
                    vector_data.extend(struct.pack('<f', element.value))
                else:
                    vector_data.extend(struct.pack('<I', int(element.value)))
            else:
                raise CodeGenError("Векторы могут содержать только числовые литералы")
        
        addr = self.machine_code.add_data(vector_data)
        self._emit(Opcode.PUSH, addr)
    
    def visit_array_access(self, node: ArrayAccess) -> Any:
        """Посетить доступ к элементу массива."""
        # Загружаем базовый адрес массива
        node.array.accept(self)
        # Загружаем индекс
        node.index.accept(self)
        
        # Вычисляем адрес элемента для вектора в формате [size][elem0][elem1]...
        # addr + 4 (пропустить size) + index * 4
        self._emit(Opcode.PUSH, 4)   # ... * 4
        self._emit(Opcode.MUL)       # index * 4
        self._emit(Opcode.PUSH, 4)   # + 4 (смещение после size)
        self._emit(Opcode.ADD)       # offset + 4
        self._emit(Opcode.ADD)       # addr + (offset+4)
        self._emit(Opcode.LOAD)     # Загрузить значение
    
    def visit_expression_statement(self, node: ExpressionStatement) -> Any:
        """Посетить выражение как оператор."""
        # Для вызовов функций не выбрасываем результат принудительно,
        # так как builtin-ы сами управляют стеком
        if isinstance(node.expression, FunctionCall):
            node.expression.accept(self)
            return
        node.expression.accept(self)
        self._emit(Opcode.POP)
    
    def visit_var_declaration(self, node: VarDeclaration) -> Any:
        """Посетить объявление переменной."""
        if node.initializer:
            node.initializer.accept(self)
        else:
            self._emit(Opcode.PUSH, 0)  # Значение по умолчанию
        
        # Выделяем место в памяти данных
        addr = self.machine_code.add_word(0)
        
        # Сохраняем значение в памяти
        self._emit(Opcode.PUSH, addr)
        self._emit(Opcode.STORE)
        
        # Записываем в таблицу символов
        self.symbols.define(node.name, {'address': addr, 'const': node.is_const})
    
    def visit_assignment(self, node: Assignment) -> Any:
        """Посетить присваивание."""
        if not self.symbols.exists(node.target.name):
            raise CodeGenError(f"Неопределенная переменная: {node.target.name}")
        
        var_info = self.symbols.get(node.target.name)
        if isinstance(var_info, dict) and var_info.get('const', False):
            raise CodeGenError(f"Нельзя изменять константу: {node.target.name}")
        
        # Для стековой архитектуры: значение, затем адрес
        node.value.accept(self)
        
        if node.operator == '=':
            pass  # Значение уже на стеке
        elif node.operator == '+=':
            # Загружаем текущее значение
            node.target.accept(self)
            self._emit(Opcode.ADD)
        elif node.operator == '-=':
            # Загружаем текущее значение
            node.target.accept(self)
            self._emit(Opcode.SUB)
        else:
            raise CodeGenError(f"Неизвестный оператор присваивания: {node.operator}")
        
        # Сохраняем в память
        addr = var_info['address']
        self._emit(Opcode.PUSH, addr)
        self._emit(Opcode.STORE)
    
    def visit_block(self, node: Block) -> Any:
        """Посетить блок."""
        self.symbols.enter_scope()
        try:
            for statement in node.statements:
                statement.accept(self)
        finally:
            self.symbols.exit_scope()
    
    def visit_if_statement(self, node: IfStatement) -> Any:
        """Посетить условный оператор."""
        # Вычисляем условие
        node.condition.accept(self)
        
        # Переход если false
        jump_to_else = self._emit(Opcode.JZ, 0)  # Заполним позже
        
        # Then ветка
        node.then_stmt.accept(self)
        
        if node.else_stmt:
            # Переход через else ветку
            jump_to_end = self._emit(Opcode.JMP, 0)
            
            # Else ветка
            else_addr = len(self.machine_code.instructions)
            self._patch_address(jump_to_else, else_addr)
            
            node.else_stmt.accept(self)
            
            # Конец if
            end_addr = len(self.machine_code.instructions)
            self._patch_address(jump_to_end, end_addr)
        else:
            # Конец if
            end_addr = len(self.machine_code.instructions)
            self._patch_address(jump_to_else, end_addr)
    
    def visit_while_statement(self, node: WhileStatement) -> Any:
        """Посетить цикл while."""
        loop_start = len(self.machine_code.instructions)
        
        # Вычисляем условие
        node.condition.accept(self)
        
        # Выход из цикла если false
        jump_to_end = self._emit(Opcode.JZ, 0)
        
        # Тело цикла
        self.loop_stack.append({'continue': loop_start, 'break': jump_to_end})
        node.body.accept(self)
        self.loop_stack.pop()
        
        # Переход к началу цикла
        self._emit(Opcode.JMP, loop_start)
        
        # Конец цикла
        end_addr = len(self.machine_code.instructions)
        self._patch_address(jump_to_end, end_addr)
    
    def visit_for_statement(self, node: ForStatement) -> Any:
        """Посетить цикл for."""
        self.symbols.enter_scope()
        try:
            # Инициализация
            if node.init:
                node.init.accept(self)
            
            loop_start = len(self.machine_code.instructions)
            
            # Условие
            if node.condition:
                node.condition.accept(self)
                jump_to_end = self._emit(Opcode.JZ, 0)
            else:
                jump_to_end = None
            
            # Тело цикла
            continue_addr = len(self.machine_code.instructions)
            if jump_to_end:
                self.loop_stack.append({'continue': continue_addr, 'break': jump_to_end})
            node.body.accept(self)
            if jump_to_end:
                self.loop_stack.pop()
            
            # Обновление
            if node.update:
                node.update.accept(self)
                self._emit(Opcode.POP)  # Убираем результат
            
            # Переход к началу
            self._emit(Opcode.JMP, loop_start)
            
            # Конец цикла
            if jump_to_end:
                end_addr = len(self.machine_code.instructions)
                self._patch_address(jump_to_end, end_addr)
                
        finally:
            self.symbols.exit_scope()
    
    def visit_function_declaration(self, node: FunctionDeclaration) -> Any:
        """Посетить объявление функции."""
        # Вставляем прыжок, чтобы на верхнем уровне пропустить тело функции
        skip_jmp_addr = self._emit(Opcode.JMP, 0)

        # Адрес функции начинается здесь
        func_addr = len(self.machine_code.instructions)
        self.symbols.functions[node.name] = func_addr

        # Входим в область видимости функции
        self.symbols.enter_scope()
        
        # Параметры уже на стеке (переданы при вызове)
        # Определяем их в локальной области видимости
        for _i, param in enumerate(reversed(node.parameters)):
            # Выделяем место в памяти для параметра
            addr = self.machine_code.add_word(0)
            self._emit(Opcode.PUSH, addr)
            self._emit(Opcode.STORE)
            self.symbols.define(param, {'address': addr, 'const': False})
        
        # Тело функции
        node.body.accept(self)
        
        # Возврат (если нет явного return)
        self._emit(Opcode.RET)
        
        self.symbols.exit_scope()
        
        # Пропатчить прыжок через тело функции
        end_addr = len(self.machine_code.instructions)
        self._patch_address(skip_jmp_addr, end_addr)
    
    def visit_return_statement(self, node: ReturnStatement) -> Any:
        """Посетить оператор возврата."""
        if node.value:
            node.value.accept(self)
        else:
            self._emit(Opcode.PUSH, 0)  # Возвращаем 0 по умолчанию
        
        self._emit(Opcode.RET)
    
    # Встроенные функции
    def _generate_print(self, arguments: List[Expression]) -> None:
        """Генерировать код для print."""
        if len(arguments) != 1:
            raise CodeGenError("print принимает ровно один аргумент")
        
        arguments[0].accept(self)
        
        # Assume the argument is a C-string address and print via port
        self._emit(Opcode.OUT, self.OUTPUT_PORT)
    
    def _generate_read(self, arguments: List[Expression]) -> None:
        """Генерировать код для read."""
        if len(arguments) != 0:
            raise CodeGenError("read не принимает аргументов")
        
        self._emit(Opcode.IN, self.INPUT_PORT)

    def _generate_print_number(self, arguments: List[Expression]) -> None:
        """Генерировать код для print_number."""
        if len(arguments) != 1:
            raise CodeGenError("print_number принимает ровно один аргумент")
        arguments[0].accept(self)
        # Output number via port 0 (Digit), per example_harv convention
        self._emit(Opcode.OUT, 0)
    
    def _generate_read_int(self, arguments: List[Expression]) -> None:
        """Генерировать код для readInt."""
        if len(arguments) != 0:
            raise CodeGenError("readInt не принимает аргументов")
        
        self._emit(Opcode.IN, self.INPUT_PORT)
        # Assume input is already numeric
    
    def _generate_alloc(self, arguments: List[Expression]) -> None:
        """Выделить блок size байт в памяти данных и вернуть адрес."""
        if len(arguments) != 1:
            raise CodeGenError("alloc(size)")
        # Получаем size как константу на этапе генерации
        arg = arguments[0]
        if not isinstance(arg, NumberLiteral) or isinstance(arg.value, float):
            raise CodeGenError("alloc требует целочисленный литерал размера")
        size = int(arg.value)
        addr = self.machine_code.add_data(b"_" * size)
        self._emit(Opcode.PUSH, addr)

    def _generate_read_line(self, arguments: List[Expression]) -> None:
        r"""Читать до \n/0 и выводить посимвольно (прежняя простая версия)."""
        if len(arguments) != 0:
            raise CodeGenError("readLine не принимает аргументов")
        loop_start = len(self.machine_code.instructions)
        self._emit(Opcode.IN, self.INPUT_PORT)
        self._emit(Opcode.DUP)
        self._emit(Opcode.PUSH, 0)
        self._emit(Opcode.EQ)
        j0 = self._emit(Opcode.JNZ, 0)
        self._emit(Opcode.DUP)
        self._emit(Opcode.PUSH, 10)
        self._emit(Opcode.EQ)
        j1 = self._emit(Opcode.JNZ, 0)
        self._emit(Opcode.OUT, self.OUTPUT_PORT)
        self._emit(Opcode.JMP, loop_start)
        end = len(self.machine_code.instructions)
        self._patch_address(j0, end)
        self._patch_address(j1, end)
        self._emit(Opcode.POP)
        self._emit(Opcode.PUSH, 0)

    def _generate_read_line_buf(self, arguments: List[Expression]) -> None:
        """readLineBuf(bufAddr, maxLen): читать в буфер C-строку, завершить 0, не переполняя."""
        if len(arguments) != ARGS_2:
            raise CodeGenError("readLineBuf(bufAddr, maxLen)")
        # Выделяем скрытую переменную p (указатель на текущую позицию)
        p_addr = self.machine_code.add_word(0)
        # Initialize p = bufAddr
        arguments[0].accept(self)             # buf
        self._emit(Opcode.PUSH, p_addr)       # buf, p_addr
        self._emit(Opcode.STORE)              # MEM[p_addr] = buf
        # loop:
        loop_start = len(self.machine_code.instructions)
        # If (p - buf) >= maxLen-1 -> end
        self._emit(Opcode.PUSH, p_addr)
        self._emit(Opcode.LOAD)               # p
        arguments[0].accept(self)             # p, buf
        self._emit(Opcode.SUB)                # p - buf
        arguments[1].accept(self)             # (p-buf), maxLen
        self._emit(Opcode.PUSH, 1)
        self._emit(Opcode.SUB)                # maxLen-1
        self._emit(Opcode.GE)
        j_end_full = self._emit(Opcode.JNZ, 0)
        # Read one char and perform checks
        self._emit(Opcode.IN, self.INPUT_PORT)
        self._emit(Opcode.DUP)
        self._emit(Opcode.PUSH, 0)
        self._emit(Opcode.EQ)
        j_end_zero = self._emit(Opcode.JNZ, 0)
        self._emit(Opcode.DUP)
        self._emit(Opcode.PUSH, 10)
        self._emit(Opcode.EQ)
        j_end_nl = self._emit(Opcode.JNZ, 0)
        self._emit(Opcode.PUSH, p_addr)
        self._emit(Opcode.LOAD)               # ch, p  (p on top)
        self._emit(Opcode.STOREB)
        # Advance pointer by 1
        self._emit(Opcode.PUSH, p_addr)
        self._emit(Opcode.LOAD)
        self._emit(Opcode.PUSH, 1)
        self._emit(Opcode.ADD)
        self._emit(Opcode.PUSH, p_addr)
        self._emit(Opcode.STORE)
        # loop
        self._emit(Opcode.JMP, loop_start)
        # end:
        end_addr = len(self.machine_code.instructions)
        self._patch_address(j_end_full, end_addr)
        self._patch_address(j_end_zero, end_addr)
        self._patch_address(j_end_nl, end_addr)
        # Write string terminator: *p = 0
        self._emit(Opcode.PUSH, p_addr)
        self._emit(Opcode.LOAD)
        self._emit(Opcode.PUSH, 0)
        self._emit(Opcode.SWAP)               # 0, p
        self._emit(Opcode.STOREB)
    
    def _generate_len(self, arguments: List[Expression]) -> None:
        """Генерировать код для len."""
        if len(arguments) != 1:
            raise CodeGenError("len принимает ровно один аргумент")
        
        arguments[0].accept(self)
        # Для векторов/массивов первые 4 байта содержат размер
        self._emit(Opcode.LOAD)

    def _generate_chr(self, arguments: List[Expression]) -> None:
        """Генерировать код для chr - преобразование числа в символ."""
        if len(arguments) != 1:
            raise CodeGenError("chr принимает ровно один аргумент")
        
        arguments[0].accept(self)
        # Return number as-is (character code); could convert to string in real impl

    def _generate_putc(self, arguments: List[Expression]) -> None:
        """Вывод одного символа (код в TOS) через порт 2."""
        if len(arguments) != 1:
            raise CodeGenError("putc принимает ровно один аргумент")
        arguments[0].accept(self)
        self._emit(Opcode.OUT, 2)

    # Векторные builtin'ы (тонкая обёртка над V_* инструкциями CPU)
    def _generate_v_load(self, arguments: List[Expression]) -> None:
        if len(arguments) != ARGS_3:
            raise CodeGenError("v_load(addr, length, reg)")
        # Порядок для стека: addr, length, reg
        arguments[0].accept(self)
        arguments[1].accept(self)
        arguments[2].accept(self)
        self._emit(Opcode.V_LOAD)

    def _generate_v_add(self, arguments: List[Expression]) -> None:
        if len(arguments) != ARGS_3:
            raise CodeGenError("v_add(reg1, reg2, result_reg)")
        # Порядок на стеке: reg1, reg2, result
        arguments[0].accept(self)
        arguments[1].accept(self)
        arguments[2].accept(self)
        self._emit(Opcode.V_ADD)

    def _generate_v_dot(self, arguments: List[Expression]) -> None:
        if len(arguments) != ARGS_2:
            raise CodeGenError("v_dot(reg1, reg2)")
        arguments[0].accept(self)
        arguments[1].accept(self)
        self._emit(Opcode.V_DOT)

    def _generate_v_store(self, arguments: List[Expression]) -> None:
        if len(arguments) != ARGS_2:
            raise CodeGenError("v_store(reg, addr)")
        # порядок на стеке: addr, reg
        arguments[1].accept(self)
        arguments[0].accept(self)
        self._emit(Opcode.V_STORE)

    def _generate_v_sum(self, arguments: List[Expression]) -> None:
        if len(arguments) != 1:
            raise CodeGenError("v_sum(reg)")
        arguments[0].accept(self)
        self._emit(Opcode.V_SUM)

    def _generate_set_interrupt_handler(self, arguments: List[Expression]) -> None:
        """Генерировать код для set_interrupt_handler."""
        if len(arguments) != ARGS_2:
            raise CodeGenError("set_interrupt_handler принимает 2 аргумента")
        
        arguments[0].accept(self)  # Номер прерывания
        arguments[1].accept(self)  # Адрес обработчика
        self._emit(Opcode.INT, 0x80)  # Системный вызов для установки обработчика

    def _generate_enable_interrupts(self, arguments: List[Expression]) -> None:
        """Генерировать код для enable_interrupts."""
        if len(arguments) != 0:
            raise CodeGenError("enable_interrupts не принимает аргументов")
        
        self._emit(Opcode.INT, 0x81)  # Системный вызов для включения прерываний

    def _generate_disable_interrupts(self, arguments: List[Expression]) -> None:
        """Генерировать код для disable_interrupts."""
        if len(arguments) != 0:
            raise CodeGenError("disable_interrupts не принимает аргументов")
        
        self._emit(Opcode.INT, 0x82)  # Системный вызов для отключения прерываний


def generate_code(program: Program) -> MachineCode:
    """Удобная функция для генерации кода."""
    generator = CodeGenerator()
    return generator.generate(program)