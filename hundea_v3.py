#!/usr/bin/env python3
"""
🎮 HunDea v3 - Multi-Store Free Games Hunter
Wrapper para mantener compatibilidad con el código v2
"""

import sys
from hundea_v2 import main


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrumpido por el usuario\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error fatal: {e}\n")
        sys.exit(1)
