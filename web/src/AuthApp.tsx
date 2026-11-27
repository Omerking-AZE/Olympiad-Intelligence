import { useCallback, useEffect, useMemo, useState, type FormEvent } from "react";
import "./AuthApp.css";
import ProblemText from "./components/ProblemText";
import type { StudentIntelligence } from "./types/student";

type User = { id: number; email: string; display_name: string };
type Problem = {
  problem_id: string; title: string; competition?: string | null; country?: string | null;
  language?: string | null; domain: string; problem_type: string; problem_text: string;
  difficulty_score: number; translation_status: string; display_language: string;
  is_machine_translated: boolean; images: string[]; last_result?: "solved" | "attempted" | null;
  final_answer?: string | null; source?: string; source_booklet?: string | null; booklet_source?: string | null;
};
type ProblemsResponse = { problems: Problem[]; total: number; limit: number; offset: number; unseen: boolean };
type Tab = "overview" | "practice" | "card";
const SKILLS = [
  ["algebra", "ALG", "Algebra"], ["geometry", "GEO", "Geometry"],
  ["number_theory", "NTH", "Number theory"], ["discrete_mathematics", "DIS", "Discrete mathematics"],
  ["proof", "PRO", "Proof"], ["reasoning", "REA", "Reasoning"],
  ["calculation", "CAL", "Calculation"], ["case_analysis", "CAS", "Case analysis"],
] as const;

