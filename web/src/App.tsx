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

type ViewKey = "overview" | "skills" | "analytics" | "problems";
type ViewIcon = "grid" | "nodes" | "chart" | "book";

const views: { id: ViewKey; label: string; caption: string; icon: ViewIcon }[] = [
  { id: "overview", label: "Overview", caption: "Your workspace", icon: "grid" },
  { id: "skills", label: "Skill map", caption: "Mathematical strengths", icon: "nodes" },
  { id: "analytics", label: "Analytics", caption: "Progress & patterns", icon: "chart" },
  { id: "problems", label: "Problem bank", caption: "Your next challenge", icon: "book" },
];

const viewCopy: Record<ViewKey, { eyebrow: string; title: string; description: string }> = {
  overview: {
    eyebrow: "YOUR MATHEMATICS WORKSPACE",
    title: "Mathematics, made measurable.",
    description: "A clearer view of what you know, where you can grow, and which problem to tackle next.",
  },
  skills: {
    eyebrow: "DIAGNOSTIC MATRIX",
    title: "Explore your skill map.",
    description: "See how each mathematical domain is currently represented in your profile.",
  },
  analytics: {
    eyebrow: "PERFORMANCE INSIGHTS",
    title: "Follow the shape of your progress.",
    description: "Review your rating snapshots, skill coverage, strengths, and areas still to measure.",
  },
  problems: {
    eyebrow: "PERSONALIZED PRACTICE",
    title: "Find your next good problem.",
    description: "Explore olympiad problems ranked with skill-priority and difficulty-fit signals.",
  },
};

function loadTheme() {
  try {
    return localStorage.getItem("oi-theme") !== "light";
  } catch {
    return true;
  }
}

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error("Request failed: " + response.status + " (" + path + ")");
  }
  return response.json() as Promise<T>;
}

function SidebarGlyph({ icon }: { icon: ViewIcon }) {
  const common = {
    width: 19,
    height: 19,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.65,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    "aria-hidden": true as const,
  };

  if (icon === "grid") {
    return <svg {...common}><rect x="3.5" y="3.5" width="7" height="7" rx="2" /><rect x="13.5" y="3.5" width="7" height="7" rx="2" /><rect x="3.5" y="13.5" width="7" height="7" rx="2" /><rect x="13.5" y="13.5" width="7" height="7" rx="2" /></svg>;
  }
  if (icon === "nodes") {
    return <svg {...common}><circle cx="12" cy="5" r="2.2" /><circle cx="5" cy="18" r="2.2" /><circle cx="19" cy="18" r="2.2" /><path d="m10.9 7-4.7 9M13.1 7l4.7 9M7.3 18h9.4" /><path d="M12 9.5v3.3" opacity=".55" /></svg>;
  }
  if (icon === "chart") {
    return <svg {...common}><path d="M4 19.5h16" /><path d="M6.5 16V11M12 16V5M17.5 16V8" /><path d="m5.5 8.5 5.1-4 5.1 2.1 3.1-2" opacity=".55" /></svg>;
  }
  return <svg {...common}><path d="M5 4.5A2.5 2.5 0 0 1 7.5 2H20v17H7.5A2.5 2.5 0 0 0 5 21.5z" /><path d="M5 4.5v17M8.5 6.5h8M8.5 10h8M8.5 13.5h5" /></svg>;
}

