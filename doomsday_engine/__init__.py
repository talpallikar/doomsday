"""
Doomsday Engine Package

Modules:
- config
- parser
- vulnerabilities
- turns
- suggester
"""

from .config import (
    ORACLE, DRAW_SPELLS, MANA_SOURCES, TUTORS,
    DRAW_COUNTS, PROTECTION_SPELLS
)
from .parser import parse_decklist
from .vulnerabilities import (
    vulnerable_to_force, vulnerable_to_fluster, vulnerable_to_surgical,
    vulnerable_to_mindbreak, vulnerable_to_dress_down,
    vulnerable_to_consign, vulnerable_to_orcish, vulnerable_to_pyroblast
)
from .turns import turns_to_win
from .suggester import suggest_viable_piles