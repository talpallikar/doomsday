"""
parser.py

Parses raw decklist text into a list of card names.
"""
import re
from typing import List

def parse_decklist(deck_str: str) -> List[str]:
    """
    Convert raw decklist text into a flat list of card names, stripping
    out set-codes and collector numbers.
    """
    deck = []
    for raw_line in deck_str.strip().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^(\d+)\s+(.+)$", line)
        if not m:
            continue
        count = int(m.group(1))
        name_part = m.group(2)
        # Strip parenthetical set codes
        name_part = re.sub(r"\s*\([^)]*\)", "", name_part)
        # Strip trailing numbers
        name_part = re.sub(r"\s+\d+$", "", name_part)
        card_name = name_part.strip()
        deck.extend([card_name] * count)
    return deck