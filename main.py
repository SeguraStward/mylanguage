#!/usr/bin/env python3
"""
Aurum IDE - Punto de entrada principal
"""

import sys
import os

from src.ide import AurumIDE


def main():
    """Función principal"""
    try:
        ide = AurumIDE()
        ide.run()
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
