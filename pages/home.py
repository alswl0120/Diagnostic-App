import json
import streamlit as st
from core.database import upsert_user, create_attempt, get_connection, count_attempts_by_name, get_latest_incomplete_attempt
from components.character import character_wave


_CSS = """
<style>
.hero {
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #6366F1 100%);
    border-radius: 20px;
    padding: 2.5rem 2rem;
    text-align: center;
    margin-bottom: 1.75rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute; top: -40px; right: -40px;
    width: 200px; height: 200px;
    background: rgba(255,255,255,0.06);
    border-radius: 50%;
}
.hero::after {
    content: '';
    position: absolute; bottom: -60px; left: -30px;
    width: 160px; height: 160px;
    background: rgba(255,255,255,0.05);
    border-radius: 50%;
}
.hero-icon { font-size: 3.5rem; margin-bottom: 0.6rem; }
.hero-title {
    font-size: 2rem; font-weight: 900; color: white;
    margin-bottom: 0.4rem; line-height: 1.2;
}
.hero-sub {
    font-size: 0.95rem; color: rgba(255,255,255,0.8);
    font-weight: 600;
}
.info-banner {
    background: #FFFBEB; border: 1.5px solid #FDE68A;
    border-radius: 12px; padding: 1rem 1.25rem;
    margin-bottom: 1.5rem; font-size: 0.9rem;
    color: #78350F; line-height: 1.65;
}
.subject-card {
    border-radius: 16px;
    padding: 1.4rem 1.2rem;
    margin-bottom: 0.5rem;
    position: relative; overflow: hidden;
}
.subject-card-math {
    background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
    border: 2px solid #C7D2FE;
}
.subject-card-science {
    background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
    border: 2px solid #A7F3D0;
}
.subject-icon { font-size: 2.2rem; margin-bottom: 0.5rem; }
.subject-title {
    font-size: 1.05rem; font-weight: 900;
    margin-bottom: 0.2rem;
}
.subject-title-math { color: #3730A3; }
.subject-title-science { color: #065F46; }
.subject-meta { font-size: 0.8rem; font-weight: 700; color: #6B7280; margin-bottom: 0.6rem; }
.domain-chip {
    display: inline-block; border-radius: 20px;
    padding: 0.15rem 0.55rem; font-size: 0.72rem; font-weight: 700;
    margin: 0.1rem;
}
.chip-math { background: #C7D2FE; color: #3730A3; }
.chip-science { background: #A7F3D0; color: #065F46; }
.name-label {
    font-size: 0.88rem; font-weight: 800; color: #374151;
    margin-bottom: 0.4rem; display: block;
}
.total-bar {
    display: flex; gap: 0.5rem; justify-content: center;
    margin-bottom: 1.5rem;
}
.total-chip {
    background: rgba(255,255,255,0.2); color: white;
    border-radius: 20px; padding: 0.25rem 0.75rem;
    font-size: 0.82rem; font-weight: 700;
    border: 1.5px solid rgba(255,255,255,0.3);
}
</style>
"""


