import React from "react";

export default function ParsedJD({ data, stats }) {
  return (
    <div className="parsed-jd">
      <div className="parsed-jd-header">
        <div>
          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "4px" }}>Role Identified</div>
          <div className="parsed-jd-title">{data.job_title}</div>
        </div>
        <div className="stats-row">
          {stats && (
            <>
              <div className="stat-chip">🔍 Scanned <span>{stats.total_scanned}</span> profiles</div>
              <div className="stat-chip">✅ Shortlisted <span>{stats.shortlisted}</span> candidates</div>
            </>
          )}
        </div>
      </div>

      <div className="jd-meta">
        {data.location && <div className="jd-meta-item">📍 {data.location}</div>}
        {(data.min_experience || data.max_experience) && (
          <div className="jd-meta-item">
            💼 {data.min_experience}–{data.max_experience >= 99 ? "15+" : data.max_experience} years
          </div>
        )}
      </div>

      {data.summary && (
        <p style={{ fontSize: "0.88rem", color: "var(--text-muted)", marginBottom: "14px", lineHeight: "1.6" }}>
          {data.summary}
        </p>
      )}

      <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "8px" }}>
        Required Skills
      </div>
      <div className="skills-row">
        {data.required_skills?.map((s) => (
          <span key={s} className="skill-tag">{s}</span>
        ))}
        {data.preferred_skills?.map((s) => (
          <span key={s} className="skill-tag preferred">{s} ★</span>
        ))}
      </div>
    </div>
  );
}
