import streamlit as st
from pathlib import Path
from core.auth import get_user, get_dev_user, is_teacher
from core.database import init_db, DB_PATH, get_pending_sync_items, get_connection
from core.sync import try_sync

st.set_page_config(
    page_title="Learning Level Assessment",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif !important;
}
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stDeployButton { display: none; }
[data-testid="collapsedControl"] { display: none; }

/* Page background */
.stApp {
    background: #F0F2F8;
}
.block-container {
    background: white;
    border-radius: 16px;
    padding: 2rem 2.5rem !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.08);
    max-width: 780px !important;
    margin-top: 1.5rem !important;
    margin-bottom: 1.5rem !important;
}

/* Global button styles */
div[data-testid="stButton"] button {
    border-radius: 14px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    transition: all 0.15s ease !important;
    cursor: pointer !important;
}
/* Primary buttons */
div[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
    border: none !important;
    color: white !important;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
    min-height: 48px !important;
}
div[data-testid="stButton"] button[kind="primary"]:hover {
    background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%) !important;
    box-shadow: 0 6px 18px rgba(99, 102, 241, 0.45) !important;
    transform: translateY(-1px) !important;
}
/* Secondary buttons */
div[data-testid="stButton"] button[kind="secondary"] {
    background: white !important;
    border: 2.5px solid #E5E7EB !important;
    color: #374151 !important;
    min-height: 48px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
}
div[data-testid="stButton"] button[kind="secondary"]:hover {
    border-color: #6366F1 !important;
    background: #EEF2FF !important;
    color: #4338CA !important;
    box-shadow: 0 2px 10px rgba(99,102,241,0.15) !important;
}
/* Answer card buttons — full-width secondary */
div[data-testid="stButton"] button[kind="secondary"][data-answer="true"] {
    min-height: 62px !important;
    text-align: left !important;
    padding: 0.9rem 1.25rem !important;
    font-size: 1.02rem !important;
    border-radius: 14px !important;
    border: 2.5px solid #E5E7EB !important;
}

/* Progress bar */
div[data-testid="stProgress"] > div > div > div > div {
    background: linear-gradient(90deg, #6366F1, #818CF8) !important;
    border-radius: 8px !important;
}
div[data-testid="stProgress"] > div > div {
    height: 10px !important;
    border-radius: 8px !important;
    background: #E5E7EB !important;
}

/* Expander */
div[data-testid="stExpander"] {
    border: 1.5px solid #E5E7EB !important;
    border-radius: 12px !important;
}

/* Nav bar */
.nav-bar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.5rem 0 1rem 0;
    border-bottom: 2px solid #F3F4F6;
    margin-bottom: 1.75rem;
}
.nav-logo {
    font-size: 1rem; font-weight: 900; color: #4F46E5;
    letter-spacing: -0.3px;
}
.nav-steps { display: flex; align-items: center; gap: 0.2rem; }
.nav-step {
    font-size: 0.75rem; color: #9CA3AF; font-weight: 700;
    padding: 0.2rem 0.55rem; border-radius: 20px;
}
.nav-step-active {
    font-size: 0.75rem; color: #4F46E5; font-weight: 800;
    padding: 0.2rem 0.55rem; border-radius: 20px;
    background: #EEF2FF;
}
.nav-step-done {
    font-size: 0.75rem; color: #10B981; font-weight: 800;
    padding: 0.2rem 0.55rem; border-radius: 20px;
    background: #ECFDF5;
}
.nav-sep { color: #D1D5DB; font-size: 0.75rem; margin: 0 0.1rem; }
</style>
""", unsafe_allow_html=True)


def _offline_indicator():
    try:
        conn = get_connection()
        pending = get_pending_sync_items(conn=conn)
        conn.close()
        n = len(pending)
    except Exception:
        n = 0
    if n > 0:
        st.markdown(f'<div style="background:#FFFBEB;border:1.5px solid #FDE68A;border-radius:8px;padding:0.35rem 0.9rem;font-size:0.75rem;font-weight:700;color:#92400E;margin-bottom:0.5rem;">📡 {n} item(s) pending sync · Will upload automatically when online</div>', unsafe_allow_html=True)


def _init():
    Path("/app/storage").mkdir(parents=True, exist_ok=True)
    init_db(DB_PATH)

    if "user" not in st.session_state:
        dev = get_dev_user()
        if dev:
            st.session_state["user"] = dev
        else:
            try:
                user = get_user(dict(st.context.headers))
            except Exception:
                user = {"user_id": "anonymous", "email": "", "name": "", "roles": ""}
            st.session_state["user"] = user

    if "page" not in st.session_state:
        st.session_state["page"] = "home"

    if not st.session_state.get("_synced_this_session"):
        try:
            conn = get_connection()
            try_sync(conn=conn)
            conn.close()
        except Exception:
            pass
        st.session_state["_synced_this_session"] = True


def _nav_bar(page: str):
    steps = [("home", "Start"), ("math", "🔢 Math"), ("science", "🔬 Science"), ("results", "✨ Results")]
    order = {"home": 0, "math": 1, "science": 2, "results": 3, "dashboard": 3}
    cur = order.get(page, 0)

    parts = []
    for i, (key, label) in enumerate(steps):
        if i < cur:
            parts.append(f'<span class="nav-step-done">✓ {label}</span>')
        elif i == cur:
            parts.append(f'<span class="nav-step-active">{label}</span>')
        else:
            parts.append(f'<span class="nav-step">{label}</span>')
        if i < len(steps) - 1:
            parts.append('<span class="nav-sep">›</span>')

    user = st.session_state.get("user", {})
    badge = ""
    if is_teacher(user.get("roles", "")):
        badge = '<span style="font-size:0.72rem;background:#EEF2FF;color:#4F46E5;padding:0.2rem 0.6rem;border-radius:20px;font-weight:800;">👩‍🏫 Teacher</span>'

    st.markdown(f"""
        <div class="nav-bar">
            <div class="nav-logo">📋 Assessment</div>
            <div class="nav-steps">{"".join(parts)}</div>
            {badge}
        </div>
    """, unsafe_allow_html=True)


def main():
    _init()
    page = st.session_state["page"]
    _nav_bar(page)
    _offline_indicator()

    if page == "home":
        from pages.home import render
        render()
    elif page == "math":
        from pages.math_section import render
        render()
    elif page == "science":
        from pages.science_section import render
        render()
    elif page == "results":
        from pages.results import render
        render()
    elif page == "progress":
        from pages.progress import render
        render()
    elif page == "dashboard":
        from pages.dashboard import render
        render()
    else:
        st.session_state["page"] = "home"
        st.rerun()


if __name__ == "__main__" or True:
    main()
