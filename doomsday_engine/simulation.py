
"""
simulation.py

Deterministic simulation of Doomsday piles against opponent interaction.
"""

from typing import List, Tuple, Dict
from .config import ORACLE, DRAW_SPELLS, MANA_SOURCES

def _can_counter_fow(card: str, storm_count: int) -> bool:
    """Force of Will can counter any nonzero mana cost spell (placeholder: any instant/sorcery or Oracle)."""
    return card in DRAW_SPELLS or card == ORACLE or card == "Doomsday"

def _can_counter_pyroblast(card: str, storm_count: int) -> bool:
    """Pyroblast counters blue instants/sorceries or Oracle/Doomsday."""
    return card in DRAW_SPELLS or card == ORACLE or card == "Doomsday"

def _can_counter_fluster(pile_card: str, storm_count: int) -> bool:
    """
    Flusterstorm requires at least one spell on the stack (storm_count > 1).
    It counters only instant/sorcery spells.
    """
    return storm_count > 1 and (pile_card in DRAW_SPELLS or pile_card == ORACLE or pile_card == "Doomsday")

def _can_counter_mindbreak(pile_card: str, storm_count: int) -> bool:
    """
    Mindbreak Trap X where X = storm_count can counter X spells on the stack.
    We assume it can counter the key target if storm_count >= 1.
    """
    return storm_count >= 1 and (pile_card in DRAW_SPELLS or pile_card == ORACLE or pile_card == "Doomsday")

def _can_counter_dress_down(card: str, storm_count: int) -> bool:
    """Dress Down can target Oracle on the battlefield to temporarily remove abilities."""
    return card == ORACLE

# Mapping of hate card to its counter function
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
    Returns a tuple of (outcome, storm_count):
      - outcome: "win" if Oracle resolves, otherwise the key of the hate that stopped you.
      - storm_count: number of spells cast when the outcome occurred.
    """
    if initial_hand is None:
        initial_hand = []

    storm_count = 0

    # Cast sequence: iterate through each card in play_pattern
    for card in play_pattern:
        # Increment storm count for each instant/sorcery or Doomsday/Oracle
        if card in DRAW_SPELLS or card in {"Doomsday", ORACLE}:
            storm_count += 1

        # Check each enabled hate card
        for hate_key, counter_func in HATE_CHECKS.items():
            if not opponent_disruption.get(hate_key, False):
                continue
            if counter_func(card, storm_count):
                # Return the hate_key (e.g., "has_force_of_will") as the cause
                return hate_key, storm_count

        # If this was the Oracle, and it's not countered, you win
        if card == ORACLE:
            return "win", storm_count

    # If we never cast Oracle
    return "no_oracle", storm_count
