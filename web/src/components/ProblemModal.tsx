import { useEffect } from "react";

import {
  createPortal,
} from "react-dom";

import type {
  Recommendation,
} from "./Recommendations";

import ReportIssue from "./ReportIssue";

type Props = {
  problem: Recommendation;
  title: string;
  onClose: () => void;
};

function clean(
  value?: string | null
) {
  return value
    ? String(value).trim()
    : "";
}

export default function ProblemModal({
  problem,
  title,
  onClose,
}: Props) {
  useEffect(() => {
    const previous =
      document.body.style
        .overflow;

    document.body.style.overflow =
      "hidden";

    const onKeyDown = (
      event: KeyboardEvent
    ) => {
      if (
        event.key ===
        "Escape"
      ) {
        onClose();
      }
    };

    window.addEventListener(
      "keydown",
      onKeyDown
    );

    return () => {
      document.body.style.overflow =
        previous;

      window.removeEventListener(
        "keydown",
        onKeyDown
      );
    };
  }, [onClose]);

  const statement =
    clean(
      problem.problem_text ||
        problem.problem_markdown
    );

  const competition =
    clean(
      problem.competition
    );

  const subtitle = [
    competition,
    problem.year,
    problem.problem_number
      ? `P${problem.problem_number}`
      : "",
  ]
    .filter(Boolean)
    .join(" · ");

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
        aria-labelledby="problem-modal-title"
      >
        <header className="oi-problem-header">
          <div>
            <span className="oi-eyebrow">
              PROBLEM VIEW
            </span>

            <h2 id="problem-modal-title">
              {title}
            </h2>

            <div className="oi-problem-subtitle">
              {subtitle ||
                "Olympiad problem"}
            </div>
          </div>

          <button
            type="button"
            className="oi-problem-close"
            onClick={onClose}
            aria-label="Close"
          >
            ×
          </button>
        </header>

        <div className="oi-problem-meta-strip">
          <div>
            <span>
              DOMAIN
            </span>

            <strong>
              {
                problem.target_domain
              }
            </strong>
          </div>

          <div>
            <span>
              TYPE
            </span>

            <strong>
              {
                problem.problem_type ||
                "Olympiad problem"
              }
            </strong>
          </div>

          <div>
            <span>
              DIFFICULTY
            </span>

            <strong>
              {Number(
                problem.difficulty_score
              ).toFixed(1)}
            </strong>
          </div>

          <div>
            <span>
              FIT
            </span>

            <strong>
              {Number(
                problem.difficulty_fit
              ).toFixed(1)}
            </strong>
          </div>
        </div>

        <div className="oi-problem-body">
          <div className="oi-problem-kicker">
            PROBLEM STATEMENT
          </div>

          {statement ? (
            <div className="oi-problem-text">
              {statement}
            </div>
          ) : (
            <div className="oi-problem-unavailable">
              <strong>
                Problem statement is
                not attached yet.
              </strong>

              <p>
                The recommendation
                metadata is ready,
                but the full MathNet
                statement has not been
                exported into the
                recommendation JSON.
              </p>
            </div>
          )}
        </div>

        <footer className="oi-problem-footer">
          <div className="oi-problem-source">
            <span>
              {problem.source ||
                "MATHNET"}
            </span>

            <strong>
              {problem.problem_id}
            </strong>
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

            {problem.source_url && (
              <a
                className="oi-source-link"
                href={
                  problem.source_url
                }
                target="_blank"
                rel="noreferrer"
              >
                Source ↗
              </a>
            )}

            <button
              type="button"
              className="oi-problem-done"
              onClick={
                onClose
              }
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