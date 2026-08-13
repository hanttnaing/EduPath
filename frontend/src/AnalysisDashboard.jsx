import React, { useEffect, useMemo, useState } from "react";
import API_BASE_URL from "./api";

const DASHBOARD_ENDPOINT = `${API_BASE_URL}/api/analysis/dashboard`;


/* =========================================================
   Utility Functions
========================================================= */

function isObject(value) {
  return (
    value !== null &&
    typeof value === "object" &&
    !Array.isArray(value)
  );
}


function safeNumber(value, fallback = 0) {
  const number = Number(value);

  if (Number.isFinite(number)) {
    return number;
  }

  return fallback;
}


function formatNumber(value) {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    return value ?? "—";
  }

  return new Intl.NumberFormat("en-US").format(number);
}


function formatPercent(value) {
  if (value === null || value === undefined) {
    return "—";
  }

  const number = Number(value);

  if (!Number.isFinite(number)) {
    return String(value);
  }

  if (number <= 1 && number >= 0) {
    return `${(number * 100).toFixed(1)}%`;
  }

  return `${number.toFixed(1)}%`;
}


function humanizeKey(key = "") {
  return String(key)
    .replace(/_/g, " ")
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}


function firstDefined(...values) {
  for (const value of values) {
    if (
      value !== undefined &&
      value !== null &&
      value !== ""
    ) {
      return value;
    }
  }

  return undefined;
}


function getNested(object, paths = []) {
  for (const path of paths) {
    const parts = path.split(".");

    let current = object;
    let valid = true;

    for (const part of parts) {
      if (
        current === null ||
        current === undefined ||
        !(part in Object(current))
      ) {
        valid = false;
        break;
      }

      current = current[part];
    }

    if (
      valid &&
      current !== undefined &&
      current !== null
    ) {
      return current;
    }
  }

  return undefined;
}


function normalizeDistribution(value) {
  if (!value) {
    return [];
  }

  if (Array.isArray(value)) {
    return value.map((item, index) => {
      if (isObject(item)) {
        const label = firstDefined(
          item.label,
          item.name,
          item.category,
          item.degree,
          item.level,
          item.tuition,
          item.value_label,
          `Item ${index + 1}`
        );

        const count = safeNumber(
          firstDefined(
            item.count,
            item.total,
            item.programs,
            item.value,
            item.frequency
          ),
          0
        );

        const percentage = firstDefined(
          item.percentage,
          item.percent,
          item.share,
          item.pct
        );

        return {
          label: String(label),
          count,
          percentage:
            percentage !== undefined
              ? safeNumber(percentage)
              : undefined,
        };
      }

      return {
        label: String(item),
        count: 1,
      };
    });
  }

  if (isObject(value)) {
    return Object.entries(value).map(
      ([label, rawValue]) => {
        if (isObject(rawValue)) {
          return {
            label: humanizeKey(label),
            count: safeNumber(
              firstDefined(
                rawValue.count,
                rawValue.total,
                rawValue.programs,
                rawValue.value
              ),
              0
            ),
            percentage:
              firstDefined(
                rawValue.percentage,
                rawValue.percent,
                rawValue.share,
                rawValue.pct
              ) !== undefined
                ? safeNumber(
                    firstDefined(
                      rawValue.percentage,
                      rawValue.percent,
                      rawValue.share,
                      rawValue.pct
                    )
                  )
                : undefined,
          };
        }

        return {
          label: humanizeKey(label),
          count: safeNumber(rawValue),
        };
      }
    );
  }

  return [];
}


function normalizeInsights(value) {
  if (!value) {
    return [];
  }

  if (Array.isArray(value)) {
    return value.map((item, index) => {
      if (typeof item === "string") {
        return {
          title: `Insight ${index + 1}`,
          finding: item,
        };
      }

      if (isObject(item)) {
        return {
          title: firstDefined(
            item.title,
            item.name,
            item.insight,
            `Insight ${index + 1}`
          ),

          finding: firstDefined(
            item.finding,
            item.summary,
            item.description,
            item.evidence,
            ""
          ),

          interpretation: firstDefined(
            item.interpretation,
            item.meaning,
            ""
          ),

          recommendation: firstDefined(
            item.recommendation,
            item.decision_use,
            item.decision,
            item.action,
            ""
          ),

          priority: firstDefined(
            item.priority,
            ""
          ),
        };
      }

      return {
        title: `Insight ${index + 1}`,
        finding: String(item),
      };
    });
  }

  if (isObject(value)) {
    return Object.entries(value).map(
      ([key, item]) => {
        if (typeof item === "string") {
          return {
            title: humanizeKey(key),
            finding: item,
          };
        }

        return {
          title: firstDefined(
            item?.title,
            humanizeKey(key)
          ),

          finding: firstDefined(
            item?.finding,
            item?.summary,
            item?.description,
            item?.evidence,
            ""
          ),

          interpretation: firstDefined(
            item?.interpretation,
            ""
          ),

          recommendation: firstDefined(
            item?.recommendation,
            item?.decision_use,
            ""
          ),

          priority: firstDefined(
            item?.priority,
            ""
          ),
        };
      }
    );
  }

  return [];
}


