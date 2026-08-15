# Step 152.7C-5C-1C-2B Partial Repair Simulation

This read-only simulation isolates the unresolved SINGA status while retaining the existing 18-record architecture.

## Safe candidates

- `sch_hk_001.scholarship_status` — SAFE_RESTORE_FROM_VERIFIED_SOURCE — PASS
- `sch_kr_001.scholarship_status` — SAFE_RESTORE_FROM_VERIFIED_SOURCE — PASS
- `sch_tw_001.monthly_allowance` — STRUCTURED_SCHEMA_MIGRATION — PASS

## Research blocker excluded

- `sch_sg_001.scholarship_status` — `RESEARCH_BLOCKER_EXCLUDED_FROM_PARTIAL_REPAIR`.
- The live and simulated SINGA document was not changed.

## Taiwan allowance representation

The invalid scalar is proposed as `None`. Three structured tiers preserve Undergraduate 15000 TWD/month, Master's 20000 TWD/month, and Doctorate 20000 TWD/month.

## Validation

- Simulated records: 3; passed: 3; failed: 0.
- Baseline compatibility: PASS (12/12).

- Validation source: `LIVE_MONGODB`.
- Fresh live database recheck required before any write: `NO`.

MongoDB, verified research, immutable baseline, cleaned datasets, and source-plan files were not modified.
