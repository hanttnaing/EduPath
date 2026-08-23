import { useEffect, useMemo, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { authFetch, readApiError } from './api'
import './MyAnalyticsPage.css'


const SCORE_MAXIMUMS = {
  degree_level: 20,
  preferred_country: 15,
  field_similarity: 20,
  funding_type: 20,
  scholarship_status: 10,
  nationality: 5,
  gpa: 5,
  english: 5,
}


const EVIDENCE_COLORS = [
  '#16a34a',
  '#f59e0b',
  '#94a3b8',
]


function shortLabel(value, maximum = 22) {
  const text = String(value || 'Opportunity')

  if (text.length <= maximum) {
    return text
  }

  return `${text.slice(0, maximum - 3)}...`
}


function formatMetric(value) {
  const number = Number(value)

  if (!Number.isFinite(number)) {
    return '?'
  }

  return Number.isInteger(number)
    ? String(number)
    : number.toFixed(1)
}


function humanizeKey(value) {
  return String(value || '')
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase()
    )
}


function getGapCategory(text) {
  const value = String(text || '').toLowerCase()

  if (
    value.includes('field') ||
    value.includes('major')
  ) {
    return 'Field alignment'
  }

  if (value.includes('gpa')) {
    return 'GPA requirement'
  }

  if (
    value.includes('english') ||
    value.includes('ielts') ||
    value.includes('toefl')
  ) {
    return 'English requirement'
  }

  if (
    value.includes('nationality') ||
    value.includes('citizenship')
  ) {
    return 'Nationality evidence'
  }

  if (value.includes('age')) {
    return 'Age requirement'
  }

  if (
    value.includes('deadline') ||
    value.includes('application date')
  ) {
    return 'Deadline evidence'
  }

  if (
    value.includes('budget') ||
    value.includes('tuition') ||
    value.includes('financial')
  ) {
    return 'Financial fit'
  }

  return 'Other requirement'
}


function isUnknownGap(text) {
  const value = String(text || '').toLowerCase()

  return (
    value.includes('unavailable') ||
    value.includes('unknown') ||
    value.includes('not available') ||
    value.includes('not provided') ||
    value.includes('not specified')
  )
}


