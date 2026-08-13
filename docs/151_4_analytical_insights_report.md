# EduPath Step 151.4 Analytical Insights Report

## Analysis Scope

This report describes the current EduPath dataset only. The results should not yet be generalised to every university, program or scholarship in Japan or other countries.

## Current Dataset

- Programs: 36
- Scholarships: 12
- Program countries represented: 1
- Scholarship countries represented: 1

## Key Program Tuition Statistics

- Mean tuition: 628,466.67 JPY
- Median tuition: 535,800.00 JPY
- Minimum tuition: 535,800.00 JPY
- Maximum tuition: 1,160,000.00 JPY
- Tuition coverage: 100.00%

## Analytical Findings

### 1. Program Degree Distribution

**Priority:** HIGH

**Finding:** Master is the dominant degree level in the current EduPath program dataset.

**Evidence:** 32 of 36 programs (88.89%) are Master programs.

**Interpretation:** The current program dataset is strongly concentrated at the Master level. This means the current EduPath program coverage is more representative of Master-level opportunities than of other degree levels.

**Recommendation:** During future data expansion, prioritise underrepresented degree levels so that recommendation results can support a broader range of students.

### 2. Program Tuition Analysis

**Priority:** HIGH

**Finding:** Most current program tuition values are concentrated around a common annual tuition level, while some programs have substantially higher tuition.

**Evidence:** Mean tuition = 628,466.67 JPY; median = 535,800.00 JPY; maximum = 1,160,000.00 JPY; most common tuition = 535,800.00 JPY (66.67% of current programs).

**Interpretation:** The mean tuition is noticeably higher than the median. This indicates that a smaller number of higher-fee programs are pulling the average upward.

**Recommendation:** For affordability analysis, EduPath should display both median and mean tuition. Median tuition is useful for describing the typical program, while the mean still shows the effect of more expensive programs.

### 3. University Representation

**Priority:** MEDIUM

**Finding:** Program coverage across currently represented universities was assessed for balance.

**Evidence:** 12 universities are represented in the program collection. Program counts range from 3 to 3 per represented university.

**Interpretation:** Within the universities currently represented in the program collection, program counts are evenly distributed. This reduces the risk that one included university dominates the current program dataset.

**Recommendation:** Future expansion should focus more on adding additional universities and additional degree/program categories rather than repeatedly adding many records from the same universities.

### 4. Scholarship Funding Distribution

**Priority:** MEDIUM

**Finding:** Fully Funded is the dominant funding category in the current scholarship dataset.

**Evidence:** 12 of 12 scholarships (100.00%) are classified as Fully Funded.

**Interpretation:** The current scholarship collection is highly concentrated in the 'Fully Funded' funding category. This is useful for fully funded scholarship discovery, but it does not yet represent the full variety of funding models available.

**Recommendation:** During later scholarship-data expansion, add other funding categories such as partial funding, tuition waivers, university grants and other relevant scholarship types.

### 5. Scholarship Status Distribution

**Priority:** MEDIUM

**Finding:** The dominant scholarship status is 'upcoming'.

**Evidence:** 12 of 12 scholarships (100.00%) have status 'upcoming'.

**Interpretation:** The current scholarship collection is concentrated in a single lifecycle status: 'upcoming'. This reflects the current collection focus rather than the complete scholarship market.

**Recommendation:** When the dataset is expanded, retain status history and include open, upcoming and closed/archived records where appropriate. This will support future trend and application cycle analysis.

### 6. Scholarship Requirement Data Quality

**Priority:** HIGH

**Finding:** Eligibility-data completeness was analysed.

**Evidence:** Average coverage across selected scholarship requirement fields is 2.78%. Low-coverage fields: eligible_nationalities (0.00%), minimum_gpa (0.00%), english_requirement (0.00%), age_limit (0.00%), fields_of_study (8.33%), application_deadline (8.33%).

**Interpretation:** Several scholarship eligibility fields are incomplete. The recommendation engine can still treat missing values as uncertainty, but confidence in eligibility decisions will improve when these fields are verified.

**Recommendation:** Prioritise verification of low-coverage scholarship fields, especially nationality eligibility, GPA requirements, English-language requirements, age limits and deadlines.

### 7. Geographic Coverage

**Priority:** HIGH

**Finding:** The geographic scope of current program and scholarship data was assessed.

**Evidence:** Program countries represented: 1 (Japan). Scholarship countries represented: 1 (Japan).

**Interpretation:** The current program and scholarship analysis is intentionally country-focused. Therefore, the current findings are suitable for analysing the collected EduPath dataset but should not yet be generalised to all universities or scholarships across East and Southeast Asia.

**Recommendation:** Keep the current Japan dataset as the validated baseline. Later, expand programs and scholarships country-by-country using the same verification, relationship-integrity and analysis pipeline.

## Overall Conclusion

EduPath now has an analytical layer that goes beyond descriptive charts. The system identifies dataset patterns, interprets their meaning and converts them into actionable recommendations for data expansion and recommendation-system improvement.
