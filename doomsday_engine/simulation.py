"""
simulation.py

Deterministic simulation of Doomsday piles against opponent interaction,
with full mana cost and mana production accounting.
Includes detailed step-by-step simulation for drill-down.
Supports initial mana pool and extra land drops.
"""

from typing import List, Tuple, Dict, Any
from .config import ORACLE, DRAW_SPELLS, TURN_SPELLS, MANA_PRODUCE, MANA_COSTS

# --- Hate‐check helpers ---
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
    initial_hand: List[str] = None,
    initial_pool: Dict[str, int] = None,
    land_drops: int = 0
) -> Tuple[str, int]:
    """
    Simulate resolving the given play_pattern against enabled opponent disruptions.
    Accounts for:
      - starting hand (initial_hand),
      - starting mana in pool (initial_pool),
      - extra land drops (land_drops),
      - mana production (MANA_PRODUCE),
      - mana costs (MANA_COSTS),
      - Force of Will alternate cost.

    Returns (outcome, storm_count):
      - outcome: "win", "insufficient_mana_for_<card>", or hate_key
      - storm_count: number of spells cast when outcome occurred
    """
    # --- Initialize hand and mana pool ---
    if initial_hand is None:
        initial_hand = []
    if initial_pool:
        pool = initial_pool.copy()
    else:
        pool = {"U": 0, "B": 0, "C": 0}
    # add generic mana from land drops
    if land_drops:
        pool["C"] = pool.get("C", 0) + land_drops

    storm_count = 0

    for card in play_pattern:
        # 1) Mana production step
        if card in MANA_PRODUCE:
            for color, amt in MANA_PRODUCE[card].items():
                pool[color] = pool.get(color, 0) + amt
            continue

        # 2) Pay mana cost (skip cost for Force of Will)
        if card != "Force of Will":
            cost = MANA_COSTS.get(card, {})
            for color, amt in cost.items():
                if pool.get(color, 0) < amt:
                    # Can't pay for this spell
                    return f"insufficient_mana_for_{card}", storm_count
            for color, amt in cost.items():
                pool[color] -= amt

        # 3) Spell cast: increment storm_count for instants/sorceries, Doomsday, Oracle, FoW
        if card in DRAW_SPELLS or card in TURN_SPELLS or card in {"Doomsday", ORACLE, "Force of Will"}:
            storm_count += 1

        # 4) Opponent hate checks
        for hate_key, counter_func in HATE_CHECKS.items():
            if opponent_disruption.get(hate_key, False):
                if counter_func(card, storm_count):
                    return hate_key, storm_count

        # 5) Oracle resolves => win
        if card == ORACLE:
            return "win", storm_count

    # If we never cast Oracle
    return "no_oracle", storm_count


def simulate_detailed_pile(
    play_pattern: List[str],
    opponent_disruption: Dict[str, bool],
    initial_hand: List[str] = None,
    initial_pool: Dict[str, int] = None,
    land_drops: int = 0
) -> List[Dict[str, Any]]:
    """
    Step-by-step simulation with:
      - mana pool before/after,
      - storm count before/after,
      - spell type (mana_production, cast_spell, failed_cast),
      - vulnerabilities and outcome.

    Supports the same initial_hand, initial_pool, land_drops parameters.
    """
    if initial_hand is None:
        initial_hand = []
    if initial_pool:
        pool = initial_pool.copy()
    else:
        pool = {"U": 0, "B": 0, "C": 0}
    if land_drops:
        pool["C"] = pool.get("C", 0) + land_drops

    storm_count = 0
    steps: List[Dict[str, Any]] = []

    for idx, card in enumerate(play_pattern, start=1):
        step: Dict[str, Any] = {
            "step": idx,
            "card": card,
            "pool_before": pool.copy(),
            "storm_before": storm_count,
            "type": None,
            "vulnerable_to": [],
            "outcome": None
        }

        # Mana production
        if card in MANA_PRODUCE:
            step["type"] = "mana_production"
            for color, amt in MANA_PRODUCE[card].items():
                pool[color] = pool.get(color, 0) + amt

        else:
            # Pay cost
            if card != "Force of Will":
                cost = MANA_COSTS.get(card, {})
                for color, amt in cost.items():
                    if pool.get(color, 0) < amt:
                        step["type"] = "failed_cast"
                        step["outcome"] = f"insufficient_mana_for_{card}"
                        break
                else:
                    for color, amt in cost.items():
                        pool[color] -= amt
                    step["type"] = "cast_spell"
            else:
                step["type"] = "cast_spell"

            # Increment storm if it was a spell
            if step["type"] == "cast_spell":
                if card in DRAW_SPELLS or card in TURN_SPELLS or card in {"Doomsday", ORACLE, "Force of Will"}:
                    storm_count += 1
                # Check hate
                for hate_key, counter_func in HATE_CHECKS.items():
                    if opponent_disruption.get(hate_key, False) and counter_func(card, storm_count):
                        step["vulnerable_to"].append(hate_key)
                        step["outcome"] = hate_key
                # Oracle win
                if card == ORACLE and step["outcome"] is None:
                    step["outcome"] = "win"

        step["pool_after"] = pool.copy()
        step["storm_after"] = storm_count
        steps.append(step)

        # Stop early if we have an outcome on a non-mana step
        if step["outcome"] and step["type"] != "mana_production":
            break

    return steps