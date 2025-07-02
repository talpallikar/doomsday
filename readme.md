
# Magic: The Gathering Vintage Doomsday Engine

Author: @RPSBonjwa

A **Streamlit** and **Jupyter**-friendly toolkit that helps Vintage players engineer optimal **Doomsday** piles while accounting for opponent disruption and real mana constraints.

[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/talpallikar/doomsday/main/app.py)

---

## Features

- **Decklist Parsing**: Read `.txt` files with counts, set codes, and collector numbers.
- **Pile Suggestions**: Enumerate 5-card piles that win via **Thassa’s Oracle**.
- **Opponent Interaction**: Deterministic simulation against:

  - Force of Will (alternate cost)
  - Flusterstorm
  - Mindbreak Trap
  - Dress Down
  - Pyroblast
  - Consign to Memory
  - Orcish Bowmasters
  - Surgical Extraction

- **Mana Accounting**: Models artifacts, rituals, lands, and real mana costs 
  via **Scryfall**-cached data.
- **Extra Turns**: Recognizes **Time Walk** for 0‑turn or 1‑turn wins.
- **0-Turn Win**: Factor in starting hand draw spells (e.g. Brainstorm).
- **Interactive UI**: Streamlit sidebar controls, two‑column results, metrics.
- **Notebook Support**: `notebook_utils.py` for quick prototyping in Jupyter.

---

## Quickstart

### 1. Clone & Install

```bash
git clone https://github.com/talpallikar/doomsday.git
cd your-repo
pip install -r requirements.txt
```

### 2. Add Decklists

Put your Vintage deck `.txt` files into the `decks/` folder. Example:

```
decks/
├── discoverN_turbo.txt
├── tsubasa_cat_lurrus.txt
└── my_custom_list.txt
```

### 3. Launch the Streamlit App

```bash
streamlit run app.py
```

Visit <http://localhost:8501> to interactively generate Doomsday piles.

### 4. Use in Jupyter

```python
from notebook_utils import generate_suggestions

df = generate_suggestions(
    deck_text=open('decks/default_doomsday.txt').read(),
    constraints={
        "max_life_loss": 6,
        "min_mana_sources": 1,
        "must_include_oracle": True,
        "must_include_draw": True
    },
    opponent_disruption={
        "has_force_of_will": True,
        "has_flusterstorm": True,
        # ...
    },
    initial_hand=["Brainstorm", "Lotus Petal"],
    top_n=10
)
df
```

---

## Configuration

All core settings live in **`doomsday_engine/config.json`**:

- **`oracle`**: Win condition card.
- **`draw_spells`**, **`tutors`**, **`protection_spells`**, **`turn_spells`**.
- **`draw_counts`**: Multi-draw spell values (Ancestral Recall, Gush...).
- **`mana_produce`**: How much mana each source generates.
- **Decklists**: Auto-detected from `decks/*.txt`.

---

## Scryfall Cache

We use a **flat-JSON cache** to fetch `mana_cost` from Scryfall:

- Cached under `doomsday_engine/cache/cards/`.
- **TTL** is 1 week (configurable in `scryfall_cache.py`).
- Parses `{2}{U}{U}{B}` into `{"C":2,"U":2,"B":1}` automatically.

---

## Development

- **Python** ≥ 3.9
- **Dependencies** in `requirements.txt`:
  - `streamlit`, `pandas`, `requests`
- **Run tests**:
  ```bash
  pytest test_doomsday_engine.py
  ```

---

## Contributing

1. Fork the repo  
2. Create a feature branch  
3. Submit a PR with clear details  
4. We’ll review and merge 

---

## License

[MIT License](LICENSE)

