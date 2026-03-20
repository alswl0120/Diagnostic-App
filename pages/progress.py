import json
import streamlit as st
import plotly.graph_objects as go
from core.database import get_attempts_by_name, get_connection

LEVEL_LABELS = {1: "Emerging", 2: "Developing", 3: "Proficient", 4: "Advanced"}
LEVEL_COLORS = {1: "#94A3B8", 2: "#F59E0B", 3: "#6366F1", 4: "#10B981"}
ATYPE_LABELS = {"baseline": "Baseline", "midline": "Midline", "endline": "Endline"}
ATYPE_COLORS = {"baseline": "#6366F1", "midline": "#F59E0B", "endline": "#10B981"}

GROUP_COLORS = {"기초": "#EF4444", "중간": "#F59E0B", "상위": "#10B981"}
GROUP_BG = {"기초": "#FEF2F2", "중간": "#FFFBEB", "상위": "#ECFDF5"}

DOMAIN_LABELS = {
    "number": "Number", "algebra": "Algebra",
    "geometry_measurement": "Geometry & Meas.", "handling_data": "Handling Data",
    "diversity_matter": "Diversity of Matter", "cycles": "Cycles",
    "systems": "Systems", "forces_energy": "Forces & Energy",
    "humans_environment": "Humans & Env.",
}

_CSS = """
<style>
.prog-hero {
    background: linear-gradient(135deg, #1E1B4B 0%, #312E81 50%, #4338CA 100%);
    border-radius: 18px; padding: 1.75rem 2rem; margin-bottom: 1.5rem; color: white;
}
.prog-title { font-size: 1.5rem; font-weight: 900; margin-bottom: 0.2rem; }
.prog-sub { font-size: 0.85rem; opacity: 0.7; }
.prog-section { font-size: 0.72rem; font-weight: 900; text-transform: uppercase; letter-spacing: 0.1em; color: #9CA3AF; margin: 1.25rem 0 0.75rem; }
.attempt-card {
    background: white; border: 2px solid #F3F4F6; border-radius: 14px;
    padding: 1rem 1.25rem; margin-bottom: 0.6rem;
    display: flex; justify-content: space-between; align-items: center;
}
.ac-left { display: flex; flex-direction: column; gap: 0.2rem; }
.ac-label { font-size: 0.78rem; font-weight: 800; }
.ac-date { font-size: 0.72rem; color: #9CA3AF; font-weight: 600; }
.ac-right { display: flex; align-items: center; gap: 0.75rem; }
.level-badge {
    font-size: 0.8rem; font-weight: 800; padding: 0.25rem 0.75rem;
    border-radius: 20px;
}
.delta-up { color: #10B981; font-size: 0.82rem; font-weight: 800; }
.delta-down { color: #EF4444; font-size: 0.82rem; font-weight: 800; }
.delta-same { color: #9CA3AF; font-size: 0.82rem; font-weight: 700; }
.group-badge {
    font-size: 0.75rem; font-weight: 800; padding: 0.2rem 0.65rem; border-radius: 20px;
}
.no-history {
    text-align: center; padding: 3rem 1rem; color: #9CA3AF;
}
</style>
"""


def _get_atype_label(attempt: dict, index: int) -> str:
    atype = attempt.get("assessment_type") or ("baseline" if index == 0 else "endline")
    return ATYPE_LABELS.get(atype, atype.title())


def _delta_html(current: int, previous: int | None) -> str:
    if previous is None:
        return '<span class="delta-same">—</span>'
    diff = current - previous
    if diff > 0:
        return f'<span class="delta-up">▲ +{diff} level</span>'
    if diff < 0:
        return f'<span class="delta-down">▼ {diff} level</span>'
    return '<span class="delta-same">= No change</span>'


