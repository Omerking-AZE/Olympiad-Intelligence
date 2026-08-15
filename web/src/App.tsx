import { useEffect, useState } from "react";

import "./App.css";

import SkillsGrid from "./components/SkillsGrid";
import ProgressChart from "./components/ProgressChart";
import Recommendations, {
  type Recommendation,
} from "./components/Recommendations";

import type {
  ProgressPoint,
  Skill,
  StudentIntelligence,
} from "./types/student";


const skills: Skill[] = [
  {
    code: "ALG",
    name: "Algebra",
    key: "algebra",
  },
  {
    code: "GEO",
    name: "Geometry",
    key: "geometry",
  },
  {
    code: "NTH",
    name: "Number Theory",
    key: "number_theory",
  },
  {
    code: "DMC",
    name: "Discrete Math",
    key: "discrete_mathematics",
  },
  {
    code: "PRO",
    name: "Proof",
    key: "proof",
  },
  {
    code: "REA",
    name: "Reasoning",
    key: "reasoning",
  },
  {
    code: "CAL",
    name: "Calculation",
    key: "calculation",
  },
  {
    code: "CAS",
    name: "Case Analysis",
    key: "case_analysis",
  },
];


function formatSkillName(skill: string) {
  return skill
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) =>
      char.toUpperCase()
    );
}


