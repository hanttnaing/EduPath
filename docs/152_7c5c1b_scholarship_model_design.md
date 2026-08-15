# Step 152.7C-5C-1B Scholarship Model Design

This is a design-only, backward-compatible resolution. No database, source research, baseline, schema, or API behavior was changed.

## Existing fields to keep

- `ielts_requirement: int | float | None`
- `toefl_requirement: int | None`
- `age_limit: int | None`
- `monthly_allowance: int | float | None`

## New optional fields proposed

- `ielts_requirement_text: str | None = None` — preserves alternatives and non-numeric English conditions.
- `toefl_requirement_text: str | None = None` — preserves test format/equivalence qualifiers.
- `age_requirement_details: list[AgeRequirement] | None = None` — stores degree-specific operator/max-age rules.
- `monthly_allowance_details: list[AllowanceTier] | None = None` — stores degree-specific amount/currency tiers.

## Fields that require no change

- Thailand `age_limit` can safely store `45` because existing logic treats it as a maximum.
- Existing scalar fields remain available to all current API clients.

## Normalization rules

- Extract a scalar only when its qualifiers are retained in a companion field.
- Never invent a numeric score for non-numeric English requirements.
- Never collapse degree-specific ages or stipend tiers into one scalar.
- Preserve missing values as `None`.

## Conflict resolutions

- `sch_my_001.ielts_requirement` — **BACKWARD_COMPATIBLE_TEXT_EXTENSION**: The numeric baseline is usable only while the alternative/equivalence condition remains available as text.
- `sch_my_001.toefl_requirement` — **BACKWARD_COMPATIBLE_TEXT_EXTENSION**: The PBT score is usable only while test format and equivalence wording remain available as text.
- `sch_my_001.age_limit` — **STRUCTURED_EXTENSION_RECOMMENDED**: One scalar age limit cannot express two degree-specific maxima.
- `sch_tw_001.monthly_allowance` — **STRUCTURED_EXTENSION_RECOMMENDED**: One scalar allowance would misrepresent the degree-dependent stipend.
- `sch_th_001.ielts_requirement` — **BACKWARD_COMPATIBLE_TEXT_EXTENSION**: No numeric IELTS threshold is verified; text preserves the non-numeric requirement without invention.
- `sch_th_001.age_limit` — **SAFE_NUMERIC_NORMALIZATION**: Existing recommendation code treats age_limit as a maximum and rejects ages above it; <=45 is therefore losslessly represented by 45.

## ID provenance

All six IDs were generated deliberately in the Step 152.7C-3 integration layer and are unique in the live collection. The verified research CSV should retain blank internal IDs.

- `sch_hk_001` — INTEGRATION_GENERATED_ID; NO_REPAIR_REQUIRED.
- `sch_my_001` — INTEGRATION_GENERATED_ID; NO_REPAIR_REQUIRED.
- `sch_sg_001` — INTEGRATION_GENERATED_ID; NO_REPAIR_REQUIRED.
- `sch_kr_001` — INTEGRATION_GENERATED_ID; NO_REPAIR_REQUIRED.
- `sch_tw_001` — INTEGRATION_GENERATED_ID; NO_REPAIR_REQUIRED.
- `sch_th_001` — INTEGRATION_GENERATED_ID; NO_REPAIR_REQUIRED.

## Algorithm impact

- Numeric threshold plus descriptive alternative: use the scalar for threshold screening, but treat a failed scalar check as potentially eligible when the text records an accepted equivalent/exemption; surface the text for review.
- Degree-specific age requirements: select the structured rule matching the candidate degree before comparing age; do not use a global maximum.
- Degree-specific allowance amounts: select matching tiers for ranking/display; do not compare an absent scalar as zero.
- Non-numeric English requirements: do not hard-reject numerically; flag for document/institution-specific verification.

## API compatibility impact

Adding optional fields with default `None` is backward-compatible for current clients and preserves existing scalar response fields. Structured child models require additive response-schema and serialization tests. No endpoint behavior should change until compatibility validation passes.

## Next step gate

All six conflicts have documented meaning-preserving strategies. Step 152.7C-5C-1C — Schema Extension Implementation and Compatibility Validation may proceed.
