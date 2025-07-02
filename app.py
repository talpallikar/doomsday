import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os

from doomsday_engine import (
    parse_decklist,
    suggest_viable_piles,
    generate_pile_details
)

# ─── Page Config & Global CSS ────────────────────────────────────────────────
st.set_page_config(page_title="Vintage Doomsday Pile Suggester", layout="wide")
st.markdown("""
<style>
  .stDataFrame td, .stDataFrame th { padding: .4rem .8rem; font-size:0.9rem; }
  /* Make the sidebar collapse on narrow viewports */
  @media (max-width: 600px) {
    .css-jn99sy { display: none; }
  }
</style>
""", unsafe_allow_html=True)

# ─── Inputs: Two Rows, Two Columns Each ────────────────────────────────────────

# Row 1: Decklist & Initial Hand
col1, col2 = st.columns(2)
with col1:
    st.header("1. Decklist")
    DECK_FOLDER = "decks"
    deck_files = sorted(f for f in os.listdir(DECK_FOLDER) if f.endswith(".txt"))
    choice = st.selectbox("Pick a deck or paste your own:", ["<Paste your own>", *deck_files])
    uploaded = st.file_uploader("…or upload .txt deck", type="txt")
    if uploaded:
        deck_text = uploaded.getvalue().decode()
    elif choice != "<Paste your own>":
        deck_text = open(os.path.join(DECK_FOLDER, choice)).read()
    else:
        deck_text = st.text_area("Paste decklist (one card per line):", height=180)

with col2:
    st.header("2. Initial Hand")
    initial_hand_input = st.text_input("Comma-separated cards in hand:", "")

# Row 2: Constraints & Opponent Hate
col3, col4 = st.columns(2)
with col3:
    st.header("3. Constraints")
    max_life    = st.slider("Max life loss", 0, 20, 6)
    min_mana    = st.slider("Min mana sources", 0, 5, 1)
    must_oracle = st.checkbox("Require Oracle", True)
    must_draw   = st.checkbox("Require draw spell", True)
    constraints = {
        "max_life_loss":    max_life,
        "min_mana_sources": min_mana,
        "must_include_oracle": must_oracle,
        "must_include_draw":   must_draw
    }

with col4:
    st.header("4. Opponent Disruption")
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

# ─── Session State & Generate Button ─────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = None
if "selected_pile" not in st.session_state:
    st.session_state.selected_pile = None

if st.button("Generate Piles", use_container_width=True):
    deck = parse_decklist(deck_text)
    initial_hand = [c.strip() for c in initial_hand_input.split(",")] if initial_hand_input else []
    suggestions = suggest_viable_piles(deck, constraints, od, initial_hand, top_n=50)
    df = pd.DataFrame(suggestions)
    df["play_pattern_str"] = df["play_pattern"].apply(lambda x: " → ".join(x))
    st.session_state.df = df
    st.session_state.selected_pile = None

# ─── Results: Summary & Drill-Down Side by Side ───────────────────────────────
if st.session_state.df is not None:
    df = st.session_state.df

    # Two columns: summary table + drill-down selection
    summary_col, detail_col = st.columns([2, 1])

    with summary_col:
        st.header("✅ Suggested Piles")
        st.dataframe(df, use_container_width=True)

    with detail_col:
        st.header("🔎 Drill-Down")
        selected = st.selectbox(
            "Select a pile:",
            options=df.index.tolist(),
            format_func=lambda i: df.at[i, "play_pattern_str"],
            key="selected_pile"
        )
        if st.session_state.selected_pile is not None:
            play_list = df.at[st.session_state.selected_pile, "play_pattern"]
            detail_df = generate_pile_details(play_list, od,
                                              [c.strip() for c in initial_hand_input.split(",")] if initial_hand_input else [])
            st.table(detail_df)

# ─── Analytics Snippet ───────────────────────────────────────────────────────
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