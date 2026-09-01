# Automation Framework Design for QA

## Suggested repository layout

```text
tests/        # test intent and assertions
validators/   # reusable data/API/AI check functions
test_data/    # versioned synthetic or masked inputs
config/       # environment-specific non-secret configuration
reports/      # generated evidence, excluded from source control where appropriate
```

## CI behavior

Run fast deterministic checks on every pull request. Run environment/database/API suites after deployment to a test environment. Publish reports and fail the job for release-blocking rules. Quarantine a flaky test only with an owner, expiry and alternate monitoring control.

## Practice

Extend `02_Reusable_Validator_Example.py` with a not-null rule and a permitted-status rule. Add positive, negative and boundary cases before changing the validator.
