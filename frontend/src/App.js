import React, { useState } from "react";
import "./App.css";
import Dashboard from "./components/Dashboard";
import JDInput from "./components/JDInput";
import CandidateCard from "./components/CandidateCard";
import OutreachModal from "./components/OutreachModal";
import ParsedJD from "./components/ParsedJD";
import Loader from "./components/Loader";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";

function App() {
  const [step, setStep] = useState("input"); // input | loading | results
  const [jd, setJd] = useState("");
  const [parsedJD, setParsedJD] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [stats, setStats] = useState(null);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [error, setError] = useState("");

  const handleScout = async () => {
    if (!jd.trim()) return;
    setStep("loading");
    setError("");
    try {
      const res = await fetch(`${API_BASE}/scout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_description: jd }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Scouting failed");
      setParsedJD(data.parsed_jd);
      setCandidates(data.candidates);
      setStats({
        total_scanned: data.total_scanned,
        shortlisted: data.shortlisted,
      });
      setStep("results");
    } catch (err) {
      setError(err.message);
      setStep("input");
    }
  };

  const handleReset = () => {
    setStep("input");
    setJd("");
    setParsedJD(null);
    setCandidates([]);
    setStats(null);
    setError("");
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-inner">
          <div className="logo">
            <span className="logo-icon">⚡</span>
            <span className="logo-text">TalentScout AI</span>
          </div>
          <div className="header-tagline">AI-Powered Talent Scouting & Engagement Agent</div>
          {step === "results" && (
            <button className="btn-reset" onClick={handleReset}>
              ← New Search
            </button>
          )}
        </div>
      </header>

      <main className="main">
        {step === "input" && (
          <JDInput jd={jd} setJd={setJd} onScout={handleScout} error={error} />
        )}
        {step === "loading" && <Loader />}
        {step === "results" && (
          <div className="results-layout">
            {parsedJD && <ParsedJD data={parsedJD} stats={stats} />}
            <div className="candidates-section">
              <div className="section-header">
                <h2>Shortlisted Candidates</h2>
                <span className="badge">{candidates.length} matches</span>
              </div>
              <div className="candidates-grid">
                {candidates.map((item, idx) => (
                  <CandidateCard
                    key={item.candidate.id}
                    rank={idx + 1}
                    data={item}
                    onOutreach={() => setSelectedCandidate(item)}
                  />
                ))}
              </div>
            </div>
          </div>
        )}
      </main>

      {selectedCandidate && (
        <OutreachModal
          data={selectedCandidate}
          jobTitle={parsedJD?.job_title || ""}
          onClose={() => setSelectedCandidate(null)}
          apiBase={API_BASE}
        />
      )}
    </div>
  );
}

export default App;
