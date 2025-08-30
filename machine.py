#!/usr/bin/env python3
"""Машина для выполнения программ на стековом процессоре."""

import argparse
import sys
from pathlib import Path

from comp.processor import StackProcessor
from isa.machine_code import MachineCode


def main() -> None:
    """Главная функция машины."""
    parser = argparse.ArgumentParser(
        description="Машина для выполнения программ на стековом процессоре"
    )
    
    parser.add_argument("program_file", help="Файл с машинным кодом (.bin)")
    parser.add_argument("-d", "--data", help="Файл с данными для памяти данных")
    parser.add_argument("-i", "--input", help="Файл с входными данными")
    parser.add_argument("-o", "--output", help="Файл для вывода результатов")
    parser.add_argument("--max-cycles", type=int, default=1000000, help="Максимальное количество тактов")
    parser.add_argument("--verbose", action="store_true", help="Подробный вывод")
    
    args = parser.parse_args()
    
    try:
        # Загружаем программу
        program_path = Path(args.program_file)
        if not program_path.exists():
            print(f"Ошибка: файл программы '{args.program_file}' не найден", file=sys.stderr)
            sys.exit(1)
        
        print(f"Загрузка программы: {args.program_file}")
        instructions = MachineCode.load_instruction_memory(str(program_path))
        print(f"Загружено {len(instructions)} инструкций")
        
        # Создаем процессор
        processor = StackProcessor()
        processor.load_program(instructions)
        
        # Загружаем данные
        if args.data:
            data_path = Path(args.data)
            if data_path.exists():
                print(f"Загрузка данных: {args.data}")
                data = MachineCode.load_data_memory(str(data_path))
                processor.load_data(data)
                print(f"Загружено {len(data)} байт данных")
        
        # Запускаем выполнение
        print(f"Запуск выполнения (максимум {args.max_cycles} тактов)...")
        result = processor.run(args.max_cycles)
        
        # Выводим результаты
        print("=== РЕЗУЛЬТАТЫ ВЫПОЛНЕНИЯ ===")
        print(f"Состояние: {result['state']}")
        print(f"Выполнено инструкций: {result['instructions_executed']}")
        print(f"Затрачено тактов: {result['cycles_executed']}")
        print(f"Финальный PC: {result['final_pc']}")
        
        # Вывод данных
        if result['output']:
            print(f"\nВЫВОД ПРОГРАММЫ:")
            output_text = ""
            for value in result['output']:
                if 32 <= value <= 126:  # Печатаемые ASCII символы
                    output_text += chr(value)
                elif value == 10:  # Перевод строки
                    output_text += '\n'
                else:
                    output_text += f"[{value}]"
            
            print(output_text)
            
            # Сохраняем вывод в файл
            if args.output:
                output_path = Path(args.output)
                output_path.write_text(output_text, encoding='utf-8')
                print(f"\nВывод сохранен в: {args.output}")
        
        # Успешное завершение
        if result['state'] == 'halted':
            print("\nПрограмма завершена успешно.")
            sys.exit(0)
        else:
            print(f"\nПрограмма завершена с состоянием: {result['state']}")
            sys.exit(1)
        
    except Exception as e:
        print(f"Ошибка выполнения: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 