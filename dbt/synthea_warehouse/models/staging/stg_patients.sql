select
    "Id" as patient_id,
    "BIRTHDATE" as birth_date,
    "DEATHDATE" as death_date,
    "FIRST" as first_name,
    "LAST" as last_name,
    "GENDER" as gender,
    "RACE" as race,
    "ETHNICITY" as ethnicity,
    "MARITAL" as marital_status,
    "CITY" as city,
    "STATE" as state,
    "COUNTY" as county,
    "ZIP" as zip,
    "INCOME" as income,
    "HEALTHCARE_EXPENSES" as healthcare_expenses,
    "HEALTHCARE_COVERAGE" as healthcare_coverage

from {{ source('raw', 'patients') }}
