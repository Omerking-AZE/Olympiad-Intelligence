import ReportIssue from "./ReportIssue";

export type Recommendation = {
  problem_id: string;

  title?: string | null;

  competition?: string | null;
  year?: number | null;
  problem_number?: number | null;
  section?: string | null;

  target_domain: string;

  difficulty_score: number;

  student_skill: number;

  recommendation_skill: number;

  weakness_priority: number;

  weakness_classification: string;

  weakness_confidence: number;

  difficulty_gap: number;

  difficulty_fit: number;

  adaptive_score: number;

  training_zone: boolean;

  skill_unknown: boolean;

  problem_type: string;

  metadata_status?: string | null;

  match_score?: number | null;

  source?: string | null;

  source_url?: string | null;
};

type RecommendationsProps = {
  recommendations: Recommendation[];
};

function cleanText(
  value?: string | null
): string {
  if (
    value === null ||
    value === undefined
  ) {
    return "";
  }

  return String(value).trim();
}

function getProblemTitle(
  problem: Recommendation
): string {
  const title = cleanText(
    problem.title
  );

  if (title) {
    return title;
  }

  const competition =
    cleanText(
      problem.competition
    );

  const year =
    problem.year !== null &&
    problem.year !== undefined
      ? Number(problem.year)
      : null;

  const problemNumber =
    problem.problem_number !==
      null &&
    problem.problem_number !==
      undefined
      ? Number(
          problem.problem_number
        )
      : null;

  if (
    competition &&
    year !== null &&
    Number.isFinite(year) &&
    problemNumber !== null &&
    Number.isFinite(problemNumber)
  ) {
    const normalizedCompetition =
      competition
        .toUpperCase()
        .includes("IMO")
        ? "IMO"
        : competition;

    return (
      `${normalizedCompetition} ` +
      `${year} ` +
      `P${problemNumber}`
    );
  }

  if (
    competition &&
    year !== null &&
    Number.isFinite(year)
  ) {
    return (
      `${competition} ${year}`
    );
  }

  if (competition) {
    return competition;
  }

  return "Olympiad Problem";
}

function formatDomain(
  value: string
): string {
  if (!value) {
    return "Mathematics";
  }

  const labels: Record<
    string,
    string
  > = {
    algebra: "Algebra",
    geometry: "Geometry",
    number_theory:
      "Number Theory",
    discrete_mathematics:
      "Discrete Mathematics",
    calculus: "Calculus",
    statistics: "Statistics",
  };

  return (
    labels[value] ||
    value
      .replaceAll("_", " ")
      .replace(/\b\w/g, (letter) =>
        letter.toUpperCase()
      )
  );
}

function formatProblemType(
  value: string
): string {
  if (!value) {
    return "Olympiad problem";
  }

  const labels: Record<
    string,
    string
  > = {
    "proof and answer":
      "Proof and answer",
    "proof only":
      "Proof only",
    "final answer only":
      "Final answer only",
    MCQ: "Multiple choice",
  };

  return (
    labels[value] ||
    value
  );
}

function formatScore(
  value: number,
  digits = 0
): string {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    return "—";
  }

  return number.toFixed(
    digits
  );
}

export default function Recommendations({
  recommendations,
}: RecommendationsProps) {
  const visibleRecommendations =
    recommendations.slice(
      0,
      15
    );

  if (
    visibleRecommendations.length === 0
  ) {
    return (
      <section className="section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">
              AI TRAINING PATH
            </p>

            <h2>
              Recommended Problems
            </h2>
          </div>
        </div>

        <div className="empty-state">
          <p>
            No recommendations available
            right now.
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">
            AI TRAINING PATH
          </p>

          <h2>
            Recommended Problems
          </h2>
        </div>

        <span className="section-note">
          Personalized for your profile
        </span>
      </div>

      <div className="recommendation-grid">
        {visibleRecommendations.map(
          (problem) => {
            const title =
              getProblemTitle(
                problem
              );

            const domain =
              formatDomain(
                problem.target_domain
              );

            const type =
              formatProblemType(
                problem.problem_type
              );

            return (
              <article
                className="problem-card"
                key={
                  problem.problem_id
                }
              >
                <div className="problem-top">
                  <span>
                    {domain}
                  </span>

                  <span>
                    {formatScore(
                      problem.difficulty_score
                    )}
                  </span>
                </div>

                <h3 className="problem-title">
                  {title}
                </h3>

                <p className="problem-type">
                  {type}
                </p>

                <div className="problem-meta">
                  <div className="problem-metric">
                    <span className="metric-label">
                      SKILL
                    </span>

                    <strong>
                      {formatScore(
                        problem.student_skill
                      )}
                    </strong>
                  </div>

                  <div className="problem-metric">
                    <span className="metric-label">
                      FIT
                    </span>

                    <strong>
                      {formatScore(
                        problem.difficulty_fit,
                        1
                      )}
                    </strong>
                  </div>
                </div>

                <button
                  type="button"
                  className="problem-button"
                >
                  View Problem
                </button>

                <ReportIssue
                  problemId={
                    problem.problem_id
                  }
                  currentTitle={
                    title
                  }
                />
              </article>
            );
          }
        )}
      </div>
    </section>
  );
}