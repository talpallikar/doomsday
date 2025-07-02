
"""
suggester.py

Suggest viable Doomsday piles with deterministic simulation against opponent hate.
"""

import itertools
from typing import List, Tuple, Dict, Any
from .parser import parse_decklist
from .config import DRAW_SPELLS, MANA_SOURCES, ORACLE, PROTECTION_SPELLS, TURN_SPELLS
from .vulnerabilities import (
    vulnerable_to_force, vulnerable_to_fluster, vulnerable_to_surgical,
    vulnerable_to_mindbreak, vulnerable_to_dress_down,
    vulnerable_to_consign, vulnerable_to_orcish, vulnerable_to_pyroblast
)
from .turns import turns_to_win
from .simulation import simulate_pile

def suggest_viable_piles(
    deck: List[str],
    constraints: Dict[str, Any],
    opponent_disruption: Dict[str, bool],
    initial_hand: List[str] = None,
    top_n: int = 20
) -> List[Dict[str, Any]]:
    """
    Return up to top_n suggested piles with metadata:
      - 'pile': tuple of 5 card names
      - 'play_pattern': list of spells cast in order
      - 'turns_to_win': int
      - 'outcome': 'win' or hate key that stopped the pile
      - 'storm_count': number of spells cast when outcome occurred
      - 'risk_score': int (# vulnerabilities minus protections)
      - 'vulnerabilities': list of hate keys the pile is vulnerable to
      - 'protection_count': int
    """
    if initial_hand is None:
        initial_hand = []

    unique_cards = list(set(deck))
    suggestions = []

    for pile in itertools.combinations(unique_cards, 5):
        pile_set = set(pile)

        # Basic constraints
        if constraints.get("must_include_oracle", True) and ORACLE not in pile_set:
            continue
        if constraints.get("must_include_draw", True) and not (pile_set & DRAW_SPELLS):
            continue
        if len(pile_set & MANA_SOURCES) < constraints.get("min_mana_sources", 1):
            continue
        life_loss = len(pile_set & {"Street Wraith", "Gitaxian Probe"}) * 2
        if life_loss > constraints.get("max_life_loss", 20):
            continue

        # Identify vulnerabilities
        vulns = []
        od = opponent_disruption
        if od.get("has_force_of_will") and vulnerable_to_force(pile):
            vulns.append("has_force_of_will")
        if od.get("has_flusterstorm") and vulnerable_to_fluster(pile):
            vulns.append("has_flusterstorm")
        if od.get("has_surgical_extraction") and vulnerable_to_surgical(pile):
            vulns.append("has_surgical_extraction")
        if od.get("has_mindbreak_trap") and vulnerable_to_mindbreak(pile):
            vulns.append("has_mindbreak_trap")
        if od.get("has_dress_down") and vulnerable_to_dress_down(pile):
            vulns.append("has_dress_down")
        if od.get("has_consign_to_memory") and vulnerable_to_consign(pile):
            vulns.append("has_consign_to_memory")
        if od.get("has_orcish_bowmasters") and vulnerable_to_orcish(pile):
            vulns.append("has_orcish_bowmasters")
        if od.get("has_pyroblast") and vulnerable_to_pyroblast(pile):
            vulns.append("has_pyroblast")

        # Protection count and risk score
        protection_count = len(pile_set & PROTECTION_SPELLS)
        risk_score = max(0, len(vulns) - protection_count)

        # Build play pattern: protections -> mana -> turn spells -> Doomsday -> draws -> Oracle
        protections = [c for c in pile if c in PROTECTION_SPELLS]
        mana = [c for c in pile if c in MANA_SOURCES and c not in protections]
        turn_spells = [c for c in pile if c in TURN_SPELLS]
        draw_spells = [c for c in pile if c in DRAW_SPELLS and c not in protections]
        play_pattern = protections + mana + turn_spells + ["Doomsday"] + draw_spells + [ORACLE]

        # Calculate turns to win
        turns = turns_to_win(tuple(play_pattern), initial_hand)

        # Simulate against hate
        outcome, storm_count = simulate_pile(play_pattern, opponent_disruption, initial_hand)

        suggestions.append({
            "pile": pile,
            "play_pattern": play_pattern,
            "turns_to_win": turns,
            "outcome": outcome,
            "storm_count": storm_count,
            "risk_score": risk_score,
            "vulnerabilities": vulns or ["None"],
            "protection_count": protection_count
        })

    # Sort by risk_score, then turns_to_win
    suggestions.sort(key=lambda x: (x["risk_score"], x["turns_to_win"]))
    return suggestions[:top_n]
