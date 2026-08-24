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


/* ============================================================
   HELPERS
   ============================================================ */

function clean(
  value?: string | null
): string {
  return value
    ? String(value).trim()
    : "";
}


function titleFor(
  problem: Recommendation
): string {
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
): string {
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
): string {
  const number =
    Number(value);

  return Number.isFinite(
    number
  )
    ? number.toFixed(digits)
    : "—";
}


/* ============================================================
   WHY THIS PROBLEM?
   Uses only real recommendation data.
   ============================================================ */

function getRecommendationReason(
  problem: Recommendation
): string {
  if (problem.skill_unknown) {
    return (
      "A useful problem for measuring a skill we have not assessed yet."
    );
  }

  const weakness =
    clean(
      problem.weakness_classification
    );

  const weaknessName =
    weakness
      ? prettyDomain(weakness)
      : "this area";

  if (
    problem.weakness_priority >=
      0.8 &&
    problem.weakness_confidence >=
      0.6
  ) {
    return (
      `A strong choice for improving ${weaknessName}, one of your current focus areas.`
    );
  }

  if (
    problem.weakness_priority >=
      0.8
  ) {
    return (
      `Targets ${weaknessName}, which is an important area to improve.`
    );
  }

  if (
    problem.training_zone &&
    problem.difficulty_fit >= 45
  ) {
    return (
      "An excellent match for your current level and training zone."
    );
  }

  if (
    problem.training_zone
  ) {
    return (
      "Fits your current training zone and gives you a useful next challenge."
    );
  }

  if (
    problem.difficulty_fit >=
    45
  ) {
    return (
      "A strong difficulty match for your current level."
    );
  }

  if (
    problem.difficulty_fit >=
    35
  ) {
    return (
      "A little more challenging than usual, making it useful for progression."
    );
  }

  if (
    problem.weakness_confidence >=
    0.7
  ) {
    return (
      "Recommended with high confidence based on your current profile."
    );
  }

  return (
    "Selected as part of your personalized training path."
  );
}


/* ============================================================
   COMPONENT
   ============================================================ */

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


  /* ==========================================================
     FILTER
     ========================================================== */

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


  /* ==========================================================
     RENDER
     ========================================================== */

  return (
    <section
      className="oi-section"
      id="recommendations-section"
    >

      {/* ======================================================
          SECTION HEADER
          ====================================================== */}

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


      {/* ======================================================
          EMPTY STATE
          ====================================================== */}

      {visible.length === 0 ? (

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

              const reason =
                getRecommendationReason(
                  problem
                );

              return (
                <article
                  className="oi-problem-card"
                  key={
                    problem.problem_id
                  }
                >

                  {/* ==================================================
                      TOP META
                      ================================================== */}

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


                  {/* ==================================================
                      TITLE
                      ================================================== */}

                  <h3>
                    {title}
                  </h3>


                  {/* ==================================================
                      TYPE
                      ================================================== */}

                  <p className="oi-problem-type">
                    {
                      problem.problem_type ||
                      "Olympiad problem"
                    }
                  </p>


                  {/* ==================================================
                      WHY THIS PROBLEM
                      ================================================== */}

                  <p className="problem-reason">
                    {reason}
                  </p>


                  {/* ==================================================
                      METRICS
                      ================================================== */}

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


                  {/* ==================================================
                      ACTIONS
                      ================================================== */}

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


      {/* ========================================================
          PROBLEM MODAL
          ======================================================== */}

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