"""
suggester.py

Suggest viable Doomsday piles based on constraints and opponent profile.
"""
import itertools
from typing import List, Tuple, Dict, Any
from .parser import parse_decklist
from .config import DRAW_SPELLS, MANA_SOURCES, ORACLE
from .vulnerabilities import (
    vulnerable_to_force, vulnerable_to_fluster, vulnerable_to_surgical,
    vulnerable_to_mindbreak, vulnerable_to_dress_down,
    vulnerable_to_consign, vulnerable_to_orcish, vulnerable_to_pyroblast
)
from .turns import turns_to_win

def suggest_viable_piles(
    deck: List[str],
    constraints: Dict[str, Any],
    opponent_disruption: Dict[str, bool],
    initial_hand: List[str] = None,
    top_n: int = 20
) -> List[Dict[str, Any]]:
    unique_cards = list(set(deck))
    suggestions = []

    for pile in itertools.combinations(unique_cards, 5):
        pile_set = set(pile)
        if constraints.get("must_include_oracle", True) and ORACLE not in pile_set:
            continue
        if constraints.get("must_include_draw", True) and not (pile_set & DRAW_SPELLS):
            continue
        if len(pile_set & MANA_SOURCES) < constraints.get("min_mana_sources", 1):
            continue
        life_loss_cards = pile_set & {"Street Wraith", "Gitaxian Probe"}
        if len(life_loss_cards) * 2 > constraints.get("max_life_loss", 20):
            continue

        vulns = []
        od = opponent_disruption
        if od.get("has_force_of_will") and vulnerable_to_force(pile):
            vulns.append("Force of Will")
        if od.get("has_flusterstorm") and vulnerable_to_fluster(pile):
            vulns.append("Flusterstorm")
        if od.get("has_surgical_extraction") and vulnerable_to_surgical(pile):
            vulns.append("Surgical Extraction")
        if od.get("has_mindbreak_trap") and vulnerable_to_mindbreak(pile):
            vulns.append("Mindbreak Trap")
        if od.get("has_dress_down") and vulnerable_to_dress_down(pile):
            vulns.append("Dress Down")
        if od.get("has_consign_to_memory") and vulnerable_to_consign(pile):
            vulns.append("Consign to Memory")
        if od.get("has_orcish_bowmasters") and vulnerable_to_orcish(pile):
            vulns.append("Orcish Bowmasters")
        if od.get("has_pyroblast") and vulnerable_to_pyroblast(pile):
            vulns.append("Pyroblast")

        ordered = sorted(pile, key=lambda c: (
            0 if c in MANA_SOURCES else
            1 if c in DRAW_SPELLS else
            2 if c == ORACLE else
            3
        ))
        play_pattern = " → ".join(ordered)
        turns = turns_to_win(ordered, initial_hand)

        suggestions.append({
            "pile": pile,
            "vulnerabilities": vulns or ["None"],
            "play_pattern": play_pattern,
            "turns_to_win": turns
        })

    suggestions.sort(key=lambda x: (len(x["vulnerabilities"]), x["turns_to_win"]))
    return suggestions[:top_n]