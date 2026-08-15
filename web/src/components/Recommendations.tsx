import {
  useMemo,
  useState,
} from "react";

import ReportIssue from "./ReportIssue";
import ProblemModal from "./ProblemModal";

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

  problem_text?: string | null;

  problem_markdown?: string | null;

  final_answer?: string | null;
};

type RecommendationsProps = {
  recommendations: Recommendation[];

  searchQuery?: string;
};

function clean(
  value?: string | null
) {
  return value
    ? String(value).trim()
    : "";
}

function titleFor(
  problem: Recommendation
) {
  const title =
    clean(problem.title);

  if (title) {
    return title;
  }

  const competition =
    clean(
      problem.competition
    );

  if (
    competition &&
    problem.year &&
    problem.problem_number
  ) {
    return `${
      competition
        .toUpperCase()
        .includes("IMO")
        ? "IMO"
        : competition
    } ${problem.year} P${problem.problem_number}`;
  }

  if (
    competition &&
    problem.year
  ) {
    return `${competition} ${problem.year}`;
  }

  return (
    competition ||
    "Olympiad Problem"
  );
}

function prettyDomain(
  value: string
) {
  return value
    ? value
        .replaceAll(
          "_",
          " "
        )
        .replace(
          /\b\w/g,
          (letter) =>
            letter.toUpperCase()
        )
    : "Mathematics";
}

function metric(
  value: number,
  digits = 0
) {
  const number =
    Number(value);

  return Number.isFinite(
    number
  )
    ? number.toFixed(digits)
    : "—";
}

export default function Recommendations({
  recommendations,
  searchQuery = "",
}: RecommendationsProps) {
  const [
    selected,
    setSelected,
  ] =
    useState<Recommendation | null>(
      null
    );

  const visible =
    useMemo(() => {
      const query =
        searchQuery
          .trim()
          .toLowerCase();

      const source =
        recommendations.slice(
          0,
          15
        );

      if (!query) {
        return source;
      }

      return source.filter(
        (item) => {
          const haystack = [
            titleFor(item),
            item.target_domain,
            item.problem_type,
            item.competition ??
              "",
            item.source ??
              "",
            item.problem_id,
          ]
            .join(" ")
            .toLowerCase();

          return haystack.includes(
            query
          );
        }
      );
    }, [
      recommendations,
      searchQuery,
    ]);

  return (
    <section
      className="oi-section"
      id="recommendations-section"
    >
      <div className="oi-section-heading">
        <div>
          <span className="oi-eyebrow">
            AI TRAINING PATH
          </span>

          <h2>
            Recommended Problems
          </h2>
        </div>

        <span className="oi-section-note">
          Personalized for your profile
        </span>
      </div>

      {visible.length ===
      0 ? (
        <div className="oi-empty-state">
          No recommendations match
          the current filter.
        </div>
      ) : (
        <div className="oi-recommendation-grid">
          {visible.map(
            (problem) => {
              const title =
                titleFor(
                  problem
                );

              return (
                <article
                  className="oi-problem-card"
                  key={
                    problem.problem_id
                  }
                >
                  <div className="oi-problem-card-top">
                    <span>
                      {prettyDomain(
                        problem.target_domain
                      )}
                    </span>

                    <span className="oi-difficulty-badge">
                      {metric(
                        problem.difficulty_score
                      )}
                    </span>
                  </div>

                  <h3>
                    {title}
                  </h3>

                  <p className="oi-problem-type">
                    {
                      problem.problem_type ||
                      "Olympiad problem"
                    }
                  </p>

                  <div className="oi-problem-card-metrics">
                    <div>
                      <span>
                        SKILL
                      </span>

                      <strong>
                        {metric(
                          problem.student_skill
                        )}
                      </strong>
                    </div>

                    <div>
                      <span>
                        FIT
                      </span>

                      <strong>
                        {metric(
                          problem.difficulty_fit,
                          1
                        )}
                      </strong>
                    </div>

                    <div>
                      <span>
                        ADAPTIVE
                      </span>

                      <strong>
                        {metric(
                          problem.adaptive_score,
                          2
                        )}
                      </strong>
                    </div>
                  </div>

                  <div className="oi-problem-card-actions">
                    <button
                      type="button"
                      className="oi-primary-button"
                      onClick={() =>
                        setSelected(
                          problem
                        )
                      }
                    >
                      View problem
                      <span>
                        →
                      </span>
                    </button>

                    <ReportIssue
                      problemId={
                        problem.problem_id
                      }
                      currentTitle={
                        title
                      }
                    />
                  </div>
                </article>
              );
            }
          )}
        </div>
      )}

      {selected && (
        <ProblemModal
          problem={
            selected
          }
          title={titleFor(
            selected
          )}
          onClose={() =>
            setSelected(
              null
            )
          }
        />
      )}
    </section>
  );
}