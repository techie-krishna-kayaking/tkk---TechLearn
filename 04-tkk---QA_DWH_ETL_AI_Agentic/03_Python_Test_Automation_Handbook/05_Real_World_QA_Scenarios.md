# Real-World QA Scenario — Green Validator, Bad Data

A validator passes because it checks only row count. A duplicate/missing pair preserves count but corrupts revenue. Add business-key, amount and duplicate assertions with mismatch output; test the validator against deliberately corrupt fixture data before trusting CI.
