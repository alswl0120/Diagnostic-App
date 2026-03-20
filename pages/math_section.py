import time
import streamlit as st
import streamlit.components.v1 as components
from assessment.loader import get_ordered_items, get_questions_by_domain
from assessment.session import init_responses, record_response, get_domain_and_local_index
from components.character import character_think
from components.tts import tts_button

SUBJECT = "math"
TOTAL_ITEMS = 20
TIME_LIMIT_SECS = 13 * 60

DOMAIN_LABELS = {
    "number": "Number",
    "algebra": "Algebra",
    "geometry_measurement": "Geometry & Measurement",
    "handling_data": "Handling Data",
}
DOMAIN_ORDER = ["number", "algebra", "geometry_measurement", "handling_data"]
DOMAIN_SIZES = {"number": 6, "algebra": 5, "geometry_measurement": 5, "handling_data": 4}
OPTION_LETTERS = ["A", "B", "C", "D"]

_CSS = """
<style>
.math-header {
    display: flex; justify-content: space-between; align-items: flex-start;
    margin-bottom: 0.6rem;
}
.section-tag {
    background: linear-gradient(135deg, #6366F1, #4F46E5);
    color: white; border-radius: 20px;
    padding: 0.25rem 0.85rem; font-size: 0.78rem; font-weight: 800;
    display: inline-block; margin-bottom: 0.5rem;
}
.progress-row {
    display: flex; justify-content: space-between;
    font-size: 0.82rem; color: #6B7280; font-weight: 700;
    margin-bottom: 0.35rem;
}
.domain-tag {
    background: #EEF2FF; color: #4F46E5;
    border-radius: 20px; padding: 0.18rem 0.65rem;
    font-size: 0.78rem; font-weight: 800;
}
.q-card {
    background: linear-gradient(135deg, #F8FAFF 0%, #EEF2FF 100%);
    border: 2px solid #C7D2FE;
    border-radius: 16px;
    padding: 1.75rem 2rem;
    margin: 0.85rem 0 1.25rem 0;
    position: relative;
}
.q-number {
    font-size: 0.72rem; font-weight: 800; color: #6366F1;
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
.s-dot {
    width: 11px; height: 11px; border-radius: 3px;
    transition: all 0.2s;
}
.s-done { background: #6366F1; }
.s-curr { background: #A5B4FC; }
.s-todo { background: #E5E7EB; }
.stepper-lbl { font-size: 0.62rem; color: #9CA3AF; font-weight: 700; }
.warn-bar {
    background: #FFFBEB; border: 1.5px solid #FDE68A;
    border-radius: 10px; padding: 0.4rem 0.9rem;
    font-size: 0.75rem; font-weight: 700; color: #92400E;
    text-align: center; margin-top: 1rem;
}
</style>
"""


def _timer(started_at: float, limit: int):
    elapsed = int(time.time() - started_at)
    remaining = max(0, limit - elapsed)
    urgent = remaining < 120
    color = "#EF4444" if urgent else "#4F46E5"
    bg = "#FEF2F2" if urgent else "#EEF2FF"
    components.html(f"""
        <div style="text-align:right; padding:0 0 4px 0;">
          <span style="font-family:'Nunito',sans-serif; font-size:0.95rem; font-weight:800;
                       color:{color}; background:{bg}; padding:0.3rem 0.75rem;
                       border-radius:20px; border:2px solid {color}22;">
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
                dots.append('<div class="s-dot s-done"></div>')
            elif j == info["cur"]:
                dots.append('<div class="s-dot s-curr"></div>')
            else:
                dots.append('<div class="s-dot s-todo"></div>')
        short = DOMAIN_LABELS.get(d, d).split()[0]
        dots_html = "".join(dots)
        parts.append(f'<div class="stepper-group"><div class="stepper-dots">{dots_html}</div><div class="stepper-lbl">{short}</div></div>')
    st.markdown('<div class="stepper-row">' + "".join(parts) + '</div>', unsafe_allow_html=True)


def render():
    st.markdown(_CSS, unsafe_allow_html=True)

    if "math_responses" not in st.session_state:
        grouped = get_questions_by_domain(SUBJECT)
        st.session_state["math_responses"] = init_responses(SUBJECT, grouped)
        st.session_state["math_item_index"] = 0
        st.session_state["math_started_at"] = time.time()

    ordered = get_ordered_items(SUBJECT)
    idx = st.session_state["math_item_index"]
    item = ordered[idx]
    domain, local_idx = get_domain_and_local_index(ordered, idx)
    sel_key = f"math_sel_{idx}"
    current_sel = st.session_state.get(sel_key)

    col_info, col_timer = st.columns([3, 1])
    with col_info:
        st.markdown('<span class="section-tag">🔢 Mathematics</span>', unsafe_allow_html=True)
        dlabel = DOMAIN_LABELS.get(domain, domain)
        st.markdown(f'<div class="progress-row"><span>Question <b>{idx + 1}</b> / {TOTAL_ITEMS}</span><span class="domain-tag">{dlabel}</span></div>', unsafe_allow_html=True)
        st.progress(idx / TOTAL_ITEMS)
    with col_timer:
        _timer(st.session_state.get("math_started_at", time.time()), TIME_LIMIT_SECS)

    _stepper(ordered, idx)

    stem = item['stem']
    st.markdown(f'<div class="q-card"><div class="q-number">Question {idx + 1} of {TOTAL_ITEMS}</div><div class="q-stem">{stem}</div></div>', unsafe_allow_html=True)
    tts_button(stem, color="#6366F1", bg="#EEF2FF", border="#C7D2FE")

    col_ans, col_char = st.columns([3, 1])
    with col_ans:
        st.markdown('<div class="answer-label">Choose your answer</div>', unsafe_allow_html=True)
        for i, opt in enumerate(item["options"]):
            is_sel = current_sel == i
            label = f"✓  {opt}" if is_sel else opt
            btn_type = "primary" if is_sel else "secondary"
            if st.button(label, key=f"math_opt_{idx}_{i}", type=btn_type, use_container_width=True):
                st.session_state[sel_key] = i
                st.rerun()
    with col_char:
        msgs = ["Think carefully! 🤔", "You've got this! 💪", "Take your time! ⏳", "Almost there! 🌟"]
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
            record_response(st.session_state["math_responses"], domain, local_idx, current_sel)
            st.session_state["math_item_index"] = idx + 1
            if idx + 1 >= TOTAL_ITEMS:
                st.session_state["page"] = "science"
            st.rerun()
    if idx > 0:
        with col2:
            if st.button("← Back", use_container_width=True):
                st.session_state["math_item_index"] = idx - 1
                st.rerun()

    st.markdown('<div class="warn-bar">⚠️ Do not refresh the page — your answers will be lost</div>', unsafe_allow_html=True)
