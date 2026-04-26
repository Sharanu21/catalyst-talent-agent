import React, { useState, useRef, useEffect } from "react";

export default function OutreachModal({ data, jobTitle, onClose, apiBase }) {
  const { candidate, outreach } = data;
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [interestScore, setInterestScore] = useState(outreach?.interest_score || 50);
  const [interestLevel, setInterestLevel] = useState(outreach?.interest_level || "Medium");
  const [showSimulated, setShowSimulated] = useState(true);
  const chatRef = useRef(null);

  useEffect(() => {
    if (outreach?.conversation) {
      setMessages(outreach.conversation.map((m) => ({ role: m.role, message: m.message })));
    }
  }, [outreach]);

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMsg = { role: "recruiter", message: input };
    const newHistory = [...messages, userMsg];
    setMessages(newHistory);
    setInput("");
    setLoading(true);
    setShowSimulated(false);

    try {
      const res = await fetch(`${apiBase}/outreach-chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          candidate_id: candidate.id,
          candidate_name: candidate.name,
          candidate_skills: candidate.skills,
          job_title: jobTitle,
          message: input,
          chat_history: newHistory,
        }),
      });
      const result = await res.json();
      if (result.success) {
        setMessages([...newHistory, { role: "candidate", message: result.reply }]);
        setInterestScore(result.interest_score);
        setInterestLevel(result.interest_level);
      }
    } catch (err) {
      setMessages([...newHistory, { role: "candidate", message: "Sorry, I'm having trouble connecting. Please try again." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-header">
          <div>
            <h3>💬 {candidate.name}</h3>
            <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginTop: "2px" }}>
              {candidate.current_role} · {showSimulated ? "AI-simulated outreach" : "Live AI conversation"}
            </div>
          </div>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="interest-live">
          <span>Interest:</span>
          <div className="interest-live-bar">
            <div className="interest-live-fill" style={{ width: `${interestScore}%` }} />
          </div>
          <span style={{ fontWeight: 600, color: interestScore >= 70 ? "var(--success)" : interestScore >= 40 ? "var(--warning)" : "var(--danger)" }}>
            {interestScore}/100 · {interestLevel}
          </span>
        </div>

        <div className="chat-area" ref={chatRef}>
          {showSimulated && (
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textAlign: "center", padding: "4px 12px", background: "var(--surface2)", borderRadius: "100px", alignSelf: "center" }}>
              AI-simulated outreach conversation
            </div>
          )}
          {messages.map((msg, idx) => (
            <div key={idx} className={`chat-msg ${msg.role}`}>
              <div className="chat-msg-label">{msg.role === "recruiter" ? "🧑 Recruiter" : `🙋 ${candidate.name}`}</div>
              <div className="chat-bubble">{msg.message}</div>
            </div>
          ))}
          {loading && (
            <div className="chat-msg candidate">
              <div className="chat-msg-label">🙋 {candidate.name}</div>
              <div className="chat-bubble" style={{ color: "var(--text-muted)" }}>typing...</div>
            </div>
          )}
        </div>

        <div className="chat-input-area">
          <input
            className="chat-input"
            placeholder="Ask the candidate anything..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
          />
          <button className="chat-send" onClick={sendMessage} disabled={loading || !input.trim()}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
