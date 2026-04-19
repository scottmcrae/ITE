"""
ABFM ITE Browser & Quiz — Streamlit App
Covers 2015–2024 in-training exam questions (1,960 total)
"""

import json
import random
import re
import streamlit as st

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ABFM ITE Question Bank",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* ── Global background & text — Claude-style dark grey ── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #2d2d2d !important;
    color: #e3e3e3 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #262626 !important;
}
[data-testid="stSidebar"] * {
    color: #e3e3e3 !important;
}

/* All text elements */
p, li, label, span, div, h1, h2, h3, h4, h5, h6 {
    color: #e3e3e3 !important;
}

/* Inputs */
input, textarea, [data-testid="stTextInput"] input {
    background-color: #383838 !important;
    color: #e3e3e3 !important;
    border-color: #4a4a4a !important;
}

/* Selectbox / multiselect */
[data-testid="stSelectbox"] div,
[data-testid="stMultiSelect"] div {
    background-color: #383838 !important;
    color: #e3e3e3 !important;
}

/* Radio buttons */
[data-testid="stRadio"] label {
    color: #e3e3e3 !important;
}

/* Buttons */
[data-testid="stButton"] button {
    background-color: #383838 !important;
    color: #e3e3e3 !important;
    border: 1px solid #4a4a4a !important;
}
[data-testid="stButton"] button:hover {
    background-color: #424242 !important;
    border-color: #666666 !important;
}

/* Containers / cards */
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #333333 !important;
    border-color: #444444 !important;
}

/* Expander */
[data-testid="stExpander"] {
    background-color: #333333 !important;
    border-color: #444444 !important;
}
[data-testid="stExpander"] summary {
    color: #e3e3e3 !important;
}

/* Metric */
[data-testid="stMetric"] label,
[data-testid="stMetric"] div {
    color: #e3e3e3 !important;
}

/* Success / error / warning */
[data-testid="stAlert"] {
    background-color: #333333 !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    background-color: #333333 !important;
    color: #e3e3e3 !important;
}

