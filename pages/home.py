import streamlit as st
from core.database import upsert_user, create_attempt, get_connection, init_db


def render():
    st.markdown("""
        <style>
        .main-title { font-size: 2rem; font-weight: 700; color: #1E3A5F; margin-bottom: 0.2rem; }
        .sub-title { font-size: 1rem; color: #64748B; margin-bottom: 2rem; }
        .info-box { background: #F0F7FF; border-left: 4px solid #3B82F6; padding: 1rem; border-radius: 4px; margin-bottom: 1.5rem; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-title">Learning Level Assessment</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Ghana Junior High School — Grade 1</div>', unsafe_allow_html=True)

    st.markdown("""
        <div class="info-box">
        This assessment helps identify your learning level in <b>Mathematics</b> and <b>Science</b>.
        It is not a test — there are no pass or fail marks. Be honest and do your best.<br><br>
        <b>Time:</b> About 28 minutes &nbsp;|&nbsp; <b>Mathematics:</b> 20 questions &nbsp;|&nbsp; <b>Science:</b> 18 questions
        </div>
    """, unsafe_allow_html=True)

    user = st.session_state.get("user", {})
    default_name = user.get("name", "")

    name = st.text_input("Enter your name to begin", value=default_name, placeholder="e.g. Ama Owusu")

    if st.button("Start Assessment", type="primary", disabled=not name.strip()):
        conn = get_connection()
        upsert_user(
            user.get("user_id", "anonymous"),
            user.get("email", ""),
            name.strip(),
            "student",
            conn=conn
        )
        attempt_id = create_attempt(user.get("user_id", "anonymous"), name.strip(), conn=conn)
        conn.close()

        st.session_state["student_name"] = name.strip()
        st.session_state["attempt_id"] = attempt_id
        st.session_state["page"] = "math"
        st.rerun()