async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(path, {
    credentials: "same-origin", ...init,
    headers: { ...(init.body ? { "Content-Type": "application/json" } : {}), ...init.headers },
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.error || "Request failed (" + response.status + ")");
  return payload as T;
}
function tierFor(rating: number) {
  if (rating >= 95) return "ICON";
  if (rating >= 90) return "ELITE";
  if (rating >= 85) return "SPECIAL";
  if (rating >= 80) return "RARE";
  if (rating >= 70) return "SILVER";
  return "BRONZE";
}
function xml(value: string) {
  return value.replace(/[<>&'"]/g, (ch) => ({ "<":"&lt;", ">":"&gt;", "&":"&amp;", "'":"&apos;", '"':"&quot;" }[ch] || ch));
}
function downloadCard(profile: StudentIntelligence) {
  const rating = Math.round(profile.overall_rating || 55);
  const tier = tierFor(rating);
  const themes: Record<string, string[]> = {
    BRONZE:["#2b160f","#985b36","#f2c18c"], SILVER:["#202733","#8c9bab","#f4f7fc"],
    RARE:["#091a3d","#326bb4","#a9dbff"], SPECIAL:["#170c32","#7045ac","#e0c2ff"],
    ELITE:["#2b1242","#9d4bd0","#ffdb8a"], ICON:["#392707","#b9871e","#fff1a8"],
  };
  const colors = themes[tier];
  const stats = SKILLS.map((item, i) => {
    const y = 790 + i * 75;
    const score = Math.round(Number(profile.skill_ratings?.[item[0]] ?? 55));
    return '<g><text x="115" y="' + y + '" fill="' + colors[2] + '" font-size="25" font-weight="700">' + item[1] +
      '</text><rect x="215" y="' + (y - 22) + '" width="430" height="14" rx="7" fill="#fff" opacity=".18"/><rect x="215" y="' +
      (y - 22) + '" width="' + (4.3 * score) + '" height="14" rx="7" fill="' + colors[2] +
      '"/><text x="690" y="' + y + '" fill="#fff" font-size="26" text-anchor="end" font-weight="700">' + score + '</text></g>';
  }).join("");
  const svg = '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="1200" viewBox="0 0 900 1200">' +
    '<defs><linearGradient id="bg" x2="0" y2="1"><stop stop-color="' + colors[0] + '"/><stop offset="1" stop-color="' + colors[1] +
    '"/></linearGradient><pattern id="grid" width="36" height="36" patternUnits="userSpaceOnUse"><path d="M0 0H36M0 0V36" stroke="' +
    colors[2] + '" stroke-opacity=".11" fill="none"/></pattern></defs><rect x="18" y="18" width="864" height="1164" rx="48" fill="url(#bg)" stroke="' +
    colors[2] + '" stroke-width="6"/><rect x="34" y="34" width="832" height="1132" rx="36" fill="url(#grid)"/><circle cx="450" cy="285" r="150" fill="none" stroke="' +
    colors[2] + '" stroke-width="3"/><text x="450" y="82" fill="' + colors[2] +
    '" text-anchor="middle" font-size="26" letter-spacing="7">OLYMPIAD INTELLIGENCE</text><text x="120" y="250" fill="' + colors[2] +
    '" font-size="50" font-weight="800">' + rating + '</text><text x="120" y="291" fill="#fff" font-size="22" letter-spacing="3">OVR</text>' +
    '<text x="450" y="505" fill="#fff" font-size="48" text-anchor="middle" font-weight="800">' + xml(profile.student_name || "Olympiad Student") +
    '</text><text x="450" y="552" fill="' + colors[2] + '" font-size="26" text-anchor="middle" letter-spacing="5">' + tier +
    ' MATHEMATICS CARD</text><text x="115" y="680" fill="' + colors[2] + '" font-size="23" letter-spacing="5">SKILL PROFILE</text>' +
    stats + '<path d="M115 1070H785" stroke="' + colors[2] + '" opacity=".55"/><text x="450" y="1115" fill="#fff" opacity=".82" font-size="20" text-anchor="middle">' +
    profile.problems_solved + ' solved · ' + profile.problems_attempted + ' attempted</text><text x="450" y="1150" fill="' + colors[2] +
    '" font-size="15" text-anchor="middle" letter-spacing="3">PERSONAL PRACTICE PROFILE</text></svg>';
  const url = URL.createObjectURL(new Blob([svg], { type: "image/svg+xml;charset=utf-8" }));
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "olympiad-intelligence-" + profile.student_name.toLowerCase().replace(/[^a-z0-9]+/g, "-") + "-card.svg";
  document.body.appendChild(anchor); anchor.click(); anchor.remove(); URL.revokeObjectURL(url);
}

function AuthScreen({ onAuthenticated }: { onAuthenticated: (user: User) => void }) {
  const [mode, setMode] = useState<"login" | "signup">("signup");
  const [name, setName] = useState(""); const [email, setEmail] = useState("");
  const [password, setPassword] = useState(""); const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(""); setBusy(true);
    try {
      const result = await api<{ user: User }>("/api/auth/" + mode, {
        method:"POST", body:JSON.stringify({ name, email, password }),
      });
      onAuthenticated(result.user);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not sign in.");
    } finally { setBusy(false); }
  }
  return <main className="oi-auth-screen">
    <div className="oi-auth-orbit oi-auth-orbit-a"/><div className="oi-auth-orbit oi-auth-orbit-b"/>
    <section className="oi-auth-card">
      <div className="oi-auth-brand"><span>∑</span><div><strong>OLYMPIAD</strong><small>INTELLIGENCE</small></div></div>
      <div className="oi-auth-eyebrow">YOUR PERSONAL MATHEMATICS PROFILE</div>
      <h1>{mode === "signup" ? "Make progress measurable." : "Welcome back."}</h1>
      <p className="oi-auth-intro">{mode === "signup" ? "Create your own workspace. Your practice history, skill ratings, and player card belong to your account." : "Sign in to continue your personalized olympiad training."}</p>
      <div className="oi-auth-tabs">
        <button className={mode === "signup" ? "active" : ""} type="button" onClick={() => {setMode("signup");setError("");}}>Create account</button>
        <button className={mode === "login" ? "active" : ""} type="button" onClick={() => {setMode("login");setError("");}}>Sign in</button>
      </div>
      <form onSubmit={submit} className="oi-auth-form">
        {mode === "signup" && <label>Your name<input autoComplete="name" value={name} onChange={(e)=>setName(e.target.value)} placeholder="How should we call you?" minLength={2} maxLength={60} required/></label>}
        <label>Email address<input type="email" autoComplete="email" value={email} onChange={(e)=>setEmail(e.target.value)} placeholder="you@example.com" maxLength={254} required/></label>
        <label>Password<input type="password" autoComplete={mode === "signup" ? "new-password" : "current-password"} value={password} onChange={(e)=>setPassword(e.target.value)} placeholder={mode === "signup" ? "At least 10 characters" : "Your password"} minLength={mode === "signup" ? 10 : 1} maxLength={200} required/></label>
        {error && <div className="oi-inline-error" role="alert">{error}</div>}
        <button className="oi-primary-cta" type="submit" disabled={busy}>{busy ? "Please wait…" : mode === "signup" ? "Create my profile" : "Sign in"} <span>↗</span></button>
      </form>
      <div className="oi-auth-foot"><span>✦</span> Your data is kept separate from other student profiles.</div>
    </section>
    <div className="oi-auth-footer">A PERSONAL PRACTICE SPACE · BUILT AROUND MATHEMATICAL THINKING</div>
  </main>;
}

function PlayerCard({ profile, onDownload }: { profile: StudentIntelligence; onDownload: () => void }) {
  const rating = Math.round(profile.overall_rating || 55); const tier = tierFor(rating);
  const [expanded, setExpanded] = useState(false);
  return <section className="oi-card-page">
    <div className="oi-section-heading"><div><span className="oi-eyebrow">YOUR PLAYER IDENTITY</span><h2>MathNet player card</h2><p>Built from your own recorded practice. It changes as your skill ratings develop.</p></div>
      <button className="oi-primary-cta compact" type="button" onClick={onDownload}>↓ Download card</button></div>
    <div className={"oi-fifa-card tier-" + tier.toLowerCase()}>
      <div className="oi-fifa-topline"><span>✦ OLYMPIAD INTELLIGENCE</span><span>{tier}</span></div>
      <div className="oi-fifa-main"><div className="oi-fifa-rating"><strong>{rating}</strong><span>OVR</span></div><div className="oi-fifa-emblem">∑</div></div>
      <h3>{profile.student_name}</h3><div className="oi-fifa-subtitle">MATHEMATICS · PERSONAL PROFILE</div><div className="oi-fifa-divider"/>
      <div className="oi-fifa-stats">{SKILLS.map(([key,code,label])=><div key={key}><span>{code}</span><strong>{Math.round(profile.skill_ratings?.[key] ?? 55)}</strong><small>{label}</small></div>)}</div>
      <div className="oi-fifa-bottom"><span>{profile.problems_solved} SOLVED</span><span>{profile.problems_attempted} ATTEMPTS</span></div>
    </div>
    <div className="oi-card-note"><strong>About this rating</strong><p>Your overall rating is a personal practice index based on your eight skill areas. It is not an official contest score or a comparison with other students.</p></div>
    <button className="oi-secondary-cta oi-card-expand" onClick={()=>setExpanded(v=>!v)} type="button">{expanded ? "Hide card details −" : "How the card is calculated +"}</button>
    {expanded && <div className="oi-card-note"><p>New accounts begin with a neutral baseline. Recording a problem as solved or attempted updates the corresponding domain rating. Repeated submissions of the same problem are prevented so one task cannot inflate your score indefinitely.</p></div>}
  </section>;
}

function ProblemDialog({ problem, onClose, onRecorded }: {
  problem: Problem; onClose: () => void; onRecorded: (profile: StudentIntelligence) => void;
}) {
  const [busy,setBusy]=useState(false); const [error,setError]=useState(""); const [showAnswer,setShowAnswer]=useState(false);
  async function record(result:"solved"|"attempted") {
    setBusy(true);setError("");
    try {
      const payload=await api<{profile:StudentIntelligence}>("/api/attempts",{method:"POST",body:JSON.stringify({problem_id:problem.problem_id,result})});
      onRecorded(payload.profile);
    } catch(reason) {setError(reason instanceof Error?reason.message:"Could not save this attempt.");}
    finally {setBusy(false);}
  }
  return <div className="oi-dialog-backdrop" role="presentation" onMouseDown={e=>{if(e.target===e.currentTarget)onClose();}}>
    <section className="oi-problem-dialog-new" role="dialog" aria-modal="true" aria-labelledby="oi-dialog-title">
      <header><div><span className="oi-eyebrow">PROBLEM · {problem.problem_id}</span><h2 id="oi-dialog-title">{problem.title}</h2><p>{[problem.competition,problem.country,problem.domain].filter(Boolean).join(" · ")}</p></div><button type="button" onClick={onClose} aria-label="Close">×</button></header>
      <div className="oi-dialog-tags"><span>{problem.domain}</span><span>{problem.problem_type}</span><span>Difficulty estimate {Math.round(problem.difficulty_score)}</span></div>
      {problem.translation_status==="pending" && <div className="oi-translation-notice"><strong>English translation pending</strong><span>This item is displayed in its source language ({problem.display_language}). Run the translation step in the setup guide to create an English display text.</span></div>}
      {problem.is_machine_translated && <div className="oi-translation-notice"><strong>Machine translation · review recommended</strong><span>Mathematical wording should be checked against the original source.</span></div>}
      <div className="oi-problem-statement"><ProblemText text={problem.problem_text || "The source does not provide a text statement for this record."}/></div>
      {problem.images.length>0 && <div className="oi-problem-images">{problem.images.map(src=><img src={src} alt="Problem figure" key={src} loading="lazy"/>)}</div>}
      {problem.final_answer && <div className="oi-answer-area"><button className="oi-secondary-cta" type="button" onClick={()=>setShowAnswer(v=>!v)}>{showAnswer?"Hide extracted answer":"Reveal extracted answer"}</button>{showAnswer&&<p>{problem.final_answer}</p>}</div>}
      <footer><div className="oi-source-meta"><span>SOURCE</span><strong>{problem.source||"MathNet"}</strong><small>{problem.booklet_source||problem.source_booklet||"Dataset source"}</small></div>
        <div className="oi-record-actions">{error&&<span className="oi-inline-error">{error}</span>}{problem.last_result?<span className="oi-recorded-label">Recorded: {problem.last_result}</span>:<><button type="button" className="oi-secondary-cta" disabled={busy} onClick={()=>record("attempted")}>Attempted</button><button type="button" className="oi-primary-cta compact" disabled={busy} onClick={()=>record("solved")}>{busy?"Saving…":"Solved ✓"}</button></>}</div></footer>
    </section>
  </div>;
}

function PracticeBank({ onProfileUpdated }: { onProfileUpdated:(profile:StudentIntelligence)=>void }) {
  const [items,setItems]=useState<Problem[]>([]);const [query,setQuery]=useState("");const [domain,setDomain]=useState("");
  const [offset,setOffset]=useState(0);const [total,setTotal]=useState(0);const [selected,setSelected]=useState<Problem|null>(null);
  const [loading,setLoading]=useState(false);const [error,setError]=useState("");
  const page=useCallback(async(append:boolean)=>{
    setLoading(true);setError("");const start=append?offset:0;
    try {
      const params=new URLSearchParams({search:query,domain,offset:String(start),limit:"24",unseen:"1"});
      const result=await api<ProblemsResponse>("/api/problems?"+params.toString());
      setItems(current=>append?[...current,...result.problems]:result.problems);setTotal(result.total);setOffset(start+result.problems.length);
    }catch(reason){setError(reason instanceof Error?reason.message:"Could not load problems.");}
    finally{setLoading(false);}
  },[domain,offset,query]);
  useEffect(() => {
    let cancelled = false;
    const timer = window.setTimeout(() => {
      setLoading(true);
      setError("");
      const params = new URLSearchParams({ search: query, domain, offset: "0", limit: "24", unseen: "1" });
      api<ProblemsResponse>("/api/problems?" + params.toString())
        .then((result) => {
          if (cancelled) return;
          setItems(result.problems);
          setTotal(result.total);
          setOffset(result.problems.length);
        })
        .catch((reason: unknown) => {
          if (!cancelled) setError(reason instanceof Error ? reason.message : "Could not load problems.");
        })
        .finally(() => {
          if (!cancelled) setLoading(false);
        });
    }, 180);
    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [query, domain]);
  function record(profile:StudentIntelligence){onProfileUpdated(profile);setItems(current=>current.filter(p=>p.problem_id!==selected?.problem_id));setTotal(v=>Math.max(0,v-1));setSelected(null);}
  const domains=["","Algebra","Geometry","Number Theory","Discrete","Combinatorics","Calculus"];
  return <section className="oi-practice-page">
    <div className="oi-section-heading"><div><span className="oi-eyebrow">PERSONALIZED PROBLEM BANK</span><h2>Find your next challenge.</h2><p>Each account gets its own practice order and its own rating history.</p></div><div className="oi-problem-count"><strong>{total.toLocaleString()}</strong><span>unseen matches</span></div></div>
    <div className="oi-bank-controls"><label className="oi-bank-search"><span>⌕</span><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search a competition, topic, or statement…" aria-label="Search problems"/></label>
      <select value={domain} onChange={e=>setDomain(e.target.value)} aria-label="Filter by domain">{domains.map(value=><option value={value} key={value}>{value||"All domains"}</option>)}</select></div>
    {error&&<div className="oi-inline-error">{error}</div>}
    {!loading&&items.length===0&&<div className="oi-empty-bank"><span>∑</span><strong>{total===0?"No unseen problems match yet.":"No problems found."}</strong><p>Try another search or remove the domain filter. Your recorded problems remain in your profile history.</p></div>}
    <div className="oi-bank-grid">{items.map((problem,index)=><article key={problem.problem_id} className="oi-bank-card">
      <div className="oi-bank-card-top"><span>{problem.domain}</span><b>{Math.round(problem.difficulty_score)}</b></div><div className="oi-bank-index">PROBLEM {String(index+1).padStart(3,"0")}</div>
      <h3>{problem.title}</h3><p>{[problem.competition,problem.country].filter(Boolean).join(" · ")||"MathNet problem"}</p>
      <div className="oi-bank-card-bottom"><span className={problem.translation_status==="pending"?"is-pending":""}>{problem.translation_status==="pending"?"Translate · "+(problem.language||"unknown"):problem.is_machine_translated?"Translated · review":"English"}</span><button type="button" onClick={()=>setSelected(problem)}>Open problem <span>↗</span></button></div>
    </article>)}</div>
    {items.length>0&&items.length<total&&<div className="oi-load-more"><button type="button" onClick={()=>void page(true)} disabled={loading}>{loading?"Loading…":"Load more problems"}</button></div>}
    {selected&&<ProblemDialog problem={selected} onClose={()=>setSelected(null)} onRecorded={record}/>}
  </section>;
}

export default function AuthApp() {
  const [user,setUser]=useState<User|null>(null);const [profile,setProfile]=useState<StudentIntelligence|null>(null);
  const [tab,setTab]=useState<Tab>("overview");const [loading,setLoading]=useState(true);const [error,setError]=useState("");
  const refreshProfile=useCallback(async()=>{const result=await api<StudentIntelligence>("/api/profile");setProfile(result);return result;},[]);
  useEffect(()=>{
    let active=true;
    api<{id:number;email:string;display_name:string}>("/api/me").then(async session=>{
      if(!active)return;setUser({id:session.id,email:session.email,display_name:session.display_name});
      const loaded=await api<StudentIntelligence>("/api/profile");if(active)setProfile(loaded);
    }).catch(()=>{if(active)setUser(null);}).finally(()=>{if(active)setLoading(false);});
    return()=>{active=false;};
  },[]);
  async function logout(){try{await api("/api/auth/logout",{method:"POST",body:JSON.stringify({})});}catch{/* clear local view */}setUser(null);setProfile(null);setTab("overview");}
  function authenticated(next:User){setUser(next);void refreshProfile().catch(reason=>setError(reason instanceof Error?reason.message:"Profile unavailable."));}
  const greeting=useMemo(()=>{const first=profile?.student_name?.trim().split(/\s+/)[0];return first?"Welcome, "+first+".":"Your mathematics, in focus.";},[profile?.student_name]);
  if(loading)return <main className="oi-auth-loading"><div className="oi-loader-mark">∑</div><span>Preparing your workspace…</span></main>;
  if(!user)return <AuthScreen onAuthenticated={authenticated}/>;
  return <main className="oi-platform">
    <header className="oi-platform-header">
      <a className="oi-platform-brand" href="#" onClick={e=>{e.preventDefault();setTab("overview");}}><span>∑</span><strong>OLYMPIAD <i>INTELLIGENCE</i></strong></a>
      <nav className="oi-platform-nav" aria-label="Workspace">
        <button className={tab==="overview"?"active":""} onClick={()=>setTab("overview")} type="button">Overview</button>
        <button className={tab==="practice"?"active":""} onClick={()=>setTab("practice")} type="button">Problem bank</button>
        <button className={tab==="card"?"active":""} onClick={()=>setTab("card")} type="button">My card</button>
      </nav>
      <div className="oi-platform-user"><div><strong>{user.display_name}</strong><small>PERSONAL PROFILE</small></div><button type="button" onClick={logout}>Log out ↗</button></div>
    </header>
    <div className="oi-platform-content">
      {tab==="overview"&&profile&&<section className="oi-overview-page">
        <div className="oi-welcome-heading"><div><span className="oi-eyebrow">YOUR MATHEMATICS WORKSPACE</span><h1>{greeting}</h1><p>Explore your skills, build a problem-solving record, and let your profile reflect the work you put in.</p></div><div className="oi-welcome-symbol">∑</div></div>
        <div className="oi-stats-grid">
          <article className="oi-stat-card oi-stat-primary"><span>OVERALL RATING</span><strong>{profile.overall_rating}<small> OVR</small></strong><p>{tierFor(profile.overall_rating)} · personal practice index</p></article>
          <article className="oi-stat-card"><span>PROBLEMS SOLVED</span><strong>{profile.problems_solved}</strong><p>Marked as solved in your profile</p></article>
          <article className="oi-stat-card"><span>ATTEMPTS RECORDED</span><strong>{profile.problems_attempted}</strong><p>Unique problems attempted</p></article>
          <article className="oi-stat-card"><span>SKILLS MEASURED</span><strong>{8-profile.unknown_skills.length}<small> / 8</small></strong><p>Domains with recorded practice</p></article>
        </div>
        <div className="oi-overview-grid">
          <article className="oi-panel"><div className="oi-panel-heading"><div><span className="oi-eyebrow">SKILL MATRIX</span><h2>Your mathematical profile</h2></div><button onClick={()=>setTab("card")} type="button">View player card ↗</button></div>
            <div className="oi-skill-bars">{SKILLS.map(([key,code,label])=>{const rating=Math.round(profile.skill_ratings?.[key]??55);const measured=!profile.unknown_skills.includes(key);return <div className="oi-skill-bar-row" key={key}><span>{code}</span><div><strong>{label}</strong><div className="oi-skill-track"><i style={{width:rating+"%"}}/></div></div><b>{measured?rating:"—"}</b></div>;})}</div>
          </article>
          <article className="oi-panel oi-next-panel"><span className="oi-eyebrow">YOUR NEXT STEP</span><div className="oi-next-icon">✦</div><h2>One good problem at a time.</h2><p>Practice across algebra, geometry, number theory, proof, and more. Every recorded attempt shapes your personal rating.</p><button type="button" className="oi-primary-cta" onClick={()=>setTab("practice")}>Explore the problem bank ↗</button></article>
        </div>
        <div className="oi-profile-footnote"><span>✦</span><p>Ratings are personal estimates from recorded practice, not official olympiad grades. New profiles begin from a neutral baseline and improve as evidence is collected.</p></div>
      </section>}
      {tab==="practice"&&<PracticeBank onProfileUpdated={setProfile}/>}
      {tab==="card"&&profile&&<PlayerCard profile={profile} onDownload={()=>downloadCard(profile)}/>}
      {error&&<div className="oi-inline-error">{error}</div>}
    </div>
    <footer className="oi-platform-footer"><strong>OLYMPIAD INTELLIGENCE</strong><span>Personal practice · Mathematical thinking · Progress over time</span><span>{user.email}</span></footer>
  </main>;
}
