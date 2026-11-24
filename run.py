#!/usr/bin/env python3
"""
Ejecuta un programa Aurum desde la terminal, sin abrir el IDE.

Uso:
    python run.py examples/factorial.auro
    python run.py examples/lectura.auro --input 7 Ana
    python run.py examples/factorial.auro --bytecode   # muestra el bytecode generado
"""

import argparse
import sys
from pathlib import Path

from src.compiler import AurumCompiler


def main() -> int:
    parser = argparse.ArgumentParser(description="Compila y ejecuta un programa Aurum.")
    parser.add_argument("archivo", type=Path, help="archivo fuente .auro")
    parser.add_argument("--input", nargs="*", default=[], metavar="VALOR",
                        help="valores que leerá read(), en orden")
    parser.add_argument("--bytecode", action="store_true",
                        help="imprime el bytecode antes de ejecutar")
    args = parser.parse_args()

    source = args.archivo.read_text(encoding="utf-8")
    compiler = AurumCompiler()
    compilation = compiler.compile(source)

    if not compilation.success:
        for error in compilation.errors:
            print(f"error: {error}", file=sys.stderr)
        return 1

    if args.bytecode:
        for i, instruction in enumerate(compilation.instructions):
            print(f"{i:4d}  {instruction}")
        print("-" * 40)

    execution = compiler.execute(compilation, args.input)
    for line in execution.output:
        print(line)

    if not execution.success:
        for error in execution.errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
