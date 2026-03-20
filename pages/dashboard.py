import json
import io
import csv
import streamlit as st
from core.database import get_all_attempts, get_class_domain_averages, get_connection
from core.auth import is_teacher

LEVEL_LABELS = {1: "Emerging", 2: "Developing", 3: "Proficient", 4: "Advanced"}
DOMAIN_LABELS = {
    "number": "Number", "algebra": "Algebra",
    "geometry_measurement": "Geometry & Measurement", "handling_data": "Handling Data",
    "diversity_matter": "Diversity of Matter", "cycles": "Cycles",
    "systems": "Systems", "forces_energy": "Forces and Energy",
    "humans_environment": "Humans and the Environment",
}


def render():
    user = st.session_state.get("user", {})
    if not is_teacher(user.get("roles", "")):
        st.error("Access restricted to teachers.")
        return

    st.markdown("## Class Dashboard")
    st.markdown("Overview of all completed assessments.")

    conn = get_connection()
    attempts = get_all_attempts(conn=conn)
    averages = get_class_domain_averages(conn=conn)
    conn.close()

    if not attempts:
        st.info("No completed assessments yet.")
        return

    st.markdown(f"**Total students assessed:** {len(attempts)}")
    st.markdown("---")

    if averages:
        st.markdown("#### Class Average by Domain")
        chart_data = {
            DOMAIN_LABELS.get(row["domain_key"], row["domain_key"]): round(row["avg_score"] * 100, 1)
            for row in averages
        }
        st.bar_chart(chart_data)
        st.markdown("---")

    st.markdown("#### Individual Results")
    for attempt in attempts:
        math_scores = json.loads(attempt.get("math_scores") or "{}")
        science_scores = json.loads(attempt.get("science_scores") or "{}")
        overall = attempt.get("overall_level", 1)
        completed = (attempt.get("completed_at") or "")[:16]

        with st.expander(f"{attempt['student_name']} — {LEVEL_LABELS.get(overall, '?')} — {completed}"):
            col_m, col_s = st.columns(2)
            with col_m:
                st.markdown("**Mathematics**")
                for domain, ds in math_scores.items():
                    label = DOMAIN_LABELS.get(domain, domain)
                    st.markdown(f"- {label}: {int(ds['score']*100)}% ({LEVEL_LABELS.get(ds['level'], '?')})")
            with col_s:
                st.markdown("**Science**")
                for domain, ds in science_scores.items():
                    label = DOMAIN_LABELS.get(domain, domain)
                    st.markdown(f"- {label}: {int(ds['score']*100)}% ({LEVEL_LABELS.get(ds['level'], '?')})")

    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["Student Name", "Email", "Overall Level", "Completed At",
                     "Number", "Algebra", "Geometry & Measurement", "Handling Data",
                     "Diversity of Matter", "Cycles", "Systems", "Forces and Energy", "Humans and Environment"])

    domain_keys = ["number", "algebra", "geometry_measurement", "handling_data",
                   "diversity_matter", "cycles", "systems", "forces_energy", "humans_environment"]

    for attempt in attempts:
        math_scores = json.loads(attempt.get("math_scores") or "{}")
        science_scores = json.loads(attempt.get("science_scores") or "{}")
        all_scores = {**math_scores, **science_scores}
        row = [
            attempt["student_name"],
            attempt.get("email", ""),
            LEVEL_LABELS.get(attempt.get("overall_level", 1), ""),
            (attempt.get("completed_at") or "")[:16],
        ] + [f"{int(all_scores.get(d, {}).get('score', 0) * 100)}%" for d in domain_keys]
        writer.writerow(row)

    st.download_button(
        label="Export All Results (CSV)",
        data=csv_buffer.getvalue(),
        file_name="class_results.csv",
        mime="text/csv",
    )

    if st.button("← Back"):
        st.session_state["page"] = "results"
        st.rerun()
