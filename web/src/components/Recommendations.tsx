import {
  useEffect,
  useState,
} from "react";

import { createPortal } from "react-dom";

import ReportIssue from "./ReportIssue";


/* ============================================================
   TYPES
   ============================================================ */

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

  /*
   * These fields are optional because the current
   * recommendation JSON may not contain them yet.
   */
  problem_text?: string | null;

  problem_markdown?: string | null;

  final_answer?: string | null;
};


type RecommendationsProps = {
  recommendations: Recommendation[];
};


/* ============================================================
   HELPERS
   ============================================================ */

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

    statistics:
      "Statistics",
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

    MCQ:
      "Multiple choice",
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


function getProblemText(
  problem: Recommendation
): string {
  const markdown =
    cleanText(
      problem.problem_markdown
    );

  if (markdown) {
    return markdown;
  }

  const text =
    cleanText(
      problem.problem_text
    );

  if (text) {
    return text;
  }

  return "";
}


/* ============================================================
   PROBLEM MODAL
   ============================================================ */

type ProblemModalProps = {
  problem: Recommendation;
  title: string;
  onClose: () => void;
};


function ProblemModal({
  problem,
  title,
  onClose,
}: ProblemModalProps) {
  const problemText =
    getProblemText(problem);

  const domain =
    formatDomain(
      problem.target_domain
    );

  const type =
    formatProblemType(
      problem.problem_type
    );

  useEffect(() => {
    const previousOverflow =
      document.body.style.overflow;

    document.body.style.overflow =
      "hidden";

    const handleEscape = (
      event: KeyboardEvent
    ) => {
      if (
        event.key === "Escape"
      ) {
        onClose();
      }
    };

    window.addEventListener(
      "keydown",
      handleEscape
    );

    return () => {
      document.body.style.overflow =
        previousOverflow;

      window.removeEventListener(
        "keydown",
        handleEscape
      );
    };
  }, [onClose]);

  return createPortal(
    <div
      className="oi-problem-overlay"
      role="presentation"
      onMouseDown={(event) => {
        if (
          event.target ===
          event.currentTarget
        ) {
          onClose();
        }
      }}
    >
      <section
        className="oi-problem-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="oi-problem-title"
      >

        {/* ==================================================
            HEADER
            ================================================== */}

        <header className="oi-problem-header">

          <div className="oi-problem-header-left">

            <div className="oi-problem-badge">
              PROBLEM
            </div>

            <div>

              <div className="oi-problem-eyebrow">
                AI TRAINING PATH
              </div>

              <h2
                id="oi-problem-title"
                className="oi-problem-title-large"
              >
                {title}
              </h2>

            </div>

          </div>


          <button
            type="button"
            className="oi-problem-close"
            onClick={onClose}
            aria-label="Close problem"
          >
            <svg
              width="17"
              height="17"
              viewBox="0 0 24 24"
              fill="none"
              aria-hidden="true"
            >
              <path
                d="M6 6L18 18"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
              />

              <path
                d="M18 6L6 18"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
              />
            </svg>
          </button>

        </header>


        {/* ==================================================
            METADATA
            ================================================== */}

        <div className="oi-problem-meta-grid">

          <div className="oi-problem-meta-card">

            <span>
              DOMAIN
            </span>

            <strong>
              {domain}
            </strong>

          </div>


          <div className="oi-problem-meta-card">

            <span>
              TYPE
            </span>

            <strong>
              {type}
            </strong>

          </div>


          <div className="oi-problem-meta-card">

            <span>
              DIFFICULTY
            </span>

            <strong>
              {formatScore(
                problem.difficulty_score,
                1
              )}
            </strong>

          </div>


          <div className="oi-problem-meta-card">

            <span>
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


        {/* ==================================================
            PROBLEM
            ================================================== */}

        <div className="oi-problem-body">

          <div className="oi-problem-section-label">
            PROBLEM STATEMENT
          </div>


          {problemText ? (

            <div className="oi-problem-text">
              {problemText}
            </div>

          ) : (

            <div className="oi-problem-unavailable">

              <div className="oi-problem-unavailable-icon">
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  aria-hidden="true"
                >
                  <path
                    d="M12 8V13"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                  />

                  <circle
                    cx="12"
                    cy="17"
                    r="1"
                    fill="currentColor"
                  />
                </svg>
              </div>

              <div>

                <strong>
                  Problem text unavailable
                </strong>

                <p>
                  The recommendation metadata
                  does not currently contain
                  the full problem statement.
                </p>

              </div>

            </div>

          )}

        </div>


        {/* ==================================================
            FOOTER
            ================================================== */}

        <footer className="oi-problem-footer">

          <div className="oi-problem-source">

            {problem.source ? (
              <>
                <span>
                  SOURCE
                </span>

                <strong>
                  {problem.source}
                </strong>
              </>
            ) : (
              <>
                <span>
                  PROBLEM ID
                </span>

                <strong>
                  {problem.problem_id}
                </strong>
              </>
            )}

          </div>


          <div className="oi-problem-actions">

            <ReportIssue
              problemId={
                problem.problem_id
              }
              currentTitle={
                title
              }
            />


            <button
              type="button"
              className="oi-problem-done"
              onClick={onClose}
            >
              Close
            </button>

          </div>

        </footer>

      </section>
    </div>,
    document.body
  );
}


/* ============================================================
   RECOMMENDATIONS
   ============================================================ */

export default function Recommendations({
  recommendations,
}: RecommendationsProps) {

  const visibleRecommendations =
    recommendations.slice(
      0,
      15
    );

  const [
    selectedProblem,
    setSelectedProblem,
  ] =
    useState<Recommendation | null>(
      null
    );


  /* ==========================================================
     EMPTY STATE
     ========================================================== */

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


  /* ==========================================================
     UI
     ========================================================== */

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


                {/* =================================================
                    ACTIONS
                    ================================================= */}

                <div className="problem-actions">

                  <button
                    type="button"
                    className="problem-button"
                    onClick={() =>
                      setSelectedProblem(
                        problem
                      )
                    }
                  >

                    <span>
                      View Problem
                    </span>

                    <svg
                      width="15"
                      height="15"
                      viewBox="0 0 24 24"
                      fill="none"
                      aria-hidden="true"
                    >
                      <path
                        d="M5 12H19"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                      />

                      <path
                        d="M13 6L19 12L13 18"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>

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


      {/* ========================================================
          PROBLEM MODAL
          ======================================================== */}

      {selectedProblem && (
        <ProblemModal
          problem={
            selectedProblem
          }
          title={
            getProblemTitle(
              selectedProblem
            )
          }
          onClose={() =>
            setSelectedProblem(null)
          }
        />
      )}

    </section>
  );
}