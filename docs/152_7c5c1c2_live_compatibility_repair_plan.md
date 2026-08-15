# Step 152.7C-5C-1C-2 Live Compatibility Repair Plan

This package is read-only. It proposes updates to existing integrated records but applies none.

## Live validation

- Checked: 18
- Passing: 14
- Failing: 4

## Proposed repairs

- `sch_hk_001.scholarship_status` — **SAFE_RESTORE_FROM_VERIFIED_SOURCE**: Official Hong Kong Research Grants Council information states that the HKPFS 2026/27 application window ran from 1 September 2025 to 1 December 2025. The integrated record represents that completed cycle.
- `sch_kr_001.scholarship_status` — **SAFE_RESTORE_FROM_VERIFIED_SOURCE**: Official Study in Korea/NIIED schedule information places 2026 graduate applications in February-March and selection through June; the 2026 GKS Graduate Degree final result announcement was published in July 2026.
- `sch_sg_001.scholarship_status` — **RESEARCH_REQUIRED**: Authoritative current application-cycle status remains unconfirmed; no value may be invented.
- `sch_tw_001.monthly_allowance` — **STRUCTURED_SCHEMA_MIGRATION**: The verified stipend has two degree-dependent amounts; clearing the invalid scalar and storing both tiers preserves meaning without selecting a misleading number.

## Simulation

- Records simulated: 4
- Passed: 3
- Failed: 1

Singapore remains blocked because no authoritative cycle status is available. No placeholder was used.

## Safety

MongoDB, verified research, baseline, cleaned data, schemas, API routes, and frontend files were not modified.
