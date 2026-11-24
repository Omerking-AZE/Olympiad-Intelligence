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
  unknownSkills: string[];
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
  score: number | undefined,
  isUnknown: boolean
): Exclude<
  Filter,
  "All"
> {
  if (isUnknown || !Number.isFinite(score)) {
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
  unknownSkills,
}: SkillsGridProps) {
  const [filter, setFilter] =
    useState<Filter>("All");

  const visible = useMemo(() => {
    return skills.filter(
      (skill) => {
        if (filter === "All") {
          return true;
        }

        const isUnknown = unknownSkills.includes(skill.key);
        return getLevel(ratings[skill.key], isUnknown) === filter;
      }
    );
  }, [
    filter,
    ratings,
    skills,
    unknownSkills,
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
            const isUnknown = unknownSkills.includes(skill.key);
            const rawScore = ratings[skill.key];
            const score = isUnknown || !Number.isFinite(rawScore)
              ? null
              : rawScore;

            const level = getLevel(rawScore, isUnknown);
            const pct = score === null
              ? 0
              : Math.max(0, Math.min(100, score));

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
                    {score === null ? "—" : score}
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
                    {score === null ? "Not measured" : `${pct}% index`}
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