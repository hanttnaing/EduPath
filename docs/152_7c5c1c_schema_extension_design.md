# Step 152.7C-5C-1C Schema Extension

The existing `ScholarshipResponse` model was extended additively. Existing fields were not removed or renamed.

## New nested models

- `AgeRequirement`: optional `degree_level`, `operator`, `age`, and `description` fields.
- `AllowanceTier`: optional `degree_level`, `amount`, `currency`, and `description` fields.

## New optional response fields

- `ielts_requirement_text: str | None = None`
- `toefl_requirement_text: str | None = None`
- `age_requirement_details: list[AgeRequirement] | None = None`
- `monthly_allowance_details: list[AllowanceTier] | None = None`

All defaults are `None`; old documents and clients remain compatible.

## Validation outcome

- Conflict cases: 8/8 passed.
- Immutable baseline: 12/12 passed.
- Live MongoDB snapshot: 14/18 passed.
- API structural compatibility: PASS.

The live failures, if any, are pre-existing record issues and were not hidden or repaired in this schema step. No MongoDB records, verified research, baseline data, or frontend files were changed.
