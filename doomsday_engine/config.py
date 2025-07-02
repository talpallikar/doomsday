
"""
Configuration module for Doomsday engine.
Loads card lists and draw counts from config.json.
"""

import json
from pathlib import Path
from .scryfall_cache import get_mana_cost
from .parser import parse_decklist

# Building the cache of mana costs for all cards in the decks directory.
# 1. Point to your decks directory (adjust the path if needed)
DECKS_DIR = Path(__file__).parent.parent / "decks"

# 2. Gather every card name from each decklist .txt
ALL_CARDS = set()
for deck_file in DECKS_DIR.glob("*.txt"):
    text = deck_file.read_text(encoding="utf-8")
    hand = parse_decklist(text)
    ALL_CARDS.update(hand)

# 3. (Optionally) Add any other key cards you want to include
# ALL_CARDS |= {"Doomsday", "Thassa's Oracle", "Time Walk", ...}

# 4. Build the mana-cost lookup via your flat-JSON cache
MANA_COSTS: Dict[str, Dict[str,int]] = {
    card: get_mana_cost(card)
    for card in sorted(ALL_CARDS)
}

CONFIG_PATH = Path(__file__).parent / "config.json"

with open(CONFIG_PATH) as f:
    _cfg = json.load(f)

ORACLE = _cfg["oracle"]
DRAW_SPELLS = set(_cfg["draw_spells"])

# Derive the set of mana‐source cards from the mana_produce mapping
MANA_PRODUCE = _cfg.get("mana_produce", {})
MANA_SOURCES = set(MANA_PRODUCE.keys())

TUTORS = set(_cfg["tutors"])
DRAW_COUNTS = _cfg["draw_counts"]
PROTECTION_SPELLS = set(_cfg["protection_spells"])
TURN_SPELLS = set(_cfg.get("turn_spells", []))
