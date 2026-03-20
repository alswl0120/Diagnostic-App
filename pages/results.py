import streamlit as st
import plotly.graph_objects as go
from recommendations.activities import get_recommendations, get_priority_gaps
from report.pdf_generator import generate_report
from core.auth import is_teacher
from core.database import classify_group, add_sync_item, get_connection
from components.character import character_celebrate

LEVEL_LABELS = {1: "Emerging", 2: "Developing", 3: "Proficient", 4: "Advanced"}
GROUP_COLORS = {"기초": "#EF4444", "중간": "#F59E0B", "상위": "#10B981"}
GROUP_BG = {"기초": "#FEF2F2", "중간": "#FFFBEB", "상위": "#ECFDF5"}
ATYPE_COLORS = {"baseline": "#6366F1", "midline": "#F59E0B", "endline": "#10B981"}
ATYPE_LABELS = {"baseline": "Baseline", "midline": "Midline", "endline": "Endline"}
LEVEL_COLORS = {1: "#94A3B8", 2: "#F59E0B", 3: "#6366F1", 4: "#10B981"}
LEVEL_BG = {1: "#F1F5F9", 2: "#FFFBEB", 3: "#EEF2FF", 4: "#ECFDF5"}
LEVEL_BORDER = {1: "#CBD5E1", 2: "#FDE68A", 3: "#C7D2FE", 4: "#A7F3D0"}
LEVEL_EMOJI = {1: "🌱", 2: "📈", 3: "⭐", 4: "🏆"}

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
_ALL = {**SECTION_LABELS["math"], **SECTION_LABELS["science"]}

_CSS = """
<style>
.result-hero {
    background: linear-gradient(135deg, #1E1B4B 0%, #312E81 50%, #4338CA 100%);
    border-radius: 20px; padding: 2rem 2rem 1.75rem;
    margin-bottom: 1.75rem; text-align: center;
    position: relative; overflow: hidden;
}
.result-hero::before {
    content:''; position:absolute; top:-50px; right:-50px;
    width:200px; height:200px; background:rgba(255,255,255,0.05); border-radius:50%;
}
.result-name {
    font-size: 1.6rem; font-weight: 900; color: white; margin-bottom: 0.2rem;
}
.result-sub { font-size: 0.85rem; color: rgba(255,255,255,0.6); margin-bottom: 1.25rem; font-weight:600; }
.overall-badge {
    display: inline-flex; align-items: center; gap: 0.5rem;
    padding: 0.6rem 1.5rem; border-radius: 50px;
    font-size: 1.1rem; font-weight: 900;
    border: 2px solid rgba(255,255,255,0.3);
    background: rgba(255,255,255,0.15);
    color: white;
}
.section-hdr {
    font-size: 0.72rem; font-weight: 900; text-transform: uppercase;
    letter-spacing: 0.1em; color: #9CA3AF;
    margin: 1.5rem 0 0.75rem;
}
.domain-card {
    background: white; border: 2px solid #F3F4F6;
    border-radius: 14px; padding: 1rem 1.1rem;
    margin-bottom: 0.5rem;
    transition: border-color 0.2s;
}
.domain-card:hover { border-color: #E0E7FF; }
.dc-top {
    display: flex; justify-content: space-between;
    align-items: center; margin-bottom: 0.3rem;
}
.dc-label { font-size: 0.88rem; font-weight: 800; color: #1F2937; }
.dc-chip {
    border-radius: 20px; padding: 0.15rem 0.6rem;
    font-size: 0.72rem; font-weight: 800;
}
.dc-meta { font-size: 0.75rem; color: #9CA3AF; font-weight: 700; margin-bottom: 0.45rem; }
.bar-track { background: #F3F4F6; border-radius: 6px; height: 9px; overflow: hidden; }
.gap-card {
    border: 2px solid #FDE68A; background: linear-gradient(135deg, #FFFBEB, #FEF3C7);
    border-radius: 14px; padding: 0.85rem 1.1rem; margin-bottom: 0.5rem;
    display: flex; justify-content: space-between; align-items: center;
}
.gap-label { font-size: 0.9rem; font-weight: 800; color: #78350F; }
.gap-badge {
    font-size: 0.75rem; font-weight: 800; padding: 0.2rem 0.65rem;
    border-radius: 20px;
}
.review-item {
    background: white; border-radius: 12px; padding: 1rem 1.1rem;
    margin-bottom: 0.6rem; border: 2px solid #F3F4F6;
}
.ri-correct { border-left: 4px solid #10B981; }
.ri-wrong { border-left: 4px solid #EF4444; }
.ri-q { font-size: 0.88rem; font-weight: 800; color: #1F2937; margin-bottom: 0.4rem; }
.ri-ans { font-size: 0.82rem; line-height: 1.6; }
.ri-domain { font-size: 0.68rem; color: #D1D5DB; font-weight: 700; margin-top: 0.3rem; }
</style>
"""


