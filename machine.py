"""Machine to execute programs on the stack-based processor."""

import argparse
import sys
import json
from pathlib import Path

from comp.processor import StackProcessor, ProcessorError
from isa.machine_code import MachineCode


def main() -> None:
    """Главная функция машины."""
    parser = argparse.ArgumentParser(
        description="Machine to execute programs on the stack-based processor",
    )
    
    parser.add_argument("program_file", help="Instruction memory file (.bin)")
    parser.add_argument("-d", "--data", help="Data memory file")
    parser.add_argument("-i", "--input", help="Input file (queued byte-by-byte)")
    parser.add_argument("-o", "--output", help="Output file")
    parser.add_argument("--schedule", help="JSON schedule file for input/interrupts")
    parser.add_argument("--log-exec", help="Save execution log to a file")
    parser.add_argument("--max-cycles", type=int, default=1000000, help="Max cycles")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    try:
        # Загружаем программу
        program_path = Path(args.program_file)
        if not program_path.exists():
            sys.stderr.write(f"Ошибка: файл программы '{args.program_file}' не найден\n")
            sys.exit(1)
        
        sys.stdout.write(f"Loading program: {args.program_file}\n")
        instructions = MachineCode.load_instruction_memory(str(program_path))
        sys.stdout.write(f"Loaded {len(instructions)} instructions\n")
        
        # Создаем процессор
        processor = StackProcessor()
        processor.load_program(instructions)
        
        # Загружаем данные
        if args.data:
            data_path = Path(args.data)
            if data_path.exists():
                sys.stdout.write(f"Loading data: {args.data}\n")
                data = MachineCode.load_data_memory(str(data_path))
                processor.load_data(data)
                sys.stdout.write(f"Loaded {len(data)} bytes of data\n")
        
        # Загрузка входа: расписание, файл или stdin (если передан через пайп)
        if args.schedule:
            schedule_path = Path(args.schedule)
            if not schedule_path.exists():
                sys.stderr.write(f"Error: schedule file '{args.schedule}' not found\n")
                sys.exit(1)
            try:
                schedule = json.loads(schedule_path.read_text(encoding='utf-8'))
            except (json.JSONDecodeError, OSError) as e:
                sys.stderr.write(f"Schedule read error: {e}\n")
                sys.exit(1)
            # Ожидается ключ "input": список объектов {cycle:int, data:int}
            for ev in schedule.get("input", []):
                cycle = int(ev.get("cycle", 0))
                data = ev.get("data", 0)
                data_val = ord(data[0]) if isinstance(data, str) and len(data) > 0 else int(data)
                processor.schedule_input_event(cycle, data_val)
        elif args.input:
            input_path = Path(args.input)
            if not input_path.exists():
                sys.stderr.write(f"Error: input file '{args.input}' not found\n")
                sys.exit(1)
            content = input_path.read_text(encoding='utf-8')
            # Немедленно наполняем буфер ввода для синхронного IN
            for ch in content:
                processor.input_buffer.append(ord(ch))
        else:
            # Если вход не указан, но в stdin есть данные (запуск через пайп), читаем их
            try:
                if not sys.stdin.isatty():
                    content = sys.stdin.read()
                    for ch in content:
                        processor.input_buffer.append(ord(ch))
            except OSError:
                # Safely ignore stdin errors, leaving the buffer empty
                content = ""

        # Запускаем выполнение
        sys.stdout.write(f"Start execution (max {args.max_cycles} cycles)...\n")
        result = processor.run(args.max_cycles)
        
        # Выводим результаты
        sys.stdout.write("\n=== EXECUTION RESULTS ===\n")
        sys.stdout.write(f"State: {result['state']}\n")
        sys.stdout.write(f"Instructions executed: {result['instructions_executed']}\n")
        sys.stdout.write(f"Cycles executed: {result['cycles_executed']}\n")
        sys.stdout.write(f"Final PC: {result['final_pc']}\n")
        
        # Вывод данных
        if result['output']:
            sys.stdout.write("\nPROGRAM OUTPUT:\n")
            output_text = ""
            ascii_min = 32
            ascii_max = 126
            newline = 10
            for value in result['output']:
                if ascii_min <= value <= ascii_max:  # printable ASCII
                    output_text += chr(value)
                elif value == newline:  # newline
                    output_text += "\n"
                else:
                    output_text += f"[{value}]"
            
            sys.stdout.write(f"{output_text}\n")
            
            # Сохраняем вывод в файл
            if args.output:
                output_path = Path(args.output)
                output_path.write_text(output_text, encoding='utf-8')
                sys.stdout.write(f"\nOutput saved to: {args.output}\n")
        
        # Сохранить журнал тактов
        if args.log_exec:
            log_path = Path(args.log_exec)
            log_path.write_text("\n".join(result.get('execution_log', [])), encoding='utf-8')
            if args.verbose:
                sys.stdout.write(f"Execution log saved: {args.log_exec}\n")

        # Успешное завершение
        if result['state'] == 'halted':
            sys.stdout.write("\nProgram finished successfully.\n")
            sys.exit(0)
        else:
            sys.stdout.write(f"\nProgram finished with state: {result['state']}\n")
            sys.exit(1)
        
    except (OSError, ValueError, KeyError, TypeError, ProcessorError) as e:
        sys.stderr.write(f"Execution error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()