#!/usr/bin/env python3
"""Golden тесты для проверки корректности работы транслятора и машины."""

import os
import sys
import subprocess
import tempfile
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class GoldenTest:
    """Класс для управления golden тестами."""
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.examples_dir = root_dir / "examples"
        self.golden_dir = root_dir / "golden"
        self.golden_dir.mkdir(exist_ok=True)
    
    def normalize_output(self, output: str) -> str:
        """Нормализовать вывод, убрав изменяющиеся части."""
        import re
        
        # Убираем пути к временным файлам
        output = re.sub(r'/var/folders/[^/]+/[^/]+/[^/]+/[^/]+', '/tmp/tempfile', output)
        output = re.sub(r'/tmp/tmp[a-zA-Z0-9_]+', '/tmp/tempfile', output)
        
        # Убираем другие временные пути
        output = re.sub(r'tmp[a-zA-Z0-9_]+/', 'tempfile/', output)
        
        return output
    
    def run_test(self, test_name: str, source_file: str, input_data: str = "") -> Tuple[int, str, str, str, str]:
        """Запустить один тест и вернуть код возврата, stdout, stderr, exec_log, debug_listing."""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Транслируем программу
            cmd = [
                sys.executable, "translator.py",
                str(self.examples_dir / source_file),
                "-o", str(temp_path / "program"),
                "--debug"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.root_dir)
            if result.returncode != 0:
                return result.returncode, "", f"Translation error: {result.stderr}", "", ""
            # Читаем отладочный листинг транслятора
            debug_listing_path = temp_path / "program_debug.txt"
            debug_listing = ""
            if debug_listing_path.exists():
                debug_listing = debug_listing_path.read_text(encoding='utf-8')
            
            # Запускаем машину
            cmd = [
                sys.executable, "machine.py",
                str(temp_path / "program.bin"),
                "-d", str(temp_path / "program_data.bin"),
                "--log-exec", str(temp_path / "exec.log")
            ]
            
            if input_data:
                # Если есть входные данные
                result = subprocess.run(cmd, input=input_data, capture_output=True, text=True, cwd=self.root_dir)
            else:
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.root_dir)
            
            # Нормализуем вывод
            normalized_stdout = self.normalize_output(result.stdout)
            normalized_stderr = self.normalize_output(result.stderr)
            # Читаем журнал тактов
            exec_log_path = temp_path / "exec.log"
            exec_log = ""
            if exec_log_path.exists():
                exec_log = exec_log_path.read_text(encoding='utf-8')
            
            return result.returncode, normalized_stdout, normalized_stderr, exec_log, debug_listing
    
    def save_golden(self, test_name: str, return_code: int, stdout: str, stderr: str, exec_log: str, debug_listing: str) -> None:
        """Сохранить эталонный результат (включая журнал тактов и отладочный листинг транслятора)."""
        golden_file = self.golden_dir / f"{test_name}.json"
        
        data = {
            "return_code": return_code,
            "stdout": stdout,
            "stderr": stderr,
            "exec_log": exec_log,
            "debug_listing": debug_listing
        }
        
        with open(golden_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Эталон сохранен: {golden_file}")
    
    def load_golden(self, test_name: str) -> Optional[Dict]:
        """Загрузить эталонный результат."""
        golden_file = self.golden_dir / f"{test_name}.json"
        
        if not golden_file.exists():
            return None
        
        with open(golden_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def compare_results(self, test_name: str, actual: Tuple[int, str, str, str, str]) -> bool:
        """Сравнить результат с эталоном."""
        golden = self.load_golden(test_name)
        if golden is None:
            print(f"❌ {test_name}: Эталон не найден")
            return False
        
        actual_code, actual_stdout, actual_stderr, actual_exec_log, actual_debug_listing = actual
        
        if (golden["return_code"] == actual_code and
            golden["stdout"] == actual_stdout and
            golden["stderr"] == actual_stderr and
            golden.get("exec_log", "") == actual_exec_log and
            golden.get("debug_listing", "") == actual_debug_listing):
            print(f"✅ {test_name}: PASSED")
            return True
        else:
            print(f"❌ {test_name}: FAILED")
            print(f"   Ожидалось: код={golden['return_code']}")
            print(f"   Получено:  код={actual_code}")
            if golden["stdout"] != actual_stdout:
                print(f"   Stdout различается:")
                print(f"     Ожидалось: {repr(golden['stdout'])}")
                print(f"     Получено:  {repr(actual_stdout)}")
            if golden["stderr"] != actual_stderr:
                print(f"   Stderr различается:")
                print(f"     Ожидалось: {repr(golden['stderr'])}")
                print(f"     Получено:  {repr(actual_stderr)}")
            if golden.get("exec_log", "") != actual_exec_log:
                print(f"   Exec log различается (первые 200 симв.):")
                print(f"     Ожидалось: {repr(golden.get('exec_log', '')[:200])}...")
                print(f"     Получено:  {repr(actual_exec_log[:200])}...")
            if golden.get("debug_listing", "") != actual_debug_listing:
                print(f"   Debug listing различается (первые 200 симв.):")
                print(f"     Ожидалось: {repr(golden.get('debug_listing', '')[:200])}...")
                print(f"     Получено:  {repr(actual_debug_listing[:200])}...")
            return False
    
    def generate_goldens(self) -> None:
        """Сгенерировать все эталонные тесты."""
        tests = [
            ("hello", "hello.alg", ""),
            ("simple_vector", "simple_vector.alg", ""),
            ("euler6", "euler6.alg", ""),
            ("cat", "cat.alg", "Hello\nWorld\n"),
            ("hello_user_name", "hello_user_name.alg", "A"),
            ("sort", "sort.alg", ""),
            ("double_precision", "double_precision.alg", ""),
            ("interrupt_demo", "interrupt_demo.alg", ""),
        ]
        
        print("Генерация эталонных тестов...")
        
        for test_name, source_file, input_data in tests:
            print(f"\nГенерация {test_name}...")
            result = self.run_test(test_name, source_file, input_data)
            self.save_golden(test_name, *result)
    
    def run_all_tests(self) -> bool:
        """Запустить все тесты."""
        tests = [
            ("hello", "hello.alg", ""),
            ("simple_vector", "simple_vector.alg", ""),
            ("euler6", "euler6.alg", ""),
            ("cat", "cat.alg", "Hello\nWorld\n"),
            ("hello_user_name", "hello_user_name.alg", "A"),
            ("sort", "sort.alg", ""),
            ("double_precision", "double_precision.alg", ""),
            ("interrupt_demo", "interrupt_demo.alg", ""),
        ]
        
        print("Запуск golden тестов...")
        all_passed = True
        
        for test_name, source_file, input_data in tests:
            result = self.run_test(test_name, source_file, input_data)
            if not self.compare_results(test_name, result):
                all_passed = False
        
        return all_passed


def main():
    """Главная функция."""
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python golden_test.py generate  - сгенерировать эталоны")
        print("  python golden_test.py test      - запустить тесты")
        sys.exit(1)
    
    root_dir = Path(__file__).parent
    tester = GoldenTest(root_dir)
    
    command = sys.argv[1]
    
    if command == "generate":
        tester.generate_goldens()
        print("\n✅ Эталонные тесты сгенерированы!")
    
    elif command == "test":
        success = tester.run_all_tests()
        if success:
            print("\n✅ Все тесты прошли успешно!")
            sys.exit(0)
        else:
            print("\n❌ Некоторые тесты не прошли")
            sys.exit(1)
    
    else:
        print(f"Неизвестная команда: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main() 