def _bar(label: str, pct: int, level: int, meta: str):
    color = LEVEL_COLORS[level]
    chip_bg = LEVEL_BG[level]
    chip_border = LEVEL_BORDER[level]
    emoji = LEVEL_EMOJI[level]
    st.markdown(f'<div class="domain-card"><div class="dc-top"><span class="dc-label">{label}</span><span class="dc-chip" style="background:{chip_bg}; color:{color}; border:1.5px solid {chip_border};">{emoji} {LEVEL_LABELS[level]}</span></div><div class="dc-meta">{meta}</div><div class="bar-track"><div style="background:linear-gradient(90deg,{color},{color}99);width:{pct}%;height:100%;border-radius:6px;"></div></div></div>', unsafe_allow_html=True)


def _radar(all_scores: dict):
    domains = list(all_scores.keys())
    vals = [round(all_scores[d]["score"] * 100, 1) for d in domains]
    labels = [_ALL.get(d, d) for d in domains]
    v2 = vals + [vals[0]]
    l2 = labels + [labels[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=v2, theta=l2,
        fill="toself",
        fillcolor="rgba(99, 102, 241, 0.12)",
        line=dict(color="#6366F1", width=2.5),
        marker=dict(size=6, color="#4F46E5"),
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], ticksuffix="%",
                           tickfont=dict(size=9, color="#9CA3AF"), gridcolor="#F3F4F6"),
            angularaxis=dict(tickfont=dict(size=10, color="#374151", family="Nunito")),
            bgcolor="white",
        ),
        showlegend=False,
        margin=dict(l=55, r=55, t=25, b=25),
        height=330,
        paper_bgcolor="white",
    )
    st.plotly_chart(fig, use_container_width=True)


def _review(math_scores, science_scores):
    math_ordered = st.session_state.get("math_ordered", [])
    sci_ordered = st.session_state.get("science_ordered", [])
    math_resp = st.session_state.get("math_responses", {})
    sci_resp = st.session_state.get("science_responses", {})
    LETTERS = ["A", "B", "C", "D"]

    if not math_ordered and not sci_ordered:
        st.caption("Answer review is not available for this session.")
        return

    def _items(ordered, responses, subj_labels):
        dcounts = {}
        for item in ordered:
            d = item["domain"]
            if d not in dcounts:
                dcounts[d] = 0
            li = dcounts[d]
            dcounts[d] += 1
            user_ans = (responses.get(d) or [None]*20)[li] if responses.get(d) else None
            correct = item["answer_index"]
            ok = user_ans == correct
            cls = "ri-correct" if ok else "ri-wrong"
            icon = "✅" if ok else "❌"
            ul = LETTERS[user_ans] if user_ans is not None else "—"
            cl = LETTERS[correct]
            dlabel = subj_labels.get(d, d)
            if ok:
                ans_html = f'<span style="color:#10B981;font-weight:800;">✓ {cl}. {item["options"][correct]}</span>'
            else:
                utxt = f'{ul}. {item["options"][user_ans]}' if user_ans is not None else "Not answered"
                ans_html = (
                    f'<span style="color:#EF4444;">✗ Your answer: {utxt}</span><br>'
                    f'<span style="color:#10B981;font-weight:800;">✓ Correct: {cl}. {item["options"][correct]}</span>'
                )
            st.markdown(f'<div class="review-item {cls}"><div class="ri-q">{icon} {item["stem"]}</div><div class="ri-ans">{ans_html}</div><div class="ri-domain">{dlabel}</div></div>', unsafe_allow_html=True)

    if math_ordered:
        st.markdown("**🔢 Mathematics**")
        _items(math_ordered, math_resp, SECTION_LABELS["math"])
    if sci_ordered:
        st.markdown("**🔬 Science**")
        _items(sci_ordered, sci_resp, SECTION_LABELS["science"])


