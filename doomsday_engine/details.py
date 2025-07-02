# doomsday_engine/details.py

from typing import List, Dict, Any
import pandas as pd
from .simulation import simulate_detailed_pile

def generate_pile_details(
    play_pattern: List[str],
    opponent_disruption: Dict[str, bool],
    initial_hand: List[str] = None
) -> pd.DataFrame:
    """
    Runs simulate_detailed_pile(...) then returns a human-friendly DataFrame.
    """
    steps = simulate_detailed_pile(play_pattern, opponent_disruption, initial_hand)
    df = pd.DataFrame(steps)
    df['pool_before'] = df['pool_before'].apply(
        lambda d: ', '.join(f"{k}:{v}" for k,v in d.items())
    )
    df['pool_after'] = df['pool_after'].apply(
        lambda d: ', '.join(f"{k}:{v}" for k,v in d.items())
    )
    return df