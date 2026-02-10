"""
🎮 Console Hunters Package
──────────────────────────

Professional console game deal hunters.
"""

from .base_console_hunter import BaseConsoleHunter, ConsoleDeal
from .playstation_hunter import PlayStationHunter
from .xbox_hunter import XboxHunter
from .nintendo_hunter import NintendoHunter

__all__ = [
    'BaseConsoleHunter',
    'ConsoleDeal',
    'PlayStationHunter',
    'XboxHunter',
    'NintendoHunter'
]