function MathBackdrop() {
  return (
    <div className="oi-math-backdrop" aria-hidden="true">
      <svg className="oi-geometry-svg" viewBox="0 0 1440 1000" preserveAspectRatio="xMidYMin slice">
        <defs>
          <linearGradient id="oi-line-gradient" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#a78bfa" stopOpacity=".5" />
            <stop offset=".55" stopColor="#67e8f9" stopOpacity=".18" />
            <stop offset="1" stopColor="#f0abfc" stopOpacity=".42" />
          </linearGradient>
          <pattern id="oi-dot-grid" width="28" height="28" patternUnits="userSpaceOnUse">
            <circle cx="1" cy="1" r="1" fill="#c4b5fd" opacity=".3" />
          </pattern>
        </defs>
        <rect width="1440" height="1000" fill="url(#oi-dot-grid)" opacity=".2" />
        <g fill="none" stroke="url(#oi-line-gradient)" strokeWidth="1.15">
          <circle cx="1270" cy="190" r="120" />
          <circle cx="1270" cy="190" r="154" strokeDasharray="5 10" />
          <circle cx="1270" cy="190" r="188" opacity=".45" />
          <path d="M70 680 235 395 400 680Z" />
          <path d="M235 395v285M70 680h330M70 680 317 538" opacity=".5" />
          <path d="m1000 740 145-250 145 250Z" opacity=".65" />
          <path d="M1072 615h146M1145 490v250M1000 740l218-125" opacity=".35" />
          <path d="M710 80v180M620 170h180M647 107l126 126M773 107 647 233" opacity=".35" />
          <path d="M480 840h260m-130-130v260" strokeDasharray="3 9" opacity=".3" />
        </g>
        <g fill="#c4b5fd" fontFamily="Georgia, serif" fontStyle="italic" opacity=".45">
          <text x="1120" y="390" fontSize="34">∑</text>
          <text x="340" y="230" fontSize="31">π</text>
          <text x="890" y="880" fontSize="28">∠</text>
          <text x="90" y="300" fontSize="25">√x</text>
          <text x="1330" y="620" fontSize="28">∞</text>
        </g>
        <g fill="#67e8f9" opacity=".5">
          <circle cx="235" cy="395" r="4" />
          <circle cx="1270" cy="190" r="4" />
          <circle cx="1145" cy="490" r="4" />
          <circle cx="400" cy="680" r="3" />
        </g>
      </svg>
      <span className="oi-orbit oi-orbit-one" />
      <span className="oi-orbit oi-orbit-two" />
    </div>
  );
}

function MathSnapshot({ student }: { student: StudentIntelligence }) {
  const measured = skills.filter((skill) =>
    !student.unknown_skills.includes(skill.key) &&
    Number.isFinite(student.skill_ratings[skill.key])
  ).length;
  const coverage = Math.round((measured / skills.length) * 100);
  const strongestKey = student.strongest_skills[0];
  const focusKey = student.high_priority_weaknesses[0] ?? student.medium_priority_weaknesses[0];
  const skillName = (key?: string) =>
    skills.find((skill) => skill.key === key)?.name ??
    (key ? key.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase()) : "Not available");
  const strongestScore = strongestKey
    ? student.skill_ratings[strongestKey as keyof typeof student.skill_ratings]
    : null;

  return (
    <article className="oi-math-snapshot oi-glass-panel">
      <div className="oi-snapshot-heading">
        <div>
          <span className="oi-eyebrow">PROFILE COVERAGE</span>
          <h3>Mathematical snapshot</h3>
        </div>
        <span className="oi-live-mark"><i /> {student.is_demo ? "SAMPLE" : "PROFILE"}</span>
      </div>
      <div className="oi-snapshot-main">
        <div className="oi-coverage-ring" style={{ background: "conic-gradient(from -90deg, #c084fc 0 " + coverage + "%, rgba(255,255,255,.09) " + coverage + "% 100%)" }}>
          <div className="oi-coverage-inner">
            <strong>{coverage}%</strong>
            <span>measured</span>
          </div>
        </div>
        <div className="oi-coverage-copy">
          <strong>{measured} <span>/ {skills.length} domains</span></strong>
          <p>Mathematical domains with a recorded skill estimate.</p>
          <div className="oi-coverage-track"><span style={{ width: String(coverage) + "%" }} /></div>
        </div>
      </div>
      <div className="oi-snapshot-divider" />
      <div className="oi-snapshot-details">
        <div>
          <span className="oi-snapshot-detail-icon oi-detail-violet">✦</span>
          <div><small>TOP STRENGTH</small><strong>{skillName(strongestKey)}</strong></div>
          <b>{strongestScore ?? "—"}</b>
        </div>
        <div>
          <span className="oi-snapshot-detail-icon oi-detail-teal">⌁</span>
          <div><small>TRAINING FOCUS</small><strong>{skillName(focusKey)}</strong></div>
          <b>{focusKey ? "Focus" : "—"}</b>
        </div>
      </div>
      <div className="oi-formula-note"><span>f(x)</span> = patterns + practice + proof</div>
    </article>
  );
}

