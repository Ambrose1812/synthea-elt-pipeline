with total_high_utilizers as (
    select count(distinct patient_id) as total
    from {{ ref('high_utilizers') }}
),

total_non_high_utilizers as (
    select count(distinct p.patient_id) as total
    from {{ ref('stg_patients') }} p
    left join {{ ref('high_utilizers') }} h
        on p.patient_id = h.patient_id
    where h.patient_id is null
),

high_utilizer_conditions as (
    select
        c.condition_description,
        count(distinct c.patient_id) as patient_count
    from {{ ref('stg_conditions') }} c
    join {{ ref('high_utilizers') }} h
        on c.patient_id = h.patient_id
    group by c.condition_description
),

non_high_utilizer_conditions as (
    select
        c.condition_description,
        count(distinct c.patient_id) as patient_count
    from {{ ref('stg_conditions') }} c
    left join {{ ref('high_utilizers') }} h
        on c.patient_id = h.patient_id
    where h.patient_id is null
    group by c.condition_description
)

select
    coalesce(hc.condition_description, nc.condition_description) as condition_description,
    coalesce(hc.patient_count, 0) as high_utilizer_patient_count,
    round(100.0 * coalesce(hc.patient_count, 0) / (select total from total_high_utilizers), 1) as high_utilizer_pct,
    coalesce(nc.patient_count, 0) as non_high_utilizer_patient_count,
    round(100.0 * coalesce(nc.patient_count, 0) / (select total from total_non_high_utilizers), 1) as non_high_utilizer_pct,
    round(
        (100.0 * coalesce(hc.patient_count, 0) / (select total from total_high_utilizers))
        - (100.0 * coalesce(nc.patient_count, 0) / (select total from total_non_high_utilizers)),
    1) as percentage_point_difference
from high_utilizer_conditions hc
full outer join non_high_utilizer_conditions nc
    on hc.condition_description = nc.condition_description
order by percentage_point_difference desc