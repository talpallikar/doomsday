"""
turns.py

Calculate turns required to resolve a Doomsday pile.
"""
from typing import List, Tuple
from .config import ORACLE, DRAW_COUNTS, DRAW_SPELLS

def turns_to_win(pile: Tuple[str, ...], initial_hand: List[str] = None) -> int:
    """
    Calculate the minimum number of turns required to draw through
    the pile and cast Thassa's Oracle, accounting for multi-draw
    spells and initial hand.
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
    # Simulate turns
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
    return turns