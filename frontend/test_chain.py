# frontend/test_chain.py
from claude_client import generate_sql, explain_results
from sql_guard import validate_query, UnsafeQueryError
from db import run_query

question = "What's the average healthcare coverage cost for high utilizers compared to patients with diabetes?"

sql = generate_sql(question)
print("GENERATED SQL:\n", sql, "\n")

try:
    safe_sql = validate_query(sql)
    print("VALIDATED SQL:\n", safe_sql, "\n")
except UnsafeQueryError as e:
    print("BLOCKED:", e)
    safe_sql = None

if safe_sql:
    result = run_query(safe_sql)
    print("RESULT:\n", result, "\n")

    summary = result.to_string()
    explanation = explain_results(question, safe_sql, summary)
    print("EXPLANATION:\n", explanation)