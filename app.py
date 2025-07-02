import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
from doomsday_engine import parse_decklist, suggest_viable_piles, generate_pile_details

<<<<<<< HEAD
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
=======
st.sidebar.image("logo.png", width=200)
st.sidebar.markdown("#### Vintage MTG Doomsday Pile Suggester\nBuilt with ♥ using Streamlit")
st.set_page_config(page_title="Vintage Doomsday Pile Suggester", layout="wide")
st.title("Vintage Doomsday Engine")

# === 1) Decklist Input ===
st.header("1. Select a Decklist")
DECK_FOLDER = "decks"
deck_files = sorted(f for f in os.listdir(DECK_FOLDER) if f.lower().endswith(".txt"))

choice = st.selectbox(
    "Choose a decklist file (or select another input method):",
    ["<Paste your own>", *deck_files]
)

# File uploader sits next to the selectbox
uploaded_file = st.file_uploader(
    "Or upload your own .txt decklist:",
    type=["txt"]
)

if uploaded_file is not None:
    # Uploaded file takes highest priority
    deck_text = uploaded_file.getvalue().decode("utf-8")
    st.text_area("Decklist loaded from uploaded file:", deck_text, height=200)
elif choice != "<Paste your own>":
    # If user chose a file from decks/ folder
    path = os.path.join(DECK_FOLDER, choice)
    with open(path, "r") as f:
        deck_text = f.read()
    st.text_area(f"Decklist loaded from decks/{choice}:", deck_text, height=200)
else:
    # Free-form paste
    deck_text = st.text_area(
        "Paste your decklist here (one card per line, with quantities):",
        height=200
    )

# === 2) Initial Hand Input ===
st.header("2. Initial Hand")

initial_hand_input = st.text_input(
    "Enter cards you start with (comma-separated):",
    ""
)

# === 3) Constraints ===

st.header("3. Constraints")
max_life = st.slider("Maximum life loss (total)", 0, 20, 6)
min_mana = st.slider("Minimum number of mana sources in pile", 0, 5, 1)
must_oracle = st.checkbox("Must include Thassa's Oracle", value=True)
must_draw = st.checkbox("Must include at least one draw spell", value=True)

constraints = {
    "max_life_loss": max_life,
    "min_mana_sources": min_mana,
    "must_include_oracle": must_oracle,
    "must_include_draw": must_draw
}

# === 4) Opponent Disruption ===
st.header("4. Opponent Disruption")

od = {
    "has_force_of_will": st.checkbox("Force of Will", value=True),
    "has_flusterstorm": st.checkbox("Flusterstorm", value=True),
    "has_surgical_extraction": st.checkbox("Surgical Extraction", value=False),
    "has_mindbreak_trap": st.checkbox("Mindbreak Trap", value=False),
    "has_dress_down": st.checkbox("Dress Down", value=False),
    "has_consign_to_memory": st.checkbox("Consign to Memory", value=False),
    "has_orcish_bowmasters": st.checkbox("Orcish Bowmasters", value=False),
    "has_pyroblast": st.checkbox("Pyroblast", value=False)
}

# === 5) Generate & Display Suggestions ===

if st.button("Generate Piles"):
>>>>>>> parent of 93764d5 (manage state for drill-down)
    deck = parse_decklist(deck_text)
    initial_hand = [c.strip() for c in initial_hand_input.split(",")] if initial_hand_input else []
    suggestions = suggest_viable_piles(deck, constraints, od, initial_hand, top_n=50)
    df = pd.DataFrame(suggestions)
<<<<<<< HEAD
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
=======

    # Pre-format for display
    df['play_pattern_str'] = df['play_pattern'].apply(lambda x: ' → '.join(x))

    st.header("Suggested Doomsday Piles")
    st.dataframe(df)

    # Drill-down selector
    selected = st.selectbox(
        "Drill into a pile",
        options=df.index.tolist(),
        format_func=lambda i: df.at[i, 'play_pattern_str']
    )

    if selected is not None:
        st.subheader("Pile Drill-Down")
        # Grab the list directly, no split()
        play_list = df.at[selected, 'play_pattern']
        detail_df = generate_pile_details(play_list, od, initial_hand)
        st.table(detail_df)

# Analytics snippet
>>>>>>> parent of 93764d5 (manage state for drill-down)
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