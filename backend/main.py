from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import json
import os
import time
from dotenv import load_dotenv

load_dotenv(override=True)

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


def call_llm(prompt: str, max_tokens: int = 150) -> str:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.4
    )
    return response.choices[0].message.content


def parse_jd(jd_text: str) -> dict:
    jd_short = jd_text[:500]
    prompt = f"""Extract from JD and return ONLY JSON no markdown:
JD: {jd_short}
{{"job_title":"","required_skills":[],"preferred_skills":[],"min_experience":0,"max_experience":10,"location":"","key_responsibilities":[],"summary":""}}"""
    raw = call_llm(prompt, 200).strip().replace("```json","").replace("```","").strip()
    return json.loads(raw)


def score_candidate(candidate: dict, jd: dict) -> dict:
    prompt = f"""Job:{jd['job_title']} needs:{','.join(jd['required_skills'][:4])} exp:{jd['min_experience']}-{jd['max_experience']}yrs.
Candidate:{candidate['name']} {candidate['experience_years']}yrs skills:{','.join(candidate['skills'][:5])}.
Analyze carefully and return ONLY JSON:
{{"match_score":0,"skill_match_pct":0,"experience_fit":"","matched_skills":[],"missing_skills":[],"explanation":"your analysis","strengths":[],"concerns":[]}}"""
    raw = call_llm(prompt, 150).strip().replace("```json","").replace("```","").strip()
    return json.loads(raw)


def simulate_outreach(candidate: dict, jd: dict) -> dict:
    prompt = f"""Recruiter outreach: {candidate['name']} ({candidate['current_role']},{candidate['experience_years']}yrs) for {jd['job_title']}. Available:{candidate['availability']}.
Return ONLY JSON:
{{"conversation":[{{"role":"recruiter","message":"Hi {candidate['name']}, saw your profile for {jd['job_title']} role - interested?"}},{{"role":"candidate","message":"[reply]"}},{{"role":"recruiter","message":"[follow up]"}},{{"role":"candidate","message":"[reply]"}}],"interest_score":0,"interest_level":"","interest_signals":[],"availability_confirmed":true,"interest_summary":""}}"""
    raw = call_llm(prompt, 250).strip().replace("```json","").replace("```","").strip()
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
                if match_score >= 45:
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
                time.sleep(1)
            except Exception:
                time.sleep(1)
                continue

        scored_candidates.sort(key=lambda x: x["combined_score"], reverse=True)
        shortlist = scored_candidates[:8]

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
        last_msgs = request.chat_history[-3:] if len(request.chat_history) > 3 else request.chat_history
        history_text = "\n".join([f"{m['role'].upper()}:{m['message']}" for m in last_msgs])
        prompt = f"""You are {request.candidate_name} for {request.job_title}. Skills:{','.join(request.candidate_skills[:4])}.
{history_text}
Recruiter:{request.message}
Reply in 2 sentences only. Return ONLY reply text."""
        reply = call_llm(prompt, 80).strip()

        interest_raw = call_llm(
            f"""Reply:"{reply[:100]}". Analyze interest level. Return ONLY JSON:{{"interest_score":0,"interest_level":""}}""",
            40
        ).strip().replace("```json","").replace("```","").strip()
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