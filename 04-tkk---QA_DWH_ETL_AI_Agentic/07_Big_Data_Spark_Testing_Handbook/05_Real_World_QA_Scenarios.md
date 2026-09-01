# Real-World QA Scenario — Month-End Spark Timeout

Daily runs pass; month-end fails due to one customer key dominating a join. Use representative skew data, measure P95/max partition runtime, verify output after retry and validate no partial partition publish. Add skew and SLA checks to regression.
