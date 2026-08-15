import type {
  Skill,
  StudentIntelligence,
} from "../types/student";

type HeroSectionProps = {
  student: StudentIntelligence;
  skills: Skill[];
};

export default function HeroSection({
  student,
  skills,
}: HeroSectionProps) {
  const successRate =
    student.problems_attempted > 0
      ? Math.round(
          (student.problems_solved /
            student.problems_attempted) *
            100
        )
      : 0;

  return (
    <section className="oi-hero-section">
      <div className="oi-hero-copy">
        <span className="oi-eyebrow">
          MATH PLAYER PROFILE
        </span>

        <h1>
          {student.student_name}
        </h1>

        <p>
          Your personalized olympiad
          intelligence profile, tuned to
          your recent performance and
          training needs.
        </p>

        <div className="oi-hero-stats">
          <div className="oi-stat-card">
            <span>OVR</span>
            <strong>
              {student.overall_rating}
            </strong>
          </div>

          <div className="oi-stat-card">
            <span>TIER</span>
            <strong>
              {student.tier}
            </strong>
          </div>

          <div className="oi-stat-card">
            <span>SOLVED</span>
            <strong>
              {student.problems_solved}
            </strong>
          </div>

          <div className="oi-stat-card">
            <span>SUCCESS</span>
            <strong>
              {successRate}%
            </strong>
          </div>
        </div>
      </div>

      <div className="oi-holo-card">
        <div className="oi-holo-orbit oi-holo-orbit-a" />
        <div className="oi-holo-orbit oi-holo-orbit-b" />
        <div className="oi-holo-glow" />

        <div className="oi-holo-content">
          <div className="oi-holo-kicker">
            CURRENT RATING
          </div>

          <div className="oi-holo-rating">
            {student.overall_rating}
          </div>

          <div className="oi-holo-tier">
            {student.tier}
          </div>

          <div className="oi-holo-name">
            {student.student_name.toUpperCase()}
          </div>

          <div className="oi-holo-skill-grid">
            {skills
              .slice(0, 4)
              .map((skill) => (
                <div
                  key={skill.code}
                >
                  <span>
                    {skill.code}
                  </span>

                  <strong>
                    {
                      student.skill_ratings[
                        skill.key
                      ]
                    }
                  </strong>
                </div>
              ))}
          </div>
        </div>
      </div>
    </section>
  );
}