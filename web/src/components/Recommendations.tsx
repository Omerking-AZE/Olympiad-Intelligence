export type Recommendation = {
  problem_id: string;

  // Human-readable olympiad metadata
  contest_name?: string;
  contest_year?: number;
  problem_number?: number;

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
};

type Props = {
  recommendations: Recommendation[];
};

function getProblemTitle(
  problem: Recommendation
) {
  if (
    problem.contest_name &&
    problem.contest_year &&
    problem.problem_number
  ) {
    return `${problem.contest_name} ${problem.contest_year} P${problem.problem_number}`;
  }

  // Fallback until metadata is available.
  return problem.problem_id;
}

export default function Recommendations({
  recommendations,
}: Props) {
  const visible = recommendations.slice(
    0,
    6
  );

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
          Personalized
        </span>
      </div>

      <div className="recommendation-grid">
        {visible.map((problem) => (
          <article
            className="problem-card"
            key={problem.problem_id}
          >
            <div className="problem-top">
              <span>
                {problem.target_domain}
              </span>

              <span>
                {Math.round(
                  problem.difficulty_score
                )}
              </span>
            </div>

            <h3 className="problem-title">
              {getProblemTitle(problem)}
            </h3>

            <p className="problem-type">
              {problem.problem_type}
            </p>

            <div className="problem-meta">
              <div className="problem-metric">
                <span className="metric-label">
                  SKILL
                </span>

                <strong>
                  {problem.student_skill}
                </strong>
              </div>

              <div className="problem-metric">
                <span className="metric-label">
                  FIT
                </span>

                <strong>
                  {problem.difficulty_fit.toFixed(
                    1
                  )}
                </strong>
              </div>
            </div>

            <button className="problem-button">
              View Problem
            </button>
          </article>
        ))}
      </div>
    </section>
  );
}