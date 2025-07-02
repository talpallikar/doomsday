
"""
simulation.py

Deterministic simulation of Doomsday piles against opponent interaction,
with full mana cost and mana production accounting.
Special-case Force of Will as castable via alternate cost.
"""

from typing import List, Tuple, Dict
from .config import ORACLE, DRAW_SPELLS, TURN_SPELLS, MANA_PRODUCE, MANA_COSTS

# Hate checks:
def _can_counter_fow(card: str, storm_count: int) -> bool:
    return card in DRAW_SPELLS or card == ORACLE or card in TURN_SPELLS or card == "Doomsday"

def _can_counter_pyroblast(card: str, storm_count: int) -> bool:
    return card in DRAW_SPELLS or card == ORACLE or card in TURN_SPELLS or card == "Doomsday"

def _can_counter_fluster(card: str, storm_count: int) -> bool:
    return storm_count > 1 and (card in DRAW_SPELLS or card == ORACLE or card == "Doomsday")

def _can_counter_mindbreak(card: str, storm_count: int) -> bool:
    return storm_count >= 1 and (card in DRAW_SPELLS or card == ORACLE or card == "Doomsday")

def _can_counter_dress_down(card: str, storm_count: int) -> bool:
    return card == ORACLE

HATE_CHECKS = {
    "has_force_of_will": _can_counter_fow,
    "has_pyroblast":    _can_counter_pyroblast,
    "has_flusterstorm": _can_counter_fluster,
    "has_mindbreak_trap": _can_counter_mindbreak,
    "has_dress_down":   _can_counter_dress_down
}

def simulate_pile(
    play_pattern: List[str],
    opponent_disruption: Dict[str, bool],
    initial_hand: List[str] = None
) -> Tuple[str, int]:
    """
    Simulate resolving the given play pattern against enabled opponent disruptions.
    Accounts for mana production (MANA_PRODUCE) and mana costs (MANA_COSTS).
    Force of Will is treated as castable via its alternate cost.
    Returns (outcome, storm_count):
      - outcome: "win", "insufficient_mana_for_<card>", or hate key
      - storm_count: spells cast when outcome occurred
    """
    if initial_hand is None:
        initial_hand = []

    # Initialize mana pool
    pool: Dict[str, int] = {"U": 0, "B": 0, "C": 0}
    storm_count = 0

    for card in play_pattern:
        # 1) Mana production
        if card in MANA_PRODUCE:
            for color, amt in MANA_PRODUCE[card].items():
                pool[color] = pool.get(color, 0) + amt
            continue

        # 2) Pay mana cost (Force of Will has alternate cost)
        if card != "Force of Will":
            cost = MANA_COSTS.get(card, {})
            for color, amt in cost.items():
                if pool.get(color, 0) < amt:
                    return f"insufficient_mana_for_{card}", storm_count
            for color, amt in cost.items():
                pool[color] -= amt
        # else: skip cost for Force of Will

        # 3) Spell cast: storm count
        if card in DRAW_SPELLS or card in TURN_SPELLS or card in {"Doomsday", ORACLE, "Force of Will"}:
            storm_count += 1

        # 4) Opponent hate checks
        for hate_key, counter_func in HATE_CHECKS.items():
            if opponent_disruption.get(hate_key, False):
                if counter_func(card, storm_count):
                    return hate_key, storm_count

        # 5) Oracle resolves
        if card == ORACLE:
            return "win", storm_count

    return "no_oracle", storm_count
