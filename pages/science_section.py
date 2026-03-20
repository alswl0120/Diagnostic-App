import streamlit as st
from assessment.loader import get_ordered_items, get_questions_by_domain
from assessment.session import init_responses, record_response, get_domain_and_local_index
from core.scoring import score_section, compute_overall_level
from core.database import save_attempt_results, save_domain_scores, get_connection

SUBJECT = "science"
SECTION_LABEL = "Science"
TOTAL_ITEMS = 18


def render():
    if "science_responses" not in st.session_state:
        grouped = get_questions_by_domain(SUBJECT)
        st.session_state["science_responses"] = init_responses(SUBJECT, grouped)
        st.session_state["science_item_index"] = 0

    ordered = get_ordered_items(SUBJECT)
    idx = st.session_state["science_item_index"]

    progress = idx / TOTAL_ITEMS
    st.progress(progress, text=f"Science — Question {idx + 1} of {TOTAL_ITEMS}")

    item = ordered[idx]
    domain, local_idx = get_domain_and_local_index(ordered, idx)

    st.markdown(f"### Q{idx + 1}. {item['stem']}")
    st.markdown("")

    selected = st.radio(
        "Select your answer:",
        options=item["options"],
        index=None,
        key=f"science_q_{idx}",
        label_visibility="collapsed"
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Next →", type="primary", disabled=selected is None):
            answer_index = item["options"].index(selected)
            record_response(st.session_state["science_responses"], domain, local_idx, answer_index)
            st.session_state["science_item_index"] = idx + 1

            if idx + 1 >= TOTAL_ITEMS:
                _finalize()
            st.rerun()

    if idx > 0:
        with col2:
            if st.button("← Back"):
                st.session_state["science_item_index"] = idx - 1
                st.rerun()


def _finalize():
    math_grouped = get_questions_by_domain("math")
    science_grouped = get_questions_by_domain("science")

    math_scores = score_section(st.session_state["math_responses"], math_grouped)
    science_scores = score_section(st.session_state["science_responses"], science_grouped)

    all_scores = {**math_scores, **science_scores}
    overall_level = compute_overall_level(all_scores)

    attempt_id = st.session_state["attempt_id"]
    conn = get_connection()
    save_attempt_results(
        attempt_id,
        st.session_state["math_responses"],
        st.session_state["science_responses"],
        math_scores,
        science_scores,
        overall_level,
        conn=conn
    )
    save_domain_scores(attempt_id, {"math": math_scores, "science": science_scores}, conn=conn)
    conn.close()

    st.session_state["math_scores"] = math_scores
    st.session_state["science_scores"] = science_scores
    st.session_state["overall_level"] = overall_level
    st.session_state["page"] = "results"
