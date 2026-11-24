"""
Pruebas de extremo a extremo: compila y ejecuta programas Aurum reales.

Ejecutar con:  python -m unittest discover tests
"""

import unittest
from pathlib import Path

from src.compiler import AurumCompiler

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def run(source: str, inputs=None):
    compiler = AurumCompiler()
    compilation, execution = compiler.compile_and_run(source, inputs or [])
    return compilation, execution


def run_file(name: str, inputs=None):
    return run((EXAMPLES / name).read_text(encoding="utf-8"), inputs)


class ExamplesTest(unittest.TestCase):

    def test_factorial(self):
        _, execution = run_file("factorial.auro")
        self.assertTrue(execution.success)
        self.assertEqual(execution.output[4], "5! = 120")
        self.assertEqual(execution.output[-1], "2^10 = 1024")

    def test_fizzbuzz(self):
        _, execution = run_file("fizzbuzz.auro")
        self.assertEqual(execution.output[:5], ["1", "2", "Fizz", "4", "Buzz"])
        self.assertEqual(execution.output[-1], "FizzBuzz")

    def test_primos(self):
        _, execution = run_file("primos.auro")
        self.assertEqual(execution.output,
                         ["2", "3", "5", "7", "11", "13", "17", "19", "23", "29"])

    def test_lectura_con_entrada(self):
        _, execution = run_file("lectura.auro", ["Ana", "aurum"])
        self.assertEqual(execution.output, ["Hola, Ana. Estás programando en Aurum."])


class ErrorsTest(unittest.TestCase):

    def test_error_de_tipos(self):
        compilation, _ = run('func main() -> void { int x = "hola" }')
        self.assertFalse(compilation.success)
        self.assertTrue(any("int" in e for e in compilation.errors))

    def test_variable_no_declarada(self):
        compilation, _ = run('func main() -> void { print("" + y) }')
        self.assertFalse(compilation.success)

    def test_error_de_sintaxis(self):
        compilation, _ = run('func main() -> void { if (true { } }')
        self.assertFalse(compilation.success)


if __name__ == "__main__":
    unittest.main()
