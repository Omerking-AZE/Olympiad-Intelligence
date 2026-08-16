import { useEffect } from "react";
import { createPortal } from "react-dom";

import ProblemText from "./ProblemText";
import ReportIssue from "./ReportIssue";

import type {
  Recommendation,
} from "./Recommendations";


type ProblemModalProps = {
  problem: Recommendation;
  title: string;
  onClose: () => void;
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


function formatDomain(
  value?: string | null
): string {
  const cleaned =
    cleanText(value);

  if (!cleaned) {
    return "Mathematics";
  }

  return cleaned
    .replaceAll("_", " ")
    .replace(
      /\b\w/g,
      (letter) =>
        letter.toUpperCase()
    );
}


function formatCompetition(
  value?: string | null
): string {
  const cleaned =
    cleanText(value);

  if (!cleaned) {
    return "";
  }

  if (
    cleaned
      .toUpperCase()
      .includes("IMO")
  ) {
    return "IMO";
  }

  return cleaned;
}


function formatProblemType(
  value?: string | null
): string {
  const cleaned =
    cleanText(value);

  if (!cleaned) {
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
    labels[cleaned] ||
    cleaned
  );
}


function formatNumber(
  value?: number | null,
  digits = 1
): string {
  if (
    value === null ||
    value === undefined
  ) {
    return "—";
  }

  const number =
    Number(value);

  if (
    !Number.isFinite(number)
  ) {
    return "—";
  }

  return number.toFixed(
    digits
  );
}


export default function ProblemModal({
  problem,
  title,
  onClose,
}: ProblemModalProps) {
  const statement =
    cleanText(
      problem.problem_text ??
        problem.problem_markdown
    );

  const competition =
    formatCompetition(
      problem.competition
    );

  const domain =
    formatDomain(
      problem.target_domain
    );

  const problemType =
    formatProblemType(
      problem.problem_type
    );

  const identifier =
    [
      competition,
      problem.year,
      problem.problem_number
        ? `P${problem.problem_number}`
        : "",
    ]
      .filter(Boolean)
      .join(" · ");


  /*
   * Lock page scrolling and support Escape.
   */
  useEffect(() => {
    const previousOverflow =
      document.body.style.overflow;

    document.body.style.overflow =
      "hidden";

    const handleKeyDown = (
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
      handleKeyDown
    );

    return () => {
      document.body.style.overflow =
        previousOverflow;

      window.removeEventListener(
        "keydown",
        handleKeyDown
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
        aria-describedby="oi-problem-description"
      >

        {/* =====================================================
            HEADER
            ===================================================== */}

        <header className="oi-problem-header">

          <div className="oi-problem-header-content">

            <span className="oi-eyebrow">
              PROBLEM VIEW
            </span>

            <h2
              id="oi-problem-title"
            >
              {title}
            </h2>

            <p
              id="oi-problem-description"
              className="oi-problem-subtitle"
            >
              {identifier ||
                "Olympiad problem"}
            </p>

          </div>


          <button
            type="button"
            className="oi-problem-close"
            onClick={onClose}
            aria-label="Close problem"
          >
            ×
          </button>

        </header>


        {/* =====================================================
            METADATA
            ===================================================== */}

        <div className="oi-problem-meta-strip">

          <div>
            <span>
              DOMAIN
            </span>

            <strong>
              {domain}
            </strong>
          </div>


          <div>
            <span>
              TYPE
            </span>

            <strong>
              {problemType}
            </strong>
          </div>


          <div>
            <span>
              DIFFICULTY
            </span>

            <strong>
              {formatNumber(
                problem.difficulty_score
              )}
            </strong>
          </div>


          <div>
            <span>
              FIT
            </span>

            <strong>
              {formatNumber(
                problem.difficulty_fit
              )}
            </strong>
          </div>

        </div>


        {/* =====================================================
            PROBLEM STATEMENT
            ===================================================== */}

        <div className="oi-problem-body">

          <div className="oi-problem-kicker">
            PROBLEM STATEMENT
          </div>


          {statement ? (

            <ProblemText
              text={statement}
            />

          ) : (

            <div className="oi-problem-unavailable">

              <strong>
                Problem statement
                unavailable
              </strong>

              <p>
                The problem metadata
                exists, but no statement
                was provided.
              </p>

            </div>

          )}

        </div>


        {/* =====================================================
            FOOTER
            ===================================================== */}

        <footer className="oi-problem-footer">

          <div className="oi-problem-source">

            <span>
              SOURCE
            </span>

            <strong>
              {
                cleanText(
                  problem.source
                ) ||
                "MATHNET"
              }
            </strong>

            <small>
              {
                problem.problem_id
              }
            </small>

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


            {cleanText(
              problem.source_url
            ) && (
              <a
                className="oi-source-link"
                href={
                  problem.source_url ??
                  undefined
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