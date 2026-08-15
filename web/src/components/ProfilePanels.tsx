import type {
  StudentIntelligence,
} from "../types/student";

type ProfilePanelsProps = {
  student: StudentIntelligence;
};

function formatSkillName(
  value: string
) {
  return value
    .replaceAll("_", " ")
    .replace(
      /\b\w/g,
      (char) =>
        char.toUpperCase()
    );
}

export default function ProfilePanels({
  student,
}: ProfilePanelsProps) {
  const strengths =
    student.strongest_skills.slice(
      0,
      3
    );

  const weaknesses = [
    ...student.high_priority_weaknesses,
    ...student.medium_priority_weaknesses,
  ].slice(0, 4);

  const unknown =
    student.unknown_skills.slice(
      0,
      4
    );

  return (
    <section className="oi-panel-grid">
      <article className="oi-panel-card">
        <div className="oi-panel-eyebrow">
          STRENGTHS
        </div>

        <h2>
          Strongest Areas
        </h2>

        <div className="oi-rank-list">
          {strengths.length
            ? strengths.map(
                (
                  skill,
                  index
                ) => (
                  <div
                    key={skill}
                    className="oi-rank-row"
                  >
                    <span>
                      {String(
                        index + 1
                      ).padStart(
                        2,
                        "0"
                      )}
                    </span>

                    <strong>
                      {formatSkillName(
                        skill
                      )}
                    </strong>

                    <b>
                      {
                        student.skill_ratings[
                          skill as keyof typeof student.skill_ratings
                        ]
                      }
                    </b>
                  </div>
                )
              )
            : (
              <div className="oi-empty-row">
                Not enough data
              </div>
            )}
        </div>
      </article>

      <article className="oi-panel-card oi-panel-accent">
        <div className="oi-panel-eyebrow">
          TRAINING FOCUS
        </div>

        <h2>
          Areas to Improve
        </h2>

        <div className="oi-rank-list">
          {weaknesses.length
            ? weaknesses.map(
                (
                  skill,
                  index
                ) => (
                  <div
                    key={skill}
                    className="oi-rank-row"
                  >
                    <span>
                      {String(
                        index + 1
                      ).padStart(
                        2,
                        "0"
                      )}
                    </span>

                    <strong>
                      {formatSkillName(
                        skill
                      )}
                    </strong>

                    <b>
                      {
                        student.skill_ratings[
                          skill as keyof typeof student.skill_ratings
                        ]
                      }
                    </b>
                  </div>
                )
              )
            : (
              <div className="oi-empty-row">
                No major weaknesses
                detected
              </div>
            )}
        </div>
      </article>

      {unknown.length > 0 && (
        <article className="oi-panel-card oi-panel-wide">
          <div className="oi-panel-eyebrow">
            DATA COVERAGE
          </div>

          <h2>
            Areas Not Yet Measured
          </h2>

          <div className="oi-unknown-grid">
            {unknown.map(
              (skill) => (
                <div
                  className="oi-unknown-chip"
                  key={skill}
                >
                  {formatSkillName(
                    skill
                  )}
                </div>
              )
            )}
          </div>
        </article>
      )}
    </section>
  );
}