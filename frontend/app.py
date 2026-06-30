# frontend/app.py
import streamlit as st

from claude_client import generate_sql, explain_results, generate_insight_report
from sql_guard import validate_query, UnsafeQueryError
from db import run_query

st.set_page_config(page_title="Synthea Healthcare Analytics", layout="wide")
st.title("Synthea Healthcare Analytics")

tab_chat, tab_insights = st.tabs(["Chat", "Insights"])

with tab_chat:
    st.subheader("Ask a question about the patient population")
    question = st.text_input("Question", placeholder="e.g. How many high utilizers are there?")

    if st.button("Ask") and question:
        with st.spinner("Generating SQL..."):
            try:
                sql = generate_sql(question)
            except Exception as e:
                st.error(f"Failed to generate SQL: {e}")
                sql = None

        if sql:
            st.code(sql, language="sql")

            try:
                safe_sql = validate_query(sql)
            except UnsafeQueryError as e:
                st.error(f"Query blocked by safety check: {e}")
                safe_sql = None

            if safe_sql:
                with st.spinner("Running query..."):
                    try:
                        result = run_query(safe_sql)
                    except Exception as e:
                        st.error(f"Query execution failed: {e}")
                        result = None

                if result is not None:
                    st.dataframe(result)
                    with st.spinner("Generating explanation..."):
                        explanation = explain_results(question, safe_sql, result.to_string())
                    st.markdown(f"**What this means:** {explanation}")

with tab_insights:
    st.subheader("Generated insight report")

    if st.button("Generate Report"):
        top_conditions_sql = (
            "SELECT condition_description, high_utilizer_pct, non_high_utilizer_pct, "
            "percentage_point_difference "
            "FROM analytics.condition_prevalence_comparison "
            "ORDER BY percentage_point_difference DESC "
            "LIMIT 10"
        )
        coverage_sql = (
            "SELECT ROUND(AVG(healthcare_coverage)::numeric, 2) AS avg_coverage, "
            "COUNT(*) AS patient_count FROM analytics.high_utilizers"
        )

        with st.spinner("Querying marts..."):
            top_conditions = run_query(top_conditions_sql)
            coverage = run_query(coverage_sql)

        with st.spinner("Writing report..."):
            report = generate_insight_report(top_conditions.to_string(), coverage.to_string())

        st.markdown(report)
        st.dataframe(top_conditions)