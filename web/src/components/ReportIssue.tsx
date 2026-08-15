import {
  useEffect,
  useState,
} from "react";

import {
  createPortal,
} from "react-dom";

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
    value:
      "competition",
    label:
      "Wrong competition",
  },
  {
    value: "year",
    label:
      "Wrong year",
  },
  {
    value:
      "problem_number",
    label:
      "Wrong problem number",
  },
  {
    value:
      "wrong_problem",
    label:
      "Wrong problem",
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

  useEffect(() => {
    if (!open) {
      return;
    }

    const previous =
      document.body.style
        .overflow;

    document.body.style.overflow =
      "hidden";

    return () => {
      document.body.style.overflow =
        previous;
    };
  }, [open]);

  useEffect(() => {
    if (!open) {
      return;
    }

    const handleEscape = (
      event: KeyboardEvent
    ) => {
      if (
        event.key !==
          "Escape" ||
        submitting
      ) {
        return;
      }

      setOpen(false);
      setSubmitted(false);
      setSuggestedValue("");
      setDescription("");
      setIssueType(
        "problem_number"
      );
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
    setError("");
  }

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
      typeof crypto !==
        "undefined" &&
      "randomUUID" in crypto
        ? crypto.randomUUID()
        : `req_${Date.now()}_${Math.random()
            .toString(36)
            .slice(2)}`;

    try {
      const response =
        await fetch(
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

      let data: ServerResponse =
        {};

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

      setSubmitted(
        true
      );
    } catch (
      submitError
    ) {
      console.error(
        "Report submission failed:",
        submitError
      );

      setError(
        "Couldn't submit the report. Please make sure the report server is running."
      );
    } finally {
      setSubmitting(
        false
      );
    }
  }

  const modal = open
    ? createPortal(
        <div
          className="oi-report-overlay"
          role="presentation"
          onMouseDown={(
            event
          ) => {
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
            aria-labelledby="oi-report-title"
          >
            {!submitted ? (
              <>
                <header className="oi-report-header">
                  <div className="oi-report-heading">
                    <div
                      className="oi-report-icon"
                      aria-hidden="true"
                    >
                      !
                    </div>

                    <div>
                      <div className="oi-report-eyebrow">
                        DATA QUALITY
                      </div>

                      <h2
                        id="oi-report-title"
                        className="oi-report-title"
                      >
                        Report information
                      </h2>

                      <p className="oi-report-subtitle">
                        Help us keep problem
                        information accurate.
                      </p>
                    </div>
                  </div>

                  <button
                    type="button"
                    className="oi-report-close"
                    onClick={close}
                    disabled={
                      submitting
                    }
                    aria-label="Close report dialog"
                  >
                    ×
                  </button>
                </header>

                <div className="oi-report-body">
                  <div>
                    <span className="oi-report-label">
                      CURRENT INFORMATION
                    </span>

                    <div className="oi-current-card">
                      <span className="oi-current-title">
                        {
                          currentTitle
                        }
                      </span>

                      <span className="oi-current-id">
                        Problem ID ·{" "}
                        {problemId}
                      </span>
                    </div>
                  </div>

                  <div>
                    <span className="oi-report-label">
                      WHAT'S WRONG?
                    </span>

                    <div className="oi-issue-grid">
                      {ISSUE_OPTIONS.map(
                        (
                          option
                        ) => {
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
                              disabled={
                                submitting
                              }
                              aria-pressed={
                                selected
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

                  <div>
                    <label
                      className="oi-report-label"
                      htmlFor={`suggested-${problemId}`}
                    >
                      SUGGESTED CORRECTION
                    </label>

                    <input
                      id={`suggested-${problemId}`}
                      className="oi-report-input"
                      value={
                        suggestedValue
                      }
                      onChange={(
                        event
                      ) =>
                        setSuggestedValue(
                          event
                            .target
                            .value
                        )
                      }
                      placeholder="Example: IMO 2023 P2"
                      autoComplete="off"
                      disabled={
                        submitting
                      }
                    />
                  </div>

                  <div>
                    <div className="oi-label-row">
                      <label
                        className="oi-report-label"
                        htmlFor={`details-${problemId}`}
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
                      onChange={(
                        event
                      ) =>
                        setDescription(
                          event
                            .target
                            .value
                        )
                      }
                      placeholder="Tell us what should be changed..."
                      rows={5}
                      disabled={
                        submitting
                      }
                    />
                  </div>

                  {error && (
                    <div
                      className="oi-report-error"
                      role="alert"
                    >
                      {error}
                    </div>
                  )}
                </div>

                <footer className="oi-report-footer">
                  <button
                    type="button"
                    className="oi-cancel-button"
                    onClick={close}
                    disabled={
                      submitting
                    }
                  >
                    Cancel
                  </button>

                  <button
                    type="button"
                    className="oi-submit-button"
                    onClick={
                      submit
                    }
                    disabled={
                      submitting ||
                      !suggestedValue.trim()
                    }
                  >
                    {submitting
                      ? "Submitting..."
                      : "Submit report"}
                  </button>
                </footer>
              </>
            ) : (
              <div className="oi-success">
                <div className="oi-success-icon">
                  ✓
                </div>

                <div className="oi-report-eyebrow">
                  THANK YOU
                </div>

                <h2 className="oi-success-title">
                  Report submitted
                </h2>

                <p className="oi-success-text">
                  Your correction has
                  been saved and will be
                  reviewed for accuracy.
                </p>

                <button
                  type="button"
                  className="oi-submit-button"
                  onClick={
                    close
                  }
                >
                  Done
                </button>
              </div>
            )}
          </section>
        </div>,
        document.body
      )
    : null;

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
        <span className="oi-report-button-icon">
          !
        </span>

        Report information
      </button>

      {modal}
    </>
  );
}