def _line_chart(attempts: list):
    dates = [(a.get("completed_at") or a.get("started_at") or "")[:10] for a in attempts]
    levels = [a.get("overall_level") or 1 for a in attempts]
    atypes = [_get_atype_label(a, i) for i, a in enumerate(attempts)]
    colors = [ATYPE_COLORS.get(a.get("assessment_type", "baseline"), "#6366F1") for a in attempts]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=levels,
        mode="lines+markers+text",
        line=dict(color="#6366F1", width=3),
        marker=dict(size=14, color=colors, line=dict(color="white", width=2)),
        text=atypes,
        textposition="top center",
        textfont=dict(size=10, color="#374151"),
        hovertemplate="<b>%{text}</b><br>Date: %{x}<br>Level: %{y}<extra></extra>",
    ))
    fig.update_layout(
        yaxis=dict(
            range=[0.5, 4.5], tickvals=[1, 2, 3, 4],
            ticktext=["Emerging", "Developing", "Proficient", "Advanced"],
            gridcolor="#F3F4F6", tickfont=dict(size=10),
        ),
        xaxis=dict(tickfont=dict(size=10), gridcolor="#F3F4F6"),
        margin=dict(l=10, r=10, t=20, b=10),
        height=260,
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def _domain_progress_chart(attempts: list):
    if len(attempts) < 2:
        return
    first = attempts[0]
    last = attempts[-1]
    math1 = json.loads(first.get("math_scores") or "{}")
    sci1 = json.loads(first.get("science_scores") or "{}")
    math2 = json.loads(last.get("math_scores") or "{}")
    sci2 = json.loads(last.get("science_scores") or "{}")

    all1 = {**math1, **sci1}
    all2 = {**math2, **sci2}
    domains = [d for d in all1 if d in all2]
    if not domains:
        return

    labels = [DOMAIN_LABELS.get(d, d) for d in domains]
    vals1 = [round(all1[d]["score"] * 100) for d in domains]
    vals2 = [round(all2[d]["score"] * 100) for d in domains]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Baseline", x=labels, y=vals1, marker_color="#C7D2FE"))
    fig.add_trace(go.Bar(name="Latest", x=labels, y=vals2, marker_color="#6366F1"))
    fig.update_layout(
        barmode="group",
        yaxis=dict(range=[0, 110], ticksuffix="%", gridcolor="#F3F4F6"),
        xaxis=dict(tickfont=dict(size=9)),
        legend=dict(orientation="h", y=1.12, font=dict(size=10)),
        margin=dict(l=10, r=10, t=30, b=10),
        height=250,
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    st.plotly_chart(fig, use_container_width=True)


def render():
    st.markdown(_CSS, unsafe_allow_html=True)

    student_name = st.session_state.get("student_name", "")
    if not student_name:
        st.warning("No student selected. Please start from the home page.")
        if st.button("← Back to Home"):
            st.session_state["page"] = "home"
            st.rerun()
        return

    conn = get_connection()
    attempts = get_attempts_by_name(student_name, conn=conn)
    conn.close()

    st.markdown(f'<div class="prog-hero"><div class="prog-title">📈 Progress: {student_name}</div><div class="prog-sub">Learning growth over time · {len(attempts)} assessment(s) completed</div></div>', unsafe_allow_html=True)

    if not attempts:
        st.markdown('<div class="no-history">📭 No completed assessments yet.<br><span style="font-size:0.85rem;">Complete your first assessment to start tracking progress.</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="prog-section">📊 Overall Level Over Time</div>', unsafe_allow_html=True)
        _line_chart(attempts)

        st.markdown('<div class="prog-section">📋 Assessment History</div>', unsafe_allow_html=True)
        prev_level = None
        for i, attempt in enumerate(attempts):
            level = attempt.get("overall_level") or 1
            atype_label = _get_atype_label(attempt, i)
            date = (attempt.get("completed_at") or "")[:16]
            group = attempt.get("group_label") or ""
            lc = LEVEL_COLORS.get(level, "#94A3B8")
            delta = _delta_html(level, prev_level)
            gc = GROUP_COLORS.get(group, "#9CA3AF")
            gbg = GROUP_BG.get(group, "#F9FAFB")
            group_html = f'<span class="group-badge" style="background:{gbg};color:{gc};">{group}</span>' if group else ""
            st.markdown(
                f'<div class="attempt-card"><div class="ac-left"><span class="ac-label" style="color:{ATYPE_COLORS.get(attempt.get("assessment_type","baseline"),"#6366F1")};">{atype_label}</span><span class="ac-date">{date}</span></div>'
                f'<div class="ac-right">{delta}<span class="level-badge" style="background:{lc}22;color:{lc};">{LEVEL_LABELS[level]}</span>{group_html}</div></div>',
                unsafe_allow_html=True
            )
            prev_level = level

        if len(attempts) >= 2:
            st.markdown('<div class="prog-section">📉 Domain Comparison (Baseline vs Latest)</div>', unsafe_allow_html=True)
            _domain_progress_chart(attempts)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Results", use_container_width=True):
            st.session_state["page"] = "results"
            st.rerun()
    with col2:
        if st.button("🔄 New Assessment", use_container_width=True, type="primary"):
            keys = ["math_responses", "science_responses", "math_scores", "science_scores",
                    "math_item_index", "science_item_index", "attempt_id", "overall_level",
                    "_show_science_intro", "math_ordered", "science_ordered",
                    "math_started_at", "science_started_at"]
            for k in keys:
                st.session_state.pop(k, None)
            for k in list(st.session_state.keys()):
                if k.startswith("math_sel_") or k.startswith("sci_sel_"):
                    del st.session_state[k]
            st.session_state["page"] = "home"
            st.rerun()
