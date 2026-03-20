import streamlit as st
from recommendations.activities import get_recommendations, get_priority_gaps
from report.pdf_generator import generate_report
from core.auth import is_teacher

LEVEL_LABELS = {1: "Emerging", 2: "Developing", 3: "Proficient", 4: "Advanced"}
LEVEL_COLORS = {1: "#EF4444", 2: "#F97316", 3: "#3B82F6", 4: "#22C55E"}
LEVEL_BAR = {1: "█░░░", 2: "██░░", 3: "███░", 4: "████"}

SECTION_LABELS = {
    "math": {
        "number": "Number",
        "algebra": "Algebra",
        "geometry_measurement": "Geometry & Measurement",
        "handling_data": "Handling Data",
    },
    "science": {
        "diversity_matter": "Diversity of Matter",
        "cycles": "Cycles",
        "systems": "Systems",
        "forces_energy": "Forces and Energy",
        "humans_environment": "Humans and the Environment",
    },
}


def _score_card(domain_label: str, ds: dict):
    level = ds["level"]
    color = LEVEL_COLORS[level]
    bar = LEVEL_BAR[level]
    pct = int(ds["score"] * 100)
    st.markdown(f"""
        <div style="border:1px solid #E2E8F0; border-radius:6px; padding:0.7rem 1rem; margin-bottom:0.5rem; background:#fff;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:600; color:#1E3A5F;">{domain_label}</span>
                <span style="color:{color}; font-family:monospace; font-weight:700;">{bar} {LEVEL_LABELS[level]}</span>
            </div>
            <div style="color:#64748B; font-size:0.85rem;">{ds['correct']}/{ds['total']} correct &nbsp;·&nbsp; {pct}%</div>
        </div>
    """, unsafe_allow_html=True)


def render():
    math_scores = st.session_state.get("math_scores", {})
    science_scores = st.session_state.get("science_scores", {})
    overall_level = st.session_state.get("overall_level", 1)
    student_name = st.session_state.get("student_name", "Student")
    user = st.session_state.get("user", {})

    overall_color = LEVEL_COLORS[overall_level]
    st.markdown(f"""
        <div style="background:#1E3A5F; color:white; padding:1.2rem 1.5rem; border-radius:8px; margin-bottom:1.5rem;">
            <div style="font-size:1.3rem; font-weight:700;">{student_name}</div>
            <div style="font-size:0.9rem; opacity:0.8;">Learning Level Assessment — Results</div>
            <div style="margin-top:0.5rem; font-size:1.1rem;">
                Overall Level: <span style="color:{overall_color}; font-weight:700;">
                {LEVEL_LABELS[overall_level]}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_m, col_s = st.columns(2)
    with col_m:
        st.markdown("#### Mathematics")
        for domain, ds in math_scores.items():
            _score_card(SECTION_LABELS["math"].get(domain, domain), ds)

    with col_s:
        st.markdown("#### Science")
        for domain, ds in science_scores.items():
            _score_card(SECTION_LABELS["science"].get(domain, domain), ds)

    all_scores = {**math_scores, **science_scores}
    gaps = get_priority_gaps(all_scores)

    if gaps:
        st.markdown("---")
        st.markdown("#### Priority Learning Areas")
        st.markdown("These domains need the most support:")
        for domain in gaps:
            ds = all_scores[domain]
            label = SECTION_LABELS["math"].get(domain) or SECTION_LABELS["science"].get(domain, domain)
            color = LEVEL_COLORS[ds["level"]]
            st.markdown(f"- **{label}** — <span style='color:{color}'>{LEVEL_LABELS[ds['level']]}</span> ({int(ds['score']*100)}%)", unsafe_allow_html=True)

    recs = get_recommendations(all_scores)
    gap_recs = {d: recs[d] for d in gaps if d in recs}

    if gap_recs:
        st.markdown("---")
        st.markdown("#### Recommended Next Activities")
        for domain, text in gap_recs.items():
            label = SECTION_LABELS["math"].get(domain) or SECTION_LABELS["science"].get(domain, domain)
            with st.expander(f"{label}"):
                st.markdown(text)

    st.markdown("---")
    math_recs = {d: recs[d] for d in math_scores if d in recs}
    science_recs = {d: recs[d] for d in science_scores if d in recs}

    result = {
        "attempt_id": st.session_state.get("attempt_id", 0),
        "student_name": student_name,
        "math_scores": math_scores,
        "science_scores": science_scores,
        "overall_level": overall_level,
        "completed_at": "",
    }
    try:
        pdf_bytes = generate_report(result, math_recs, science_recs)
        st.download_button(
            label="Download Report (PDF)",
            data=pdf_bytes,
            file_name=f"diagnostic_report_{student_name.replace(' ', '_')}.pdf",
            mime="application/pdf",
        )
    except Exception:
        st.info("PDF generation requires the reportlab package to be installed.")

    if is_teacher(user.get("roles", "")):
        if st.button("View Class Dashboard"):
            st.session_state["page"] = "dashboard"
            st.rerun()

    if st.button("Start New Assessment"):
        for key in ["math_responses", "science_responses", "math_scores", "science_scores",
                    "math_item_index", "science_item_index", "attempt_id", "overall_level"]:
            st.session_state.pop(key, None)
        st.session_state["page"] = "home"
        st.rerun()