def render():
    st.markdown(_CSS, unsafe_allow_html=True)

    math_scores = st.session_state.get("math_scores", {})
    science_scores = st.session_state.get("science_scores", {})
    overall_level = st.session_state.get("overall_level", 1)
    student_name = st.session_state.get("student_name", "Student")
    user = st.session_state.get("user", {})
    all_scores = {**math_scores, **science_scores}

    oc = LEVEL_COLORS[overall_level]
    em = LEVEL_EMOJI[overall_level]

    group = classify_group(overall_level)
    gc = GROUP_COLORS.get(group, "#9CA3AF")
    gbg = GROUP_BG.get(group, "#F9FAFB")
    atype = st.session_state.get("assessment_type", "baseline")
    atc = ATYPE_COLORS.get(atype, "#6366F1")
    atl = ATYPE_LABELS.get(atype, atype.title())

    try:
        conn = get_connection()
        add_sync_item("attempt_result", {
            "attempt_id": st.session_state.get("attempt_id", 0),
            "student_name": student_name,
            "overall_level": overall_level,
            "assessment_type": atype,
            "group_label": group,
        }, conn=conn)
        conn.close()
    except Exception:
        pass

    col_hero, col_char = st.columns([2, 1])
    with col_hero:
        st.markdown(f'<div class="result-hero"><div class="result-name">🎊 {student_name}</div><div class="result-sub">Assessment Complete · Here are your results</div><div class="overall-badge">{em} Overall Level: {LEVEL_LABELS[overall_level]}</div><div style="margin-top:0.75rem;display:flex;gap:0.5rem;justify-content:center;flex-wrap:wrap;"><span style="background:{gbg};color:{gc};border-radius:20px;padding:0.2rem 0.75rem;font-size:0.8rem;font-weight:800;">👥 Group: {group}</span><span style="background:{atc}22;color:{atc};border-radius:20px;padding:0.2rem 0.75rem;font-size:0.8rem;font-weight:800;">📊 {atl}</span></div></div>', unsafe_allow_html=True)
    with col_char:
        msgs = {1: "Keep going! Every step counts! 💪", 2: "Good effort! You're improving! 📈", 3: "Well done! You're on track! ⭐", 4: "Outstanding! You're a star! 🏆"}
        character_celebrate(msgs[overall_level])

    st.markdown('<div class="section-hdr">📡 Domain Overview</div>', unsafe_allow_html=True)
    _radar(all_scores)

    col_m, col_s = st.columns(2)
    with col_m:
        st.markdown('<div class="section-hdr">🔢 Mathematics</div>', unsafe_allow_html=True)
        for domain, ds in math_scores.items():
            label = SECTION_LABELS["math"].get(domain, domain)
            pct = int(ds["score"] * 100)
            _bar(label, pct, ds["level"], f"{ds['correct']}/{ds['total']} correct · {pct}%")

    with col_s:
        st.markdown('<div class="section-hdr">🔬 Science</div>', unsafe_allow_html=True)
        for domain, ds in science_scores.items():
            label = SECTION_LABELS["science"].get(domain, domain)
            pct = int(ds["score"] * 100)
            _bar(label, pct, ds["level"], f"{ds['correct']}/{ds['total']} correct · {pct}%")

    gaps = get_priority_gaps(all_scores)
    if gaps:
        st.markdown("---")
        st.markdown('<div class="section-hdr">⚠️ Priority Learning Areas</div>', unsafe_allow_html=True)
        st.caption("Focus on these domains first for the most improvement:")
        for domain in gaps:
            ds = all_scores[domain]
            label = _ALL.get(domain, domain)
            color = LEVEL_COLORS[ds["level"]]
            bg = LEVEL_BG[ds["level"]]
            st.markdown(f'<div class="gap-card"><span class="gap-label">{label}</span><span class="gap-badge" style="background:{bg}; color:{color};">{LEVEL_EMOJI[ds["level"]]} {LEVEL_LABELS[ds["level"]]} · {int(ds["score"]*100)}%</span></div>', unsafe_allow_html=True)

    recs = get_recommendations(all_scores)
    gap_recs = {d: recs[d] for d in gaps if d in recs}
    if gap_recs:
        st.markdown("---")
        st.markdown('<div class="section-hdr">💡 Recommended Activities</div>', unsafe_allow_html=True)
        for domain, text in gap_recs.items():
            label = _ALL.get(domain, domain)
            with st.expander(f"📚 {label}"):
                st.markdown(text)

    st.markdown("---")
    st.markdown('<div class="section-hdr">📝 Answer Review</div>', unsafe_allow_html=True)
    with st.expander("See all questions and your answers"):
        _review(math_scores, science_scores)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
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
            label="📄 Download My Report (PDF)",
            data=pdf_bytes,
            file_name=f"diagnostic_{student_name.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary",
        )
    except Exception:
        st.info("PDF requires the reportlab package.")

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 New Assessment", use_container_width=True):
            keys_to_clear = [
                "math_responses", "science_responses", "math_scores", "science_scores",
                "math_item_index", "science_item_index", "attempt_id", "overall_level",
                "_show_science_intro", "math_ordered", "science_ordered",
                "math_started_at", "science_started_at",
            ]
            for k in keys_to_clear:
                st.session_state.pop(k, None)
            for k in list(st.session_state.keys()):
                if k.startswith("math_sel_") or k.startswith("sci_sel_"):
                    del st.session_state[k]
            st.session_state["page"] = "home"
            st.rerun()
    with col2:
        if st.button("📈 My Progress", use_container_width=True, type="primary"):
            st.session_state["page"] = "progress"
            st.rerun()
    if is_teacher(user.get("roles", "")):
        with col3:
            if st.button("📊 Class Dashboard", use_container_width=True):
                st.session_state["page"] = "dashboard"
                st.rerun()
