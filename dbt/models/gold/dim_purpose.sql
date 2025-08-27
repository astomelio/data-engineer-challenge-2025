-- Loan purpose dimension table with surrogate key
with silver as (
  select distinct purpose_name from {{ ref('silver_loans') }}
)
select
  purpose_name,
  dense_rank() over(order by purpose_name) as purpose_id
from silver
