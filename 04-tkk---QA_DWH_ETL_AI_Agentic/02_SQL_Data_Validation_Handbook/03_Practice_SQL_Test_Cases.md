# Practice — SQL Test Design

For a `fct_orders` table, write SQL and expected outcomes for:

1. Mandatory order ID/customer/date checks.
2. One order ID appears once at fact grain.
3. Amount is non-negative and currency is in the contract.
4. Every customer key exists in `dim_customer`.
5. Source-to-target keys reconcile for a daily incremental load.
6. Revenue reconciles by date, currency and status.
7. Late/cancelled/refunded orders behave as specified.

Then create a defect report for a join multiplication that doubles revenue but preserves the number of business dates.
