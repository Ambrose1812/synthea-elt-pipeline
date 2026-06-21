with qualifying_encounters as (

    select
        patient_id,
        encounter_id,
        start_date
    from {{ ref('stg_encounters') }}
    where encounter_class in ('emergency', 'inpatient')

),

windowed_counts as (

    select
        a.patient_id,
        a.encounter_id,
        a.start_date,
        count(b.encounter_id) as encounters_in_window
    from qualifying_encounters a
    join qualifying_encounters b
        on a.patient_id = b.patient_id
        and b.start_date between a.start_date - interval '365 days' and a.start_date
    group by a.patient_id, a.encounter_id, a.start_date

)

select
    patient_id,
    max(encounters_in_window) as max_encounters_in_any_12mo_window
from windowed_counts
group by patient_id