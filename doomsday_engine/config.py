"""
Configuration module for Doomsday engine.
Loads card lists, draw counts, mana production, and costs from config.json and decks directory.
"""

import json
import time
from pathlib import Path
from typing import Dict
from .scryfall_cache import get_mana_cost
from .parser import parse_decklist

# Load static config
CONFIG_PATH = Path(__file__).parent / "config.json"
with open(CONFIG_PATH) as f:
    _cfg = json.load(f)

ORACLE = _cfg["oracle"]
DRAW_SPELLS = set(_cfg["draw_spells"])
TUTORS = set(_cfg["tutors"])
DRAW_COUNTS = _cfg["draw_counts"]
PROTECTION_SPELLS = set(_cfg["protection_spells"])
TURN_SPELLS = set(_cfg.get("turn_spells", []))
MANA_PRODUCE = _cfg.get("mana_produce", {})

# Derive MANA_SOURCES from the mana_produce mapping
MANA_SOURCES = set(MANA_PRODUCE.keys())

# Build ALL_CARDS from decks/ directory
DECKS_DIR = Path(__file__).parent.parent / "decks"
ALL_CARDS = set()
for deck_file in DECKS_DIR.glob("*.txt"):
    text = deck_file.read_text(encoding="utf-8")
    cards = parse_decklist(text)
    ALL_CARDS.update(cards)

# Optionally include any additional cards
# ALL_CARDS |= {"Doomsday", ORACLE, "Time Walk"}

# Build mana cost lookup using flat-file Scryfall cache
MANA_COSTS: Dict[str, Dict[str, int]] = {}
for card in sorted(ALL_CARDS):
    try:
        MANA_COSTS[card] = get_mana_cost(card)
        # be polite to Scryfall
        time.sleep(0.1)
    except Exception:
        MANA_COSTS[card] = {}