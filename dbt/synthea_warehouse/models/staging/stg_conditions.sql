select
    "PATIENT" as patient_id,
    "ENCOUNTER" as encounter_id,
    "CODE" as condition_code,
    "DESCRIPTION" as condition_description,
    "START" as start_date,
    "STOP" as stop_date
from {{ source('raw', 'conditions') }}