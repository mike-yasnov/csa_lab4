"""Golden tests for translator and machine correctness."""

import re
import sys
import subprocess
import tempfile
import json
from pathlib import Path
from typing import Any, Dict, Tuple


class GoldenTest:
    """Golden test runner and manager."""

    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        self.examples_dir = root_dir / "examples"
        self.golden_dir = root_dir / "golden"
        self.golden_dir.mkdir(exist_ok=True)
    
    def normalize_output(self, text: str) -> str:
        """Normalize output by removing ephemeral paths."""
        # Strip random macOS temp sandbox path
        text = re.sub(r"/var/folders/[^/]+/[^/]+/[^/]+/[^/]+", "<tempfile>", text)
        # Strip Python tempfile prefixes (use dynamic tmpdir to avoid hardcoded /tmp)
        tmpdir = re.escape(tempfile.gettempdir())
        text = re.sub(rf"{tmpdir}/tmp[a-zA-Z0-9_]+", "<tempfile>", text)  # noqa: S108
        # Normalize generic tmp prefixes in logs
        return re.sub(r"tmp[a-zA-Z0-9_]+/", "tempfile/", text)
    
    def run_test(
        self,
        _test_name: str,
        source_file: str,
        input_data: str = "",
        schedule_data: Dict[str, Any] | None = None,
    ) -> Tuple[int, str, str, str, str]:
        """Run one test and return: code, stdout, stderr, exec_log, debug_listing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Транслируем программу
            cmd = [
                sys.executable, "translator.py",
                str(self.examples_dir / source_file),
                "-o", str(temp_path / "program"),
                "--debug",
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.root_dir,
                check=False,
                shell=False,
            )
            if result.returncode != 0:
                return result.returncode, "", f"Translation error: {result.stderr}", "", ""
            # Читаем отладочный листинг транслятора
            debug_listing_path = temp_path / "program_debug.txt"
            debug_listing = ""
            if debug_listing_path.exists():
                debug_listing = debug_listing_path.read_text(encoding='utf-8')
            
            # Run the machine
            cmd = [
                sys.executable, "machine.py",
                str(temp_path / "program.bin"),
                "-d", str(temp_path / "program_data.bin"),
                "--log-exec", str(temp_path / "exec.log"),
            ]
            # If schedule provided, save it and pass as a file
            if schedule_data is not None:
                schedule_path = temp_path / "schedule.json"
                schedule_path.write_text(json.dumps(schedule_data), encoding='utf-8')
                cmd.extend(["--schedule", str(schedule_path)])
            
            if input_data:
                # With input data
                result = subprocess.run(
                    cmd,
                    input=input_data,
                    capture_output=True,
                    text=True,
                    cwd=self.root_dir,
                    check=False,
                    shell=False,
                )
            else:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=self.root_dir,
                    check=False,
                    shell=False,
                )
            
            # Нормализуем вывод
            normalized_stdout = self.normalize_output(result.stdout)
            normalized_stderr = self.normalize_output(result.stderr)
            # Читаем журнал тактов
            exec_log_path = temp_path / "exec.log"
            exec_log = ""
            if exec_log_path.exists():
                exec_log = exec_log_path.read_text(encoding='utf-8')
            
            return result.returncode, normalized_stdout, normalized_stderr, exec_log, debug_listing
    
    def save_golden(self, test_name: str, result: Tuple[int, str, str, str, str]) -> None:
        """Save golden result (including exec log and translator debug listing)."""
        golden_file = self.golden_dir / f"{test_name}.json"
        return_code, stdout, stderr, exec_log, debug_listing = result
        
        data = {
            "return_code": return_code,
            "stdout": stdout,
            "stderr": stderr,
            "exec_log": exec_log,
            "debug_listing": debug_listing,
        }
        
        with golden_file.open('w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        sys.stdout.write(f"Golden saved: {golden_file}\n")
    
    def load_golden(self, test_name: str) -> Dict[str, Any] | None:
        """Load golden result."""
        golden_file = self.golden_dir / f"{test_name}.json"
        
        if not golden_file.exists():
            return None
        with golden_file.open('r', encoding='utf-8') as f:
            return json.load(f)
    
    def compare_results(self, test_name: str, actual: Tuple[int, str, str, str, str]) -> bool:
        """Compare actual result with golden one."""
        golden = self.load_golden(test_name)
        if golden is None:
            sys.stdout.write(f"❌ {test_name}: Golden not found\n")
            return False
        
        actual_code, actual_stdout, actual_stderr, actual_exec_log, actual_debug_listing = actual
        
        if (golden["return_code"] == actual_code and
            golden["stdout"] == actual_stdout and
            golden["stderr"] == actual_stderr and
            golden.get("exec_log", "") == actual_exec_log and
            golden.get("debug_listing", "") == actual_debug_listing):
            sys.stdout.write(f"✅ {test_name}: PASSED\n")
            return True
        else:
            sys.stdout.write(f"❌ {test_name}: FAILED\n")
            sys.stdout.write(f"   Expected: code={golden['return_code']}\n")
            sys.stdout.write(f"   Got:      code={actual_code}\n")
            if golden["stdout"] != actual_stdout:
                sys.stdout.write("   Stdout differs:\n")
                sys.stdout.write(f"     Expected: {golden['stdout']!r}\n")
                sys.stdout.write(f"     Got:      {actual_stdout!r}\n")
            if golden["stderr"] != actual_stderr:
                sys.stdout.write("   Stderr differs:\n")
                sys.stdout.write(f"     Expected: {golden['stderr']!r}\n")
                sys.stdout.write(f"     Got:      {actual_stderr!r}\n")
            if golden.get("exec_log", "") != actual_exec_log:
                sys.stdout.write("   Exec log differs (first 200 chars):\n")
                sys.stdout.write(f"     Expected: {golden.get('exec_log', '')[:200]!r}...\n")
                sys.stdout.write(f"     Got:      {actual_exec_log[:200]!r}...\n")
            if golden.get("debug_listing", "") != actual_debug_listing:
                sys.stdout.write("   Debug listing differs (first 200 chars):\n")
                sys.stdout.write(f"     Expected: {golden.get('debug_listing', '')[:200]!r}...\n")
                sys.stdout.write(f"     Got:      {actual_debug_listing[:200]!r}...\n")
            return False
    
    def generate_goldens(self) -> None:
        """Сгенерировать все эталонные тесты."""
        tests = [
            ("hello", "hello.alg", "", None),
            ("simple_vector", "simple_vector.alg", "", None),
            ("euler6", "euler6.alg", "", None),
            ("cat", "cat.alg", "Hello\nWorld\n", None),
            ("hello_user_name", "hello_user_name.alg", "A\n", None),
            ("sort", "sort.alg", "", None),
            ("double_precision", "double_precision.alg", "", None),
            # interrupt schedule: input tokens at cycles 10,20,30
            ("interrupt_demo", "interrupt_demo.alg", "", {"input": [
                {"cycle": 10, "data": "X"},
                {"cycle": 20, "data": "Y"},
                {"cycle": 30, "data": "Z"},
            ]}),
        ]
        
        sys.stdout.write("Generating golden tests...\n")
        
        for test_name, source_file, input_data, schedule in tests:
            sys.stdout.write(f"\nGenerating {test_name}...\n")
            result = self.run_test(test_name, source_file, input_data, schedule)
            self.save_golden(test_name, result)
    
    def run_all_tests(self) -> bool:
        """Run all golden tests."""
        tests = [
            ("hello", "hello.alg", "", None),
            ("simple_vector", "simple_vector.alg", "", None),
            ("euler6", "euler6.alg", "", None),
            ("cat", "cat.alg", "Hello\nWorld\n", None),
            ("hello_user_name", "hello_user_name.alg", "A\n", None),
            ("sort", "sort.alg", "", None),
            ("double_precision", "double_precision.alg", "", None),
            ("interrupt_demo", "interrupt_demo.alg", "", {"input": [
                {"cycle": 10, "data": "X"},
                {"cycle": 20, "data": "Y"},
                {"cycle": 30, "data": "Z"},
            ]}),
        ]
        
        sys.stdout.write("Running golden tests...\n")
        all_passed = True
        
        for test_name, source_file, input_data, schedule in tests:
            result = self.run_test(test_name, source_file, input_data, schedule)
            if not self.compare_results(test_name, result):
                all_passed = False
        
        return all_passed


CLI_MIN_ARGS = 2


def main() -> None:
    """CLI entry point."""
    if len(sys.argv) < CLI_MIN_ARGS:
        sys.stdout.write("Usage:\n")
        sys.stdout.write("  python golden_test.py generate  - generate goldens\n")
        sys.stdout.write("  python golden_test.py test      - run tests\n")
        sys.exit(1)
    
    root_dir = Path(__file__).parent
    tester = GoldenTest(root_dir)
    
    command = sys.argv[1]
    
    if command == "generate":
        tester.generate_goldens()
        sys.stdout.write("\n✅ Golden tests generated!\n")
    
    elif command == "test":
        success = tester.run_all_tests()
        if success:
            sys.stdout.write("\n✅ All tests passed!\n")
            sys.exit(0)
        else:
            sys.stdout.write("\n❌ Some tests failed\n")
            sys.exit(1)
    
    else:
        sys.stdout.write(f"Unknown command: {command}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()