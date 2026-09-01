# Production Troubleshooting — Interview Q&A

**First action in a quality incident?** Confirm impact and contain unsafe publish/action while preserving evidence; avoid untracked reruns that destroy diagnosis.

**How do you distinguish source from pipeline issue?** Compare source receipt/profile/cut-off to staging/target and trace a known affected key through lineage/run records.

**What makes a good postmortem?** Blameless timeline, evidence, impact, causal factors, containment, corrective/preventive action with owner/date and verification of effectiveness.

**When should you rollback?** When impact/risk exceeds approved threshold and rollback is safer than continued exposure; validate rollback data/state and customer communication.

**How do you communicate uncertainty?** Clearly state known facts, current hypothesis, evidence next step, impact range, containment and decision owner—never present inference as certainty.
