''' 
Deterministic simulation of Doomsday piles against opponent interaction,
with full mana cost and mana production accounting.
Includes detailed step-by-step simulation for drill-down.
'''

from typing import List, Tuple, Dict, Any
from .config import ORACLE, DRAW_SPELLS, TURN_SPELLS, MANA_PRODUCE, MANA_COSTS

# Hate checks
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

    pool: Dict[str, int] = {"U": 0, "B": 0, "C": 0}
    storm_count = 0

    for card in play_pattern:
        # Mana production
        if card in MANA_PRODUCE:
            for color, amt in MANA_PRODUCE[card].items():
                pool[color] = pool.get(color, 0) + amt
            continue

        # Pay mana cost (skip for Force of Will)
        if card != "Force of Will":
            cost = MANA_COSTS.get(card, {})
            for color, amt in cost.items():
                if pool.get(color, 0) < amt:
                    return f"insufficient_mana_for_{card}", storm_count
            for color, amt in cost.items():
                pool[color] -= amt

        # Spell cast: increment storm_count
        if card in DRAW_SPELLS or card in TURN_SPELLS or card in {"Doomsday", ORACLE, "Force of Will"}:
            storm_count += 1

        # Opponent hate checks
        for hate_key, counter in HATE_CHECKS.items():
            if opponent_disruption.get(hate_key, False) and counter(card, storm_count):
                return hate_key, storm_count

        # Oracle resolves
        if card == ORACLE:
            return "win", storm_count

    return "no_oracle", storm_count

def simulate_detailed_pile(
    play_pattern: List[str],
    opponent_disruption: Dict[str, bool],
    initial_hand: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Step-by-step simulation with mana pool, storm count, and vulnerabilities.
    Returns a list of step dicts for drill-down.
    """
    if initial_hand is None:
        initial_hand = []

    pool: Dict[str, int] = {"U":0, "B":0, "C":0}
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
            # Increment storm_count if spell
            if step["type"] == "cast_spell":
                if card in DRAW_SPELLS or card in TURN_SPELLS or card in {"Doomsday", ORACLE, "Force of Will"}:
                    storm_count += 1
                # Hate checks
                for hate_key, counter in HATE_CHECKS.items():
                    if opponent_disruption.get(hate_key, False) and counter(card, storm_count):
                        step["vulnerable_to"].append(hate_key)
                        step["outcome"] = hate_key
                # Oracle win
                if card == ORACLE and step["outcome"] is None:
                    step["outcome"] = "win"
        step["pool_after"] = pool.copy()
        step["storm_after"] = storm_count
        steps.append(step)
        # Stop if outcome
        if step["outcome"] is not None and step["type"] != "mana_production":
            break

    return steps
