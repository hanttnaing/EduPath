# EduPath Step 152.7B Scholarship Collection Guide

This staging dataset is used to collect verified scholarship records before import.

## Expansion Target

- Current scholarships: 12
- Minimum target: 30
- New records required: 18
- Expected dataset after expansion: 30

## Country Allocation

- Hong Kong: 3 scholarships
- Malaysia: 3 scholarships
- Singapore: 3 scholarships
- South Korea: 3 scholarships
- Taiwan: 3 scholarships
- Thailand: 3 scholarships

## Collection Rules

1. Use official government, university, or scholarship-provider sources.
2. Do not invent missing GPA, English, age or nationality requirements.
3. If an official source does not publish a value, leave the field empty or UNKNOWN according to the existing schema.
4. Record the official URL used for verification.
5. Do not import staging data into MongoDB until Step 152.7C validation passes.

## Current MongoDB Scholarship Fields

- `accommodation_support`
- `age_limit`
- `allowance_currency`
- `application_cycle`
- `application_deadline`
- `application_opening_date`
- `collected_at`
- `content_hash`
- `country_id`
- `created_at`
- `data_quality_status`
- `database_updated_at`
- `degree_levels`
- `eligible_nationalities`
- `fields_of_study`
- `freshness_status`
- `funding_type`
- `gpa_scale`
- `health_insurance`
- `host_university_id`
- `ielts_requirement`
- `last_verified_at`
- `minimum_gpa`
- `monthly_allowance`
- `official_website`
- `provider_name`
- `provider_type`
- `required_documents`
- `scholarship_id`
- `scholarship_name`
- `scholarship_status`
- `source_url`
- `toefl_requirement`
- `travel_allowance`
- `tuition_coverage`