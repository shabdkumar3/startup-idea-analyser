# 🔮 Startup Oracle

> **Give me your startup idea — I'll tell you if it'll live or die.**

## 🚀 Live Demo

👉 **[startup-oracle.streamlit.app](https://startup-oracle.streamlit.app/)**

---

## 🧠 What is this?

Startup Oracle is a **12-agent autonomous AI system** that validates startup ideas like a VC firm would. Type your idea → the pipeline runs a full analysis → you get a VC-grade report with an **Oracle Score (0–100)** and a clear verdict: **BUILD IT / PIVOT / KILL IT**.

No fluff. Just cold, hard analysis.

---

## ⚙️ How it works

The system runs 12 specialized AI agents in a **LangGraph pipeline** — some in parallel, some sequential:

```
Idea Input
    │
    ▼
Idea Decomposer
    │
    ├──────────────────────┬─────────────────────┐
    ▼                      ▼                     ▼
Market Research      Competitor Intel       Graveyard Research
    │                      │                     │
    └──────────────────────┴─────────────────────┘
                           │
                       Sync Node
                           │
                    User Pain Miner
                           │
                     Market Sizer
                           │
                    Moat Detector
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
          Bull Agent               Bear Agent
              │                         │
              └────────────┬────────────┘
                           ▼
                     Judge Verdict
                           │
                       MVP Plan
                           │
                     Final Report
```

---

## 📊 What you get

| Section | Details |
|---------|---------|
| **Oracle Score** | 0–100 overall viability score |
| **Verdict** | BUILD IT / PIVOT / KILL IT |
| **Score Breakdown** | Problem Severity, Market Size, Defensibility, Monetization, Exec Complexity, Founder Fit |
| **Market Analysis** | TAM / SAM / SOM with reasoning + moat analysis |
| **Competitor Intel** | Real competitors with strengths, weaknesses, pricing, funding |
| **Graveyard** | Failed startups in the same space + lessons learned |
| **User Pain** | Real complaints, Reddit quotes, willingness to pay |
| **Bull vs Bear Debate** | Arguments for and against, with judge verdict |
| **MVP Plan** | Must-have features, tech stack, 100-user acquisition plan |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **LLM** | DeepSeek V3.1 via NVIDIA NIM API |
| **Agent Framework** | LangGraph (StateGraph) |
| **LLM Orchestration** | LangChain |
| **Web Search** | DuckDuckGo + Tavily |
| **Data Validation** | Pydantic v2 |
| **Frontend** | Streamlit |
| **Deployment** | Streamlit Community Cloud |

---

## 🏃 Run locally

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/startup-oracle.git
cd startup-oracle
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set up `.env`**
```env
NVIDIA_API_KEY=your_nvidia_api_key
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=deepseek-ai/deepseek-v3.1
TAVILY_API_KEY=your_tavily_api_key
```

**4. Run**
```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
startup-oracle/
├── app.py          # Streamlit UI
├── graph.py        # LangGraph pipeline definition
├── agents.py       # All 12 agent functions
├── schemas.py      # Pydantic models for structured output
├── tools.py        # Web search (DDG + Tavily)
├── config.py       # Environment variable loader
├── requirements.txt
└── .env            # (not committed — add your own)
```

---


## 📌 Project Status

Built as a portfolio project to demonstrate **agentic AI systems** with LangGraph. 

**What's working:**
- ✅ Full 12-agent pipeline end-to-end
- ✅ Structured output with Pydantic validation
- ✅ Parallel agent execution (market + competitor + graveyard run simultaneously)
- ✅ Live progress indicator during analysis
- ✅ Multi-source web search (DDG + Tavily)

---

*Built with LangGraph + DeepSeek + Streamlit*
