"""Translator from ALG-like source to stack-architecture machine code."""

import argparse
import sys
from pathlib import Path
from typing import Any

from lang.lexer import tokenize, LexerError
from lang.parser import parse, ParseError
from lang.codegen import generate_code, CodeGenError


def main() -> None:
    """Главная функция транслятора."""
    parser = argparse.ArgumentParser(
        description="Translator from ALG-like source to stack-architecture machine code",
    )
    
    parser.add_argument(
        "source_file",
        help="Input source file",
    )
    
    parser.add_argument(
        "-o", "--output",
        default="program",
        help="Output base filename (default: program)",
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Write debug listing",
    )
    
    parser.add_argument(
        "--ast",
        action="store_true",
        help="Print AST",
    )
    
    args = parser.parse_args()
    
    try:
        # Читаем исходный код
        source_path = Path(args.source_file)
        if not source_path.exists():
            sys.stderr.write(f"Error: file '{args.source_file}' not found\n")
            sys.exit(1)
        
        source_code = source_path.read_text(encoding="utf-8")
        sys.stdout.write(f"Reading source file: {args.source_file}\n")
        
        # Лексический анализ
        sys.stdout.write("Lexical analysis...\n")
        tokens = tokenize(source_code)
        sys.stdout.write(f"Found {len(tokens)} tokens\n")
        
        # Синтаксический анализ
        sys.stdout.write("Parsing...\n")
        ast = parse(tokens)
        sys.stdout.write("AST built successfully\n")
        
        if args.ast:
            sys.stdout.write("\nAST:\n")
            print_ast(ast, 0)
            sys.stdout.write("\n")
        
        # Генерация кода
        sys.stdout.write("Generating machine code...\n")
        machine_code = generate_code(ast)
        sys.stdout.write(f"Generated {len(machine_code.instructions)} instructions\n")
        sys.stdout.write(f"Data memory size: {len(machine_code.data_memory)} bytes\n")
        
        # Сохраняем файлы
        output_base = args.output
        
        # Память команд (бинарный файл)
        instr_file = f"{output_base}.bin"
        machine_code.save_instruction_memory(instr_file)
        sys.stdout.write(f"Instruction memory saved to: {instr_file}\n")
        
        # Память данных (бинарный файл)
        data_file = f"{output_base}_data.bin"
        machine_code.save_data_memory(data_file)
        sys.stdout.write(f"Data memory saved to: {data_file}\n")
        
        # Отладочный листинг
        if args.debug:
            debug_file = f"{output_base}_debug.txt"
            machine_code.save_debug_listing(debug_file)
            sys.stdout.write(f"Debug listing saved to: {debug_file}\n")
        
        sys.stdout.write("Translation finished successfully!\n")
        
    except LexerError as e:
        sys.stderr.write(f"Lexical error: {e}\n")
        sys.exit(1)
    except ParseError as e:
        sys.stderr.write(f"Parse error: {e}\n")
        sys.exit(1)
    except CodeGenError as e:
        sys.stderr.write(f"Code generation error: {e}\n")
        sys.exit(1)


def print_ast(node: Any, indent: int) -> None:
    """Вывести AST в читаемом виде."""
    indent_str = "  " * indent
    
    if hasattr(node, "__class__"):
        class_name = node.__class__.__name__
        sys.stdout.write(f"{indent_str}{class_name}\n")
        
        # Печатаем поля узла
        if hasattr(node, "__dict__"):
            for key, value in node.__dict__.items():
                if key.startswith("_"):
                    continue

                sys.stdout.write(f"{indent_str}  {key}:")

                if isinstance(value, list):
                    sys.stdout.write("\n")
                    for item in value:
                        print_ast(item, indent + 2)
                elif hasattr(value, "__class__") and hasattr(value, "__dict__"):
                    sys.stdout.write("\n")
                    print_ast(value, indent + 2)
                else:
                    sys.stdout.write(f" {value}\n")
    else:
        sys.stdout.write(f"{indent_str}{node}\n")


if __name__ == "__main__":
    main()