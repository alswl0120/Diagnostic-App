import json
import io
import csv
import streamlit as st
import plotly.graph_objects as go
from core.database import get_all_attempts, get_class_domain_averages, get_connection, update_group_label, classify_group
from core.auth import is_teacher
from i18n import UI

LEVEL_LABELS = UI["levels"]
LEVEL_COLORS = {1: "#94A3B8", 2: "#F59E0B", 3: "#3B82F6", 4: "#10B981"}
GROUP_COLORS = {"기초": "#EF4444", "중간": "#F59E0B", "상위": "#10B981"}
GROUP_BG = {"기초": "#FEF2F2", "중간": "#FFFBEB", "상위": "#ECFDF5"}
ATYPE_COLORS = {"baseline": "#6366F1", "midline": "#F59E0B", "endline": "#10B981"}

DOMAIN_KEYS = [
    "number", "algebra", "geometry_measurement", "handling_data",
    "diversity_matter", "cycles", "systems", "forces_energy", "humans_environment",
]
DOMAIN_LABELS = {
    "number": "Number", "algebra": "Algebra",
    "geometry_measurement": "Geometry & Meas.", "handling_data": "Handling Data",
    "diversity_matter": "Diversity of Matter", "cycles": "Cycles",
    "systems": "Systems", "forces_energy": "Forces & Energy",
    "humans_environment": "Humans & Env.",
}

_CSS = """
<style>
.dash-hero {
    background: linear-gradient(135deg, #1E293B 0%, #334155 100%);
    color: white; padding: 1.5rem 2rem; border-radius: 14px; margin-bottom: 1.5rem;
}
.dash-title { font-size: 1.4rem; font-weight: 800; }
.dash-sub { font-size: 0.85rem; opacity: 0.65; }
.stat-card {
    background: white; border: 1px solid #E2E8F0; border-radius: 10px;
    padding: 1rem 1.25rem; text-align: center;
}
.stat-num { font-size: 2rem; font-weight: 800; color: #1E293B; }
.stat-label { font-size: 0.78rem; color: #64748B; margin-top: 0.1rem; }
.section-title {
    font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.08em; color: #64748B; margin: 1.25rem 0 0.75rem 0;
}
.group-stat-card {
    border-radius: 12px; padding: 0.85rem 1rem; text-align: center;
}
.gs-num { font-size: 1.6rem; font-weight: 900; }
.gs-label { font-size: 0.75rem; font-weight: 700; opacity: 0.8; }
</style>
"""


def _heatmap(attempts: list):
    student_names = [a["student_name"] for a in attempts]
    domain_short = [DOMAIN_LABELS.get(d, d) for d in DOMAIN_KEYS]

    z, text = [], []
    for attempt in attempts:
        math_s = json.loads(attempt.get("math_scores") or "{}")
        science_s = json.loads(attempt.get("science_scores") or "{}")
        all_s = {**math_s, **science_s}
        row_z, row_t = [], []
        for d in DOMAIN_KEYS:
            score = all_s.get(d, {}).get("score", None)
            if score is not None:
                row_z.append(round(score * 100))
                row_t.append(f"{round(score * 100)}%")
            else:
                row_z.append(None)
                row_t.append("—")
        z.append(row_z)
        text.append(row_t)

    fig = go.Figure(data=go.Heatmap(
        z=z, x=domain_short, y=student_names,
        colorscale=[[0.0, "#FEE2E2"], [0.4, "#FEF3C7"], [0.6, "#DBEAFE"], [0.8, "#D1FAE5"], [1.0, "#A7F3D0"]],
        zmin=0, zmax=100,
        text=text, texttemplate="%{text}", textfont=dict(size=10),
        hovertemplate="<b>%{y}</b><br>%{x}: %{text}<extra></extra>",
        colorbar=dict(title="Score %", tickvals=[0, 40, 60, 80, 100], ticktext=["0%", "40%", "60%", "80%", "100%"], thickness=12),
    ))
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        height=max(200, 40 * len(attempts) + 80),
        paper_bgcolor="white",
        xaxis=dict(side="top", tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=10), autorange="reversed"),
    )
    st.plotly_chart(fig, use_container_width=True)


