
"""doomsday_engine.py

Core functionality for parsing decklists, identifying disruption vulnerabilities,
calculating turns to win (accounting for multi-draw spells and initial hand), 
and suggesting viable Doomsday piles.
"""

from collections import Counter
import itertools

# === Card Tags ===
ORACLE = "Thassa's Oracle"
DRAW_SPELLS = {"Gitaxian Probe", "Street Wraith", "Gush", "Brainstorm", "Ponder", "Preordain", "Ideas Unbound"}
MANA_SOURCES = {"Dark Ritual", "Lotus Petal", "Black Lotus", "Mox Jet", "Mox Sapphire", "Underground Sea", "Island", "Watery Grave"}
TUTORS = {"Demonic Tutor", "Demonic Consultation"}
LOSES_TO_PYRO = {"Brainstorm", "Ponder", "Preordain", "Gitaxian Probe", "Ancestral Recall", "Gush", "Force of Will", "Force of Negation", "Thassa's Oracle"}
PROTECTION_SPELLS = {"Force of Will", "Flusterstorm"}

# === Multi-draw mapping ===
# Number of cards drawn by specific spells
DRAW_COUNTS = {
    "Ancestral Recall": 3,
    "Gush": 2
}

# === Parsing ===
import re

def parse_decklist(deck_str):
    """
    Convert raw decklist text into a flat list of card names, stripping
    out set‐codes in parentheses and trailing collector numbers.
    """
    deck = []
    for raw_line in deck_str.strip().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        # Match count at start, then everything else
        m = re.match(r"^(\d+)\s+(.+)$", line)
        if not m:
            continue
        count = int(m.group(1))
        name_part = m.group(2)
        # Strip any parenthetical set‐codes: "Card Name (2ED)"
        name_part = re.sub(r"\s*\([^)]*\)", "", name_part)
        # Strip any trailing numbers (collector IDs)
        name_part = re.sub(r"\s+\d+$", "", name_part)
        card_name = name_part.strip()
        deck.extend([card_name] * count)
    return deck


# === Vulnerability Detection ===
def vulnerable_to_force(pile):
    return any(card == ORACLE or card in DRAW_SPELLS for card in pile)

def vulnerable_to_fluster(pile):
    return any(card in DRAW_SPELLS or card == "Dark Ritual" for card in pile)

def vulnerable_to_surgical(pile):
    return any(card in {ORACLE, "Gush", "Dig Through Time", "Treasure Cruise"} for card in pile)

def vulnerable_to_mindbreak(pile):
    nonmana = [c for c in pile if c not in MANA_SOURCES and c != "Island"]
    return len(nonmana) >= 3

def vulnerable_to_dress_down(pile):
    return ORACLE in pile

def vulnerable_to_consign(pile):
    return 

def vulnerable_to_orcish(pile):
    return any(card in (DRAW_SPELLS, DRAW_COUNTS) for card in pile)

def vulnerable_to_pyroblast(pile):
    return any(card in LOSES_TO_PYRO for card in pile)

# === Turn Calculation ===
def turns_to_win(pile, initial_hand=None):
    """
    Calculate the minimum number of turns required to draw through the pile
    and cast Thassa's Oracle, accounting for multi-draw spells and initial hand.
    initial_hand: list of cards in hand before starting the pile draw.
    """
    if initial_hand is None:
        initial_hand = []
    # If Oracle is already in hand
    if ORACLE in initial_hand:
        return 0

    # Pre-draw from hand: count draws from hand-based draw spells
    idx = 0
    for card in initial_hand:
        if card in DRAW_COUNTS:
            # draw COUNT cards from pile
            idx += DRAW_COUNTS[card]
        elif card in DRAW_SPELLS:
            # default draw of 1 for other draw spells
            idx += 1
        # cap at pile length
        if idx >= len(pile):
            idx = len(pile)
            break
    # If Oracle drawn from pre-draw
    if ORACLE in pile[:idx]:
        return 0

    # Now simulate turns
    turns = 0
    n = len(pile)
    while idx < n:
        turns += 1
        # Draw the top card of the pile this turn
        card = pile[idx]
        idx += 1
        # Determine how many cards that spell draws
        draw_count = DRAW_COUNTS.get(card, 1)
        # Draw the extra cards immediately within the same turn
        extra = draw_count - 1
        # adjust idx for extra draws
        idx += extra if idx + extra <= n else (n - idx)
        # Check if Oracle drawn
        if ORACLE in pile[:idx]:
            break
    return turns

# === Suggestion Logic ===
def suggest_viable_piles(deck, constraints, opponent_disruption, initial_hand=None, top_n=20):
    """
    Return up to top_n suggested piles with metadata:
      - 'pile': tuple of 5 card names
      - 'vulnerabilities': list of strings
      - 'play_pattern': recommended cast order
      - 'turns_to_win': integer number of turns
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
        life_loss_cards = pile_set & {"Street Wraith", "Gitaxian Probe"}
        if len(life_loss_cards) * 2 > constraints.get("max_life_loss", 20):
            continue

        # Opponent vulnerabilities
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

        # Play pattern
        ordered = sorted(pile, key=lambda c: (
            0 if c in MANA_SOURCES else
            1 if c in DRAW_SPELLS else
            2 if c == ORACLE else
            3
        ))
        play_pattern = " → ".join(ordered)

        # Turns to win
        turns = turns_to_win(ordered, initial_hand)

        suggestions.append({
            "pile": pile,
            "vulnerabilities": vulns or ["None"],
            "play_pattern": play_pattern,
            "turns_to_win": turns
        })

    # Sort by fewest vulnerabilities then fastest win
    suggestions.sort(key=lambda x: (x["turns_to_win"], len(x["vulnerabilities"])))
    return suggestions[:top_n]
