
"""
simulation.py

Deterministic simulation of Doomsday piles against opponent interaction.
"""

from typing import List, Tuple, Dict
from .config import ORACLE, DRAW_SPELLS, TURN_SPELLS
from .config import MANA_COSTS
from .config import MANA_PRODUCE, MANA_COSTS

def _can_counter_fow(card: str, storm_count: int) -> bool:
    return card in DRAW_SPELLS or card == ORACLE or card in TURN_SPELLS or card == "Doomsday"

def _can_counter_pyroblast(card: str, storm_count: int) -> bool:
    return card in DRAW_SPELLS or card == ORACLE or card in TURN_SPELLS or card == "Doomsday"

def _can_counter_fluster(card: str, storm_count: int) -> bool:
    return storm_count > 1 and (card in DRAW_SPELLS or card == ORACLE or card in TURN_SPELLS or card == "Doomsday")

def _can_counter_mindbreak(card: str, storm_count: int) -> bool:
    return storm_count >= 1 and (card in DRAW_SPELLS or card == ORACLE or card in TURN_SPELLS or card == "Doomsday")

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
    if initial_hand is None:
        initial_hand = []
    # Initialize mana pool from MANA_PRODUCE
    pool: Dict[str,int] = {"U":0, "B":0, "C":0}

    storm_count = 0
    for card in play_pattern:
    # 1) If it’s a mana source, add its production to the pool
    if card in MANA_PRODUCE:
        for color, amt in MANA_PRODUCE[card].items():
            pool[color] = pool.get(color, 0) + amt
        # pay no storm or cast steps for lands, but you may want to count them as spells if desired
        continue

    # 2) Otherwise it's a spell—check cost
    cost = MANA_COSTS.get(card, {})
    for color, amt in cost.items():
        if pool.get(color, 0) < amt:
            return f"insufficient_mana_for_{card}", storm_count
    # subtract the cost
    for color, amt in cost.items():
        pool[color] -= amt

    # 3) Now proceed with storm_count, hate checks, oracle win...
    if card in DRAW_SPELLS or card in {"Doomsday", ORACLE}:
        storm_count += 1

        for hate_key, counter_func in HATE_CHECKS.items():
            if not opponent_disruption.get(hate_key, False):
                continue
            if counter_func(card, storm_count):
                return hate_key, storm_count

        if card == ORACLE:
            return "win", storm_count

    return "no_oracle", storm_count