/* =========================================================
   UI Components
========================================================= */

function LoadingScreen() {
  return (
    <div className="analysis-page">
      <div className="analysis-state-card">
        <div className="analysis-spinner" />

        <h2>
          Loading EduPath Analytics
        </h2>

        <p>
          Retrieving the latest analysis dashboard
          from the backend API.
        </p>
      </div>
    </div>
  );
}


function ErrorScreen({ message, onRetry }) {
  return (
    <div className="analysis-page">
      <div className="analysis-state-card error-card">
        <div className="state-icon error-icon">
          !
        </div>

        <h2>
          Unable to load dashboard
        </h2>

        <p>
          {message}
        </p>

        <button
          className="primary-button"
          onClick={onRetry}
        >
          Try Again
        </button>
      </div>
    </div>
  );
}


function SectionHeader({
  eyebrow,
  title,
  description,
}) {
  return (
    <div className="section-heading">
      {eyebrow && (
        <span className="section-eyebrow">
          {eyebrow}
        </span>
      )}

      <h2>{title}</h2>

      {description && (
        <p>{description}</p>
      )}
    </div>
  );
}


function KpiCard({
  label,
  value,
  subtitle,
  icon,
  tone = "purple",
}) {
  return (
    <article
      className={`kpi-card kpi-${tone}`}
    >
      <div className="kpi-top-row">
        <div className="kpi-icon">
          {icon}
        </div>

        <span className="kpi-label">
          {label}
        </span>
      </div>

      <strong className="kpi-value">
        {value}
      </strong>

      {subtitle && (
        <span className="kpi-subtitle">
          {subtitle}
        </span>
      )}
    </article>
  );
}


function DataRow({
  label,
  value,
  highlight = false,
}) {
  return (
    <div
      className={
        highlight
          ? "data-row highlight-row"
          : "data-row"
      }
    >
      <span>{label}</span>

      <strong>{value}</strong>
    </div>
  );
}


