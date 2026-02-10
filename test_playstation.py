"""
🎮 Test PlayStation Hunter - Quick Test
────────────────────────────────────────

Quick test for PlayStation hunter with PlatPrices API.

Author: HunDeaBot Team
"""

import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

# Import hunter
from modules.consoles.playstation_hunter_api import test_playstation

if __name__ == "__main__":
    test_playstation()
