"""
notebook_utils.py

Helper functions for using the doomsday_engine package in notebooks.
"""
import pandas as pd
from doomsday_engine import parse_decklist, suggest_viable_piles

def load_deck_from_text(deck_text: str):
    """Parse decklist text into a list of card names."""
    return parse_decklist(deck_text)

def generate_suggestions(
    deck_text: str,
    constraints: dict,
    opponent_disruption: dict,
    initial_hand: list = None,
    top_n: int = 10
) -> pd.DataFrame:
    """Return a DataFrame of suggested piles given inputs."""
    deck = load_deck_from_text(deck_text)
    suggestions = suggest_viable_piles(deck, constraints, opponent_disruption, initial_hand, top_n)
    return pd.DataFrame(suggestions)