export default function App() {

  const [student, setStudent] =
    useState<StudentIntelligence | null>(
      null
    );

  const [progression, setProgression] =
    useState<ProgressPoint[]>([]);

  const [recommendations, setRecommendations] =
    useState<Recommendation[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);


  /* ========================================================
     INITIAL THEME
     ======================================================== */

  const [darkMode, setDarkMode] =
    useState(() => {
      const savedTheme =
        localStorage.getItem(
          "oi-theme"
        );

      return savedTheme !== "light";
    });


  /* ========================================================
     LOAD BACKEND DATA
     ======================================================== */

  useEffect(() => {

    Promise.all([
      fetch(
        "/data/student_intelligence.json"
      ).then(async (response) => {

        if (!response.ok) {
          throw new Error(
            `Student data error: ${response.status}`
          );
        }

        return response.json();
      }),

      fetch(
        "/data/student_progression.json"
      ).then(async (response) => {

        if (!response.ok) {
          throw new Error(
            `Progression data error: ${response.status}`
          );
        }

        return response.json();
      }),

      fetch(
        "/data/adaptive_recommendations.json"
      ).then(async (response) => {

        if (!response.ok) {
          throw new Error(
            `Recommendation data error: ${response.status}`
          );
        }

        return response.json();
      }),
    ])

      .then(
        ([
          studentData,
          progressionData,
          recommendationData,
        ]) => {

          setStudent(
            studentData
          );

          setProgression(
            progressionData
          );

          setRecommendations(
            recommendationData
          );

          setLoading(false);
        }
      )

      .catch((err: Error) => {

        setError(
          err.message
        );

        setLoading(false);
      });

  }, []);


  /* ========================================================
     THEME
     ======================================================== */

  const toggleTheme = () => {

    setDarkMode((current) => {

      const next =
        !current;

      localStorage.setItem(
        "oi-theme",
        next
          ? "dark"
          : "light"
      );

      return next;
    });

  };


  /* ========================================================
     LOADING
     ======================================================== */

  if (loading) {

    return (
      <div className="app-state">

        <div className="state-card">

          <div className="state-title">
            OLYMPIAD INTELLIGENCE
          </div>

          <div className="state-text">
            Loading student profile...
          </div>

        </div>

      </div>
    );
  }


  /* ========================================================
     ERROR
     ======================================================== */

  if (error || !student) {

    return (
      <div className="app-state">

        <div className="state-card error-state">

          <div className="state-title">
            PROFILE UNAVAILABLE
          </div>

          <div className="state-text">
            {error ??
              "Student data could not be loaded."}
          </div>

        </div>

      </div>
    );
  }


  /* ========================================================
     CALCULATED DISPLAY VALUES
     ======================================================== */

  const successRate =
    student.problems_attempted > 0
      ? Math.round(
          (
            student.problems_solved /
            student.problems_attempted
          ) * 100
        )
      : 0;


  const strongest =
    student.strongest_skills
      .slice(0, 3)
      .map((skill) => ({
        name:
          formatSkillName(skill),

        value:
          student.skill_ratings[
            skill as keyof typeof student.skill_ratings
          ],
      }));


  const weaknesses = [
    ...student.high_priority_weaknesses,
    ...student.medium_priority_weaknesses,
  ]
    .slice(0, 3)
    .map((skill) => ({
      name:
        formatSkillName(skill),

      value:
        student.skill_ratings[
          skill as keyof typeof student.skill_ratings
        ],
    }));


  const unknownSkills =
    student.unknown_skills.map(
      formatSkillName
    );


  /* ========================================================
     UI
     ======================================================== */

  return (

    <div
      className={`app ${
        darkMode
          ? "theme-dark"
          : "theme-light"
      }`}
    >

      {/* ====================================================
          HEADER
          ==================================================== */}

      <header className="topbar">

        <div className="brand-group">

          <div className="brand">
            OLYMPIAD
          </div>

          <div className="brand-subtitle">
            INTELLIGENCE
          </div>

        </div>


        <div className="header-actions">

          <div className="topbar-status">
            STUDENT PROFILE
          </div>

          <button
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label="Toggle theme"
            type="button"
          >

            <span className="theme-icon">
              {darkMode
                ? "☀"
                : "☾"}
            </span>

            <span>
              {darkMode
                ? "LIGHT"
                : "DARK"}
            </span>

          </button>

        </div>

      </header>


      {/* ====================================================
          MAIN DASHBOARD
          ==================================================== */}

      <main className="dashboard">


        {/* ==================================================
            HERO
            ================================================== */}

        <section className="hero">

          <div className="hero-text">

            <p className="eyebrow">
              MATH PLAYER PROFILE
            </p>

            <h1>
              {student.student_name}
            </h1>

            <p className="description">
              Your personalized olympiad
              intelligence profile.
            </p>


            <div className="hero-stats">

              <div className="stat-box">

                <span>
                  OVR
                </span>

                <strong>
                  {student.overall_rating}
                </strong>

              </div>


              <div className="stat-box">

                <span>
                  TIER
                </span>

                <strong>
                  {student.tier}
                </strong>

              </div>


              <div className="stat-box">

                <span>
                  SOLVED
                </span>

                <strong>
                  {student.problems_solved}
                </strong>

              </div>


              <div className="stat-box">

                <span>
                  SUCCESS
                </span>

                <strong>
                  {successRate}%
                </strong>

              </div>

            </div>

          </div>


          {/* =================================================
              MINI PROFILE CARD
              ================================================= */}

          <div className="mini-card">

            <div className="mini-rating">
              {student.overall_rating}
            </div>

            <div className="mini-label">
              OVR
            </div>

            <div className="mini-name">
              {student.student_name.toUpperCase()}
            </div>

            <div className="mini-skills">

              {skills
                .slice(0, 4)
                .map((skill) => (

                  <span
                    key={skill.code}
                  >

                    {skill.code}{" "}

                    {
                      student.skill_ratings[
                        skill.key
                      ]
                    }

                  </span>

                ))}

            </div>

          </div>

        </section>


        {/* ==================================================
            SKILLS
            ================================================== */}

        <SkillsGrid
          skills={skills}
          ratings={
            student.skill_ratings
          }
        />


        {/* ==================================================
            STRENGTHS + WEAKNESSES
            ================================================== */}

        <section className="profile-grid">


          <div className="info-panel">

            <p className="eyebrow">
              STRENGTHS
            </p>

            <h2>
              Strongest Areas
            </h2>


            <div className="rank-list">

              {strongest.length > 0 ? (

                strongest.map(
                  (skill, index) => (

                    <div
                      key={skill.name}
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
                        {skill.name}
                      </strong>

                      <b>
                        {skill.value}
                      </b>

                    </div>

                  )
                )

              ) : (

                <div>

                  <strong>
                    Not enough data
                  </strong>

                </div>

              )}

            </div>

          </div>


          <div className="info-panel weakness-panel">

            <p className="eyebrow">
              TRAINING FOCUS
            </p>

            <h2>
              Areas to Improve
            </h2>


            <div className="rank-list">

              {weaknesses.length > 0 ? (

                weaknesses.map(
                  (skill, index) => (

                    <div
                      key={skill.name}
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
                        {skill.name}
                      </strong>

                      <b>
                        {skill.value}
                      </b>

                    </div>

                  )
                )

              ) : (

                <div>

                  <strong>
                    No major weaknesses detected
                  </strong>

                </div>

              )}

            </div>

          </div>

        </section>


        {/* ==================================================
            UNKNOWN SKILLS
            ================================================== */}

        {unknownSkills.length > 0 && (

          <section className="section">

            <div className="info-panel">

              <p className="eyebrow">
                DATA COVERAGE
              </p>

              <h2>
                Areas Not Yet Measured
              </h2>


              <div className="rank-list">

                {unknownSkills.map(
                  (skill) => (

                    <div
                      key={skill}
                    >

                      <span>
                        —
                      </span>

                      <strong>
                        {skill}
                      </strong>

                      <b>
                        ?
                      </b>

                    </div>

                  )
                )}

              </div>

            </div>

          </section>

        )}


        {/* ==================================================
            OVR PROGRESSION
            ================================================== */}

        <section className="section">

          <div className="section-heading">

            <div>

              <p className="eyebrow">
                PLAYER DEVELOPMENT
              </p>

              <h2>
                OVR Progression
              </h2>

            </div>


            <span className="section-note">
              Historical performance
            </span>

          </div>


          <div className="chart-panel">

            <ProgressChart
              data={progression}
            />

          </div>

        </section>


        {/* ==================================================
            REAL AI RECOMMENDATIONS
            ================================================== */}

        <Recommendations
          recommendations={
            recommendations
          }
        />


      </main>

    </div>
  );
}