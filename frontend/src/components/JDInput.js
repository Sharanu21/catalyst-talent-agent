import React from "react";

const SAMPLE_JD = `Job Title: Senior Backend Engineer

We are looking for a Senior Backend Engineer to join our growing engineering team.

Responsibilities:
- Design and build scalable microservices using Java and Spring Boot
- Work with PostgreSQL, Redis, and Kafka for data storage and messaging
- Deploy and manage services on AWS using Docker and Kubernetes
- Collaborate with frontend teams on REST API design
- Participate in code reviews and mentor junior developers

Requirements:
- 4-7 years of backend development experience
- Strong proficiency in Java and Spring Boot
- Experience with microservices architecture
- Hands-on experience with PostgreSQL and Redis
- Knowledge of Docker and Kubernetes
- Experience with AWS or any cloud platform
- Strong understanding of REST API design
- Excellent problem-solving and communication skills

Nice to have:
- Experience with Kafka or other message brokers
- Knowledge of CI/CD pipelines
- Open source contributions

Location: Bengaluru, India (Hybrid)
CTC: 20-35 LPA`;

export default function JDInput({ jd, setJd, onScout, error }) {
  return (
    <div className="jd-input-page">
      <div className="jd-hero">
        <h1>Find Your Perfect Candidate</h1>
        <p>Paste a job description. Our AI agent scouts, matches, and engages candidates — instantly.</p>
      </div>
      <div className="jd-card">
        <label>Job Description</label>
        <textarea
          className="jd-textarea"
          placeholder="Paste your job description here — role, skills, experience, location, responsibilities..."
          value={jd}
          onChange={(e) => setJd(e.target.value)}
        />
        <div className="jd-actions">
          <button
            className="btn-primary"
            onClick={onScout}
            disabled={!jd.trim()}
          >
            ⚡ Scout Candidates
          </button>
          <button
            className="sample-btn"
            onClick={() => setJd(SAMPLE_JD)}
          >
            Load Sample JD
          </button>
        </div>
        {error && <div className="error-msg">⚠️ {error}</div>}
      </div>
    </div>
  );
}
