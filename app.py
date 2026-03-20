import streamlit as st
from pathlib import Path
from core.auth import get_user, get_dev_user
from core.database import init_db, DB_PATH

st.set_page_config(
    page_title="Learning Level Assessment",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
    <style>
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stDeployButton { display: none; }
    </style>
""", unsafe_allow_html=True)


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
                user = {"user_id": None, "email": None, "name": None, "roles": ""}
            st.session_state["user"] = user

    if "page" not in st.session_state:
        st.session_state["page"] = "home"


def main():
    _init()
    page = st.session_state["page"]

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
    elif page == "dashboard":
        from pages.dashboard import render
        render()
    else:
        st.session_state["page"] = "home"
        st.rerun()


if __name__ == "__main__" or True:
    main()
