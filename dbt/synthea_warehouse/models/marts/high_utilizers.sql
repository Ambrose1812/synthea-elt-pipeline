select
    s.patient_id,
    s.max_encounters_in_any_12mo_window,
    p.gender,
    p.race,
    p.ethnicity,
    p.marital_status,
    p.city,
    p.state,
    p.county,
    p.income,
    p.healthcare_expenses,
    p.healthcare_coverage
from {{ ref('patient_encounter_summary') }} s
join {{ ref('stg_patients') }} p
    on s.patient_id = p.patient_id
where s.max_encounters_in_any_12mo_window >= 3