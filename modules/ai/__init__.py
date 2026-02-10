"""
🧠 AI Modules for HunDeaBot
────────────────────────────

Triple AI Validation System:
- Level 1: SmartDealValidator (Pattern Detection)
- Level 2: AutonomousDealResearcher (Multi-Source API)
- Level 3: WebPoweredInvestigator (Web Intelligence)

Usage:
    from modules.ai import SmartDealValidator
    from modules.ai import AutonomousDealResearcher
    from modules.ai import WebPoweredInvestigator
"""

from .smart_deal_validator import SmartDealValidator
from .autonomous_researcher import AutonomousDealResearcher
from .web_investigator import WebPoweredInvestigator

__all__ = [
    'SmartDealValidator',
    'AutonomousDealResearcher',
    'WebPoweredInvestigator'
]

__version__ = '3.0.0'
