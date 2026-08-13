import type {
  Skill,
  SkillRatings,
} from "../types/student";

type Props = {
  skills: Skill[];
  ratings: SkillRatings;
};

function SkillCard({
  skill,
  value,
}: {
  skill: Skill;
  value: number;
}) {
  return (
    <div className="skill-card">
      <div className="skill-top">
        <span className="skill-code">
          {skill.code}
        </span>

        <span className="skill-value">
          {value}
        </span>
      </div>

      <span className="skill-name">
        {skill.name}
      </span>

      <div className="skill-bar">
        <div
          className="skill-fill"
          style={{
            width: `${Math.max(
              0,
              Math.min(value, 100)
            )}%`,
          }}
        />
      </div>
    </div>
  );
}

export default function SkillsGrid({
  skills,
  ratings,
}: Props) {
  return (
    <section className="section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">
            PLAYER ATTRIBUTES
          </p>

          <h2>
            Olympiad Skills
          </h2>
        </div>

        <span className="section-note">
          8 core attributes
        </span>
      </div>

      <div className="skills-grid">
        {skills.map((skill) => (
          <SkillCard
            key={skill.code}
            skill={skill}
            value={ratings[skill.key]}
          />
        ))}
      </div>
    </section>
  );
}