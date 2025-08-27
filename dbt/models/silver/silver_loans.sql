{# DuckDB local - Silver Layer #}
with src as (
    select * from {{ source('raw', 'raw_loans') }}
),
clean as (
    select
        "Loan ID"::varchar                        as loan_id,
        "Customer ID"::varchar                    as customer_id,
        -- Remove placeholder values for missing loan amounts
        nullif("Current Loan Amount", 99999999)   as current_loan_amount,
        -- Standardize credit scores (some are in 1000+ scale, convert to 850 scale)
        case
            when "Credit Score" is null then null
            when "Credit Score" > 900 then round("Credit Score"/10.0)
            else round("Credit Score")
        end::int                                   as credit_score,
        -- Standardize loan terms
        case when lower(coalesce("Term", '')) like '%short%' then 'Short Term' else 'Long Term' end as term,
        -- Clean and standardize loan purposes
        replace(coalesce(nullif(trim("Purpose"), ''), 'Other'), '_', ' ') as purpose_name,
        -- Standardize home ownership values
        case
            when "Home Ownership" in ('Home Mortgage','HaveMortgage') then 'Mortgage'
            when "Home Ownership" = 'Own Home' then 'Own'
            when "Home Ownership" = 'Rent' then 'Rent'
            else 'Other'
        end                                         as home_ownership,
        -- Extract numeric years from job tenure field
        try_cast(regexp_extract(coalesce("Years in current job", ''), '([0-9]+)', 1) as int) as job_tenure_years,
        "Loan Status"                               as loan_status,
        "Annual Income"                             as annual_income,
        "Monthly Debt"                              as monthly_debt,
        "Years of Credit History"                   as years_credit_history,
        "Months since last delinquent"              as months_since_last_delinquent,
        "Number of Open Accounts"                   as n_open_accounts,
        "Number of Credit Problems"                 as n_credit_problems,
        "Current Credit Balance"                    as current_credit_balance,
        "Maximum Open Credit"                       as max_open_credit,
        -- Convert NULL bankruptcies and tax liens to 0 (no history)
        coalesce("Bankruptcies",0)                  as bankruptcies,
        coalesce("Tax Liens",0)                     as tax_liens
    from src
),
ranked as (
    select
        *,
        -- Deduplicate records by loan_id (keep first occurrence)
        row_number() over (partition by loan_id order by loan_id) as rn
    from clean
)
select
    loan_id,
    customer_id,
    current_loan_amount,
    credit_score,
    term,
    purpose_name,
    home_ownership,
    job_tenure_years,
    loan_status,
    annual_income,
    monthly_debt,
    years_credit_history,
    months_since_last_delinquent,
    n_open_accounts,
    n_credit_problems,
    current_credit_balance,
    max_open_credit,
    bankruptcies,
    tax_liens
from ranked
where rn = 1  -- Keep only first occurrence of each loan_id
