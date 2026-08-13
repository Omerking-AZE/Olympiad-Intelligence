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

type EditRequest = {
  id: string;
  problem_id: string;
  current_title: string;
  issue_type: IssueType;
  suggested_value: string;
  description: string;
  created_at: string;
  status: "PENDING";
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

  useEffect(() => {
    if (!open) {
      return;
    }

    const handleEscape = (
      event: KeyboardEvent
    ) => {
      if (event.key === "Escape") {
        close();
      }
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
  });

  function close() {
    setOpen(false);
    setSubmitted(false);
    setSuggestedValue("");
    setDescription("");
    setIssueType(
      "problem_number"
    );
  }

  function submit() {
    const request: EditRequest = {
      id: crypto.randomUUID(),

      problem_id:
        problemId,

      current_title:
        currentTitle,

      issue_type:
        issueType,

      suggested_value:
        suggestedValue.trim(),

      description:
        description.trim(),

      created_at:
        new Date().toISOString(),

      status:
        "PENDING",
    };

    const raw =
      localStorage.getItem(
        "oi_edit_requests"
      );

    let existing: EditRequest[] =
      [];

    if (raw) {
      try {
        const parsed =
          JSON.parse(raw);

        if (
          Array.isArray(parsed)
        ) {
          existing = parsed;
        }
      } catch {
        existing = [];
      }
    }

    existing.push(request);

    localStorage.setItem(
      "oi_edit_requests",
      JSON.stringify(existing)
    );

    setSubmitted(true);
  }

  function renderModal() {
    if (!open) {
      return null;
    }

    return createPortal(
      <div
        className="report-overlay"
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
          className="report-modal"
          role="dialog"
          aria-modal="true"
          aria-labelledby="report-title"
          aria-describedby="report-description"
        >
          {!submitted ? (
            <>
              <header className="report-modal-header">
                <div className="report-heading">
                  <div className="report-icon">
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
                    <div className="report-kicker">
                      DATA QUALITY
                    </div>

                    <h2
                      id="report-title"
                      className="report-title"
                    >
                      Report information
                    </h2>

                    <p
                      id="report-description"
                      className="report-description"
                    >
                      Help us keep the problem
                      information accurate.
                    </p>
                  </div>
                </div>

                <button
                  type="button"
                  className="report-close"
                  aria-label="Close report dialog"
                  onClick={close}
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

              <div className="report-divider" />

              <div className="report-body">
                <div className="report-current">
                  <span className="report-label">
                    CURRENT INFORMATION
                  </span>

                  <div className="report-current-card">
                    <span className="report-current-title">
                      {currentTitle}
                    </span>

                    <span className="report-current-id">
                      Problem ID: {problemId}
                    </span>
                  </div>
                </div>

                <fieldset className="report-fieldset">
                  <legend className="report-label">
                    WHAT'S WRONG?
                  </legend>

                  <div className="issue-grid">
                    {ISSUE_OPTIONS.map(
                      (option) => {
                        const selected =
                          issueType ===
                          option.value;

                        return (
                          <button
                            key={option.value}
                            type="button"
                            className={`issue-option ${
                              selected
                                ? "selected"
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
                          >
                            <span
                              className="issue-radio"
                            >
                              {selected && (
                                <span />
                              )}
                            </span>

                            <span>
                              {option.label}
                            </span>
                          </button>
                        );
                      }
                    )}
                  </div>
                </fieldset>

                <div className="report-field">
                  <label
                    htmlFor={`suggested-${problemId}`}
                    className="report-label"
                  >
                    SUGGESTED CORRECTION
                  </label>

                  <input
                    id={`suggested-${problemId}`}
                    className="report-input"
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
                  />
                </div>

                <div className="report-field">
                  <label
                    htmlFor={`details-${problemId}`}
                    className="report-label"
                  >
                    DETAILS
                    <span className="optional">
                      Optional
                    </span>
                  </label>

                  <textarea
                    id={`details-${problemId}`}
                    className="report-textarea"
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
                  />
                </div>
              </div>

              <footer className="report-footer">
                <button
                  type="button"
                  className="report-cancel"
                  onClick={close}
                >
                  Cancel
                </button>

                <button
                  type="button"
                  className="report-submit"
                  disabled={
                    !suggestedValue.trim()
                  }
                  onClick={submit}
                >
                  Submit report
                </button>
              </footer>
            </>
          ) : (
            <div className="report-success">
              <div className="success-icon">
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

              <div className="report-kicker">
                THANK YOU
              </div>

              <h2 className="report-success-title">
                Report submitted
              </h2>

              <p className="report-success-text">
                Your correction has been
                saved and will be reviewed
                for accuracy.
              </p>

              <button
                type="button"
                className="report-submit success-button"
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

  return (
    <>
      <button
        type="button"
        className="report-button"
        onClick={() => setOpen(true)}
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