function Sidebar({ activeView, onNavigate, isDemo }: {
  activeView: ViewKey;
  onNavigate: (view: ViewKey) => void;
  isDemo: boolean;
}) {
  return (
    <aside className="oi-sidebar">
      <div className="oi-sidebar-section-label">WORKSPACE</div>
      <nav className="oi-side-nav" aria-label="Main navigation">
        {views.map((view) => (
          <button
            key={view.id}
            type="button"
            className={"oi-side-link " + (activeView === view.id ? "is-active" : "")}
            onClick={() => onNavigate(view.id)}
            aria-current={activeView === view.id ? "page" : undefined}
          >
            <span className="oi-side-icon"><SidebarGlyph icon={view.icon} /></span>
            <span className="oi-side-label">{view.label}<small>{view.caption}</small></span>
            <span className="oi-side-chevron">↗</span>
          </button>
        ))}
      </nav>
      <div className="oi-sidebar-spacer" />
      <div className="oi-method-card">
        <div className="oi-method-orbit"><span>π</span><i /></div>
        <div className="oi-method-label">THE METHOD</div>
        <strong>Think in patterns.</strong>
        <p>Build mathematical fluency one proof at a time.</p>
        <div className="oi-method-equation">a² + b² = c²</div>
        {isDemo && <span className="oi-sidebar-demo">DEMO DATA ACTIVE</span>}
      </div>
      <div className="oi-sidebar-foot"><span className="oi-sidebar-foot-dot" /> OLYMPIAD INTELLIGENCE <span>v1.0</span></div>
    </aside>
  );
}

