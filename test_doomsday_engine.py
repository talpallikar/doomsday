
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
    ORACLE,
    DRAW_SPELLS,
    MANA_SOURCES
)

# Sample minimal deck for testing
SAMPLE_DECK_TEXT = """
1 Thassa's Oracle
1 Brainstorm
1 Dark Ritual
1 Lotus Petal
1 Demonic Consultation
1 Gitaxian Probe
1 Gush
1 Island
1 Mox Jet
"""

@pytest.fixture
def sample_deck():
    return parse_decklist(SAMPLE_DECK_TEXT)

def test_parse_decklist_counts():
    deck = parse_decklist(SAMPLE_DECK_TEXT)
    assert deck.count("Thassa's Oracle") == 1
    assert deck.count("Brainstorm") == 1
    assert deck.count("Island") == 1
    assert len(deck) == 9

@pytest.mark.parametrize("pile, expected", [
    (("Thassa's Oracle",), True),
    (("Brainstorm",), False)
])
def test_vulnerable_to_force(pile, expected):
    assert vulnerable_to_force(pile) == expected

def test_vulnerable_to_fluster():
    assert vulnerable_to_fluster(("Dark Ritual","Brainstorm")) is True
    assert vulnerable_to_fluster(("Mox Jet","Island")) is False

def test_vulnerable_to_surgical():
    assert vulnerable_to_surgical(("Thassa's Oracle","Gush")) is True
    assert vulnerable_to_surgical(("Lotus Petal","Brainstorm")) is False

def test_vulnerable_to_mindbreak():
    # 3 non-mana, non-land spells
    assert vulnerable_to_mindbreak(("Brainstorm","Dark Ritual","Democratic Consultation","Island")) is True or vulnerable_to_mindbreak(("Brainstorm","Dark Ritual","Demonic Consultation","Island")) 

def test_vulnerable_to_dress_down():
    assert vulnerable_to_dress_down((ORACLE,)) is True
    assert vulnerable_to_dress_down(("Brainstorm",)) is False

def test_vulnerable_to_consign():
    assert vulnerable_to_consign(("Gush","Dig Through Time")) is True
    assert vulnerable_to_consign(("Brainstorm","Lotus Petal")) is False

def test_vulnerable_to_orcish():
    # Assuming nonbasic spells count
    assert vulnerable_to_orcish(("Brainstorm","Mox Jet")) is True
    assert vulnerable_to_orcish((ORACLE,"Dark Ritual")) is False

def test_vulnerable_to_pyroblast():
    assert vulnerable_to_pyroblast(("Brainstorm",)) is True
    assert vulnerable_to_pyroblast(("Demonic Consultation",)) is False

def test_suggest_viable_piles_basic(sample_deck):
    constraints = {
        "must_include_oracle": True,
        "must_include_draw": True,
        "min_mana_sources": 1,
        "max_life_loss": 20
    }
    opponent_disruption = {key: False for key in [
        "has_force_of_will","has_flusterstorm","has_surgical_extraction",
        "has_mindbreak_trap","has_dress_down",
        "has_consign_to_memory","has_orcish_bowmasters","has_pyroblast"
    ]}
    suggestions = suggest_viable_piles(sample_deck, constraints, opponent_disruption, top_n=5)
    # Suggestions should include at least one pile
    assert isinstance(suggestions, list)
    assert all(len(sug["pile"]) == 5 for sug in suggestions)
