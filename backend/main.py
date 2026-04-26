from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI(title="Catalyst Talent Scouting Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open("candidates.json", "r") as f:
    CANDIDATES = json.load(f)


class JDRequest(BaseModel):
    job_description: str


class OutreachRequest(BaseModel):
    candidate_id: int
    candidate_name: str
    candidate_skills: list
    job_title: str
    message: str
    chat_history: list = []


def call_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.7
    )
    return response.choices[0].message.content


def parse_jd(jd_text: str) -> dict:
    prompt = f"""You are an expert JD parser. Extract structured information from this job description.

JD:
{jd_text}

Return ONLY valid JSON with these exact fields, no markdown, no explanation:
{{
  "job_title": "string",
  "required_skills": ["skill1", "skill2"],
  "preferred_skills": ["skill1"],
  "min_experience": 0,
  "max_experience": 99,
  "location": "string or Remote",
  "key_responsibilities": ["responsibility1"],
  "summary": "2-3 sentence summary"
}}"""
    raw = call_llm(prompt).strip().replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def score_candidate(candidate: dict, jd: dict) -> dict:
    prompt = f"""You are an expert technical recruiter. Score this candidate against the job.

JOB: {jd['job_title']} | Skills: {', '.join(jd['required_skills'])} | Exp: {jd['min_experience']}-{jd['max_experience']}yrs

CANDIDATE: {candidate['name']} | {candidate['current_role']} at {candidate['current_company']} | {candidate['experience_years']}yrs | Skills: {', '.join(candidate['skills'])}

Return ONLY valid JSON no markdown:
{{"match_score": 75, "skill_match_pct": 80, "experience_fit": "Good Fit", "matched_skills": ["skill1"], "missing_skills": ["skill1"], "explanation": "explanation here", "strengths": ["strength1"], "concerns": ["concern1"]}}"""
    raw = call_llm(prompt).strip().replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def simulate_outreach(candidate: dict, jd: dict) -> dict:
    prompt = f"""Simulate a recruiter outreach conversation for this candidate.

JOB: {jd['job_title']}
CANDIDATE: {candidate['name']}, {candidate['current_role']}, {candidate['experience_years']}yrs, available: {candidate['availability']}

Return ONLY valid JSON no markdown:
{{"conversation": [{{"role": "recruiter", "message": "msg"}}, {{"role": "candidate", "message": "msg"}}, {{"role": "recruiter", "message": "msg"}}, {{"role": "candidate", "message": "msg"}}, {{"role": "recruiter", "message": "msg"}}, {{"role": "candidate", "message": "msg"}}], "interest_score": 75, "interest_level": "High", "interest_signals": ["signal1"], "availability_confirmed": true, "interest_summary": "summary here"}}"""
    raw = call_llm(prompt).strip().replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


@app.get("/")
def root():
    return {"message": "Catalyst Talent Scouting Agent API is running"}


@app.get("/candidates")
def get_candidates():
    return {"candidates": CANDIDATES, "total": len(CANDIDATES)}


@app.post("/parse-jd")
def parse_job_description(request: JDRequest):
    try:
        parsed = parse_jd(request.job_description)
        return {"success": True, "parsed_jd": parsed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JD parsing failed: {str(e)}")


@app.post("/scout")
def scout_candidates(request: JDRequest):
    try:
        parsed_jd = parse_jd(request.job_description)
        scored_candidates = []
        for candidate in CANDIDATES[:15]:
            try:
                score_data = score_candidate(candidate, parsed_jd)
                match_score = score_data.get("match_score", 0)
                if match_score >= 40:
                    outreach_data = simulate_outreach(candidate, parsed_jd)
                    interest_score = outreach_data.get("interest_score", 0)
                    combined_score = round(0.6 * match_score + 0.4 * interest_score, 1)
                    scored_candidates.append({
                        "candidate": candidate,
                        "match_score": match_score,
                        "interest_score": interest_score,
                        "combined_score": combined_score,
                        "score_details": score_data,
                        "outreach": outreach_data
                    })
            except Exception:
                continue

        scored_candidates.sort(key=lambda x: x["combined_score"], reverse=True)
        shortlist = scored_candidates[:10]
        return {
            "success": True,
            "parsed_jd": parsed_jd,
            "total_scanned": len(CANDIDATES),
            "shortlisted": len(shortlist),
            "candidates": shortlist
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scouting failed: {str(e)}")


@app.post("/outreach-chat")
def outreach_chat(request: OutreachRequest):
    try:
        history_text = "\n".join([f"{m['role'].upper()}: {m['message']}" for m in request.chat_history])
        prompt = f"""You are simulating {request.candidate_name}, a candidate for {request.job_title}.
Skills: {', '.join(request.candidate_skills)}

Conversation:
{history_text}

Recruiter: {request.message}

Reply as candidate naturally, under 3 sentences. Return ONLY the reply text."""
        reply = call_llm(prompt).strip()

        interest_raw = call_llm(f"""Rate candidate interest 0-100 from this conversation:
{history_text}
Latest: {reply}
Return ONLY JSON: {{"interest_score": 75, "interest_level": "High"}}""").strip().replace("```json","").replace("```","").strip()
        interest_data = json.loads(interest_raw)

        return {
            "success": True,
            "reply": reply,
            "interest_score": interest_data.get("interest_score", 50),
            "interest_level": interest_data.get("interest_level", "Medium")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
