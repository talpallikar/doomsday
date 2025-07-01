
# notebook_utils.py

"""Helper functions for loading and using the Doomsday engine in notebooks."""

from doomsday_engine import parse_decklist, suggest_viable_piles

def load_deck_from_text(deck_text):
    """Parse decklist text into a list of cards."""
    return parse_decklist(deck_text)

def generate_suggestions(deck_text, constraints, opponent_disruption, top_n=10):
    """Return a pandas DataFrame of suggested piles."""
    import pandas as pd
    deck = load_deck_from_text(deck_text)
    suggestions = suggest_viable_piles(deck, constraints, opponent_disruption, top_n)
    return pd.DataFrame(suggestions)
