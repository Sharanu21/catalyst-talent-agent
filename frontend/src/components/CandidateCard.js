import React from "react";

function getRankClass(rank) {
  if (rank === 1) return "gold";
  if (rank === 2) return "silver";
  if (rank === 3) return "bronze";
  return "";
}

function getInterestClass(level) {
  const l = (level || "").toLowerCase();
  if (l === "high") return "high";
  if (l === "medium") return "medium";
  return "low";
}

export default function CandidateCard({ rank, data, onOutreach }) {
  const { candidate, match_score, interest_score, combined_score, score_details, outreach } = data;

  return (
    <div className="candidate-card">
      <div className="card-top">
        <div className={`candidate-rank ${getRankClass(rank)}`}>#{rank}</div>
        <div className="candidate-info">
          <div className="candidate-name">{candidate.name}</div>
          <div className="candidate-role">
            {candidate.current_role} · {candidate.current_company}
          </div>
          <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginTop: "2px" }}>
            📍 {candidate.location} · {candidate.experience_years}y exp
          </div>
        </div>
        <div className="combined-score">
          <div className="combined-score-value">{combined_score}</div>
          <div className="combined-score-label">Combined</div>
        </div>
      </div>

      <div className="score-bars">
        <div className="score-bar-row">
          <div className="score-bar-label">Match Score</div>
          <div className="score-bar-track">
            <div className="score-bar-fill match" style={{ width: `${match_score}%` }} />
          </div>
          <div className="score-bar-value" style={{ color: "var(--accent)" }}>{match_score}</div>
        </div>
        <div className="score-bar-row">
          <div className="score-bar-label">Interest Score</div>
          <div className="score-bar-track">
            <div className="score-bar-fill interest" style={{ width: `${interest_score}%` }} />
          </div>
          <div className="score-bar-value" style={{ color: "var(--accent2)" }}>{interest_score}</div>
        </div>
      </div>

      {score_details?.matched_skills?.length > 0 && (
        <div className="card-tags">
          {score_details.matched_skills.slice(0, 4).map((s) => (
            <span key={s} className="tag matched">✓ {s}</span>
          ))}
          {score_details.missing_skills?.slice(0, 2).map((s) => (
            <span key={s} className="tag skill">✗ {s}</span>
          ))}
        </div>
      )}

      {score_details?.explanation && (
        <div className="card-explanation">{score_details.explanation}</div>
      )}

      {outreach?.interest_level && (
        <div className={`interest-badge ${getInterestClass(outreach.interest_level)}`}>
          {outreach.interest_level === "High" ? "🔥" : outreach.interest_level === "Medium" ? "💬" : "❄️"}
          {outreach.interest_level} Interest · {outreach.availability_confirmed ? "Available" : "Check availability"}
        </div>
      )}

      <button className="btn-outreach" onClick={onOutreach}>
        💬 View Outreach Conversation
      </button>
    </div>
  );
}
