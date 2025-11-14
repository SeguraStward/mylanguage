#!/usr/bin/env python3


import sys
import os

from src.ide_simple import AlchemistIDESimple


def main():
    """Función principal - Ejecuta el IDE de Alchemist"""
    try:
        ide = AlchemistIDESimple()
        ide.run()
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