export default function App() {
  const [darkMode, setDarkMode] = useState(loadTheme);
  const [student, setStudent] = useState<StudentIntelligence | null>(null);
  const [progression, setProgression] = useState<ProgressPoint[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeView, setActiveView] = useState<ViewKey>("overview");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    try {
      localStorage.setItem("oi-theme", darkMode ? "dark" : "light");
    } catch {
      // Theme remains usable when storage is unavailable.
    }
    document.documentElement.classList.toggle("theme-light", !darkMode);
  }, [darkMode]);

  useEffect(() => {
    let cancelled = false;
    Promise.all([
      fetchJson<StudentIntelligence>("/data/student_intelligence.json"),
      fetchJson<ProgressPoint[]>("/data/student_progression.json"),
      fetchJson<Recommendation[]>("/data/adaptive_recommendations.json"),
    ])
      .then(([studentData, progressionData, recommendationData]) => {
        if (cancelled) return;
        setStudent(studentData);
        setProgression(progressionData);
        setRecommendations(recommendationData);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : "Unable to load dashboard data.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, []);

  const filteredRecommendations = useMemo(() => {
    const normalized = searchQuery.trim().toLowerCase();
    if (!normalized) return recommendations;
    return recommendations.filter((item) => {
      const haystack = [
        item.title, item.competition, item.target_domain, item.problem_type,
        item.problem_id, item.problem_text, item.problem_markdown,
      ].filter(Boolean).join(" ").toLowerCase();
      return haystack.includes(normalized);
    });
  }, [recommendations, searchQuery]);

  if (loading) {
    return (
      <div className="oi-state-screen">
        <div className="oi-state-card oi-glass-panel">
          <div className="oi-brand-mark oi-state-mark">✦</div>
          <div className="oi-eyebrow">OLYMPIAD INTELLIGENCE</div>
          <h1>Mapping your mathematics…</h1>
          <p>Preparing your skill profile and problem recommendations.</p>
          <div className="oi-loading-line"><span /></div>
        </div>
      </div>
    );
  }

  if (error || !student) {
    return (
      <div className="oi-state-screen">
        <div className="oi-state-card oi-state-error oi-glass-panel">
          <div className="oi-brand-mark oi-state-mark">!</div>
          <div className="oi-eyebrow">PROFILE UNAVAILABLE</div>
          <h1>We couldn't load the dashboard.</h1>
          <p>{error ?? "Student data could not be loaded."}</p>
        </div>
      </div>
    );
  }

  const copy = viewCopy[activeView];
  const isDemo = Boolean(student.is_demo);

  const renderActivePage = () => {
    switch (activeView) {
      case "overview":
        return (
          <>
            <HeroSection student={student} skills={skills} />
            <div className="oi-overview-insights">
              <div className="oi-overview-chart"><ProgressChart data={progression} isDemo={isDemo} /></div>
              <MathSnapshot student={student} />
            </div>
            <ProfilePanels student={student} />
            <div className="oi-overview-recommendations">
              <div className="oi-inline-section-head">
                <div><span className="oi-eyebrow">A GOOD NEXT STEP</span><h2>Problems worth exploring</h2></div>
                <button type="button" className="oi-text-action" onClick={() => setActiveView("problems")}>Explore problem bank <span>↗</span></button>
              </div>
              <Recommendations recommendations={filteredRecommendations.slice(0, 3)} searchQuery={searchQuery} />
            </div>
          </>
        );
      case "skills":
        return (
          <>
            <SkillsGrid skills={skills} ratings={student.skill_ratings} unknownSkills={student.unknown_skills} />
            <ProfilePanels student={student} />
          </>
        );
      case "analytics":
        return (
          <>
            <div className="oi-overview-insights oi-analytics-layout">
              <div className="oi-overview-chart"><ProgressChart data={progression} isDemo={isDemo} /></div>
              <MathSnapshot student={student} />
            </div>
            <ProfilePanels student={student} />
          </>
        );
      case "problems":
        return <Recommendations recommendations={filteredRecommendations} searchQuery={searchQuery} />;
    }
  };

  return (
    <div className={"oi-app oi-glass-app " + (darkMode ? "theme-dark" : "theme-light")}>
      <MathBackdrop />
      <Topbar
        darkMode={darkMode}
        onToggleTheme={() => setDarkMode((current) => !current)}
        searchQuery={searchQuery}
        onSearchChange={(value) => {
          setSearchQuery(value);
          if (value.trim()) setActiveView("problems");
        }}
        candidateRating={student.overall_rating}
        isDemo={isDemo}
        studentName={student.student_name}
      />
      <div className="oi-workspace">
        <Sidebar activeView={activeView} onNavigate={setActiveView} isDemo={isDemo} />
        <main className="oi-main-content">
          <div className="oi-page-heading">
            <div>
              <span className="oi-eyebrow">{copy.eyebrow}</span>
              <h1>{copy.title}</h1>
              <p>{copy.description}</p>
            </div>
            <div className="oi-page-heading-meta">
              <span className="oi-date-orb"><span>∑</span></span>
              <div><small>PROFILE INDEX</small><strong>{student.overall_rating} <em>OVR</em></strong></div>
            </div>
          </div>
          <div className="oi-page-transition" key={activeView}>
            {renderActivePage()}
          </div>
          <footer className="oi-footer oi-glass-footer">
            <div><strong>OLYMPIAD INTELLIGENCE</strong><span>Mathematical thinking, made visible.</span></div>
            <div className="oi-footer-status"><span className="oi-status-dot" />{isDemo ? "ILLUSTRATIVE DEMO DATA" : "PROFILE DATA LOADED"}</div>
          </footer>
        </main>
      </div>
    </div>
  );
}