def _group_stats(attempts: list):
    counts = {"기초": 0, "중간": 0, "상위": 0}
    for a in attempts:
        g = a.get("group_label") or classify_group(a.get("overall_level", 1) or 1)
        if g in counts:
            counts[g] += 1

    cols = st.columns(3)
    items = [("기초", "Foundational"), ("중간", "Developing"), ("상위", "Advanced")]
    for col, (group, en_label) in zip(cols, items):
        with col:
            color = GROUP_COLORS[group]
            bg = GROUP_BG[group]
            st.markdown(f'<div class="group-stat-card" style="background:{bg};"><div class="gs-num" style="color:{color};">{counts[group]}</div><div class="gs-label" style="color:{color};">{group} ({en_label})</div></div>', unsafe_allow_html=True)


def render():
    user = st.session_state.get("user", {})
    if not is_teacher(user.get("roles", "")):
        st.error(UI["dashboard"]["access_denied"])
        return

    st.markdown(_CSS, unsafe_allow_html=True)

    conn = get_connection()
    all_attempts = get_all_attempts(conn=conn)
    averages = get_class_domain_averages(conn=conn)

    st.markdown(f'<div class="dash-hero"><div class="dash-title">📊 Class Dashboard</div><div class="dash-sub">{UI["dashboard"]["subtitle"]}</div></div>', unsafe_allow_html=True)

    if not all_attempts:
        conn.close()
        st.info(UI["dashboard"]["no_data"])
        return

    level_counts = {1: 0, 2: 0, 3: 0, 4: 0}
    for a in all_attempts:
        lvl = a.get("overall_level", 1) or 1
        level_counts[lvl] = level_counts.get(lvl, 0) + 1

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f'<div class="stat-card"><div class="stat-num">{len(all_attempts)}</div><div class="stat-label">Total Students</div></div>', unsafe_allow_html=True)
    for col, lvl in zip([col2, col3, col4, col5], [1, 2, 3, 4]):
        with col:
            color = LEVEL_COLORS[lvl]
            st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:{color};">{level_counts[lvl]}</div><div class="stat-label">{LEVEL_LABELS[lvl]}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">👥 Group Distribution</div>', unsafe_allow_html=True)
    _group_stats(all_attempts)

    st.markdown('<div class="section-title">Filters</div>', unsafe_allow_html=True)
    col_f1, col_f2, col_f3 = st.columns([2, 2, 3])
    with col_f1:
        level_filter = st.selectbox("Filter by level", options=["All", "Emerging", "Developing", "Proficient", "Advanced"], label_visibility="collapsed")
    with col_f2:
        group_filter = st.selectbox("Filter by group", options=["All", "기초", "중간", "상위"], label_visibility="collapsed")
    with col_f3:
        name_filter = st.text_input("Search by name", placeholder="Search student name...", label_visibility="collapsed") or ""

    level_map = {"All": None, "Emerging": 1, "Developing": 2, "Proficient": 3, "Advanced": 4}
    filtered = [
        a for a in all_attempts
        if (level_map[level_filter] is None or a.get("overall_level") == level_map[level_filter])
        and (group_filter == "All" or (a.get("group_label") or classify_group(a.get("overall_level", 1) or 1)) == group_filter)
        and name_filter.lower() in a["student_name"].lower()
    ]
    st.caption(f"Showing {len(filtered)} of {len(all_attempts)} students")

    if filtered:
        st.markdown('<div class="section-title">Student × Domain Heatmap</div>', unsafe_allow_html=True)
        _heatmap(filtered)

    if averages:
        st.markdown('<div class="section-title">Class Average by Domain</div>', unsafe_allow_html=True)
        avg_dict = {DOMAIN_LABELS.get(r["domain_key"], r["domain_key"]): round(r["avg_score"] * 100, 1) for r in averages}
        colors = []
        for v in avg_dict.values():
            if v <= 40: colors.append(LEVEL_COLORS[1])
            elif v <= 60: colors.append(LEVEL_COLORS[2])
            elif v <= 80: colors.append(LEVEL_COLORS[3])
            else: colors.append(LEVEL_COLORS[4])
        fig = go.Figure(go.Bar(x=list(avg_dict.keys()), y=list(avg_dict.values()), marker_color=colors, text=[f"{v}%" for v in avg_dict.values()], textposition="outside"))
        fig.update_layout(yaxis=dict(range=[0, 110], ticksuffix="%", gridcolor="#F1F5F9"), xaxis=dict(tickfont=dict(size=10)), margin=dict(l=10, r=10, t=10, b=10), height=280, paper_bgcolor="white", plot_bgcolor="white", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">Individual Results</div>', unsafe_allow_html=True)
    for attempt in filtered:
        math_scores = json.loads(attempt.get("math_scores") or "{}")
        science_scores = json.loads(attempt.get("science_scores") or "{}")
        overall = attempt.get("overall_level", 1) or 1
        completed = (attempt.get("completed_at") or "")[:16]
        group = attempt.get("group_label") or classify_group(overall)
        atype = attempt.get("assessment_type", "baseline") or "baseline"
        gc = GROUP_COLORS.get(group, "#9CA3AF")
        gbg = GROUP_BG.get(group, "#F9FAFB")
        atc = ATYPE_COLORS.get(atype, "#6366F1")

        with st.expander(f"**{attempt['student_name']}** — {LEVEL_LABELS[overall]} — {completed}"):
            meta_col1, meta_col2, meta_col3 = st.columns(3)
            with meta_col1:
                st.markdown(f'<span style="background:{gbg};color:{gc};border-radius:20px;padding:0.2rem 0.7rem;font-size:0.78rem;font-weight:800;">👥 {group}</span>', unsafe_allow_html=True)
            with meta_col2:
                st.markdown(f'<span style="background:{atc}22;color:{atc};border-radius:20px;padding:0.2rem 0.7rem;font-size:0.78rem;font-weight:800;">📊 {atype.title()}</span>', unsafe_allow_html=True)
            with meta_col3:
                cur_grp_idx = ["기초", "중간", "상위"].index(group) if group in ["기초", "중간", "상위"] else 0
                new_group = st.selectbox("Change group", options=["기초", "중간", "상위"], index=cur_grp_idx, key=f"grp_{attempt['id']}", label_visibility="collapsed")
                if new_group != group:
                    update_group_label(attempt["id"], new_group, conn=conn)
                    st.rerun()

            col_m, col_s = st.columns(2)
            with col_m:
                st.markdown("**Mathematics**")
                for domain, ds in math_scores.items():
                    label = DOMAIN_LABELS.get(domain, domain)
                    pct = int(ds["score"] * 100)
                    lvl_color = LEVEL_COLORS[ds["level"]]
                    st.markdown(f'<div style="font-size:0.83rem;padding:0.2rem 0;"><span style="color:{lvl_color};font-weight:700;">●</span> {label}: <b>{pct}%</b> ({LEVEL_LABELS[ds["level"]]})</div>', unsafe_allow_html=True)
            with col_s:
                st.markdown("**Science**")
                for domain, ds in science_scores.items():
                    label = DOMAIN_LABELS.get(domain, domain)
                    pct = int(ds["score"] * 100)
                    lvl_color = LEVEL_COLORS[ds["level"]]
                    st.markdown(f'<div style="font-size:0.83rem;padding:0.2rem 0;"><span style="color:{lvl_color};font-weight:700;">●</span> {label}: <b>{pct}%</b> ({LEVEL_LABELS[ds["level"]]})</div>', unsafe_allow_html=True)

    conn.close()

    st.markdown("---")
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["Student Name", "Email", "Group", "Assessment Type", "Overall Level", "Completed At"] + [DOMAIN_LABELS.get(d, d) for d in DOMAIN_KEYS])
    for attempt in all_attempts:
        math_s = json.loads(attempt.get("math_scores") or "{}")
        science_s = json.loads(attempt.get("science_scores") or "{}")
        all_s = {**math_s, **science_s}
        grp = attempt.get("group_label") or classify_group(attempt.get("overall_level", 1) or 1)
        writer.writerow([
            attempt["student_name"],
            attempt.get("email", ""),
            grp,
            attempt.get("assessment_type", "baseline"),
            LEVEL_LABELS.get(attempt.get("overall_level", 1), ""),
            (attempt.get("completed_at") or "")[:16],
        ] + [f"{int(all_s.get(d, {}).get('score', 0) * 100)}%" for d in DOMAIN_KEYS])

    col_csv, col_back = st.columns([2, 1])
    with col_csv:
        st.download_button(label=UI["dashboard"]["export_btn"], data=csv_buffer.getvalue(), file_name="class_results.csv", mime="text/csv", use_container_width=True)
    with col_back:
        if st.button(UI["dashboard"]["back_btn"], use_container_width=True):
            st.session_state["page"] = "results"
            st.rerun()
