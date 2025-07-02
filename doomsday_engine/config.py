import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"

with open(CONFIG_PATH) as f:
    cfg = json.load(f)

ORACLE = cfg["oracle"]
DRAW_SPELLS = set(cfg["draw_spells"])
MANA_SOURCES = set(cfg["mana_sources"])
TUTORS = set(cfg["tutors"])
DRAW_COUNTS = cfg["draw_counts"]
PROTECTION_SPELLS = set(cfg["protection_spells"])
