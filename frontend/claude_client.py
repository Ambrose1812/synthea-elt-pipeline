# frontend/claude_client.py
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODEL = "claude-sonnet-4-6"

# Schema reference for the analytics layer. Single source of truth,
# kept in sync with dbt's schema.yml descriptions.
SCHEMA_CONTEXT = (
    "You have access to a PostgreSQL schema called `analytics` with these tables:\n\n"
    "analytics.stg_patients\n"
    "  - patient_id (text, primary key)\n"
    "  - birth_date, death_date, first_name, last_name\n"
    "  - gender, race, ethnicity, marital_status\n"
    "  - city, state, county, zip\n"
    "  - income, healthcare_expenses, healthcare_coverage (numeric)\n\n"
    "analytics.stg_encounters\n"
    "  - encounter_id (text, primary key)\n"
    "  - patient_id (text, foreign key to stg_patients)\n"
    "  - encounter_class (text: ambulatory, emergency, inpatient, wellness, etc.)\n"
    "  - start_date, stop_date\n\n"
    "analytics.stg_conditions\n"
    "  - patient_id, encounter_id\n"
    "  - condition_description\n\n"
    "analytics.patient_encounter_summary\n"
    "  - patient_id (primary key)\n"
    "  - total_encounters, emergency_visits, inpatient_visits\n"
    "  - aggregated per-patient encounter counts\n\n"
    "analytics.high_utilizers\n"
    "  - patient_id (primary key)\n"
    "  - flags patients with high emergency/inpatient utilization\n"
    "  - healthcare_coverage (numeric)\n\n"
    "analytics.condition_prevalence_comparison\n"
    "  - compares condition prevalence between high utilizers and the general\n"
    "    patient population\n"
    "  - condition_description, high_utilizer_pct, general_population_pct\n\n"
    "Only query these tables. Never reference tables outside the `analytics` "
    "schema. Always write standard PostgreSQL syntax."
)


def generate_sql(question: str) -> str:
    """
    Translates a natural language question into a single SQL SELECT
    statement. Does not execute or validate the query; validation is
    handled separately by sql_guard.py.
    """
    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        system=(
            "You are a SQL assistant for a healthcare analytics database. "
            f"{SCHEMA_CONTEXT}\n\n"
            "Given a question, respond with ONLY a single PostgreSQL SELECT "
            "statement that answers it. No explanation, no markdown code "
            "fences, no semicolon at the end. Just the raw SQL.\n\n"
            "When a question compares two groups, each group must be scoped "
            "independently and correctly, not nested inside the other group.\n\n"
            "Example: if asked to compare 'high utilizers' vs 'patients with "
            "diabetes', the high utilizers group should come from "
            "analytics.high_utilizers, and the diabetes group should come "
            "from analytics.stg_patients joined to analytics.stg_conditions "
            "where condition_description matches diabetes - NOT filtered "
            "through analytics.high_utilizers. The two groups may overlap, "
            "but neither should be defined as a subset of the other unless "
            "the question explicitly asks for that overlap."
        ),
        messages=[{"role": "user", "content": question}],
    )
    return response.content[0].text.strip()


def explain_results(question: str, sql: str, result_summary: str) -> str:
    """
    Generates a plain-English explanation of query results for a
    non-technical stakeholder.
    """
    response = client.messages.create(
        model=MODEL,
        max_tokens=400,
        system=(
            "You explain database query results to healthcare analysts "
            "in plain English. Be concise - 2-4 sentences. Don't repeat "
            "the raw numbers verbatim, interpret what they mean." 
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Question asked: {question}\n\n"
                f"SQL that was run: {sql}\n\n"
                f"Result:\n{result_summary}"
            ),
        }],
    )
    return response.content[0].text.strip()