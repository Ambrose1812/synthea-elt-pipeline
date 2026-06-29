from datetime import datetime
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig, RenderConfig
from cosmos.constants import ExecutionMode, TestBehavior
from cosmos.profiles import PostgresUserPasswordProfileMapping

DBT_PROJECT_DIR = "/mnt/c/Official_HC_Projects/synthea-elt-pipeline/dbt/synthea_warehouse"
INGEST_PYTHON = "/mnt/c/Official_HC_Projects/synthea-elt-pipeline/ingestion/venv_wsl/bin/python"
INGEST_SCRIPT = "/mnt/c/Official_HC_Projects/synthea-elt-pipeline/ingestion/ingest.py"

profile_config = ProfileConfig(
    profile_name="synthea_warehouse",
    target_name="dev",
    profiles_yml_filepath="/home/ambrose/.dbt/profiles.yml",
)

execution_config = ExecutionConfig(
    execution_mode=ExecutionMode.LOCAL,
)

render_config = RenderConfig(
    test_behavior=TestBehavior.AFTER_ALL,
)

with DAG(
    dag_id="synthea_elt_pipeline",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["synthea", "portfolio"],
) as dag:

    ingest = BashOperator(
        task_id="ingest_raw_data",
        bash_command=f"{INGEST_PYTHON} {INGEST_SCRIPT}",
    )

    transform = DbtTaskGroup(
        group_id="dbt_transform",
        project_config=ProjectConfig(DBT_PROJECT_DIR),
        profile_config=profile_config,
        execution_config=execution_config,
        render_config=render_config,
    )

    ingest >> transform
