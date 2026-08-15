import {
  useMemo,
  useState,
} from "react";

type TopbarProps = {
  darkMode: boolean;
  onToggleTheme: () => void;
  searchQuery: string;
  onSearchChange: (
    value: string
  ) => void;
  candidateRating: number;
};

function SearchIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <circle
        cx="11"
        cy="11"
        r="6.5"
        stroke="currentColor"
        strokeWidth="1.7"
      />

      <path
        d="m16 16 4.2 4.2"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
      />
    </svg>
  );
}

export default function Topbar({
  darkMode,
  onToggleTheme,
  searchQuery,
  onSearchChange,
  candidateRating,
}: TopbarProps) {
  const [focused, setFocused] =
    useState(false);

  const ratingLabel = useMemo(() => {
    const value =
      Number(candidateRating);

    return Number.isFinite(value)
      ? Math.round(value)
      : 0;
  }, [candidateRating]);

  return (
    <header className="oi-topbar">
      <div className="oi-topbar-brand">
        <div
          className="oi-brand-mark"
          aria-hidden="true"
        >
          <svg
            viewBox="0 0 24 24"
            fill="none"
          >
            <path
              d="M12 3.5 14 8l4.7.45-3.55 3.05 1.05 4.65L12 13.7l-4.2 2.45 1.05-4.65L5.3 8.45 10 8l2-4.5Z"
              fill="currentColor"
            />
          </svg>
        </div>

        <div>
          <div className="oi-brand-title">
            OLYMPIAD INTELLIGENCE
          </div>

          <div className="oi-brand-subtitle">
            SYSTEM CORE · CANDIDATE #
            {ratingLabel} ELO
          </div>
        </div>

        <span className="oi-brand-pill">
          PRO
        </span>
      </div>

      <div
        className={`oi-topbar-search ${
          focused
            ? "is-focused"
            : ""
        }`}
      >
        <SearchIcon />

        <input
          value={searchQuery}
          onChange={(event) =>
            onSearchChange(
              event.target.value
            )
          }
          onFocus={() =>
            setFocused(true)
          }
          onBlur={() =>
            setFocused(false)
          }
          placeholder="Search problems, topics, theorems..."
          aria-label="Search recommendations"
        />

        {searchQuery && (
          <button
            type="button"
            className="oi-clear-search"
            onClick={() =>
              onSearchChange("")
            }
            aria-label="Clear search"
          >
            ×
          </button>
        )}
      </div>

      <div className="oi-topbar-actions">
        <div className="oi-status-pill">
          <span className="oi-status-dot" />
          SEASON 2026 LIVE
        </div>

        <button
          type="button"
          className="oi-theme-toggle"
          onClick={
            onToggleTheme
          }
          aria-label="Toggle theme"
        >
          <span aria-hidden="true">
            {darkMode ? "☀" : "☾"}
          </span>

          <span>
            {darkMode
              ? "LIGHT"
              : "DARK"}
          </span>
        </button>
      </div>
    </header>
  );
}