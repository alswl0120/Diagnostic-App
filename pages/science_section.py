import time
import streamlit as st
import streamlit.components.v1 as components
from assessment.loader import get_ordered_items, get_questions_by_domain
from assessment.session import init_responses, record_response, get_domain_and_local_index
from components.character import character_think
from components.tts import tts_button
from core.scoring import score_section, compute_overall_level
from core.database import save_attempt_results, save_domain_scores, get_connection

SUBJECT = "science"
TOTAL_ITEMS = 18
TIME_LIMIT_SECS = 15 * 60

DOMAIN_LABELS = {
    "diversity_matter": "Diversity of Matter",
    "cycles": "Cycles",
    "systems": "Systems",
    "forces_energy": "Forces and Energy",
    "humans_environment": "Humans and the Environment",
}
DOMAIN_ORDER = ["diversity_matter", "cycles", "systems", "forces_energy", "humans_environment"]
DOMAIN_SIZES = {"diversity_matter": 3, "cycles": 4, "systems": 4, "forces_energy": 4, "humans_environment": 3}
OPTION_LETTERS = ["A", "B", "C", "D"]

_CSS = """
<style>
.science-header {
    display: flex; justify-content: space-between; align-items: flex-start;
    margin-bottom: 0.6rem;
}
.section-tag-sci {
    background: linear-gradient(135deg, #10B981, #059669);
    color: white; border-radius: 20px;
    padding: 0.25rem 0.85rem; font-size: 0.78rem; font-weight: 800;
    display: inline-block; margin-bottom: 0.5rem;
}
.progress-row {
    display: flex; justify-content: space-between;
    font-size: 0.82rem; color: #6B7280; font-weight: 700;
    margin-bottom: 0.35rem;
}
.domain-tag-sci {
    background: #ECFDF5; color: #065F46;
    border-radius: 20px; padding: 0.18rem 0.65rem;
    font-size: 0.78rem; font-weight: 800;
}
.q-card-sci {
    background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
    border: 2px solid #A7F3D0;
    border-radius: 16px;
    padding: 1.75rem 2rem;
    margin: 0.85rem 0 1.25rem 0;
}
.q-number-sci {
    font-size: 0.72rem; font-weight: 800; color: #059669;
    text-transform: uppercase; letter-spacing: 0.08em;
    margin-bottom: 0.6rem;
}
.q-stem {
    font-size: 1.15rem; font-weight: 800; color: #1F2937; line-height: 1.6;
}
.answer-label {
    font-size: 0.8rem; font-weight: 800; color: #6B7280;
    text-transform: uppercase; letter-spacing: 0.06em;
    margin-bottom: 0.6rem;
}
.stepper-row {
    display: flex; gap: 0.75rem; margin: 0.75rem 0 1.25rem 0;
    flex-wrap: wrap; align-items: flex-end;
}
.stepper-group { display: flex; flex-direction: column; gap: 0.2rem; align-items: center; }
.stepper-dots { display: flex; gap: 0.18rem; }
.s-dot { width: 11px; height: 11px; border-radius: 3px; }
.s-done-sci { background: #10B981; }
.s-curr-sci { background: #6EE7B7; }
.s-todo { background: #E5E7EB; }
.stepper-lbl { font-size: 0.62rem; color: #9CA3AF; font-weight: 700; }
.warn-bar {
    background: #FFFBEB; border: 1.5px solid #FDE68A;
    border-radius: 10px; padding: 0.4rem 0.9rem;
    font-size: 0.75rem; font-weight: 700; color: #92400E;
    text-align: center; margin-top: 1rem;
}
.transition-box {
    text-align: center; padding: 3rem 1rem 2.5rem;
}
.transition-icon { font-size: 4rem; margin-bottom: 1rem; }
.transition-title {
    font-size: 1.8rem; font-weight: 900; color: #1F2937;
    margin-bottom: 0.6rem;
}
.transition-body {
    font-size: 1rem; color: #6B7280; font-weight: 600;
    line-height: 1.65; margin-bottom: 0.5rem;
}
.transition-cards {
    display: flex; justify-content: center; gap: 1rem;
    margin: 1.5rem 0;
}
.transition-card {
    background: #F8FAFF; border: 2px solid #C7D2FE;
    border-radius: 14px; padding: 1rem 1.5rem; text-align: center;
    min-width: 120px;
}
.tc-num { font-size: 1.6rem; font-weight: 900; color: #4F46E5; }
.tc-label { font-size: 0.78rem; color: #6B7280; font-weight: 700; }
</style>
"""


def _timer(started_at: float, limit: int):
    elapsed = int(time.time() - started_at)
    remaining = max(0, limit - elapsed)
    urgent = remaining < 120
    color = "#EF4444" if urgent else "#059669"
    bg = "#FEF2F2" if urgent else "#ECFDF5"
    components.html(f"""
        <div style="text-align:right; padding:0 0 4px 0;">
          <span style="font-family:'Nunito',sans-serif; font-size:0.95rem; font-weight:800;
                       color:{color}; background:{bg}; padding:0.3rem 0.75rem;
                       border-radius:20px; border:2px solid {color}33;">
            ⏱ <span id="t">{remaining//60:02d}:{remaining%60:02d}</span>
          </span>
        </div>
        <script>
          var r={remaining};
          (function tick(){{
            r--;
            if(r<0)r=0;
            var el=document.getElementById('t');
            if(el){{
              el.textContent=String(Math.floor(r/60)).padStart(2,'0')+':'+String(r%60).padStart(2,'0');
              if(r<120){{el.parentElement.style.color='#EF4444';el.parentElement.style.background='#FEF2F2';}}
            }}
            if(r>0)setTimeout(tick,1000);
          }})();
        </script>
    """, height=40)