/* Charts axis labels */
text { fill: #e3e3e3 !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #2d2d2d; }
::-webkit-scrollbar-thumb { background: #555555; border-radius: 3px; }

/* Explanation colors — must beat the global p override */
[data-testid="stMarkdownContainer"] p.expl-head { color: #d4813a !important; font-weight: 700; font-size: 1rem; margin: 20px 0 4px 0; }
[data-testid="stMarkdownContainer"] p.expl-sum  { color: #5fad7e !important; margin: 6px 0 2px 0; }
[data-testid="stMarkdownContainer"] p.expl-para { color: #c8c8c8 !important; margin: 2px 0 8px 0; padding-left: 1rem; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

# ─── Load data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_questions():
    with open("abfm_questions.json", "r") as f:
        return json.load(f)

questions = load_questions()

# ─── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.title("🩺 ABFM ITE Bank")
st.sidebar.caption("2015–2024 · 1,960 questions")

mode = st.sidebar.radio("Mode", ["📖 Browse", "🧠 Quiz", "📋 Summaries"], label_visibility="collapsed")

all_years = sorted(set(q["year"] for q in questions))
year_options = ["All Years"] + all_years
default_year_index = 0 if mode == "🧠 Quiz" else 1
selected_year = st.sidebar.selectbox("Filter by year", options=year_options, index=default_year_index)
selected_years = all_years if selected_year == "All Years" else [selected_year]

# Keyword search (shared between modes)
search_term = st.sidebar.text_input("🔍 Search question text", placeholder="e.g. diabetes, chest pain")

# ─── Filtered pool ────────────────────────────────────────────────────────────
pool = [
    q for q in questions
    if q["year"] in selected_years
    and (not search_term or search_term.lower() in q["stem"].lower())
]

st.sidebar.markdown(f"**{len(pool):,}** questions")

# ─── Helper: render explanation ───────────────────────────────────────────────
def render_explanation(q):
    st.markdown(f"**Answer: {q['correct_letter']}) {q['correct_label']}**")
    if not q.get("explanation"):
        raw = q.get("explanation_raw", "")
        if raw:
            st.markdown(raw)
        return

    parts = []
    for section in q["explanation"]:
        heading = section.get("heading")
        bullets = section.get("bullets", [])
        if heading:
            parts.append(f'<p class="expl-head">{heading}</p>')
        standalone = []
        for bullet in bullets:
            para = bullet.get("sub_paragraph", "")
            if para:
                if standalone:
                    parts.append(f'<p class="expl-para">{" ".join(standalone)}</p>')
                    standalone = []
                parts.append(f'<p class="expl-sum">{bullet["text"]}</p>')
                parts.append(f'<p class="expl-para">{para}</p>')
            else:
                standalone.append(bullet["text"])
        if standalone:
            parts.append(f'<p class="expl-para">{" ".join(standalone)}</p>')
    st.markdown("\n".join(parts), unsafe_allow_html=True)


# ─── Helper: render a single question card ────────────────────────────────────
def render_question_card(q, show_answer=True, quiz_key=None):
    st.markdown(f"##### {q['year']} · Q{q['number']}")
    st.markdown(q["stem"])

    choices = q.get("choices", {})
    if quiz_key is not None:
        # Interactive radio for quiz mode
        choice_labels = [f"{k}) {v}" for k, v in sorted(choices.items())]
        selected = st.radio(
            "Select answer:",
            options=choice_labels,
            key=quiz_key,
            index=None,
            label_visibility="collapsed",
        )

        if st.button("Submit", key=f"btn_{quiz_key}"):
            if selected is None:
                st.warning("Please select an answer first.")
            else:
                chosen_letter = selected[0]
                correct = q["correct_letter"]
                if chosen_letter == correct:
                    st.success(f"✅ Correct! **{correct}) {q['correct_label']}**")
                else:
                    st.error(
                        f"❌ Incorrect. You chose **{chosen_letter}**. "
                        f"Correct: **{correct}) {q['correct_label']}**"
                    )
                with st.expander("📖 Explanation", expanded=True):
                    render_explanation(q)
    else:
        # Browse mode — show choices statically
        for letter, text in sorted(choices.items()):
            is_correct = letter == q["correct_letter"]
            st.markdown(f"{letter}) {text}")

        with st.expander("📖 Explanation"):
            render_explanation(q)


# ══════════════════════════════════════════════════════════════════════════════
# MODE: BROWSE
# ══════════════════════════════════════════════════════════════════════════════
if mode == "📖 Browse":
    st.title("📖 Browse Questions")

    if not pool:
        st.warning("No questions match your filters.")
        st.stop()

    display_pool = sorted(pool, key=lambda q: (q["year"], q["number"]))

    for q in display_pool:
        with st.container(border=True):
            render_question_card(q, show_answer=True)


# ══════════════════════════════════════════════════════════════════════════════
# MODE: QUIZ
# ══════════════════════════════════════════════════════════════════════════════
elif mode == "🧠 Quiz":
    st.title("🧠 Quiz Mode")

    if not pool:
        st.warning("No questions match your filters.")
        st.stop()

    # Quiz config
    col1, col2 = st.columns(2)
    with col1:
        quiz_size = st.selectbox(
            "Number of questions", options=[5, 10, 25, 50, 100], index=1
        )
        quiz_size = min(quiz_size, len(pool))
    with col2:
        st.markdown(" ")
        if st.button("🔀 New Quiz"):
            for key in list(st.session_state.keys()):
                if key.startswith("quiz_"):
                    del st.session_state[key]
            st.session_state.quiz_questions = random.sample(pool, quiz_size)
            st.rerun()

    if "quiz_questions" not in st.session_state:
        st.session_state.quiz_questions = random.sample(pool, min(quiz_size, len(pool)))

    quiz_qs = st.session_state.quiz_questions

    for i, q in enumerate(quiz_qs):
        with st.container(border=True):
            render_question_card(q, show_answer=False, quiz_key=f"quiz_{i}_{q['year']}_{q['number']}")


# ═════════

# ══════════════════════════════════════════════════════════════════════════════
# MODE: SUMMARIES
# ══════════════════════════════════════════════════════════════════════════════
elif mode == "📋 Summaries":
    st.title("📋 Summaries")

    if not pool:
        st.warning("No questions match your filters.")
        st.stop()

    display_pool = sorted(pool, key=lambda q: (q["year"], q["number"]))

    for q in display_pool:
        # Collect all summary bullets that have a sub_paragraph
        summaries = []
        for section in q.get("explanation", []):
            heading = section.get("heading")
            for bullet in section.get("bullets", []):
                if bullet.get("sub_paragraph"):
                    summaries.append((heading, bullet["text"], bullet["sub_paragraph"]))

        if not summaries:
            continue

        with st.container(border=True):
            st.markdown(f"**Answer: {q['correct_letter']}) {q['correct_label']}**")
            parts = []
            last_heading = None
            for heading, summary, para in summaries:
                if heading and heading != last_heading:
                    parts.append(f'<p class="expl-head">{heading}</p>')
                    last_heading = heading
                parts.append(f'<p class="expl-sum">{summary}</p>')
            st.markdown("\n".join(parts), unsafe_allow_html=True)
