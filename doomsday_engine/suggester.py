"""
suggester.py

Suggest viable Doomsday piles with deterministic simulation against opponent disruption,
taking into account a starting mana pool and extra land drops.
"""

import itertools
from typing import List, Dict, Any
from .parser import parse_decklist
from .config import DRAW_SPELLS, MANA_SOURCES, ORACLE, PROTECTION_SPELLS, TURN_SPELLS
from .turns import turns_to_win
from .simulation import simulate_pile

def suggest_viable_piles(
    deck: List[str],
    constraints: Dict[str, Any],
    opponent_disruption: Dict[str, bool],
    initial_hand: List[str] = None,
    initial_pool: Dict[str, int] = None,
    land_drops: int = 0,
    top_n: int = 20
) -> List[Dict[str, Any]]:
    """
    Generate up to `top_n` Doomsday piles with metadata, simulating against the given
    opponent disruption and accounting for starting hand, starting mana pool, and
    extra land drops.

    Args:
      deck: list of all cards in your deck
      constraints: {
        must_include_oracle: bool,
        must_include_draw: bool,
        min_mana_sources: int,
        max_life_loss: int
      }
      opponent_disruption: e.g. {
        has_force_of_will: bool, has_flusterstorm: bool, ...
      }
      initial_hand: cards you begin the turn with
      initial_pool: starting mana pool, e.g. {"U":1,"B":2,"C":0}
      land_drops: extra generic mana from land drops this turn
      top_n: how many top piles to return

    Returns:
      A list of dicts, each with keys:
        - pile: tuple of 5 card names
        - play_pattern: ordered list of spells cast
        - turns_to_win: estimated turns needed
        - outcome: "win" or name of hate that stops you or "insufficient_mana_for_<card>"
        - storm_count: number of spells cast when outcome occurred
    """
    if initial_hand is None:
        initial_hand = []
    if initial_pool is None:
        initial_pool = {}

    unique_cards = list(set(deck))
    suggestions: List[Dict[str, Any]] = []

    for pile in itertools.combinations(unique_cards, 5):
        s = set(pile)

        # Basic constraints filter
        if constraints.get("must_include_oracle", True) and ORACLE not in s:
            continue
        if constraints.get("must_include_draw", True) and not (s & DRAW_SPELLS):
            continue
        if len(s & MANA_SOURCES) < constraints.get("min_mana_sources", 1):
            continue
        life_loss = len(s & {"Gitaxian Probe", "Street Wraith"}) * 2
        if life_loss > constraints.get("max_life_loss", 20):
            continue

        # Build a logical play pattern:
        # 1) Mana sources
        mana = sorted([c for c in pile if c in MANA_SOURCES])
        # 2) Extra-turn spells
        turn_spells = sorted([c for c in pile if c in TURN_SPELLS])
        # 3) Doomsday itself
        # 4) Protection spells
        protections = sorted([c for c in pile if c in PROTECTION_SPELLS])
        # 5) Draw spells
        draw_spells = sorted([c for c in pile if c in DRAW_SPELLS])
        # 6) Finish with Oracle
        play_pattern = mana + turn_spells + ["Doomsday"] + protections + draw_spells + [ORACLE]

        # Compute number of turns needed
        turns = turns_to_win(tuple(play_pattern), initial_hand)

        # Run deterministic simulation with starting mana pool & land drops
        outcome, storm_count = simulate_pile(
            play_pattern,
            opponent_disruption,
            initial_hand,
            initial_pool,
            land_drops
        )

        suggestions.append({
            "pile": pile,
            "play_pattern": play_pattern,
            "turns_to_win": turns,
            "outcome": outcome,
            "storm_count": storm_count
        })

    # Sort: winning piles first, then by fewest turns
    suggestions.sort(key=lambda x: (x["outcome"] != "win", x["turns_to_win"]))
    return suggestions[:top_n]