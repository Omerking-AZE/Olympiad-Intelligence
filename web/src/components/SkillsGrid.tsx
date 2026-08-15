import {
  useMemo,
  useState,
} from "react";

import type {
  Skill,
  SkillKey,
} from "../types/student";

type SkillsGridProps = {
  skills: Skill[];
  ratings: Record<
    SkillKey,
    number
  >;
};

const levels = [
  "All",
  "Strong",
  "Developing",
  "Unknown",
] as const;

type Filter =
  (typeof levels)[number];

function getLevel(
  score: number | undefined
): Exclude<
  Filter,
  "All"
> {
  if (!Number.isFinite(score)) {
    return "Unknown";
  }

  if ((score ?? 0) >= 80) {
    return "Strong";
  }

  return "Developing";
}

export default function SkillsGrid({
  skills,
  ratings,
}: SkillsGridProps) {
  const [filter, setFilter] =
    useState<Filter>("All");

  const visible = useMemo(() => {
    return skills.filter(
      (skill) => {
        if (filter === "All") {
          return true;
        }

        return (
          getLevel(
            ratings[skill.key]
          ) === filter
        );
      }
    );
  }, [
    filter,
    ratings,
    skills,
  ]);

  return (
    <section
      className="oi-section"
      id="skills-section"
    >
      <div className="oi-section-heading">
        <div>
          <span className="oi-eyebrow">
            DIAGNOSTIC MATRIX
          </span>

          <h2>
            Domain Mastery &amp;
            Sub-Scores
          </h2>
        </div>

        <div className="oi-filter-pills">
          {levels.map(
            (item) => (
              <button
                key={item}
                type="button"
                className={`oi-filter-pill ${
                  filter === item
                    ? "is-active"
                    : ""
                }`}
                onClick={() =>
                  setFilter(item)
                }
              >
                {item}
              </button>
            )
          )}
        </div>
      </div>

      <div className="oi-skills-grid">
        {visible.map(
          (skill) => {
            const score = Number(
              ratings[skill.key] ?? 0
            );

            const level =
              getLevel(score);

            const pct =
              Math.max(
                0,
                Math.min(
                  100,
                  score
                )
              );

            return (
              <article
                key={skill.code}
                className="oi-skill-card"
              >
                <div className="oi-skill-head">
                  <span className="oi-skill-code">
                    {skill.code}
                  </span>

                  <strong>
                    {Number.isFinite(
                      score
                    )
                      ? score
                      : "—"}
                  </strong>
                </div>

                <div className="oi-skill-name">
                  {skill.name}
                </div>

                <div className="oi-skill-meta">
                  <span>
                    {level}
                  </span>

                  <span>
                    {pct}% index
                  </span>
                </div>

                <div className="oi-progress-track">
                  <div
                    className="oi-progress-fill"
                    style={{
                      width: `${pct}%`,
                    }}
                  />
                </div>
              </article>
            );
          }
        )}
      </div>
    </section>
  );
}