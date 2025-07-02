
"""
notebook_utils.py

Helper functions for using the doomsday_engine package in notebooks.
"""
import pandas as pd
from doomsday_engine import parse_decklist, suggest_viable_piles

def load_deck_from_text(deck_text: str) -> list:
    """
    Parse decklist text into a list of card names.
    """
    return parse_decklist(deck_text)

def generate_suggestions(
    deck_text: str,
    constraints: dict,
    opponent_disruption: dict,
    initial_hand: list = None,
    top_n: int = 10
) -> pd.DataFrame:
    """
    Generate a DataFrame of suggested Doomsday piles with metadata.
    Columns include:
      - 'pile', 'play_pattern', 'turns_to_win', 'outcome',
        'storm_count', 'risk_score', 'vulnerabilities', 'protection_count'
    """
    # Parse the deck list into card names
    deck = load_deck_from_text(deck_text)

    # Get suggestions
    suggestions = suggest_viable_piles(
        deck,
        constraints,
        opponent_disruption,
        initial_hand,
        top_n
    )

    # Convert to DataFrame
    df = pd.DataFrame(suggestions)

    # Make play_pattern display nicely as a string
    if 'play_pattern' in df.columns:
        df['play_pattern'] = df['play_pattern'].apply(lambda seq: ' → '.join(seq))

    # Ensure vulnerabilities is a comma-separated string
    if 'vulnerabilities' in df.columns:
        df['vulnerabilities'] = df['vulnerabilities'].apply(lambda v: ', '.join(v))

    return df
