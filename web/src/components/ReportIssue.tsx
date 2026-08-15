import { useEffect, useState } from "react";
import { createPortal } from "react-dom";

type Props = {
  problemId: string;
  currentTitle: string;
};

type IssueType =
  | "competition"
  | "year"
  | "problem_number"
  | "wrong_problem"
  | "other";

type ServerResponse = {
  ok?: boolean;
  error?: string;
};

const ISSUE_OPTIONS: {
  value: IssueType;
  label: string;
}[] = [
  {
    value: "competition",
    label: "Wrong competition",
  },
  {
    value: "year",
    label: "Wrong year",
  },
  {
    value: "problem_number",
    label: "Wrong problem number",
  },
  {
    value: "wrong_problem",
    label: "Wrong problem",
  },
  {
    value: "other",
    label: "Other",
  },
];

export default function ReportIssue({
  problemId,
  currentTitle,
}: Props) {
  const [open, setOpen] =
    useState(false);

  const [issueType, setIssueType] =
    useState<IssueType>(
      "problem_number"
    );

  const [suggestedValue, setSuggestedValue] =
    useState("");

  const [description, setDescription] =
    useState("");

  const [submitted, setSubmitted] =
    useState(false);

  const [submitting, setSubmitting] =
    useState(false);

  const [error, setError] =
    useState("");

  /* ==========================================================
     LOCK PAGE SCROLL WHILE MODAL IS OPEN
     ========================================================== */

  useEffect(() => {
    if (!open) {
      return;
    }

    const previousOverflow =
      document.body.style.overflow;

    document.body.style.overflow =
      "hidden";

    return () => {
      document.body.style.overflow =
        previousOverflow;
    };
  }, [open]);

  /* ==========================================================
     ESCAPE KEY
     ========================================================== */

  useEffect(() => {
    if (!open) {
      return;
    }

    const handleEscape = (
      event: KeyboardEvent
    ) => {
      if (
        event.key !== "Escape" ||
        submitting
      ) {
        return;
      }

      setOpen(false);
      setSubmitted(false);
      setSuggestedValue("");
      setDescription("");
      setIssueType("problem_number");
      setError("");
    };

    window.addEventListener(
      "keydown",
      handleEscape
    );

    return () => {
      window.removeEventListener(
        "keydown",
        handleEscape
      );
    };
  }, [open, submitting]);

  /* ==========================================================
     CLOSE
     ========================================================== */

  function close() {
    if (submitting) {
      return;
    }

    setOpen(false);
    setSubmitted(false);

    setSuggestedValue("");
    setDescription("");

    setIssueType(
      "problem_number"
    );

    setSubmitting(false);
    setError("");
  }

  /* ==========================================================
     SUBMIT REPORT
     ========================================================== */

  async function submit() {
    const suggested =
      suggestedValue.trim();

    if (!suggested) {
      setError(
        "Please enter a suggested correction."
      );

      return;
    }

    setSubmitting(true);
    setError("");

    const requestId =
      typeof crypto !== "undefined" &&
      "randomUUID" in crypto
        ? crypto.randomUUID()
        : `req_${Date.now()}_${Math.random()
            .toString(36)
            .slice(2)}`;

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/reports",
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body: JSON.stringify({
            id: requestId,

            problem_id:
              problemId,

            current_title:
              currentTitle,

            issue_type:
              issueType,

            suggested_value:
              suggested,

            description:
              description.trim(),
          }),
        }
      );

      let data: ServerResponse = {};

      try {
        data =
          await response.json();
      } catch {
        data = {};
      }

      if (
        !response.ok ||
        data.ok !== true
      ) {
        throw new Error(
          data.error ||
            "The report could not be submitted."
        );
      }

      setSubmitted(true);
    } catch (submitError) {
      console.error(
        "Report submission failed:",
        submitError
      );

      setError(
        "Couldn't submit the report. Please make sure the report server is running."
      );
    } finally {
      setSubmitting(false);
    }
  }

  /* ==========================================================
     MODAL
     ========================================================== */

  function renderModal() {
    if (!open) {
      return null;
    }

    return createPortal(
      <div
        className="oi-report-overlay"
        role="presentation"
        onMouseDown={(event) => {
          if (
            event.target ===
            event.currentTarget
          ) {
            close();
          }
        }}
      >
        <section
          className="oi-report-dialog"
          role="dialog"
          aria-modal="true"
          aria-labelledby="report-title"
          aria-describedby="report-description"
        >
          {!submitted ? (
            <>
              {/* ==================================================
                  HEADER
                 ================================================== */}

              <header className="oi-report-header">
                <div className="oi-report-heading">
                  <div className="oi-report-icon">
                    <svg
                      width="18"
                      height="18"
                      viewBox="0 0 24 24"
                      fill="none"
                      aria-hidden="true"
                    >
                      <path
                        d="M12 9V13"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                      />

                      <path
                        d="M12 17.01L12.01 16.998"
                        stroke="currentColor"
                        strokeWidth="2.5"
                        strokeLinecap="round"
                      />

                      <path
                        d="M10.3 3.8L2.7 17C1.93 18.33 2.89 20 4.42 20H19.58C21.11 20 22.07 18.33 21.3 17L13.7 3.8C12.95 2.5 11.05 2.5 10.3 3.8Z"
                        stroke="currentColor"
                        strokeWidth="1.7"
                      />
                    </svg>
                  </div>

                  <div>
                    <div className="oi-report-eyebrow">
                      DATA QUALITY
                    </div>

                    <h2
                      id="report-title"
                      className="oi-report-title"
                    >
                      Report information
                    </h2>

                    <p
                      id="report-description"
                      className="oi-report-subtitle"
                    >
                      Help us keep the problem
                      information accurate.
                    </p>
                  </div>
                </div>

                <button
                  type="button"
                  className="oi-report-close"
                  aria-label="Close report dialog"
                  onClick={close}
                  disabled={submitting}
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
                  BODY
                 ================================================== */}

              <div className="oi-report-body">

                {/* CURRENT INFORMATION */}

                <div>
                  <span className="oi-report-label">
                    CURRENT INFORMATION
                  </span>

                  <div className="oi-current-card">
                    <span className="oi-current-title">
                      {currentTitle}
                    </span>

                    <span className="oi-current-id">
                      Problem ID:{" "}
                      {problemId}
                    </span>
                  </div>
                </div>

                {/* ISSUE TYPE */}

                <div
                  role="group"
                  aria-label="What's wrong?"
                >
                  <span className="oi-report-label">
                    WHAT'S WRONG?
                  </span>

                  <div className="oi-issue-grid">
                    {ISSUE_OPTIONS.map(
                      (option) => {
                        const selected =
                          issueType ===
                          option.value;

                        return (
                          <button
                            key={
                              option.value
                            }
                            type="button"
                            className={`oi-issue-option ${
                              selected
                                ? "is-selected"
                                : ""
                            }`}
                            onClick={() =>
                              setIssueType(
                                option.value
                              )
                            }
                            aria-pressed={
                              selected
                            }
                            disabled={
                              submitting
                            }
                          >
                            <span className="oi-radio">
                              {selected && (
                                <span />
                              )}
                            </span>

                            <span>
                              {
                                option.label
                              }
                            </span>
                          </button>
                        );
                      }
                    )}
                  </div>
                </div>

                {/* SUGGESTED CORRECTION */}

                <div>
                  <label
                    htmlFor={`suggested-${problemId}`}
                    className="oi-report-label"
                  >
                    SUGGESTED CORRECTION
                  </label>

                  <input
                    id={`suggested-${problemId}`}
                    className="oi-report-input"
                    value={
                      suggestedValue
                    }
                    onChange={(event) =>
                      setSuggestedValue(
                        event.target.value
                      )
                    }
                    placeholder="Example: IMO 2023 P2"
                    autoComplete="off"
                    disabled={
                      submitting
                    }
                  />
                </div>

                {/* DETAILS */}

                <div>
                  <div className="oi-label-row">
                    <label
                      htmlFor={`details-${problemId}`}
                      className="oi-report-label"
                    >
                      DETAILS
                    </label>

                    <span className="oi-optional">
                      Optional
                    </span>
                  </div>

                  <textarea
                    id={`details-${problemId}`}
                    className="oi-report-textarea"
                    value={
                      description
                    }
                    onChange={(event) =>
                      setDescription(
                        event.target.value
                      )
                    }
                    placeholder="Tell us what should be changed..."
                    rows={4}
                    disabled={
                      submitting
                    }
                  />
                </div>

                {/* ERROR */}

                {error && (
                  <div
                    className="oi-report-error"
                    role="alert"
                  >
                    {error}
                  </div>
                )}
              </div>

              {/* ==================================================
                  FOOTER
                 ================================================== */}

              <footer className="oi-report-footer">
                <button
                  type="button"
                  className="oi-cancel-button"
                  onClick={close}
                  disabled={submitting}
                >
                  Cancel
                </button>

                <button
                  type="button"
                  className="oi-submit-button"
                  disabled={
                    submitting ||
                    !suggestedValue.trim()
                  }
                  onClick={submit}
                >
                  {submitting
                    ? "Submitting..."
                    : "Submit report"}
                </button>
              </footer>
            </>
          ) : (
            /* ====================================================
               SUCCESS
               ==================================================== */

            <div className="oi-success">
              <div className="oi-success-icon">
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  aria-hidden="true"
                >
                  <path
                    d="M5 12.5L9.2 16.5L19 7"
                    stroke="currentColor"
                    strokeWidth="2.2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>

              <div className="oi-report-eyebrow">
                THANK YOU
              </div>

              <h2 className="oi-success-title">
                Report submitted
              </h2>

              <p className="oi-success-text">
                Your correction has been
                saved and will be reviewed
                for accuracy.
              </p>

              <button
                type="button"
                className="oi-submit-button"
                onClick={close}
              >
                Done
              </button>
            </div>
          )}
        </section>
      </div>,
      document.body
    );
  }

  /* ==========================================================
     TRIGGER
     ========================================================== */

  return (
    <>
      <button
        type="button"
        className="oi-report-button"
        onClick={() => {
          setOpen(true);
          setError("");
        }}
      >
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          aria-hidden="true"
        >
          <path
            d="M12 9V13"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
          />

          <path
            d="M12 17.01L12.01 16.998"
            stroke="currentColor"
            strokeWidth="2.3"
            strokeLinecap="round"
          />
        </svg>

        Report information
      </button>

      {renderModal()}
    </>
  );
}