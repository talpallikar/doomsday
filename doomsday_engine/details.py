# doomsday_engine/details.py

from typing import List, Dict, Any
import pandas as pd
from .simulation import simulate_detailed_pile

def generate_pile_details(
    play_pattern: List[str],
    opponent_disruption: Dict[str, bool],
    initial_hand: List[str] = None,
    initial_pool: Dict[str, int] = None,
    land_drops: int = 0
) -> pd.DataFrame:
    """
    Runs simulate_detailed_pile(...) then returns a human-friendly DataFrame.

    Args:
      play_pattern: ordered list of cards in the pile
      opponent_disruption: which hate cards are active
      initial_hand: cards you start with (for draw effects)
      initial_pool: starting mana pool, e.g. {"U":1,"B":2,"C":0}
      land_drops: extra generic mana from land drops

    Returns:
      DataFrame with columns:
        - step, card, type, pool_before, pool_after,
        - storm_before, storm_after, vulnerable_to, outcome
    """
    # Pass all parameters through to the detailed simulator
    steps = simulate_detailed_pile(
        play_pattern,
        opponent_disruption,
        initial_hand,
        initial_pool,
        land_drops
    )

    df = pd.DataFrame(steps)

    # Format pool dicts into strings for readability
    df['pool_before'] = df['pool_before'].apply(
        lambda d: ', '.join(f"{k}:{v}" for k, v in d.items())
    )
    df['pool_after'] = df['pool_after'].apply(
        lambda d: ', '.join(f"{k}:{v}" for k, v in d.items())
    )
    return df