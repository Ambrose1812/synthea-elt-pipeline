synthea-elt-pipeline
A healthcare data pipeline I built to get hands-on with the modern data stack: dbt, Airflow, Postgres, and now an AI-powered analytics layer, using synthetic patient data instead of real records.

The goal: find "high-utilization" patients (the people who end up in the ER or admitted over and over) and dig into what they have in common. This kind of analysis is what care management and population health teams actually do, so I wanted a project that mirrored real work instead of another toy dataset.
Why fake patients?
Real patient data is locked down for obvious reasons (HIPAA). Synthea is an open-source tool that generates fake patients with realistic medical histories, including diagnoses, ER visits, medications, and costs, so I can do the analysis without touching anyone's actual health records. Felt like the right call for something I'm putting on a public repo.
What I found
High utilizers (about 693 patients in this dataset) cluster hard on both clinical and social risk factors. Nearly half have ischemic heart disease or related cardiac findings, versus about 12% of everyone else. Diabetic kidney disease shows up in 42% of high utilizers versus 6% of the rest. But the part that actually surprised me: three of the ten most overrepresented things in this group aren't medical diagnoses at all. Unemployment, documented intimate partner abuse, and living somewhere flagged for violence all show 30+ percentage point gaps. The clinical and social stuff cluster in the same patients. That's the actual takeaway: a purely clinical care management program probably isn't enough for this group without also addressing what's going on outside the hospital.
How it's put together
Synthea spits out CSVs of synthetic patients. From there:

Synthea CSVs

    |

    v

Python ELT ingestion  ->  PostgreSQL (raw schema)

    |

    v

dbt (staging + marts, 17 tests, generated docs)

    |

    v

Airflow + Cosmos (orchestrates ingestion -> dbt, scheduled daily)

    |

    v

Streamlit + Claude API (ask questions in plain English, get SQL + answers)

Python loads the raw files into Postgres (the "EL" part)
dbt handles all the cleaning and modeling once the data's in the warehouse: staging models for each source table, then mart models (high_utilizers, condition_prevalence_comparison, patient_encounter_summary) that actually answer the research question, plus 17 tests and generated docs
Airflow runs the whole thing on a schedule (daily) using the Cosmos provider, which turns every dbt model and test into its own Airflow task instead of one black-box "run dbt" step
Streamlit + Claude sits on top. Type a question in plain English, Claude turns it into SQL, it runs against a read-only database role, and Claude explains the result back in plain language. There's also an auto-generated narrative report mode that synthesizes the findings above into something a non-technical stakeholder could read.
Bugs worth mentioning
A couple of things broke in ways that taught me more than if they'd just worked the first time:

Airflow/Cosmos test ordering. Cosmos defaults to testing each dbt model right after it builds. The problem: dbt relationship tests attach to both models being compared, not just one. So the moment Cosmos tested stg_patients, it pulled in relationship tests that secretly needed high_utilizers and patient_encounter_summary, which hadn't been built yet, since they come later in the DAG. Those tests failed for reasons that had nothing to do with stg_patients itself, and everything downstream got marked "upstream failed" as a result. Fix was setting test_behavior=AFTER_ALL so every model builds before any tests run. Full writeup in docs/airflow-dag-notes.md.

The AI layer silently scoping comparisons wrong. When I asked it to compare "high utilizers" against "patients with diabetes," it nested the diabetes group inside the high-utilizers table instead of pulling from the general population, so it answered a narrower question than what was actually asked, and the SQL ran fine and returned a plausible-looking number. That's the dangerous kind of bug: nothing crashed, it just quietly answered the wrong question. Took giving the model a concrete example of correct scoping (not just an abstract rule) to actually fix it.

Postgres ROUND() doesn't work on floats the way you'd expect. ROUND(AVG(col), 2) fails on a double precision column because Postgres only defines that two-argument version of ROUND() for numeric, not double precision. Needed an explicit cast: ROUND(AVG(col)::numeric, 2). Small thing, but it's a real Postgres gotcha worth knowing cold.
Safety design on the AI layer
Letting an LLM write and run SQL against a real database isn't something to hand-wave past. Three layers, on purpose redundant with each other:

The app connects through analytics_readonly, a Postgres role that's structurally incapable of writing or altering anything. It only allows SELECT, with ALTER DEFAULT PRIVILEGES set so the grant survives dbt rebuilding the views on every run.
Every generated query gets validated before it runs: has to be a single SELECT, no chained statements, no destructive keywords, automatic row limit.
Claude gets the actual schema (real table and column names) instead of guessing, which is most of what keeps it from hallucinating SQL in the first place.
Stack
Python, PostgreSQL, dbt, Airflow (with Astronomer Cosmos), Streamlit, Anthropic Claude API
Running it
# ingestion

cd ingestion

python ingest.py

# dbt

cd ../dbt/synthea_warehouse

dbt run

dbt test

# airflow (optional - ingestion + dbt above already populates everything)

cd ../../airflow

airflow standalone

# trigger synthea_elt_pipeline from localhost:8080

# frontend

cd ../frontend

pip install -r requirements.txt

streamlit run app.py

Needs a Postgres instance and an Anthropic API key set in frontend/.env.
Project structure
synthea-elt-pipeline/

|-- ingestion/      Python ELT scripts, raw CSV -> Postgres raw schema

|-- dbt/             staging + mart models, tests, docs

|-- airflow/         DAG definition, Cosmos orchestration config

|-- frontend/        Streamlit app, Claude API integration, SQL safety layer

|-- docs/            engineering notes from along the way

v