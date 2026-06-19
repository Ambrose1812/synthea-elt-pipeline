select
    "PATIENT" as patient_id,
    "ENCOUNTER" as encounter_id,
    "PAYER" as payer_id,
    "CODE" as medication_code,
    "DESCRIPTION" as medication_description,
    "START" as start_date,
    "STOP" as stop_date,
    "BASE_COST" as base_cost,
    "PAYER_COVERAGE" as payer_coverage,
    "DISPENSES" as dispenses,
    "TOTALCOST" as total_cost,
    "REASONCODE" as reason_code,
    "REASONDESCRIPTION" as reason_description
from {{ source('raw', 'medications') }}