function MyAnalyticsPage({
  embedded = false,
  initialData = null,
}) {
  const hasInitialData =
    Boolean(
      initialData?.profile &&
      initialData?.programData &&
      initialData?.scholarshipData &&
      initialData?.savedData
    )

  const pageClassName =
    embedded
      ? 'my-analytics-page embedded'
      : 'my-analytics-page'

  const [profile, setProfile] =
    useState(
      initialData?.profile ??
        null
    )

  const [
    programData,
    setProgramData,
  ] = useState(
    initialData?.programData ??
      null
  )

  const [
    scholarshipData,
    setScholarshipData,
  ] = useState(
    initialData?.scholarshipData ??
      null
  )

  const [savedData, setSavedData] =
    useState(
      initialData?.savedData ??
        null
    )

  const [loading, setLoading] =
    useState(
      !hasInitialData
    )

  const [error, setError] =
    useState('')


  useEffect(() => {
    if (hasInitialData) {
      setProfile(
        initialData.profile
      )

      setProgramData(
        initialData.programData
      )

      setScholarshipData(
        initialData.scholarshipData
      )

      setSavedData(
        initialData.savedData
      )

      setError('')
      setLoading(false)

      return
    }

    let cancelled = false

    const loadAnalytics = async () => {
      try {
        setLoading(true)
        setError('')

        const [
          profileResponse,
          programResponse,
          scholarshipResponse,
          savedResponse,
        ] = await Promise.all([
          authFetch(
            '/api/me/profile'
          ),

          authFetch(
            '/api/me/recommendations/programs?top_k=5'
          ),

          authFetch(
            '/api/me/recommendations/scholarships?top_k=5'
          ),

          authFetch(
            '/api/me/saved'
          ),
        ])


        if (!profileResponse.ok) {
          throw new Error(
            await readApiError(
              profileResponse,
              'Unable to load your profile.'
            )
          )
        }


        if (!programResponse.ok) {
          throw new Error(
            await readApiError(
              programResponse,
              'Unable to load programme analytics.'
            )
          )
        }


        if (!scholarshipResponse.ok) {
          throw new Error(
            await readApiError(
              scholarshipResponse,
              'Unable to load scholarship analytics.'
            )
          )
        }


        if (!savedResponse.ok) {
          throw new Error(
            await readApiError(
              savedResponse,
              'Unable to load saved opportunities.'
            )
          )
        }


        const [
          profileResult,
          programResult,
          scholarshipResult,
          savedResult,
        ] = await Promise.all([
          profileResponse.json(),
          programResponse.json(),
          scholarshipResponse.json(),
          savedResponse.json(),
        ])


        if (cancelled) {
          return
        }


        setProfile(profileResult)
        setProgramData(programResult)
        setScholarshipData(
          scholarshipResult
        )
        setSavedData(savedResult)

      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : 'Unable to load personalized analytics.'
          )
        }

      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }


    loadAnalytics()


    return () => {
      cancelled = true
    }
  }, [])


  const programRecommendations =
    useMemo(
      () =>
        Array.isArray(
          programData?.recommendations
        )
          ? programData.recommendations
          : [],
      [programData]
    )


  const scholarshipRecommendations =
    useMemo(
      () =>
        Array.isArray(
          scholarshipData?.recommendations
        )
          ? scholarshipData.recommendations
          : [],
      [scholarshipData]
    )


  const allRecommendations =
    useMemo(
      () => [
        ...programRecommendations.map(
          (item) => ({
            ...item,
            analytics_type: 'Programme',
          })
        ),

        ...scholarshipRecommendations.map(
          (item) => ({
            ...item,
            analytics_type: 'Scholarship',
          })
        ),
      ],
      [
        programRecommendations,
        scholarshipRecommendations,
      ]
    )


  const bestRecommendation =
    useMemo(
      () =>
        [...allRecommendations].sort(
          (a, b) =>
            Number(
              b.match_score || 0
            ) -
            Number(
              a.match_score || 0
            )
        )[0] || null,
      [allRecommendations]
    )


  const programmeChartData =
    useMemo(
      () =>
        programRecommendations.map(
          (item, index) => ({
            name: shortLabel(
              item.program_name ||
                `Programme ${index + 1}`
            ),
            score:
              Number(
                item.match_score
              ) || 0,
          })
        ),
      [programRecommendations]
    )


  const scholarshipChartData =
    useMemo(
      () =>
        scholarshipRecommendations.map(
          (item, index) => ({
            name: shortLabel(
              item.scholarship_name ||
                `Scholarship ${index + 1}`
            ),
            score:
              Number(
                item.match_score
              ) || 0,
          })
        ),
      [scholarshipRecommendations]
    )


  const scoreBreakdownData =
    useMemo(() => {
      if (!bestRecommendation) {
        return []
      }

      const breakdown =
        bestRecommendation.score_breakdown ||
        {}

      return Object.entries(
        breakdown
      ).map(([key, value]) => ({
        component:
          humanizeKey(key),

        score:
          Number(value) || 0,

        maximum:
          SCORE_MAXIMUMS[key] ?? null,
      }))
    }, [bestRecommendation])


  const evidenceData =
    useMemo(() => {
      let positive = 0
      let knownGap = 0
      let unknown = 0

      allRecommendations.forEach(
        (item) => {
          positive += Array.isArray(
            item.match_reasons
          )
            ? item.match_reasons.length
            : 0

          const gaps = Array.isArray(
            item.requirement_gaps
          )
            ? item.requirement_gaps
            : []

          gaps.forEach((gap) => {
            if (isUnknownGap(gap)) {
              unknown += 1
            } else {
              knownGap += 1
            }
          })
        }
      )

      return [
        {
          name: 'Known matches',
          value: positive,
        },
        {
          name: 'Known gaps',
          value: knownGap,
        },
        {
          name: 'Unknown evidence',
          value: unknown,
        },
      ].filter(
        (item) => item.value > 0
      )
    }, [allRecommendations])


  const gapInsights =
    useMemo(() => {
      const counter = new Map()

      allRecommendations.forEach(
        (item) => {
          const gaps = Array.isArray(
            item.requirement_gaps
          )
            ? item.requirement_gaps
            : []

          gaps.forEach((gap) => {
            const category =
              getGapCategory(gap)

            counter.set(
              category,
              (counter.get(category) || 0) +
                1
            )
          })
        }
      )

      return [...counter.entries()]
        .map(
          ([category, count]) => ({
            category,
            count,
          })
        )
        .sort(
          (a, b) =>
            b.count - a.count
        )
        .slice(0, 6)
    }, [allRecommendations])


  const savedCount =
    useMemo(() => {
      const universities =
        Array.isArray(
          savedData?.saved_universities
        )
          ? savedData.saved_universities
              .length
          : 0

      const programs =
        Array.isArray(
          savedData?.saved_programs
        )
          ? savedData.saved_programs
              .length
          : 0

      const scholarships =
        Array.isArray(
          savedData?.saved_scholarships
        )
          ? savedData.saved_scholarships
              .length
          : 0

      return (
        universities +
        programs +
        scholarships
      )
    }, [savedData])


  const eligibleCandidates =
    useMemo(
      () =>
        Number(
          programData?.eligible_candidates ||
            0
        ) +
        Number(
          scholarshipData
            ?.eligible_candidates || 0
        ),
      [
        programData,
        scholarshipData,
      ]
    )


  const profileCompleteness =
    useMemo(() => {
      if (!profile) {
        return 0
      }

      const checks = [
        Boolean(profile.nationality),
        Boolean(
          profile.target_degree_level
        ),
        Boolean(
          profile.preferred_major
        ),
        profile.gpa !== null &&
          profile.gpa !== undefined,
        Boolean(
          profile.ielts_score ||
            profile.toefl_score
        ),
        Array.isArray(
          profile.preferred_countries
        ) &&
          profile.preferred_countries
            .length > 0,
        profile.annual_budget !== null &&
          profile.annual_budget !==
            undefined,
        profile.scholarship_required
          ? Boolean(
              profile.preferred_funding_type
            )
          : true,
      ]

      const completed =
        checks.filter(Boolean).length

      return Math.round(
        (completed / checks.length) *
          100
      )
    }, [profile])


  const bestScore =
    bestRecommendation
      ? Number(
          bestRecommendation.match_score ||
            0
        )
      : 0


  if (loading) {
    return (
      <section className={pageClassName}>
        <div className="my-analytics-state">
          <div className="my-analytics-loader" />
          <h2>
            Building your analytics
          </h2>
          <p>
            EduPath is analysing your profile
            and current recommendations.
          </p>
        </div>
      </section>
    )
  }


  if (error) {
    return (
      <section className={pageClassName}>
        <div className="my-analytics-state error">
          <h2>
            Analytics unavailable
          </h2>
          <p>{error}</p>
        </div>
      </section>
    )
  }


  return (
    <section className={pageClassName}>
      {!embedded && (
      <header className="my-analytics-hero">
        <div>
          <p className="my-analytics-eyebrow">
            PERSONALIZED DECISION SUPPORT
          </p>

          <h1>
            My Analytics
          </h1>

          <p>
            Understand how your academic
            profile, preferences and known
            eligibility information affect
            your current EduPath
            recommendations.
          </p>
        </div>

        <div className="my-analytics-profile-chip">
          <span>
            Profile readiness
          </span>

          <strong>
            {profileCompleteness}%
          </strong>
        </div>
      </header>
      )}


      <div className="my-analytics-summary-grid">
        <article>
          <span>Best Match</span>

          <strong>
            {formatMetric(
              bestScore
            )}%
          </strong>

          <small>
            Highest current recommendation
            score
          </small>
        </article>


        <article>
          <span>
            Eligible Matches
          </span>

          <strong>
            {eligibleCandidates}
          </strong>

          <small>
            Candidates remaining after known
            hard eligibility rules
          </small>
        </article>


        <article>
          <span>
            Saved Opportunities
          </span>

          <strong>
            {savedCount}
          </strong>

          <small>
            Opportunities you chose to keep
          </small>
        </article>


        <article>
          <span>
            Recommendations Analysed
          </span>

          <strong>
            {allRecommendations.length}
          </strong>

          <small>
            Current personalized results used
            in this dashboard
          </small>
        </article>
      </div>


      <div className="my-analytics-two-column">
        <section className="my-analytics-card">
          <div className="my-analytics-card-heading">
            <div>
              <p>
                PROGRAMME FIT
              </p>

              <h2>
                Top Programme Matches
              </h2>
            </div>

            <span>
              Match score / 100
            </span>
          </div>


          {programmeChartData.length ? (
            <div className="my-analytics-chart tall">
              <ResponsiveContainer
                width="100%"
                height="100%"
              >
                <BarChart
                  data={
                    programmeChartData
                  }
                  layout="vertical"
                  margin={{
                    top: 8,
                    right: 20,
                    left: 20,
                    bottom: 8,
                  }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                  />

                  <XAxis
                    type="number"
                    domain={[0, 100]}
                  />

                  <YAxis
                    type="category"
                    dataKey="name"
                    width={175}
                    tick={{
                      fontSize: 12,
                    }}
                  />

                  <Tooltip />

                  <Bar
                    dataKey="score"
                    name="Match score"
                    fill="#4f46e5"
                    radius={[
                      0,
                      8,
                      8,
                      0,
                    ]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="my-analytics-empty">
              No programme recommendations
              are currently available.
            </p>
          )}
        </section>


        <section className="my-analytics-card">
          <div className="my-analytics-card-heading">
            <div>
              <p>
                SCHOLARSHIP FIT
              </p>

              <h2>
                Top Scholarship Matches
              </h2>
            </div>

            <span>
              Match score / 100
            </span>
          </div>


          {scholarshipChartData.length ? (
            <div className="my-analytics-chart tall">
              <ResponsiveContainer
                width="100%"
                height="100%"
              >
                <BarChart
                  data={
                    scholarshipChartData
                  }
                  layout="vertical"
                  margin={{
                    top: 8,
                    right: 20,
                    left: 20,
                    bottom: 8,
                  }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                  />

                  <XAxis
                    type="number"
                    domain={[0, 100]}
                  />

                  <YAxis
                    type="category"
                    dataKey="name"
                    width={175}
                    tick={{
                      fontSize: 12,
                    }}
                  />

                  <Tooltip />

                  <Bar
                    dataKey="score"
                    name="Match score"
                    fill="#0891b2"
                    radius={[
                      0,
                      8,
                      8,
                      0,
                    ]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="my-analytics-empty">
              No scholarship recommendations
              are currently available.
            </p>
          )}
        </section>
      </div>


      <div className="my-analytics-two-column my-analytics-middle-grid">
        <section className="my-analytics-card">
          <div className="my-analytics-card-heading">
            <div>
              <p>
                SCORE EXPLAINABILITY
              </p>

              <h2>
                Why Your Best Match Scores
                This Way
              </h2>
            </div>
          </div>


          {bestRecommendation ? (
            <>
              <div className="my-analytics-best-match">
                <div>
                  <span>
                    {
                      bestRecommendation
                        .analytics_type
                    }
                  </span>

                  <strong>
                    {bestRecommendation
                      .program_name ||
                      bestRecommendation
                        .scholarship_name ||
                      'Top recommendation'}
                  </strong>
                </div>

                <b>
                  {formatMetric(
                    bestScore
                  )}
                  /100
                </b>
              </div>


              <div className="my-analytics-chart breakdown">
                <ResponsiveContainer
                  width="100%"
                  height="100%"
                >
                  <BarChart
                    data={
                      scoreBreakdownData
                    }
                    layout="vertical"
                    margin={{
                      top: 10,
                      right: 24,
                      left: 24,
                      bottom: 10,
                    }}
                  >
                    <CartesianGrid
                      strokeDasharray="3 3"
                    />

                    <XAxis
                      type="number"
                      domain={[0, 20]}
                    />

                    <YAxis
                      type="category"
                      dataKey="component"
                      width={145}
                      tick={{
                        fontSize: 12,
                      }}
                    />

                    <Tooltip />

                    <Legend />

                    <Bar
                      dataKey="maximum"
                      name="Maximum points"
                      fill="#e2e8f0"
                      radius={[
                        0,
                        8,
                        8,
                        0,
                      ]}
                    />

                    <Bar
                      dataKey="score"
                      name="Points earned"
                      fill="#7c3aed"
                      radius={[
                        0,
                        8,
                        8,
                        0,
                      ]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </>
          ) : (
            <p className="my-analytics-empty">
              Generate recommendations to see
              score explainability.
            </p>
          )}
        </section>


        <section className="my-analytics-card">
          <div className="my-analytics-card-heading">
            <div>
              <p>
                EVIDENCE QUALITY
              </p>

              <h2>
                Recommendation Evidence Mix
              </h2>
            </div>
          </div>


          {evidenceData.length ? (
            <>
              <div className="my-analytics-chart pie">
                <ResponsiveContainer
                  width="100%"
                  height="100%"
                >
                  <PieChart>
                    <Pie
                      data={
                        evidenceData
                      }
                      dataKey="value"
                      nameKey="name"
                      innerRadius={62}
                      outerRadius={100}
                      paddingAngle={3}
                    >
                      {evidenceData.map(
                        (
                          item,
                          index
                        ) => (
                          <Cell
                            key={
                              item.name
                            }
                            fill={
                              EVIDENCE_COLORS[
                                index %
                                  EVIDENCE_COLORS.length
                              ]
                            }
                          />
                        )
                      )}
                    </Pie>

                    <Tooltip />

                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <p className="my-analytics-note">
                This chart summarizes the
                explainability signals across
                your current recommendations.
                Unknown evidence is kept
                separate and is not treated
                automatically as an eligibility
                failure.
              </p>
            </>
          ) : (
            <p className="my-analytics-empty">
              No recommendation evidence is
              currently available.
            </p>
          )}
        </section>
      </div>


      <div className="my-analytics-two-column my-analytics-lower-grid">
        <section className="my-analytics-card">
          <div className="my-analytics-card-heading">
            <div>
              <p>
                YOUR INPUTS
              </p>

              <h2>
                Profile Snapshot
              </h2>
            </div>
          </div>


          <div className="my-analytics-profile-grid">
            <div>
              <span>
                Target Degree
              </span>

              <strong>
                {profile
                  ?.target_degree_level ||
                  'Not set'}
              </strong>
            </div>


            <div>
              <span>
                Preferred Major
              </span>

              <strong>
                {profile
                  ?.preferred_major ||
                  'Not set'}
              </strong>
            </div>


            <div>
              <span>GPA</span>

              <strong>
                {profile?.gpa ??
                  'Not set'}

                {profile?.gpa_scale
                  ? ` / ${profile.gpa_scale}`
                  : ''}
              </strong>
            </div>


            <div>
              <span>English</span>

              <strong>
                {profile?.ielts_score
                  ? `IELTS ${profile.ielts_score}`
                  : profile?.toefl_score
                    ? `TOEFL ${profile.toefl_score}`
                    : 'Not set'}
              </strong>
            </div>


            <div>
              <span>
                Funding Goal
              </span>

              <strong>
                {profile
                  ?.preferred_funding_type ||
                  (profile
                    ?.scholarship_required
                    ? 'Not set'
                    : 'Not required')}
              </strong>
            </div>


            <div>
              <span>
                Preferred Countries
              </span>

              <strong>
                {Array.isArray(
                  profile
                    ?.preferred_countries
                ) &&
                profile
                  .preferred_countries
                  .length
                  ? profile.preferred_countries.join(
                      ', '
                    )
                  : 'Not set'}
              </strong>
            </div>


            <div>
              <span>
                Annual Budget
              </span>

              <strong>
                {profile?.annual_budget ??
                  'Not set'}

                {profile?.annual_budget
                  ? ` ${profile.budget_currency || ''}`
                  : ''}
              </strong>
            </div>


            <div>
              <span>
                Nationality
              </span>

              <strong>
                {profile?.nationality ||
                  'Not set'}
              </strong>
            </div>
          </div>
        </section>


        <section className="my-analytics-card">
          <div className="my-analytics-card-heading">
            <div>
              <p>
                NEXT ACTIONS
              </p>

              <h2>
                What To Check Next
              </h2>
            </div>
          </div>


          {gapInsights.length ? (
            <div className="my-analytics-insights">
              {gapInsights.map(
                (item) => (
                  <article
                    key={
                      item.category
                    }
                  >
                    <div>
                      <strong>
                        {
                          item.category
                        }
                      </strong>

                      <span>
                        Appears in{' '}
                        {item.count}{' '}
                        current recommendation
                        {item.count === 1
                          ? ''
                          : 's'}
                      </span>
                    </div>

                    <b>
                      {item.count}
                    </b>
                  </article>
                )
              )}
            </div>
          ) : (
            <p className="my-analytics-empty">
              No major requirement gaps were
              detected in the current
              recommendations.
            </p>
          )}
        </section>
      </div>


      <footer className="my-analytics-footer-note">
        <strong>
          How to read these analytics
        </strong>

        <p>
          Match scores describe how well an
          opportunity aligns with your current
          profile under EduPath&apos;s known
          rules and weighted criteria. They do
          not guarantee admission or
          scholarship eligibility when source
          requirements are unknown.
        </p>
      </footer>
    </section>
  )
}


export default MyAnalyticsPage
