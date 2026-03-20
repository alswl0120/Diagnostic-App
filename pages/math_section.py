import streamlit as st
from assessment.loader import get_ordered_items, get_questions_by_domain
from assessment.session import init_responses, record_response, get_domain_and_local_index

SUBJECT = "math"
SECTION_LABEL = "Mathematics"
TOTAL_ITEMS = 20


def render():
    if "math_responses" not in st.session_state:
        grouped = get_questions_by_domain(SUBJECT)
        st.session_state["math_responses"] = init_responses(SUBJECT, grouped)
        st.session_state["math_item_index"] = 0

    ordered = get_ordered_items(SUBJECT)
    idx = st.session_state["math_item_index"]

    progress = idx / TOTAL_ITEMS
    st.progress(progress, text=f"Mathematics — Question {idx + 1} of {TOTAL_ITEMS}")

    item = ordered[idx]
    domain, local_idx = get_domain_and_local_index(ordered, idx)

    st.markdown(f"### Q{idx + 1}. {item['stem']}")
    st.markdown("")

    selected = st.radio(
        "Select your answer:",
        options=item["options"],
        index=None,
        key=f"math_q_{idx}",
        label_visibility="collapsed"
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Next →", type="primary", disabled=selected is None):
            answer_index = item["options"].index(selected)
            record_response(st.session_state["math_responses"], domain, local_idx, answer_index)
            st.session_state["math_item_index"] = idx + 1

            if idx + 1 >= TOTAL_ITEMS:
                st.session_state["page"] = "science"
            st.rerun()

    if idx > 0:
        with col2:
            if st.button("← Back"):
                st.session_state["math_item_index"] = idx - 1
                st.rerun()
