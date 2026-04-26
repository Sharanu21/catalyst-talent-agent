import React, { useState, useEffect } from "react";

const STEPS = [
  "Parsing job description...",
  "Extracting required skills & experience...",
  "Scanning candidate pool...",
  "Running AI match scoring...",
  "Simulating outreach conversations...",
  "Calculating interest scores...",
  "Ranking shortlist...",
];

export default function Loader() {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => Math.min(prev + 1, STEPS.length - 1));
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="loader-page">
      <div className="loader-spinner" />
      <div className="loader-steps">
        {STEPS.map((step, idx) => (
          <div
            key={idx}
            className={`loader-step ${idx === currentStep ? "active" : idx < currentStep ? "done" : ""}`}
          >
            {idx < currentStep ? "✓ " : idx === currentStep ? "→ " : "  "}
            {step}
          </div>
        ))}
      </div>
      <p style={{ color: "var(--text-muted)", fontSize: "0.82rem" }}>
        This may take 30-60 seconds — AI is doing the heavy lifting
      </p>
    </div>
  );
}
