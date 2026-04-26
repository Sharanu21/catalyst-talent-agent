from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq, RateLimitError
import json
import os
import time
import re
import hashlib
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import OrderedDict
from dotenv import load_dotenv

load_dotenv(override=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI(title="Catalyst Talent Scouting Agent v2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open("candidates.json", "r") as f:
    CANDIDATES = json.load(f)

class LRUCache:
    def __init__(self, max_size=50, ttl_hours=24):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl = timedelta(hours=ttl_hours)
    
    def get(self, key):
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() - entry['timestamp'] < self.ttl:
                self.cache.move_to_end(key)
                return entry['data']
            else:
                del self.cache[key]
        return None
    
    def set(self, key, data):
        if key in self.cache:
            del self.cache[key]
        elif len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)
        self.cache[key] = {'data': data, 'timestamp': datetime.now()}

jd_cache = LRUCache(max_size=20)

class JDRequest(BaseModel):
    job_description: str
    
class OutreachRequest(BaseModel):
    candidate_id: int
    candidate_name: str
    candidate_skills: list
    job_title: str
    message: str
    chat_history: list = []

def call_llm_with_retry(prompt: str, max_tokens: int = 150, max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant", 
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.3
            )
            return response.choices[0].message.content
        except RateLimitError:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                time.sleep(wait_time)
            else:
                raise HTTPException(status_code=429, detail="Rate limit exceeded.")

def extract_json(text: str) -> dict:
    text = re.sub(r'```\w*\n?', '', text)
    text = text.replace('```', '').strip()
    json_patterns = [r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', r'\{[^{}]*\}']
    for pattern in json_patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            try: return json.loads(match)
            except: continue
    try: return json.loads(text)
    except: return {}

def parse_jd(jd_text: str) -> dict:
    cache_key = hashlib.md5(jd_text[:200].encode()).hexdigest()
    cached = jd_cache.get(cache_key)
    if cached: return cached
    
    prompt = f"""Extract information from JD. Return ONLY JSON:
JD: {jd_text[:800]}
{{ "job_title": "", "required_skills": [], "preferred_skills": [], "min_experience": 0, "max_experience": 10, "location": "", "key_responsibilities": [], "summary": "" }}"""
    
    raw = call_llm_with_retry(prompt, 250)
    parsed = extract_json(raw)
    parsed.setdefault('required_skills', [])
    parsed.setdefault('min_experience', 0)
    parsed.setdefault('max_experience', 10)
    jd_cache.set(cache_key, parsed)
    return parsed

def dynamic_match_score(candidate: dict, jd: dict) -> dict:
    req_skills = set(s.lower().strip() for s in jd.get('required_skills', []))
    cand_skills = set(s.lower().strip() for s in candidate.get('skills', []))
    
    matched_required = [req for req in req_skills if any(req in cand or cand in req for cand in cand_skills)]
    req_match_pct = (len(matched_required) / len(req_skills) * 100) if req_skills else 80
    
    cand_exp = candidate.get('experience_years', 0)
    min_exp = jd.get('min_experience', 0)
    max_exp = jd.get('max_experience', 15)
    
    if cand_exp < min_exp: exp_fit = "Underqualified"
    elif cand_exp > max_exp: exp_fit = "Senior/Overqualified"
    else: exp_fit = "Perfect match"
    
    final_score = (req_match_pct * 0.7) + (min(cand_exp/max(min_exp,1), 1.2) * 20)
    final_score = max(25, min(98, final_score))
    interest_estimation = 50 + (req_match_pct * 0.4)

    return {
        "match_score": round(final_score, 1),
        "interest_score": round(interest_estimation, 1),
        "combined_score": round(final_score * 0.6 + interest_estimation * 0.4, 1),
        "skill_match_pct": round(req_match_pct, 1),
        "experience_fit": exp_fit,
        "matched_skills": matched_required,
        "missing_skills": list(req_skills - set(matched_required)),
        "explanation": f"Matched {len(matched_required)} skills with {exp_fit} experience.",
        "strengths": [f"{req_match_pct:.0f}% skill match", exp_fit],
        "concerns": []
    }

def generate_outreach_simulation(candidate: dict, jd: dict, match_data: dict) -> dict:
    return {
        "conversation": [
            {"role": "recruiter", "message": f"Hi {candidate['name']}, interested in a {jd['job_title']} role?"},
            {"role": "candidate", "message": "I'd love to hear more!"}
        ],
        "interest_score": match_data['interest_score'],
        "interest_level": "High" if match_data['interest_score'] > 70 else "Medium",
        "interest_signals": ["Quick response", "Strong skill alignment"],
        "availability_confirmed": True,
        "interest_summary": "Candidate is responsive and matches core tech."
    }

@app.get("/")
def root():
    return {"message": "Catalyst v2.0 Live"}

@app.post("/scout")
def scout_candidates(request: JDRequest):
    try:
        parsed_jd = parse_jd(request.job_description)
        scored_candidates = []
        for candidate in CANDIDATES[:15]:
            match_data = dynamic_match_score(candidate, parsed_jd)
            if match_data['match_score'] >= 15:
                outreach = generate_outreach_simulation(candidate, parsed_jd, match_data)
                # Fixed: Added score_details key for frontend
                scored_candidates.append({
                    "candidate": candidate,
                    "match_score": match_data["match_score"],
                    "interest_score": match_data["interest_score"],
                    "combined_score": match_data["combined_score"],
                    "score_details": match_data,
                    "outreach": outreach
                })
            time.sleep(0.5)
        
        scored_candidates.sort(key=lambda x: x['combined_score'], reverse=True)
        shortlist = scored_candidates[:8]
        
        # Fixed: Updated return structure
        return {
            "success": True,
            "parsed_jd": parsed_jd,
            "total_scanned": len(CANDIDATES),
            "shortlisted": len(shortlist),
            "candidates": shortlist
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/outreach-chat")
def outreach_chat(request: OutreachRequest):
    prompt = f"You are {request.candidate_name}. Respond to: {request.message} in 2 sentences."
    reply = call_llm_with_retry(prompt, 100).strip()
    return {"success": True, "reply": reply, "interest_score": 80, "interest_level": "High"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)