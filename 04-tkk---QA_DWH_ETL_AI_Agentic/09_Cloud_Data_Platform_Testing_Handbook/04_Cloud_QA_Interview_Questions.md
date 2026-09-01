# Cloud Data Platform QA — Interview Q&A

**What is least-privilege testing?** Prove each role can do only approved action on approved resource/context and prove denied paths, audit events and safe errors.

**How do you test DR?** Test restore/failover against declared RPO/RTO and verify recovered data correctness, access policy, lineage and monitoring—not just infrastructure availability.

**How do you test secret rotation?** Use non-production secret lifecycle; verify old/expired credential fails safely, new credential succeeds and logs expose no secret.

**What is cloud QA beyond functional testing?** Isolation, IAM, encryption, audit, service limits, scaling, cost-safe behavior, retention, backup, failover and observability.

**How do you use cloud environments safely?** Dedicated accounts/projects/roles and synthetic/masked data; never broad production privilege for convenience.
