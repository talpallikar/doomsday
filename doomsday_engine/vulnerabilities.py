"""
vulnerabilities.py

Functions to detect vulnerability of piles to various hate cards.
"""
from .config import ORACLE, DRAW_SPELLS, MANA_SOURCES, TUTORS

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
    return any(card in {"Gush", "Demonic Consultation", "Dig Through Time", "Treasure Cruise"} for card in pile)

def vulnerable_to_orcish(pile):
    return any(card not in MANA_SOURCES and card not in {ORACLE, *DRAW_SPELLS, *TUTORS} for card in pile)

def vulnerable_to_pyroblast(pile):
    return any(card in DRAW_SPELLS or card in {"Brainstorm", "Ponder"} for card in pile)