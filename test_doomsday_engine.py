
import pytest
from doomsday_engine import (
    parse_decklist,
    vulnerable_to_force,
    vulnerable_to_fluster,
    vulnerable_to_surgical,
    vulnerable_to_mindbreak,
    vulnerable_to_dress_down,
    vulnerable_to_consign,
    vulnerable_to_orcish,
    vulnerable_to_pyroblast,
    suggest_viable_piles,
    turns_to_win,
    ORACLE,
    DRAW_SPELLS,
    MANA_SOURCES
)

# Sample minimal deck for testing
SAMPLE_DECK_TEXT = """
1 Thassa's Oracle (SLD) 1280
1 Brainstorm (FCA) 28
1 Dark Ritual (SLD) 1170
1 Lotus Petal (2ED) 230
"""

@pytest.fixture
def sample_deck():
    return parse_decklist(SAMPLE_DECK_TEXT)

def test_parse_decklist_counts(sample_deck):
    assert sample_deck.count("Thassa's Oracle") == 1
    assert sample_deck.count("Brainstorm") == 1
    assert sample_deck.count("Dark Ritual") == 1
    assert sample_deck.count("Lotus Petal") == 1
    assert len(sample_deck) == 4

@pytest.mark.parametrize("pile,expected", [
    (("Thassa's Oracle",), True),
    (("Brainstorm",), False),
])
def test_vulnerable_to_force(pile, expected):
    assert vulnerable_to_force(pile) == expected

def test_vulnerable_to_fluster():
    assert vulnerable_to_fluster(("Dark Ritual","Brainstorm")) is True
    assert vulnerable_to_fluster(("Mox Jet","Island")) is False
    assert vulnerable_to_fluster(("Thassa's Oracle", "Flusterstorm")) is False

def test_vulnerable_to_surgical():
    assert vulnerable_to_surgical(("Thassa's Oracle","Gush")) is True
    assert vulnerable_to_surgical(("Lotus Petal","Brainstorm")) is False

def test_vulnerable_to_mindbreak():
    assert vulnerable_to_mindbreak(("Brainstorm","Dark Ritual","Demonic Consultation","Island")) is True
    assert vulnerable_to_mindbreak(("Land","Lotus Petal","Mystic")) is False

def test_vulnerable_to_dress_down():
    assert vulnerable_to_dress_down((ORACLE,)) is True
    assert vulnerable_to_dress_down(("Brainstorm",)) is False

def test_vulnerable_to_consign():
    assert vulnerable_to_consign(("Gush","Dig Through Time")) is True
    assert vulnerable_to_consign(("Brainstorm","Lotus Petal")) is False

def test_vulnerable_to_orcish():
    assert vulnerable_to_orcish(("Brainstorm","Mox Jet")) is True
    assert vulnerable_to_orcish((ORACLE,"Dark Ritual")) is False

def test_vulnerable_to_pyroblast():
    assert vulnerable_to_pyroblast(("Brainstorm",)) is True
    assert vulnerable_to_pyroblast(("Demonic Consultation",)) is False

def test_turns_to_win_zero_initial_hand():
    # Oracle in hand -> 0 turns
    pile = ("Lotus Petal","Thassa's Oracle","Brainstorm")
    assert turns_to_win(pile, initial_hand=["Thassa's Oracle"]) == 0

def test_turns_to_win_basic():
    # Simple single-draw until Oracle
    assert turns_to_win(("Brainstorm","Thassa's Oracle")) == 1
    # Gush draws 2: should draw Oracle in 1 turn
    assert turns_to_win(("Gush","Thassa's Oracle")) == 1

def test_suggest_viable_piles_basic(sample_deck):
    constraints = {
        "must_include_oracle": True,
        "must_include_draw": True,
        "min_mana_sources": 1,
        "max_life_loss": 20
    }
    od = {k: False for k in [
        "has_force_of_will","has_flusterstorm","has_surgical_extraction",
        "has_mindbreak_trap","has_dress_down",
        "has_consign_to_memory","has_orcish_bowmasters","has_pyroblast"
    ]}
    suggestions = suggest_viable_piles(sample_deck, constraints, od, initial_hand=None, top_n=5)
    assert isinstance(suggestions, list)
    assert all(isinstance(s["pile"], tuple) and len(s["pile"]) == 5 for s in suggestions)
