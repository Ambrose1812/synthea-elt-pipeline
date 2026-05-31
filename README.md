# synthea-elt-pipeline

A healthcare data pipeline I built to get hands-on with the modern data stack — 
dbt, Airflow, Postgres — using synthetic patient data instead of real records.

The goal: find "high-utilization" patients (the people who end up in the ER or 
admitted over and over) and dig into what they have in common. This kind of 
analysis is what care management and population health teams actually do, so I 
wanted a project that mirrored real work instead of another toy dataset.

## Why fake patients?

Real patient data is locked down for obvious reasons (HIPAA). Synthea is an 
open-source tool that generates fake patients with realistic medical histories — 
diagnoses, ER visits, medications, costs, the whole thing — so I can do the 
analysis without touching anyone's actual health records. Felt like the right 
call for something I'm putting on a public repo.

## How it's put together

Synthea spits out CSVs of synthetic patients. From there:

- Python loads the raw files into Postgres (the "EL" part)
- dbt handles all the cleaning and modeling once the data's in the warehouse
- Airflow runs the whole thing on a schedule so it's not a pile of manual scripts
- A Claude-powered layer on top for pulling summaries out of the results

## Where I'm at

Halfway through. The following is finished: Repo setup, Synthea data generated, Postgres running, and ingestion.
Still have to expand the ingestion to all 5 tables required for my question, transform raw data in dbt, setup airflow orchestration, and add the Claude API layer.

## Stack

Python, PostgreSQL, dbt, Airflow, Anthropic Claude API
