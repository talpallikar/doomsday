import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
from doomsday_engine import load_deck_from_text, suggest_viable_piles

st.sidebar.image("logo.png", width=200)
st.sidebar.markdown("#### Vintage MTG Doomsday Pile Suggester\nBuilt with ♥ using Streamlit")
st.set_page_config(page_title="Vintage Doomsday Pile Suggester", layout="wide")
st.title("Vintage MTG Doomsday Pile Suggester Web App")

# === 1) Decklist Input ===
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
    deck = parse_decklist(deck_text)
    initial_hand = [c.strip() for c in initial_hand_input.split(",")] if initial_hand_input else []
    suggestions = suggest_viable_piles(deck, constraints, od, initial_hand, top_n=50)
    df = pd.DataFrame(suggestions)
    st.header("Suggested Doomsday Piles")
    st.dataframe(df)

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