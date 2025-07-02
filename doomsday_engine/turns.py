
"""
turns.py

Calculate turns required to resolve a Doomsday pile.
"""
from typing import List, Tuple
from .config import ORACLE, DRAW_COUNTS, DRAW_SPELLS, TURN_SPELLS

def turns_to_win(pile: Tuple[str, ...], initial_hand: List[str] = None) -> int:
    """
    Calculate the minimum number of real turns required to draw through the pile
    and cast Thassa's Oracle, accounting for multi-draw spells, initial hand draws,
    and extra turns from Time Walk.
    """
    if initial_hand is None:
        initial_hand = []
    # Pre-draw from hand
    idx = 0
    for card in initial_hand:
        draw_count = DRAW_COUNTS.get(card, 1 if card in DRAW_SPELLS else 0)
        idx += draw_count
        if idx >= len(pile):
            return 0
    # Simulate turn-by-turn drawing
    turns = 0
    n = len(pile)
    while idx < n:
        turns += 1
        card = pile[idx]
        idx += 1
        draw_count = DRAW_COUNTS.get(card, 1)
        extra = draw_count - 1
        idx += extra if idx + extra <= n else (n - idx)
        if ORACLE in pile[:idx]:
            break
    # Subtract extra turns from Time Walk
    time_walk_count = sum(1 for card in pile if card in TURN_SPELLS)
    turns = max(0, turns - time_walk_count)
    return turns
