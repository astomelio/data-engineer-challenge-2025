-- Fact table for loan analytics with dimensional relationships
with s as (
  select * from {{ ref('silver_loans') }}
), p as (
  select * from {{ ref('dim_purpose') }}
)
select
  s.loan_id,
  s.customer_id,
  p.purpose_id,
  s.loan_status,
  s.term,
  s.credit_score,
  s.current_loan_amount,
  s.annual_income,
  s.monthly_debt,
  s.years_credit_history,
  s.months_since_last_delinquent,
  s.n_open_accounts,
  s.n_credit_problems,
  s.current_credit_balance,
  s.max_open_credit,
  s.bankruptcies,
  s.tax_liens
from s
left join p using (purpose_name)
