import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from doomsday_engine import parse_decklist, suggest_viable_piles

st.sidebar.image("logo.png", width=200)
st.sidebar.markdown("#### Vintage MTG Doomsday Pile Suggester\nBuilt with ♥ using Streamlit")

DECK_PRESETS = {
    "Turbo Doomsday": """1 Ancestral Recall
1 Black Lotus
1 Brainstorm
4 Dark Ritual
…""",
    "Lurrus Doomsday": """1 Ancestral Recall
1 Lotus Petal
1 Brainstorm
4 Dark Ritual
…""",
    # add more
}

HAND_PRESETS = {
    "Empty": "",
    "Brainstorm, Force of Will, Land": "Brainstorm, Force of Will, Underground Sea",
    "Oracle": "Thassa's Oracle",
    # add more
}


st.set_page_config(page_title="Vintage Doomsday Pile Suggester", layout="wide")

st.title("Vintage MTG Doomsday Pile Suggester Web App")

# Decklist input
preset = st.selectbox("Choose a deck preset:", ["<Paste your own>", *DECK_PRESETS])
if preset == "<Paste your own>":
    deck_text = st.text_area("Paste decklist here", height=200)
else:
    deck_text = DECK_PRESETS[preset]

# Initial hand input
hand_preset = st.selectbox("Example hands:", list(HAND_PRESETS.keys()))
if hand_preset == "Empty":
    initial_hand_input = ""
else:
    initial_hand_input = HAND_PRESETS[hand_preset]
# Show editable field in case they want to tweak
initial_hand_input = st.text_input("Or edit hand (comma-separated):", initial_hand_input)


# Constraints
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

# Opponent disruption toggles
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

# Generate suggestions
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