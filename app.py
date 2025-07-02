
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

# ─── Page config & CSS ─────────────────────────────────────────────────────────
st.set_page_config(page_title="Vintage Doomsday Pile Suggester", layout="wide")
st.markdown(
    """
    <style>
      .stDataFrame td, .stDataFrame th {
        padding: .4rem .8rem;
        font-size: 0.9rem;
      }
    </style>
    """,
    unsafe_allow_html=True
)

# ─── Sidebar: Deck, Hand, Constraints, Disruption ──────────────────────────────
with st.sidebar:
    st.image("logo.png", width=200)
    st.markdown("## ▶️ Input Settings")

    deck_text = st.text_area(
        "Decklist (paste or upload .txt):",
        height=200
    )
    uploaded = st.file_uploader("", type="txt")
    if uploaded:
        deck_text = uploaded.getvalue().decode("utf-8")

    initial_hand_input = st.text_input(
        "Initial Hand (comma-separated):", ""
    )

    st.markdown("---")
    st.markdown("## ⚙️ Constraints")
    max_life    = st.slider("Max life loss", 0, 20, 6)
    min_mana    = st.slider("Min mana sources", 0, 5, 1)
    must_oracle = st.checkbox("Require Oracle", True)
    must_draw   = st.checkbox("Require draw spell", True)

    st.markdown("---")
    st.markdown("## 💥 Opponent Disruption")
    od = {
        "has_force_of_will":      st.checkbox("Force of Will", True),
        "has_flusterstorm":       st.checkbox("Flusterstorm", True),
        "has_surgical_extraction":st.checkbox("Surgical Extraction", False),
        "has_mindbreak_trap":     st.checkbox("Mindbreak Trap", False),
        "has_dress_down":         st.checkbox("Dress Down", False),
        "has_consign_to_memory":  st.checkbox("Consign to Memory", False),
        "has_orcish_bowmasters":  st.checkbox("Orcish Bowmasters", False),
        "has_pyroblast":          st.checkbox("Pyroblast", False)
    }

    generate = st.button("Generate Piles", use_container_width=True)

# ─── Main Panel: Starting Mana ─────────────────────────────────────────────────
st.header("3. Starting Mana Resources")
starting = st.multiselect(
    "Select mana sources currently in play:",
    options=list(MANA_PRODUCE.keys())
)
land_drops = st.slider(
    "Additional generic mana from land drops:",
    min_value=0, max_value=4, value=0
)

# ─── Session State Setup ───────────────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = None
if "selected_pile" not in st.session_state:
    st.session_state.selected_pile = None

# ─── Generate & Cache Pile Suggestions ────────────────────────────────────────
if generate:
    deck = parse_decklist(deck_text)
    initial_hand = (
        [c.strip() for c in initial_hand_input.split(",")]
        if initial_hand_input else []
    )
    constraints = {
        "max_life_loss":    max_life,
        "min_mana_sources": min_mana,
        "must_include_oracle": must_oracle,
        "must_include_draw":   must_draw
    }
    # Build initial mana pool from selections
    initial_pool = {}
    for src in starting:
        for clr, amt in MANA_PRODUCE[src].items():
            initial_pool[clr] = initial_pool.get(clr, 0) + amt

    suggestions = suggest_viable_piles(
        deck, constraints, od,
        initial_hand, initial_pool, land_drops, top_n=50
    )
    df = pd.DataFrame(suggestions)
    df["play_pattern_str"] = df["play_pattern"].apply(lambda x: " → ".join(x))
    st.session_state.df = df
    st.session_state.selected_pile = None

# ─── Display Results & Drill-Down ────────────────────────────────────────────
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
        initial_hand = (
            [c.strip() for c in initial_hand_input.split(",")]
            if initial_hand_input else []
        )
        # Rebuild initial_pool for simulation
        initial_pool = {}
        for src in starting:
            for clr, amt in MANA_PRODUCE[src].items():
                initial_pool[clr] = initial_pool.get(clr, 0) + amt

        detail_df = generate_pile_details(
            play_list, od, initial_hand,
            initial_pool, land_drops
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
