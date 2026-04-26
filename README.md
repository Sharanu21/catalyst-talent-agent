# ⚡ TalentScout AI — Catalyst Hackathon Submission

> AI-Powered Talent Scouting & Engagement Agent  
> Built for Deccan.ai Catalyst Hackathon 2025

## 🎯 What It Does

TalentScout AI is a fully autonomous talent scouting agent that:

1. **Parses any Job Description** → Extracts skills, experience requirements, responsibilities
2. **Discovers matching candidates** → Scans a pool of 50 realistic candidate profiles
3. **AI Match Scoring** → Scores each candidate 0-100 with full explainability (matched skills, gaps, experience fit)
4. **Simulated Outreach** → AI recruiter engages each candidate conversationally to assess genuine interest
5. **Interest Scoring** → Rates candidate interest 0-100 based on conversation signals
6. **Ranked Shortlist** → Combined score (60% match + 40% interest) with recruiter-ready output
7. **Live Chat** → Recruiter can continue chatting with any candidate in real-time

## 🏗️ Architecture

```
┌──────────────────┐     ┌─────────────────────────────────────┐
│   React Frontend │────▶│          FastAPI Backend             │
│                  │     │                                      │
│  • JD Input      │     │  ┌─────────────┐  ┌──────────────┐  │
│  • Parsed JD     │     │  │  JD Parser  │  │  Candidate   │  │
│  • Candidate     │     │  │   Agent     │  │  Discovery   │  │
│    Cards         │     │  └──────┬──────┘  └──────┬───────┘  │
│  • Score Bars    │     │         │                 │          │
│  • Outreach Chat │     │  ┌──────▼──────────────────▼──────┐  │
└──────────────────┘     │  │      Match Scoring Agent        │  │
                         │  │   (Gemini 2.0 Flash + rules)   │  │
                         │  └──────────────┬─────────────────┘  │
                         │                 │                     │
                         │  ┌──────────────▼─────────────────┐  │
                         │  │    Outreach Simulation Agent    │  │
                         │  │  (Conversational AI recruiter)  │  │
                         │  └──────────────┬─────────────────┘  │
                         │                 │                     │
                         │  ┌──────────────▼─────────────────┐  │
                         │  │       Scoring Engine            │  │
                         │  │  Combined = 0.6×Match +         │  │
                         │  │            0.4×Interest         │  │
                         │  └────────────────────────────────┘  │
                         └─────────────────────────────────────┘
                                          │
                                   ┌──────▼──────┐
                                   │  Gemini API  │
                                   │ (Free Tier)  │
                                   └─────────────┘
```

## 📊 Scoring Logic

| Dimension | Weight | How It's Calculated |
|---|---|---|
| Match Score | 60% | Skill overlap, experience fit, role alignment (AI-scored 0-100) |
| Interest Score | 40% | Outreach conversation signals — enthusiasm, availability, questions asked (AI-scored 0-100) |
| **Combined Score** | 100% | Match is weighted higher (60%) because skill alignment is critical, while interest (40%) ensures candidates are actively engaged and available.|

### Match Score Breakdown
- Required skills present in candidate profile
- Experience years within range
- Role relevance and seniority alignment
- Location match

### Interest Score Signals
- Positive language and enthusiasm
- Proactive questions about the role
- Confirmed availability
- Salary alignment

 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React.js |
| Backend | Python FastAPI |
| AI/LLM | Google Gemini 2.0 Flash (Free Tier) |
| Candidate Data | 50 mock profiles (JSON) |
| Deployment | Render (backend) + Netlify (frontend) |

##  Local Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
-  Groq API key (free)

### Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt

# Create .env file
echo "GEMINI_API_KEY=your_key_here" > .env

python main.py
```

Backend runs at: `http://localhost:8000`  
API docs at: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm start
```

Frontend runs at: `http://localhost:3000`

##  API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/candidates` | All 50 candidates |
| POST | `/parse-jd` | Parse a job description |
| POST | `/scout` | Full scouting pipeline |
| POST | `/outreach-chat` | Live AI chat with candidate |

##  APIs & Tools Used

| Tool | Purpose | Tier |
|---|---|---|
| Google Gemini 2.0 Flash | LLM for all AI agents | Free |
| FastAPI | Backend framework | Open source |
| React.js | Frontend | Open source |

##  Project Structure

```
catalyst-talent-agent/
├── backend/
│   ├── main.py              # All API endpoints + agent logic
│   ├── candidates.json      # 50 mock candidate profiles
│   ├── requirements.txt
│   └── .env                 # Your Gemini API key (not committed)
├── frontend/
│   ├── src/
│   │   ├── App.js           # Main app
│   │   ├── App.css          # All styles
│   │   └── components/
│   │       ├── JDInput.js   # JD paste interface
│   │       ├── ParsedJD.js  # Parsed JD display
│   │       ├── CandidateCard.js  # Candidate result card
│   │       ├── OutreachModal.js  # Chat modal
│   │       └── Loader.js    # Loading state
│   └── .env                 # API URL config
└── README.md
```

## 🎬 Demo Flow

1. Paste a Job Description (or use the sample JD)
2. Click "Scout Candidates"
3. AI parses the JD, scores 50 candidates, simulates outreach
4. View ranked shortlist with Match + Interest scores
5. Click any candidate to view their outreach conversation
6. Continue the conversation live with the AI-powered candidate

## Live Demo
Frontend: https://catalyst-talent-agent.netlify.app/ 
Backend: https://catalyst-talent-agent-5ahj.onrender.com

##  Sample Input (Job Description)
Senior Backend Engineer  
- 5+ years experience  
- Java / Spring Boot  
- Microservices  
- AWS
   
##  Sample Output (Top Candidates)
1. Aarav Sharma  
   Match: 92  
   Interest: 85  
   Combined: 89.8  
2. Priya Nair  
   Match: 88  
   Interest: 80  
   Combined: 84.8  

## 👤 Built By

Sharanabasav Meti  
Catalyst Hackathon — Deccan.ai 2025
