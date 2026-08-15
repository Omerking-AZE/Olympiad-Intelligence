import { useEffect, useMemo, useState } from "react";
import "./App.css";
import Topbar from "./components/Topbar";
import HeroSection from "./components/HeroSection";
import SkillsGrid from "./components/SkillsGrid";
import ProfilePanels from "./components/ProfilePanels";
import ProgressChart from "./components/ProgressChart";
import Recommendations, { type Recommendation } from "./components/Recommendations";
import type { ProgressPoint, Skill, StudentIntelligence } from "./types/student";

const skills: Skill[] = [
  { code: "ALG", name: "Algebra", key: "algebra" },
  { code: "GEO", name: "Geometry", key: "geometry" },
  { code: "NTH", name: "Number Theory", key: "number_theory" },
  { code: "DMC", name: "Discrete Math", key: "discrete_mathematics" },
  { code: "PRO", name: "Proof", key: "proof" },
  { code: "REA", name: "Reasoning", key: "reasoning" },
  { code: "CAL", name: "Calculation", key: "calculation" },
  { code: "CAS", name: "Case Analysis", key: "case_analysis" },
];

function loadTheme() {
  return localStorage.getItem("oi-theme") !== "light";
}

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(path);

  if (!response.ok) {
    throw new Error(
      `Request failed: ${response.status} (${path})`
    );
  }

  return response.json() as Promise<T>;
}

export default function App() {
  const [darkMode, setDarkMode] =
    useState(loadTheme);

  const [student, setStudent] =
    useState<StudentIntelligence | null>(
      null
    );

  const [progression, setProgression] =
    useState<ProgressPoint[]>([]);

  const [recommendations, setRecommendations] =
    useState<Recommendation[]>([]);

  const [searchQuery, setSearchQuery] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    localStorage.setItem(
      "oi-theme",
      darkMode ? "dark" : "light"
    );

    document.documentElement.classList.toggle(
      "theme-light",
      !darkMode
    );
  }, [darkMode]);

  useEffect(() => {
    let cancelled = false;

    Promise.all([
      fetchJson<StudentIntelligence>(
        "/data/student_intelligence.json"
      ),

      fetchJson<ProgressPoint[]>(
        "/data/student_progression.json"
      ),

      fetchJson<Recommendation[]>(
        "/data/adaptive_recommendations.json"
      ),
    ])
      .then(
        ([
          studentData,
          progressionData,
          recommendationData,
        ]) => {
          if (cancelled) return;

          setStudent(studentData);
          setProgression(progressionData);
          setRecommendations(
            recommendationData
          );
        }
      )
      .catch((err: unknown) => {
        if (cancelled) return;

        setError(
          err instanceof Error
            ? err.message
            : "Unable to load dashboard data."
        );
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const filteredRecommendations =
    useMemo(() => {
      const normalized =
        searchQuery.trim().toLowerCase();

      if (!normalized) {
        return recommendations;
      }

      return recommendations.filter(
        (item) => {
          const haystack = [
            item.title,
            item.competition,
            item.target_domain,
            item.problem_type,
            item.problem_id,
          ]
            .filter(Boolean)
            .join(" ")
            .toLowerCase();

          return haystack.includes(
            normalized
          );
        }
      );
    }, [
      recommendations,
      searchQuery,
    ]);

  if (loading) {
    return (
      <div className="oi-state-screen">
        <div className="oi-state-card">
          <div className="oi-brand-mark oi-state-mark">
            ✦
          </div>

          <div className="oi-eyebrow">
            OLYMPIAD INTELLIGENCE
          </div>

          <h1>
            Loading student profile…
          </h1>

          <p>
            Calibrating your current profile
            and adaptive training path.
          </p>
        </div>
      </div>
    );
  }

  if (error || !student) {
    return (
      <div className="oi-state-screen">
        <div className="oi-state-card oi-state-error">
          <div className="oi-brand-mark oi-state-mark">
            !
          </div>

          <div className="oi-eyebrow">
            PROFILE UNAVAILABLE
          </div>

          <h1>
            We couldn't load the dashboard.
          </h1>

          <p>
            {error ??
              "Student data could not be loaded."}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`oi-app ${
        darkMode
          ? "theme-dark"
          : "theme-light"
      }`}
    >
      <Topbar
        darkMode={darkMode}
        onToggleTheme={() =>
          setDarkMode(
            (current) => !current
          )
        }
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        candidateRating={
          student.overall_rating
        }
      />

      <main className="oi-dashboard">
        <HeroSection
          student={student}
          skills={skills}
        />

        <SkillsGrid
          skills={skills}
          ratings={
            student.skill_ratings
          }
        />

        <ProgressChart
          data={progression}
        />

        <ProfilePanels
          student={student}
        />

        <Recommendations
          recommendations={
            filteredRecommendations
          }
          searchQuery={searchQuery}
        />
      </main>

      <footer className="oi-footer">
        <div>
          <strong>
            OLYMPIAD INTELLIGENCE ENGINE
          </strong>

          <span>
            Evidence-driven student
            calibration
          </span>
        </div>

        <div className="oi-footer-status">
          <span className="oi-status-dot" />
          PIPELINE ONLINE
        </div>
      </footer>
    </div>
  );
}