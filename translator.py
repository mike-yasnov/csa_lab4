#!/usr/bin/env python3
"""Транслятор алголичного языка в машинный код стековой архитектуры."""

import argparse
import sys
from pathlib import Path
from typing import Any

from csa4_impl.lang.lexer import tokenize, LexerError
from csa4_impl.lang.parser import parse, ParseError
from csa4_impl.lang.codegen import generate_code, CodeGenError


def main() -> None:
    """Главная функция транслятора."""
    parser = argparse.ArgumentParser(
        description="Транслятор алголичного языка в машинный код стековой архитектуры"
    )
    
    parser.add_argument(
        "source_file",
        help="Входной файл с исходным кодом"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="program",
        help="Базовое имя выходных файлов (по умолчанию: program)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Создать отладочный листинг"
    )
    
    parser.add_argument(
        "--ast",
        action="store_true", 
        help="Вывести AST для отладки"
    )
    
    args = parser.parse_args()
    
    try:
        # Читаем исходный код
        source_path = Path(args.source_file)
        if not source_path.exists():
            print(f"Ошибка: файл '{args.source_file}' не найден", file=sys.stderr)
            sys.exit(1)
        
        source_code = source_path.read_text(encoding='utf-8')
        print(f"Чтение исходного файла: {args.source_file}")
        
        # Лексический анализ
        print("Лексический анализ...")
        tokens = tokenize(source_code)
        print(f"Найдено {len(tokens)} токенов")
        
        # Синтаксический анализ
        print("Синтаксический анализ...")
        ast = parse(tokens)
        print("AST построен успешно")
        
        if args.ast:
            print("\nAST:")
            print_ast(ast, 0)
            print()
        
        # Генерация кода
        print("Генерация машинного кода...")
        machine_code = generate_code(ast)
        print(f"Сгенерировано {len(machine_code.instructions)} инструкций")
        print(f"Размер памяти данных: {len(machine_code.data_memory)} байт")
        
        # Сохраняем файлы
        output_base = args.output
        
        # Память команд (бинарный файл)
        instr_file = f"{output_base}.bin"
        machine_code.save_instruction_memory(instr_file)
        print(f"Память команд сохранена в: {instr_file}")
        
        # Память данных (бинарный файл)
        data_file = f"{output_base}_data.bin"
        machine_code.save_data_memory(data_file)
        print(f"Память данных сохранена в: {data_file}")
        
        # Отладочный листинг
        if args.debug:
            debug_file = f"{output_base}_debug.txt"
            machine_code.save_debug_listing(debug_file)
            print(f"Отладочный листинг сохранен в: {debug_file}")
        
        print("Трансляция завершена успешно!")
        
    except LexerError as e:
        print(f"Ошибка лексического анализа: {e}", file=sys.stderr)
        sys.exit(1)
    except ParseError as e:
        print(f"Ошибка синтаксического анализа: {e}", file=sys.stderr)
        sys.exit(1)
    except CodeGenError as e:
        print(f"Ошибка генерации кода: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}", file=sys.stderr)
        sys.exit(1)


def print_ast(node: Any, indent: int) -> None:
    """Вывести AST в читаемом виде."""
    indent_str = "  " * indent
    
    if hasattr(node, '__class__'):
        class_name = node.__class__.__name__
        print(f"{indent_str}{class_name}")
        
        # Печатаем поля узла
        if hasattr(node, '__dict__'):
            for key, value in node.__dict__.items():
                if key.startswith('_'):
                    continue
                
                print(f"{indent_str}  {key}:", end="")
                
                if isinstance(value, list):
                    print()
                    for item in value:
                        print_ast(item, indent + 2)
                elif hasattr(value, '__class__') and hasattr(value, '__dict__'):
                    print()
                    print_ast(value, indent + 2)
                else:
                    print(f" {value}")
    else:
        print(f"{indent_str}{node}")


if __name__ == "__main__":
    main() 