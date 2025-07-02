import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os

from doomsday_engine import (
    parse_decklist,
    suggest_viable_piles,
    generate_pile_details,
    MANA_PRODUCE
)

# ─── Page & Sidebar Setup ─────────────────────────────────────────────────────
st.set_page_config(page_title="Vintage Doomsday Engine", layout="wide")

st.title("Vintage Doomsday Engine")
st.image("logo.png", width=200)
st.markdown("#### Vintage MTG Doomsday Pile Suggester")

# ─── 1) Decklist Input (Main Panel) ────────────────────────────────────────────
st.header("1. Select a Decklist")
DECK_FOLDER = "decks"
deck_files = sorted(f for f in os.listdir(DECK_FOLDER) if f.lower().endswith(".txt"))
choice = st.selectbox(
    "Choose a decklist file (or <Paste your own>):",
    ["<Paste your own>", *deck_files]
)
uploaded = st.file_uploader("Or upload your own .txt decklist:", type="txt")

if uploaded:
    deck_text = uploaded.getvalue().decode("utf-8")
    st.text_area("Decklist (uploaded):", deck_text, height=200)
elif choice != "<Paste your own>":
    path = os.path.join(DECK_FOLDER, choice)
    deck_text = open(path).read()
    st.text_area(f"Decklist ({choice}):", deck_text, height=200)
else:
    deck_text = st.text_area(
        "Paste your decklist here (one card per line):",
        height=200
    )

# ─── 2) Initial Hand Input ─────────────────────────────────────────────────────
st.header("2. Initial Hand")
initial_hand_input = st.text_input("Enter cards you start with (comma-separated):", "")

# ─── Starting Mana Resources ────────────────────────────────────────
st.header("3. Starting Mana Resources")
starting = st.multiselect(
    "Select mana sources currently in play:",
    options=list(MANA_PRODUCE.keys())
)
land_drops = st.slider(
    "Additional generic mana from land drops:",
    min_value=0, max_value=4, value=0
)

# ─── 3) Constraints ────────────────────────────────────────────────────────────
st.header("4. Constraints")
max_life = st.slider("Maximum life loss (total)", 0, 20, 6)
min_mana  = st.slider("Minimum mana sources in pile", 0, 5, 1)
must_oracle = st.checkbox("Must include Thassa's Oracle", value=True)
must_draw   = st.checkbox("Must include at least one draw spell", value=True)

constraints = {
    "max_life_loss":    max_life,
    "min_mana_sources": min_mana,
    "must_include_oracle": must_oracle,
    "must_include_draw":   must_draw
}

# ─── 4) Opponent Disruption ────────────────────────────────────────────────────
st.header("5. Opponent Disruption")
od = {
    "has_force_of_will":     st.checkbox("Force of Will", True),
    "has_flusterstorm":      st.checkbox("Flusterstorm", True),
    "has_surgical_extraction": st.checkbox("Surgical Extraction", False),
    "has_mindbreak_trap":    st.checkbox("Mindbreak Trap", False),
    "has_dress_down":        st.checkbox("Dress Down", False),
    "has_consign_to_memory": st.checkbox("Consign to Memory", False),
    "has_orcish_bowmasters": st.checkbox("Orcish Bowmasters", False),
    "has_pyroblast":         st.checkbox("Pyroblast", False)
}

# ─── Session State Initialization ─────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = None
if "selected_pile" not in st.session_state:
    st.session_state.selected_pile = None

# ─── 6) Generate Piles Button ─────────────────────────────────────────────────
generate = st.button("Generate Piles")

if generate:
    # Parse deck & hand
    deck = parse_decklist(deck_text)
    initial_hand = [c.strip() for c in initial_hand_input.split(",")] if initial_hand_input else []
    # Build initial mana pool from selected sources
    initial_pool = {}
    for src in starting:
        for clr, amt in MANA_PRODUCE[src].items():
            initial_pool[clr] = initial_pool.get(clr, 0) + amt
    # Compute suggestions
    suggestions = suggest_viable_piles(
        deck,
        constraints,
        od,
        initial_hand,
        initial_pool,
        land_drops,
        top_n=50
    )
    df = pd.DataFrame(suggestions)
    df["play_pattern_str"] = df["play_pattern"].apply(lambda x: " → ".join(x))
    # Cache in session
    st.session_state.df = df
    st.session_state.selected_pile = None  # reset drill-down

# ─── 7) Display Results & Drill-Down ──────────────────────────────────────────
if st.session_state.df is not None:
    df = st.session_state.df
    st.header("✅ Suggested Doomsday Piles")
    st.dataframe(df, use_container_width=True)

    st.subheader("🔎 Drill into a Pile")
    selected = st.selectbox(
        "Choose a pile to inspect:",
        options=df.index.tolist(),
        format_func=lambda i: df.at[i, "play_pattern_str"],
        key="selected_pile"
    )

    if st.session_state.selected_pile is not None:
        play_list = df.at[st.session_state.selected_pile, "play_pattern"]
        initial_hand = [c.strip() for c in initial_hand_input.split(",")] if initial_hand_input else []
        # Rebuild initial_pool for drill-down
        initial_pool = {}
        for src in starting:
            for clr, amt in MANA_PRODUCE[src].items():
                initial_pool[clr] = initial_pool.get(clr, 0) + amt
        detail_df = generate_pile_details(
            play_list,
            od,
            initial_hand,
            initial_pool,
            land_drops
        )
        st.subheader("🕵️ Pile Drill-Down")
        st.dataframe(detail_df, use_container_width=True)

# ─── Analytics Snippet ────────────────────────────────────────────────────────
GA_JS = """
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-9425Y903KE"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-9425Y903KE');
</script>
"""
components.html(GA_JS, height=0)