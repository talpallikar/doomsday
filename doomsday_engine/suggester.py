"""
suggester.py

Generate Doomsday piles with detailed debug metrics when requested.
"""

import itertools
from typing import List, Dict, Any
from .parser import parse_decklist
from .config import DRAW_SPELLS, MANA_SOURCES, ORACLE, PROTECTION_SPELLS, TURN_SPELLS
from .turns import turns_to_win
from .simulation import simulate_pile, simulate_detailed_pile

def suggest_viable_piles(
    deck: List[str],
    constraints: Dict[str, Any],
    opponent_disruption: Dict[str, bool],
    initial_hand: List[str] = None,
    initial_pool: Dict[str, int] = None,
    land_drops: int = 0,
    top_n: int = 20,
    debug: bool = False
) -> List[Dict[str, Any]]:
    """
    Generate Doomsday piles, with optional debug output.

    If debug=True, returns ALL candidate piles with extra fields:
      - leftover_pool: dict of mana left after simulation
      - failure_spell: the card at which it failed (or None for wins)
    Otherwise, returns only the top_n piles sorted by win/outcome and turns_to_win.
    """
    if initial_hand is None:
        initial_hand = []
    if initial_pool is None:
        initial_pool = {}

    unique_cards = list(set(deck))
    suggestions: List[Dict[str, Any]] = []

    for pile in itertools.combinations(unique_cards, 5):
        s = set(pile)

        # Basic constraints:
        if constraints.get("must_include_oracle", True) and ORACLE not in s:
            continue
        if constraints.get("must_include_draw", True) and not (s & DRAW_SPELLS):
            continue
        if len(s & MANA_SOURCES) < constraints.get("min_mana_sources", 1):
            continue
        life_loss = len(s & {"Gitaxian Probe", "Street Wraith"}) * 2
        if life_loss > constraints.get("max_life_loss", 20):
            continue

        # Build the play pattern
        mana         = sorted([c for c in pile if c in MANA_SOURCES])
        turn_spells  = sorted([c for c in pile if c in TURN_SPELLS])
        protections  = sorted([c for c in pile if c in PROTECTION_SPELLS])
        draw_spells  = sorted([c for c in pile if c in DRAW_SPELLS])
        play_pattern = mana + turn_spells + ["Doomsday"] + protections + draw_spells + [ORACLE]

        # Estimate turns to win
        turns = turns_to_win(tuple(play_pattern), initial_hand)

        # Simulate (summary or detailed)
        if debug:
            steps = simulate_detailed_pile(
                play_pattern,
                opponent_disruption,
                initial_hand,
                initial_pool,
                land_drops
            )
            last = steps[-1]
            outcome       = last.get("outcome", "no_oracle")
            storm_count   = last.get("storm_after", 0)
            leftover_pool = last.get("pool_after", {}).copy()
            failure_spell = last.get("card") if outcome != "win" else None
        else:
            outcome, storm_count = simulate_pile(
                play_pattern,
                opponent_disruption,
                initial_hand,
                initial_pool,
                land_drops
            )
            leftover_pool = {}
            failure_spell = None

        entry: Dict[str, Any] = {
            "pile": pile,
            "play_pattern": play_pattern,
            "turns_to_win": turns,
            "outcome": outcome,
            "storm_count": storm_count,
        }
        if debug:
            entry["leftover_pool"] = leftover_pool
            entry["failure_spell"] = failure_spell

        suggestions.append(entry)

    # If not debugging, sort and truncate
    if not debug:
        suggestions.sort(key=lambda x: (x["outcome"] != "win", x["turns_to_win"]))
        return suggestions[:top_n]

    return suggestions