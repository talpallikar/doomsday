# doomsday_engine/scryfall_cache.py

import os
import json
import time
import re
import requests
from pathlib import Path
from typing import Dict

# --- Configuration ---
CACHE_DIR = Path(__file__).parent / "cache" / "cards"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Time-to-live for each cache file (seconds). 1 week here.
CACHE_TTL = 60 * 60 * 24 * 7  

SCRYFALL_URL = "https://api.scryfall.com/cards/named"

# --- Cache Functions ---

def _cache_path(card_name: str) -> Path:
    # sanitize file name
    safe = card_name.replace(" ", "_").replace("/", "_")
    return CACHE_DIR / f"{safe}.json"

def fetch_card_data(card_name: str) -> Dict:
    """
    Return the JSON data for `card_name` from Scryfall.
    Uses a flat-file cache in CACHE_DIR with TTL = CACHE_TTL.
    """
    path = _cache_path(card_name)
    if path.exists():
        mtime = path.stat().st_mtime
        if time.time() - mtime < CACHE_TTL:
            # load from cache
            return json.loads(path.read_text(encoding="utf-8"))
    # otherwise fetch fresh
    resp = requests.get(SCRYFALL_URL, params={"exact": card_name})
    resp.raise_for_status()
    data = resp.json()
    # write to cache
    path.write_text(json.dumps(data), encoding="utf-8")
    return data

# --- Mana Cost Parsing ---

def parse_mana_cost_string(mana_str: str) -> Dict[str,int]:
    """
    Convert a Scryfall mana_cost string like "{2}{U}{U}{B}" into
    {"C":2, "U":2, "B":1}. Colorless digits map to 'C'.
    """
    symbols = re.findall(r"\{([^}]+)\}", mana_str)
    cost: Dict[str,int] = {}
    for sym in symbols:
        if sym.isdigit():
            cost["C"] = cost.get("C", 0) + int(sym)
        else:
            cost[sym] = cost.get(sym, 0) + 1
    return cost

def get_mana_cost(card_name: str) -> Dict[str,int]:
    """
    Fetch (or cache-fetch) the Scryfall data for `card_name`,
    then parse and return its mana cost dict.
    """
    data = fetch_card_data(card_name)
    mc = data.get("mana_cost", "")
    return parse_mana_cost_string(mc)