def render():
    st.markdown(_CSS, unsafe_allow_html=True)

    st.markdown('<div class="hero"><div class="hero-icon">📋</div><div class="hero-title">Learning Level Assessment</div><div class="hero-sub">Discover your strengths and areas to grow</div><div class="total-bar" style="margin-top:1rem;"><span class="total-chip">⏱ ~28 minutes</span><span class="total-chip">📝 38 questions</span><span class="total-chip">🎯 2 subjects</span></div></div>', unsafe_allow_html=True)

    col_char, col_info = st.columns([1, 2])
    with col_char:
        character_wave("Hi! Ready to discover your learning level? 🚀", seed=4)
    with col_info:
        st.markdown('<div class="info-banner">💡 This is <b>not a test</b> — there are no pass or fail marks.<br>Your answers help us understand what kind of support you need.<br>Be honest and do your best — every question matters!</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="subject-card subject-card-math"><div class="subject-icon">🔢</div><div class="subject-title subject-title-math">Mathematics</div><div class="subject-meta">20 questions · ~13 min</div><div><span class="domain-chip chip-math">Number</span><span class="domain-chip chip-math">Algebra</span><span class="domain-chip chip-math">Geometry</span><span class="domain-chip chip-math">Data</span></div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="subject-card subject-card-science"><div class="subject-icon">🔬</div><div class="subject-title subject-title-science">Science</div><div class="subject-meta">18 questions · ~15 min</div><div><span class="domain-chip chip-science">Matter</span><span class="domain-chip chip-science">Cycles</span><span class="domain-chip chip-science">Systems</span><span class="domain-chip chip-science">Energy</span><span class="domain-chip chip-science">Environment</span></div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
    st.markdown('<span class="name-label">✏️ Enter your full name to begin</span>', unsafe_allow_html=True)

    user = st.session_state.get("user", {})
    name = st.text_input(
        "name",
        value=user.get("name") or "",
        placeholder="e.g. Ama Owusu",
        label_visibility="collapsed",
    ) or ""

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    incomplete = None
    if name.strip():
        conn = get_connection()
        prev_count = count_attempts_by_name(name.strip(), conn=conn)
        incomplete = get_latest_incomplete_attempt(name.strip(), conn=conn)
        conn.close()
        if prev_count == 0 and not incomplete:
            atype = "baseline"
            atype_label = "🟢 Baseline (1st assessment)"
        elif prev_count == 1:
            atype = "midline"
            atype_label = "🟡 Midline (2nd assessment)"
        else:
            atype = "endline"
            atype_label = f"🔵 Endline (assessment #{prev_count + 1})"
        if not incomplete:
            st.markdown(f'<div style="background:#F8FAFC;border:1.5px solid #E2E8F0;border-radius:10px;padding:0.5rem 1rem;font-size:0.82rem;font-weight:700;color:#374151;margin-bottom:0.75rem;">📊 Assessment type: <span style="color:#4F46E5;">{atype_label}</span></div>', unsafe_allow_html=True)
    else:
        atype = "baseline"

    if incomplete:
        math_idx = incomplete.get("progress_math_idx", 0)
        sci_idx = incomplete.get("progress_sci_idx", 0)
        subject = "Science" if math_idx >= 20 else "Mathematics"
        q_done = min(math_idx, 20) + min(sci_idx, 18)
        st.markdown(f'<div style="background:#FFF7ED;border:2px solid #FED7AA;border-radius:12px;padding:0.75rem 1.1rem;margin-bottom:0.9rem;"><div style="font-size:0.88rem;font-weight:800;color:#92400E;">⚡ Unfinished assessment found</div><div style="font-size:0.82rem;color:#78350F;margin-top:0.2rem;">{q_done} / 38 questions completed &nbsp;·&nbsp; Next up: {subject}</div></div>', unsafe_allow_html=True)
        col_resume, col_new = st.columns(2)
        with col_resume:
            if st.button("▶ Resume", type="primary", use_container_width=True):
                math_raw = json.loads(incomplete.get("math_raw") or "{}")
                conn = get_connection()
                upsert_user(user.get("user_id") or "anonymous", user.get("email") or "", name.strip(), "student", conn=conn)
                conn.close()
                st.session_state["student_name"] = name.strip()
                st.session_state["attempt_id"] = incomplete["id"]
                st.session_state["assessment_type"] = incomplete.get("assessment_type", "baseline")
                st.session_state["math_responses"] = math_raw if math_raw else None
                st.session_state["math_item_index"] = math_idx
                if math_idx >= 20:
                    sci_raw = json.loads(incomplete.get("science_raw") or "{}")
                    st.session_state["science_responses"] = sci_raw if sci_raw else None
                    st.session_state["science_item_index"] = sci_idx
                    st.session_state["page"] = "science"
                else:
                    st.session_state["page"] = "math"
                st.rerun()
        with col_new:
            if st.button("🆕 New Assessment", use_container_width=True):
                incomplete = None
                conn = get_connection()
                upsert_user(user.get("user_id") or "anonymous", user.get("email") or "", name.strip(), "student", conn=conn)
                attempt_id = create_attempt(user.get("user_id") or "anonymous", name.strip(), assessment_type=atype, conn=conn)
                conn.close()
                st.session_state["student_name"] = name.strip()
                st.session_state["attempt_id"] = attempt_id
                st.session_state["assessment_type"] = atype
                st.session_state["page"] = "math"
                st.rerun()
    else:
        col_start, col_prog = st.columns([3, 1])
        with col_start:
            if st.button(
                "🚀  Let's Begin!" if name.strip() else "Enter your name above to start",
                type="primary",
                disabled=not name.strip(),
                use_container_width=True,
            ):
                conn = get_connection()
                upsert_user(user.get("user_id") or "anonymous", user.get("email") or "", name.strip(), "student", conn=conn)
                attempt_id = create_attempt(user.get("user_id") or "anonymous", name.strip(), assessment_type=atype, conn=conn)
                conn.close()
                st.session_state["student_name"] = name.strip()
                st.session_state["attempt_id"] = attempt_id
                st.session_state["assessment_type"] = atype
                st.session_state["page"] = "math"
                st.rerun()
        if name.strip() and prev_count > 0:
            with col_prog:
                if st.button("📈 Progress", use_container_width=True):
                    st.session_state["student_name"] = name.strip()
                    st.session_state["page"] = "progress"
                    st.rerun()
