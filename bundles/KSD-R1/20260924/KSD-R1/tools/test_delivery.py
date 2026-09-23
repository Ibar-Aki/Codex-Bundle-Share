"""Focused tamper/recovery regression tests; run with Python 3.10+ on Windows."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='ksd-delivery-test-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / 'KSD-R1'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        spec = importlib.util.spec_from_file_location('ksd_check', self.root / 'tools/check_package.py')
        self.checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.checker)

    def edit_json(self, name, operation):
        path = self.root / name
        content = json.loads(path.read_text(encoding='utf-8'))
        operation(content)
        path.write_text(json.dumps(content, ensure_ascii=False), encoding='utf-8')

    def test_formula_and_dependency_evidence(self):
        result = self.checker.check(skip_manifest=True)
        self.assertEqual((result['formulas'], result['target_formulas'], result['affected_formulas']), (936, 8, 21))

    def test_wrong_formula_is_rejected(self):
        self.edit_json('docs/変更セル仕様.json', lambda v: v['changes'][0].update(before='=0'))
        with self.assertRaisesRegex(ValueError, 'Before formula differs'):
            self.checker.check(skip_manifest=True)

    def test_wrong_dependency_with_same_count_is_rejected(self):
        self.edit_json('reference/affected_cells.json', lambda v: v['transitive_dependents'].__setitem__(0, '基準芯出し_出力③!A1'))
        with self.assertRaisesRegex(ValueError, 'Dependency list differs'):
            self.checker.check(skip_manifest=True)

    def test_changed_workbook_is_rejected(self):
        with (self.root / 'workbook/KSD-R1_restored.xlsx').open('ab') as output:
            output.write(b'changed')
        with self.assertRaisesRegex(ValueError, 'workbook identity differs'):
            self.checker.check(skip_manifest=True)

    def test_native_powershell_restore_idempotence_conflict_and_corruption(self):
        for shell in ['powershell.exe', 'pwsh.exe']:
            with self.subTest(shell=shell):
                executable = shutil.which(shell)
                self.assertIsNotNone(executable, 'Required Windows verification runtime missing: ' + shell)
                destination = Path(self.temporary.name) / shell
                command = [executable, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(self.root / 'tools/Restore-Workbook.ps1'), '-OutputDirectory', str(destination)]
                first = subprocess.run(command, capture_output=True, text=True, timeout=30)
                self.assertEqual(first.returncode, 0, first.stderr)
                self.assertIn('PASS_RESTORED', first.stdout)
                restored = destination / 'KSD-R1_restored.xlsx'
                self.assertEqual(hashlib.sha256(restored.read_bytes()).hexdigest(), self.checker.EXPECTED_SHA)
                second = subprocess.run(command, capture_output=True, text=True, timeout=30)
                self.assertEqual(second.returncode, 0, second.stderr)
                self.assertIn('PASS_EXISTING', second.stdout)
                restored.write_bytes(b'existing user file')
                conflict = subprocess.run(command, capture_output=True, text=True, timeout=30)
                self.assertNotEqual(conflict.returncode, 0)
                self.assertEqual(restored.read_bytes(), b'existing user file')
                payload = self.root / 'payload/WorkbookPayload.json'
                original = payload.read_bytes()
                self.edit_json('payload/WorkbookPayload.json', lambda v: v.update(base64='AAAA'))
                corrupt_output = Path(self.temporary.name) / (shell + '-corrupt')
                corrupted = subprocess.run(command[:-1] + [str(corrupt_output)], capture_output=True, text=True, timeout=30)
                self.assertNotEqual(corrupted.returncode, 0)
                self.assertFalse((corrupt_output / 'KSD-R1_restored.xlsx').exists())
                payload.write_bytes(original)

    def test_readme_default_restore_directory(self):
        workbook = self.root / 'workbook/KSD-R1_restored.xlsx'
        for shell in ['powershell.exe', 'pwsh.exe']:
            with self.subTest(shell=shell):
                executable = shutil.which(shell)
                self.assertIsNotNone(executable)
                workbook.unlink()
                result = subprocess.run([executable, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(self.root / 'tools/Restore-Workbook.ps1')], capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(hashlib.sha256(workbook.read_bytes()).hexdigest(), self.checker.EXPECTED_SHA)


if __name__ == '__main__':
    unittest.main(verbosity=2)
