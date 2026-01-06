import streamlit as st
import pandas as pd
import random
from helper import *


def split_name(full: str):
    toks = norm_text(full).split()
    if not toks:
        return "", ""
    if len(toks) == 1:
        return toks[0], ""
    return toks[0], toks[-1]  # first, last

def name_match(user: str, truth: str) -> bool:
    u_first, u_last = split_name(user)
    t_first, t_last = split_name(truth)

    # fallback: if either missing, use overall fuzzy
    if not u_last or not t_last:
        return close_enough(user, truth, threshold=0.84)

    last_ok  = fuzzy_ratio(u_last, t_last) >= 0.70   # forgiving on last
    first_ok = fuzzy_ratio(u_first, t_first) >= 0.65 # very forgiving on first

    # also accept first-initial match if last is strong
    first_initial_ok = (u_first[:1] == t_first[:1] and u_first[:1] != "")

    return last_ok and (first_ok or first_initial_ok)


# --- load data
df = pd.read_csv("headshot_app/temp_opponent.csv").fillna("")

st.set_page_config(page_title="Opponent Quiz", page_icon="🧠", layout="centered")
st.title("🧠 Opponent Quiz")

# session state
if "idx" not in st.session_state:
    st.session_state.idx = random.randrange(len(df))
if "reveal" not in st.session_state:
    st.session_state.reveal = False

INPUT_KEYS = ["name_in", "year_in", "home_in", "prev_in"]

for k in INPUT_KEYS:
    if k not in st.session_state:
        st.session_state[k] = ""


row = df.iloc[st.session_state.idx]

# --- show prompt
if row.get("ImageURL", ""):
    st.image(row["ImageURL"], width=220)
else:
    st.info("No ImageURL for this player.")



col1, col2, col3 = st.columns(3)
submit = col1.button("Submit ✅")
next_q = col2.button("Next 🎲")
reveal = col3.button("Reveal 👀")

if next_q:
    st.session_state.idx = random.randrange(len(df))
    st.session_state.reveal = False

    # 🔥 clear inputs
    for k in INPUT_KEYS:
        st.session_state[k] = ""

    st.rerun()



# --- inputs
name_in = st.text_input("Name", key="name_in")
year_in = st.text_input("Year (e.g., Fr., So., R-Fr.)", key="year_in")
home_in = st.text_input("Hometown (US: state ok | Intl: country ok)", key="home_in")
prev_in = st.text_input("Previous School (or 'none')", key="prev_in")

if reveal:
    st.session_state.reveal = True
if submit:
    truth_name = row.get("Full Name", "")
    truth_year = row.get("Year", "")
    truth_home = row.get("Hometown", "")
    truth_prev = row.get("Previous School", "")

    name_ok = name_match(name_in, truth_name)

    year_ok = year_match(year_in, truth_year)
    home_ok = hometown_match(home_in, truth_home)
    prev_ok = prev_school_match(prev_in, truth_prev)

    st.subheader("Results")
    st.write("Name:", "✅" if name_ok else "❌")
    st.write("Year:", "✅" if year_ok else "❌")
    st.write("Hometown:", "✅" if home_ok else "❌")
    st.write("Previous School:", "✅" if prev_ok else "❌")

    score = sum([name_ok, year_ok, home_ok, prev_ok])
    st.success(f"Score: {score}/4")

    st.session_state.reveal = True

if st.session_state.reveal:
    st.divider()
    st.markdown("### Answer key")
    st.write("**Name:**", row.get("Full Name",""))
    st.write("**Year:**", row.get("Year",""))
    st.write("**Hometown:**", row.get("Hometown",""))
    st.write("**Previous School:**", row.get("Previous School",""))
