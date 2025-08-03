#!/usr/bin/env python3
"""
AuroLang IDE - Punto de entrada principal
"""

import sys
import os

from src.ide import AuroLangIDE


def main():
    """Función principal"""
    try:
        ide = AuroLangIDE()
        ide.run()
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