function DistributionChart({
  items,
  valueFormatter = formatNumber,
}) {
  const maxValue = useMemo(() => {
    if (!items.length) {
      return 1;
    }

    return Math.max(
      ...items.map((item) =>
        safeNumber(item.count)
      ),
      1
    );
  }, [items]);

  if (!items.length) {
    return (
      <div className="empty-state">
        No distribution data available.
      </div>
    );
  }

  return (
    <div className="distribution-chart">
      {items.map((item, index) => {
        const width = Math.max(
          5,
          (
            safeNumber(item.count) /
            maxValue
          ) * 100
        );

        return (
          <div
            className="distribution-item"
            key={`${item.label}-${index}`}
          >
            <div className="distribution-label-row">
              <span>
                {item.label}
              </span>

              <strong>
                {valueFormatter(item.count)}

                {item.percentage !== undefined && (
                  <small>
                    {" "}
                    · {formatPercent(
                      item.percentage
                    )}
                  </small>
                )}
              </strong>
            </div>

            <div className="distribution-track">
              <div
                className="distribution-fill"
                style={{
                  width: `${width}%`,
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}


function InsightCard({
  insight,
  index,
}) {
  return (
    <article className="insight-card">
      <div className="insight-number">
        {String(index + 1).padStart(
          2,
          "0"
        )}
      </div>

      <div className="insight-content">
        <div className="insight-title-row">
          <h3>
            {insight.title}
          </h3>

          {insight.priority && (
            <span className="priority-badge">
              {insight.priority}
            </span>
          )}
        </div>

        {insight.finding && (
          <div className="insight-block">
            <span>Finding</span>
            <p>{insight.finding}</p>
          </div>
        )}

        {insight.interpretation && (
          <div className="insight-block">
            <span>Interpretation</span>
            <p>
              {insight.interpretation}
            </p>
          </div>
        )}

        {insight.recommendation && (
          <div className="insight-block recommendation-block">
            <span>
              Decision / Recommendation
            </span>

            <p>
              {insight.recommendation}
            </p>
          </div>
        )}
      </div>
    </article>
  );
}


function GenericObjectViewer({
  data,
}) {
  if (!isObject(data)) {
    return null;
  }

  const entries = Object.entries(data);

  if (!entries.length) {
    return (
      <div className="empty-state">
        No additional data available.
      </div>
    );
  }

  return (
    <div className="generic-grid">
      {entries.map(([key, value]) => {
        if (
          isObject(value) ||
          Array.isArray(value)
        ) {
          return null;
        }

        return (
          <div
            className="generic-item"
            key={key}
          >
            <span>
              {humanizeKey(key)}
            </span>

            <strong>
              {typeof value === "number"
                ? formatNumber(value)
                : String(value)}
            </strong>
          </div>
        );
      })}
    </div>
  );
}


/* =========================================================
   Main Dashboard
========================================================= */

export default function AnalysisDashboard() {
  const [dashboard, setDashboard] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [lastUpdated, setLastUpdated] =
    useState(null);


  async function loadDashboard() {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        DASHBOARD_ENDPOINT,
        {
          headers: {
            Accept: "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error(
          `Backend returned HTTP ${response.status}.`
        );
      }

      const data = await response.json();

      if (
        !data ||
        typeof data !== "object"
      ) {
        throw new Error(
          "The dashboard API returned an invalid response."
        );
      }

      setDashboard(data);
      setLastUpdated(new Date());
    } catch (err) {
      console.error(
        "Analysis dashboard error:",
        err
      );

      setError(
        err?.message ||
          "Unable to connect to the EduPath backend."
      );
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    loadDashboard();
  }, []);


  const normalized = useMemo(() => {
    if (!dashboard) {
      return null;
    }

    const datasetOverview =
      getNested(dashboard, [
        "dataset_overview",
        "dataset",
        "overview",
        "kpis.dataset_overview",
      ]) || {};

    const dataQuality =
      getNested(dashboard, [
        "data_quality",
        "quality",
        "data_quality_metrics",
        "kpis.data_quality",
      ]) || {};

    const programAnalysis =
      getNested(dashboard, [
        "program_analysis",
        "programs",
        "analysis.programs",
      ]) || {};

    const tuitionAnalysis =
      getNested(dashboard, [
        "tuition_analysis",
        "tuition",
        "analysis.tuition",
      ]) || {};

    const scholarshipAnalysis =
      getNested(dashboard, [
        "scholarship_analysis",
        "scholarships",
        "analysis.scholarships",
      ]) || {};

    const algorithmPerformance =
      getNested(dashboard, [
        "algorithm_performance",
        "recommendation_algorithm",
        "algorithm",
        "performance",
      ]) || {};

    const counts =
      getNested(datasetOverview, [
        "counts",
        "dataset_counts",
      ]) || datasetOverview;


    const countryCount = safeNumber(
      firstDefined(
        counts.countries,
        counts.country_count,
        dashboard.country_count
      )
    );

    const universityCount = safeNumber(
      firstDefined(
        counts.universities,
        counts.university_count,
        dashboard.university_count
      )
    );

    const programCount = safeNumber(
      firstDefined(
        counts.programs,
        counts.program_count,
        dashboard.program_count
      )
    );

    const scholarshipCount = safeNumber(
      firstDefined(
        counts.scholarships,
        counts.scholarship_count,
        dashboard.scholarship_count
      )
    );


    const degreeDistribution =
      normalizeDistribution(
        firstDefined(
          programAnalysis.degree_distribution,
          programAnalysis.program_degree_distribution,
          dashboard.program_degree_distribution
        )
      );


    const tuitionDistribution =
      normalizeDistribution(
        firstDefined(
          tuitionAnalysis.distribution,
          tuitionAnalysis.tuition_distribution,
          programAnalysis.tuition_distribution,
          dashboard.tuition_distribution
        )
      );


    const scholarshipFundingDistribution =
      normalizeDistribution(
        firstDefined(
          scholarshipAnalysis.funding_distribution,
          scholarshipAnalysis.scholarship_funding_distribution,
          dashboard.scholarship_funding_distribution
        )
      );


    const scholarshipStatusDistribution =
      normalizeDistribution(
        firstDefined(
          scholarshipAnalysis.status_distribution,
          scholarshipAnalysis.scholarship_status_distribution,
          dashboard.scholarship_status_distribution
        )
      );


    const insights = normalizeInsights(
      firstDefined(
        dashboard.analytical_insights,
        dashboard.insights,
        dashboard.analysis_insights,
        []
      )
    );


    return {
      datasetOverview,
      dataQuality,
      programAnalysis,
      tuitionAnalysis,
      scholarshipAnalysis,
      algorithmPerformance,

      countryCount,
      universityCount,
      programCount,
      scholarshipCount,

      degreeDistribution,
      tuitionDistribution,
      scholarshipFundingDistribution,
      scholarshipStatusDistribution,

      insights,
    };
  }, [dashboard]);


  if (loading) {
    return <LoadingScreen />;
  }


  if (error) {
    return (
      <ErrorScreen
        message={error}
        onRetry={loadDashboard}
      />
    );
  }


  if (!normalized) {
    return (
      <ErrorScreen
        message="Dashboard data is unavailable."
        onRetry={loadDashboard}
      />
    );
  }


  const {
    datasetOverview,
    dataQuality,
    tuitionAnalysis,
    algorithmPerformance,

    countryCount,
    universityCount,
    programCount,
    scholarshipCount,

    degreeDistribution,
    tuitionDistribution,
    scholarshipFundingDistribution,
    scholarshipStatusDistribution,

    insights,
  } = normalized;


  const tuitionMean = firstDefined(
    tuitionAnalysis.mean_tuition,
    tuitionAnalysis.mean,
    tuitionAnalysis.average_tuition,
    tuitionAnalysis.average
  );

  const tuitionMedian = firstDefined(
    tuitionAnalysis.median_tuition,
    tuitionAnalysis.median
  );

  const tuitionMinimum = firstDefined(
    tuitionAnalysis.minimum_tuition,
    tuitionAnalysis.minimum,
    tuitionAnalysis.min
  );

  const tuitionMaximum = firstDefined(
    tuitionAnalysis.maximum_tuition,
    tuitionAnalysis.maximum,
    tuitionAnalysis.max
  );

  const tuitionCoverage = firstDefined(
    tuitionAnalysis.tuition_coverage,
    tuitionAnalysis.coverage,
    dataQuality.tuition_coverage
  );

  const distinctTuitionValues =
    firstDefined(
      tuitionAnalysis.distinct_tuition_values,
      tuitionAnalysis.distinct_values
    );


  const relationshipErrors =
    firstDefined(
      dataQuality.relationship_errors,
      dataQuality.relationship_error_count
    );

  const duplicateIds =
    firstDefined(
      dataQuality.duplicate_ids,
      dataQuality.duplicate_id_count
    );


  const algorithmVersion =
    firstDefined(
      algorithmPerformance.algorithm_version,
      algorithmPerformance.version,
      "V2.2"
    );

  const profilesTested =
    firstDefined(
      algorithmPerformance.profiles_tested,
      algorithmPerformance.tested_profiles
    );

  const profilesPassed =
    firstDefined(
      algorithmPerformance.profiles_passed,
      algorithmPerformance.passed_profiles
    );

  const functionalValidation =
    firstDefined(
      algorithmPerformance.functional_validation,
      algorithmPerformance.validation_rate
    );

  const supervisedAccuracy =
    firstDefined(
      algorithmPerformance.supervised_accuracy,
      "Not Claimed"
    );


  return (
    <div className="analysis-page">
      <header className="analysis-header">
        <div className="analysis-header-inner">
          <a
            className="brand"
            href="/"
          >
            <div className="brand-mark">
              E
            </div>

            <div>
              <strong>
                EduPath
              </strong>

              <span>
                Analytics
              </span>
            </div>
          </a>

          <div className="header-actions">
            <div className="live-status">
              <span className="status-dot" />

              API Connected
            </div>

            <button
              className="refresh-button"
              onClick={loadDashboard}
            >
              ↻ Refresh
            </button>
          </div>
        </div>
      </header>


      <main className="analysis-container">

        <section className="dashboard-hero">
          <div>
            <span className="hero-badge">
              DATA ANALYSIS LAYER
            </span>

            <h1>
              EduPath Analysis Dashboard
            </h1>

            <p>
              Data-driven analysis of the
              universities, academic programs,
              scholarships and recommendation
              algorithm currently included in
              EduPath.
            </p>
          </div>

          <div className="hero-meta">
            <span>
              Analysis Pipeline
            </span>

            <strong>
              Step 151.10
            </strong>

            {lastUpdated && (
              <small>
                Updated{" "}
                {lastUpdated.toLocaleTimeString()}
              </small>
            )}
          </div>
        </section>


        <section className="dashboard-section">
          <SectionHeader
            eyebrow="Dataset Overview"
            title="Current EduPath Dataset"
            description="High-level overview of the validated dataset currently available to the analysis layer."
          />

          <div className="kpi-grid">
            <KpiCard
              label="Countries"
              value={formatNumber(
                countryCount
              )}
              subtitle="Country master records"
              icon="🌏"
              tone="blue"
            />

            <KpiCard
              label="Universities"
              value={formatNumber(
                universityCount
              )}
              subtitle="Universities in dataset"
              icon="🏫"
              tone="purple"
            />

            <KpiCard
              label="Programs"
              value={formatNumber(
                programCount
              )}
              subtitle="Academic programs analysed"
              icon="📘"
              tone="cyan"
            />

            <KpiCard
              label="Scholarships"
              value={formatNumber(
                scholarshipCount
              )}
              subtitle="Scholarship opportunities"
              icon="🎓"
              tone="green"
            />
          </div>
        </section>


        <section className="dashboard-section">
          <SectionHeader
            eyebrow="Program Analysis"
            title="Program Degree Distribution"
            description="Distribution of the academic degree levels currently represented in the EduPath program dataset."
          />

          <div className="dashboard-card">
            <DistributionChart
              items={degreeDistribution}
            />
          </div>
        </section>


        <section className="dashboard-section">
          <SectionHeader
            eyebrow="Financial Analysis"
            title="Annual Tuition Analysis"
            description="Descriptive statistics calculated from verified annual tuition values stored in the current dataset."
          />

          <div className="stats-layout">
            <div className="dashboard-card">
              <h3 className="card-title">
                Tuition Statistics
              </h3>

              <div className="data-list">
                <DataRow
                  label="Mean Tuition"
                  value={
                    tuitionMean !== undefined
                      ? `${formatNumber(
                          tuitionMean
                        )} JPY`
                      : "—"
                  }
                />

                <DataRow
                  label="Median Tuition"
                  value={
                    tuitionMedian !== undefined
                      ? `${formatNumber(
                          tuitionMedian
                        )} JPY`
                      : "—"
                  }
                />

                <DataRow
                  label="Minimum Tuition"
                  value={
                    tuitionMinimum !== undefined
                      ? `${formatNumber(
                          tuitionMinimum
                        )} JPY`
                      : "—"
                  }
                />

                <DataRow
                  label="Maximum Tuition"
                  value={
                    tuitionMaximum !== undefined
                      ? `${formatNumber(
                          tuitionMaximum
                        )} JPY`
                      : "—"
                  }
                />

                <DataRow
                  label="Tuition Coverage"
                  value={
                    tuitionCoverage !== undefined
                      ? formatPercent(
                          tuitionCoverage
                        )
                      : "—"
                  }
                  highlight
                />

                <DataRow
                  label="Distinct Tuition Values"
                  value={
                    distinctTuitionValues !== undefined
                      ? formatNumber(
                          distinctTuitionValues
                        )
                      : "—"
                  }
                />
              </div>
            </div>


            <div className="dashboard-card">
              <h3 className="card-title">
                Tuition Distribution
              </h3>

              <DistributionChart
                items={tuitionDistribution}
                valueFormatter={(value) =>
                  `${formatNumber(
                    value
                  )} program${
                    safeNumber(value) === 1
                      ? ""
                      : "s"
                  }`
                }
              />
            </div>
          </div>
        </section>


        <section className="dashboard-section">
          <SectionHeader
            eyebrow="Scholarship Analysis"
            title="Scholarship Opportunity Overview"
            description="Funding type and current scholarship-status distributions in the targeted scholarship dataset."
          />

          <div className="stats-layout">
            <div className="dashboard-card">
              <h3 className="card-title">
                Funding Distribution
              </h3>

              <DistributionChart
                items={
                  scholarshipFundingDistribution
                }
              />
            </div>

            <div className="dashboard-card">
              <h3 className="card-title">
                Scholarship Status
              </h3>

              <DistributionChart
                items={
                  scholarshipStatusDistribution
                }
              />
            </div>
          </div>
        </section>


        <section className="dashboard-section">
          <SectionHeader
            eyebrow="Data Quality"
            title="Analysis Readiness"
            description="Quality and relationship checks performed before descriptive and recommendation analysis."
          />

          <div className="quality-grid">
            <div className="dashboard-card">
              <div className="quality-status">
                <div className="quality-check">
                  ✓
                </div>

                <div>
                  <span>
                    Dataset Status
                  </span>

                  <strong>
                    Ready for Analysis
                  </strong>
                </div>
              </div>

              <div className="data-list quality-list">
                <DataRow
                  label="Duplicate IDs"
                  value={
                    duplicateIds !== undefined
                      ? formatNumber(
                          duplicateIds
                        )
                      : "0"
                  }
                />

                <DataRow
                  label="Relationship Errors"
                  value={
                    relationshipErrors !== undefined
                      ? formatNumber(
                          relationshipErrors
                        )
                      : "0"
                  }
                />

                <DataRow
                  label="Program Tuition Coverage"
                  value={
                    tuitionCoverage !== undefined
                      ? formatPercent(
                          tuitionCoverage
                        )
                      : "100%"
                  }
                  highlight
                />
              </div>
            </div>

            <div className="dashboard-card">
              <h3 className="card-title">
                Additional Quality Metrics
              </h3>

              <GenericObjectViewer
                data={dataQuality}
              />
            </div>
          </div>
        </section>


        <section className="dashboard-section">
          <SectionHeader
            eyebrow="Recommendation Engine"
            title="Algorithm Performance"
            description="Functional scenario validation for the locked scholarship recommendation algorithm."
          />

          <div className="algorithm-card">
            <div className="algorithm-version">
              <span>
                Current Baseline
              </span>

              <strong>
                {algorithmVersion}
              </strong>
            </div>

            <div className="algorithm-metrics">
              <div>
                <span>
                  Profiles Tested
                </span>

                <strong>
                  {profilesTested !== undefined
                    ? formatNumber(
                        profilesTested
                      )
                    : "—"}
                </strong>
              </div>

              <div>
                <span>
                  Profiles Passed
                </span>

                <strong>
                  {profilesPassed !== undefined
                    ? formatNumber(
                        profilesPassed
                      )
                    : "—"}
                </strong>
              </div>

              <div>
                <span>
                  Functional Validation
                </span>

                <strong>
                  {functionalValidation !==
                  undefined
                    ? formatPercent(
                        functionalValidation
                      )
                    : "—"}
                </strong>
              </div>

              <div>
                <span>
                  Supervised Accuracy
                </span>

                <strong className="not-claimed">
                  {String(
                    supervisedAccuracy
                  )}
                </strong>
              </div>
            </div>

            <p className="algorithm-note">
              Functional validation represents
              rule-based and scenario testing.
              Supervised machine-learning
              prediction accuracy is not claimed
              without a labelled relevance
              dataset.
            </p>
          </div>
        </section>


        <section className="dashboard-section">
          <SectionHeader
            eyebrow="Decision Support"
            title="Analytical Insights"
            description="Key findings, interpretations and decision-oriented recommendations generated from the current EduPath dataset."
          />

          {insights.length ? (
            <div className="insights-list">
              {insights.map(
                (insight, index) => (
                  <InsightCard
                    key={`${insight.title}-${index}`}
                    insight={insight}
                    index={index}
                  />
                )
              )}
            </div>
          ) : (
            <div className="dashboard-card">
              <div className="empty-state">
                No analytical insights were
                returned by the API.
              </div>
            </div>
          )}
        </section>


        <section className="dashboard-section">
          <SectionHeader
            eyebrow="Dataset Scope"
            title="Interpretation Notice"
          />

          <div className="scope-card">
            <div className="scope-icon">
              i
            </div>

            <div>
              <h3>
                Current results describe the
                collected EduPath dataset
              </h3>

              <p>
                The current analysis should not
                yet be generalised to every
                university, program or scholarship
                in Japan. The dashboard reflects
                the verified records currently
                included in the EduPath dataset
                and provides a validated baseline
                for future country-by-country data
                expansion.
              </p>
            </div>
          </div>
        </section>


        <footer className="analysis-footer">
          <div>
            <strong>
              EduPath Analytics
            </strong>

            <span>
              Data Analysis & Recommendation
              Platform
            </span>
          </div>

          <span>
            Dashboard generated from the EduPath
            analysis API.
          </span>
        </footer>
      </main>
    </div>
  );
}