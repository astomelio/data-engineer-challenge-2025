-- Customer dimension table with demographic attributes
select distinct
  customer_id,
  job_tenure_years,
  home_ownership
from {{ ref('silver_loans') }}
