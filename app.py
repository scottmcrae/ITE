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

mode = st.sidebar.radio("Mode", ["📖 Browse", "🧠 Quiz", "📊 Stats"], label_visibility="collapsed")

all_years = sorted(set(q["year"] for q in questions))
selected_years = st.sidebar.multiselect(
    "Filter by year",
    options=all_years,
    default=all_years,
    format_func=str,
)

# Keyword search (shared between modes)
search_term = st.sidebar.text_input("🔍 Search question text", placeholder="e.g. diabetes, chest pain")

# ─── Filtered pool ────────────────────────────────────────────────────────────
pool = [
    q for q in questions
    if q["year"] in selected_years
    and (not search_term or search_term.lower() in q["stem"].lower())
]

st.sidebar.markdown(f"**{len(pool):,}** questions match")

# ─── Helper: render explanation ───────────────────────────────────────────────
def render_explanation(q):
    st.markdown(f"**Answer: {q['correct_letter']}) {q['correct_label']}**")
    if not q.get("explanation"):
        raw = q.get("explanation_raw", "")
        if raw:
            st.markdown(raw)
        return

    for section in q["explanation"]:
        heading = section.get("heading")
        bullets = section.get("bullets", [])
        if heading:
            st.markdown(f"**{heading}**")
        for bullet in bullets:
            st.markdown(bullet["text"])
            para = bullet.get("sub_paragraph", "")
            if para:
                st.markdown(para)


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
            if show_answer and is_correct:
                st.markdown(f"{letter}) {text}")
            else:
                st.markdown(f"{letter}) {text}")

        if show_answer:
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

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        page_size = st.selectbox("Questions per page", [5, 10, 25, 50], index=1)
    with col2:
        sort_by = st.selectbox("Sort", ["Year ↑", "Year ↓", "Random"])
    with col3:
        show_answers = st.checkbox("Show answers", value=True)

    if sort_by == "Year ↑":
        display_pool = sorted(pool, key=lambda q: (q["year"], q["number"]))
    elif sort_by == "Year ↓":
        display_pool = sorted(pool, key=lambda q: (q["year"], q["number"]), reverse=True)
    else:
        display_pool = random.sample(pool, len(pool))

    total_pages = max(1, (len(display_pool) - 1) // page_size + 1)

    if "browse_page" not in st.session_state:
        st.session_state.browse_page = 1

    # Clamp page to valid range after filter changes
    st.session_state.browse_page = min(st.session_state.browse_page, total_pages)

    # Pagination controls
    pcol1, pcol2, pcol3 = st.columns([1, 2, 1])
    with pcol1:
        if st.button("⬅ Prev", disabled=st.session_state.browse_page <= 1):
            st.session_state.browse_page -= 1
            st.rerun()
    with pcol2:
        st.markdown(
            f"<p style='text-align:center'>Page {st.session_state.browse_page} of {total_pages} "
            f"({len(display_pool):,} questions)</p>",
            unsafe_allow_html=True,
        )
    with pcol3:
        if st.button("Next ➡", disabled=st.session_state.browse_page >= total_pages):
            st.session_state.browse_page += 1
            st.rerun()

    start = (st.session_state.browse_page - 1) * page_size
    page_qs = display_pool[start : start + page_size]

    for i, q in enumerate(page_qs):
        with st.container(border=True):
            render_question_card(q, show_answer=show_answers)


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
        quiz_size = st.number_input(
            "Number of questions", min_value=1, max_value=min(50, len(pool)), value=10, step=1
        )
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


# ══════════════════════════════════════════════════════════════════════════════
# MODE: STATS
# ══════════════════════════════════════════════════════════════════════════════
elif mode == "📊 Stats":
    st.title("📊 Question Bank Stats")

    # Questions by year
    st.subheader("Questions by Year")
    year_counts = {}
    for q in questions:
        year_counts[q["year"]] = year_counts.get(q["year"], 0) + 1

    import pandas as pd

    df_years = pd.DataFrame(
        [(yr, cnt) for yr, cnt in sorted(year_counts.items())],
        columns=["Year", "Questions"],
    )
    st.bar_chart(df_years.set_index("Year"))

    # Answer distribution
    st.subheader("Correct Answer Letter Distribution")
    letter_counts = {}
    for q in questions:
        l = q["correct_letter"]
        letter_counts[l] = letter_counts.get(l, 0) + 1
    df_letters = pd.DataFrame(
        sorted(letter_counts.items()), columns=["Letter", "Count"]
    )
    st.bar_chart(df_letters.set_index("Letter"))

    # Number of choices per question
    st.subheader("Answer Choice Count Distribution")
    choice_counts = {}
    for q in questions:
        n = len(q.get("choices", {}))
        choice_counts[n] = choice_counts.get(n, 0) + 1
    df_choices = pd.DataFrame(
        sorted(choice_counts.items()), columns=["# Choices", "# Questions"]
    )
    st.dataframe(df_choices, use_container_width=False)

    # Current filter summary
    st.subheader("Current Filter")
    if pool:
        col1, col2, col3 = st.columns(3)
        col1.metric("Years selected", len(selected_years))
        col2.metric("Questions in pool", len(pool))
        col3.metric("Search term", f'"{search_term}"' if search_term else "None")
    else:
        st.info("No questions match current filters.")

    # Sample question preview
    st.subheader("Random Sample from Pool")
    if pool:
        sample = random.choice(pool)
        with st.container(border=True):
            render_question_card(sample, show_answer=True)
