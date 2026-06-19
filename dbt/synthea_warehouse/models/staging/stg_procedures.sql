select
    "PATIENT" as patient_id,
    "ENCOUNTER" as encounter_id,
    "CODE" as procedure_code,
    "DESCRIPTION" as procedure_description,
    "START" as start_date,
    "STOP" as stop_date,
    "BASE_COST" as base_cost,
    "REASONCODE" as reason_code,
    "REASONDESCRIPTION" as reason_description
from {{ source('raw', 'procedures') }}