def _stepper(ordered: list, current_idx: int):
    state = {}
    for i, item in enumerate(ordered):
        d = item["domain"]
        if d not in state:
            state[d] = {"done": 0, "cur": -1, "size": DOMAIN_SIZES.get(d, 0)}
        if i < current_idx:
            state[d]["done"] += 1
        elif i == current_idx:
            state[d]["cur"] = state[d]["done"]

    parts = []
    for d in DOMAIN_ORDER:
        if d not in state:
            continue
        info = state[d]
        dots = []
        for j in range(info["size"]):
            if j < info["done"]:
                dots.append('<div class="s-dot s-done-sci"></div>')
            elif j == info["cur"]:
                dots.append('<div class="s-dot s-curr-sci"></div>')
            else:
                dots.append('<div class="s-dot s-todo"></div>')
        short = DOMAIN_LABELS.get(d, d).split()[0]
        dots_html = "".join(dots)
        parts.append(f'<div class="stepper-group"><div class="stepper-dots">{dots_html}</div><div class="stepper-lbl">{short}</div></div>')
    st.markdown('<div class="stepper-row">' + "".join(parts) + '</div>', unsafe_allow_html=True)


def render():
    st.markdown(_CSS, unsafe_allow_html=True)

    if "science_responses" not in st.session_state:
        grouped = get_questions_by_domain(SUBJECT)
        st.session_state["science_responses"] = init_responses(SUBJECT, grouped)
        st.session_state["science_item_index"] = 0
        st.session_state["_show_science_intro"] = True

    if st.session_state.get("_show_science_intro", False):
        _show_transition()
        return

    ordered = get_ordered_items(SUBJECT)
    idx = st.session_state["science_item_index"]
    item = ordered[idx]
    domain, local_idx = get_domain_and_local_index(ordered, idx)
    sel_key = f"sci_sel_{idx}"
    current_sel = st.session_state.get(sel_key)

    col_info, col_timer = st.columns([3, 1])
    with col_info:
        st.markdown('<span class="section-tag-sci">🔬 Science</span>', unsafe_allow_html=True)
        dlabel = DOMAIN_LABELS.get(domain, domain)
        st.markdown(f'<div class="progress-row"><span>Question <b>{idx + 1}</b> / {TOTAL_ITEMS}</span><span class="domain-tag-sci">{dlabel}</span></div>', unsafe_allow_html=True)
        st.progress(idx / TOTAL_ITEMS)
    with col_timer:
        _timer(st.session_state.get("science_started_at", time.time()), TIME_LIMIT_SECS)

    _stepper(ordered, idx)

    stem = item['stem']
    st.markdown(f'<div class="q-card-sci"><div class="q-number-sci">Question {idx + 1} of {TOTAL_ITEMS}</div><div class="q-stem">{stem}</div></div>', unsafe_allow_html=True)
    tts_button(stem, color="#059669", bg="#ECFDF5", border="#A7F3D0")

    col_ans, col_char = st.columns([3, 1])
    with col_ans:
        st.markdown('<div class="answer-label">Choose your answer</div>', unsafe_allow_html=True)
        for i, opt in enumerate(item["options"]):
            is_sel = current_sel == i
            label = f"✓  {opt}" if is_sel else opt
            btn_type = "primary" if is_sel else "secondary"
            if st.button(label, key=f"sci_opt_{idx}_{i}", type=btn_type, use_container_width=True):
                st.session_state[sel_key] = i
                st.rerun()
    with col_char:
        msgs = ["Great question! 🔬", "Think it through! 🌿", "You know this! 💡", "Almost done! 🌟"]
        character_think(msgs[idx % len(msgs)], seed=idx)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([3, 2, 4])
    with col1:
        if st.button(
            "Next →",
            type="primary",
            disabled=current_sel is None,
            use_container_width=True,
        ):
            record_response(st.session_state["science_responses"], domain, local_idx, current_sel)
            st.session_state["science_item_index"] = idx + 1
            if idx + 1 >= TOTAL_ITEMS:
                _finalize()
            st.rerun()
    if idx > 0:
        with col2:
            if st.button("← Back", use_container_width=True):
                st.session_state["science_item_index"] = idx - 1
                st.rerun()

    st.markdown('<div class="warn-bar">⚠️ Do not refresh the page — your answers will be lost</div>', unsafe_allow_html=True)


def _show_transition():
    st.markdown("""
        <div class="transition-box">
            <div class="transition-icon">🎉</div>
            <div class="transition-title">Mathematics Complete!</div>
            <div class="transition-body">
                Amazing effort! You've finished all 20 Math questions.<br>
                Now let's move on to the Science section.
            </div>
            <div class="transition-cards">
                <div class="transition-card">
                    <div class="tc-num">18</div>
                    <div class="tc-label">Questions</div>
                </div>
                <div class="transition-card">
                    <div class="tc-num">~15</div>
                    <div class="tc-label">Minutes</div>
                </div>
                <div class="transition-card">
                    <div class="tc-num">5</div>
                    <div class="tc-label">Topics</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Continue to Science 🔬", type="primary", use_container_width=True):
            st.session_state["_show_science_intro"] = False
            st.session_state["science_started_at"] = time.time()
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
        conn=conn,
    )
    save_domain_scores(attempt_id, {"math": math_scores, "science": science_scores}, conn=conn)
    conn.close()

    st.session_state["math_scores"] = math_scores
    st.session_state["science_scores"] = science_scores
    st.session_state["overall_level"] = overall_level
    st.session_state["math_ordered"] = get_ordered_items("math")
    st.session_state["science_ordered"] = get_ordered_items("science")
    st.session_state["page"] = "results"
