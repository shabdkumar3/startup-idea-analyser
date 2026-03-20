from schemas import *
from tools import search_web
from langchain_openai import ChatOpenAI
from config import NVIDIA_API_KEY, NVIDIA_BASE_URL, NVIDIA_MODEL
import json, re

if not NVIDIA_API_KEY:
    raise ValueError("Missing NVIDIA_API_KEY in .env")

model = ChatOpenAI(
    api_key=NVIDIA_API_KEY.strip(),
    base_url=NVIDIA_BASE_URL.strip().rstrip("/"),
    model=NVIDIA_MODEL.strip(),
    temperature=0.2,
    timeout=120,
    max_retries=2,
)

# ── Helper: replaces model.with_structured_output(Schema).invoke(messages) ────
# NVIDIA NIM rejects nested JSON schemas ($defs/$ref). Instead we prompt the
# model to return plain JSON and parse + validate it ourselves.
def invoke_structured(schema_class, messages):
    messages = [dict(m) for m in messages]          # shallow copy so we don't mutate

    # Append the expected JSON structure to the last user message
    schema = schema_class.model_json_schema()
    schema_str = json.dumps(schema, indent=2)
    messages[-1]["content"] += (
        f"\n\nYou MUST respond with ONLY a valid JSON object. "
        f"No markdown fences, no explanation, just raw JSON.\n"
        f"JSON schema to follow:\n{schema_str}"
    )

    # Tell the system message to return JSON only
    for m in messages:
        if m.get("role") == "system":
            m["content"] += " Always respond with raw JSON only — no markdown, no prose."
            break

    res = model.invoke(messages)
    text = res.content.strip()

    # Strip markdown fences if the model adds them anyway
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    text = text.strip()

    # Find the first { or [ in case there's any leading text
    start = min(
        (text.find(c) for c in ["{", "["] if text.find(c) != -1),
        default=0
    )
    text = text[start:]

    return schema_class.model_validate(json.loads(text))
# ──────────────────────────────────────────────────────────────────────────────


def decompose_idea_node(state: OracleState) -> dict:
    raw_idea = state["raw_idea"]

    result = invoke_structured(StartupIdea, [
        {"role": "system", "content": "You are a sharp startup analyst. Decompose the founder's idea into precise structured components. Be specific — no vague answers."},
        {"role": "user",   "content": f"Startup idea: {raw_idea}"}
    ])

    return {
        "structured_idea": result,
        "agent_logs": ["Idea Decomposer — done"]
    }


def market_research_node(state: OracleState):
    structured_idea = state["structured_idea"]
    keywords = " ".join(structured_idea.keywords[:3])
    market_size  = search_web(f"{keywords} market size 2026")
    growth_trend = search_web(f"{keywords} industry growth trends")
    demand       = search_web(f"{structured_idea.industry} market demand")
    results      = market_size + growth_trend + demand

    response = invoke_structured(MarketSignals, [
        {"role": "system", "content": "You are a market research analyst."},
        {"role": "user",   "content": f"Search results:\n{results}\n\nExtract market signals."}
    ])

    return {
        "market_signals": response,
        "agent_logs": ["Market Research — done"],
        "sources": [keywords, structured_idea.industry]
    }


def competitor_intel_node(state: OracleState):
    structured_idea = state["structured_idea"]
    keywords = " ".join(structured_idea.keywords[:3])
    industry = structured_idea.industry

    top_startups            = search_web(f"{keywords} top startups 2026")
    competitor_alternatives = search_web(f"{keywords} competitors alternatives")
    top_companies           = search_web(f"best {industry} companies")
    competitors             = top_companies + top_startups + competitor_alternatives

    response = invoke_structured(CompetitorList, [
        {"role": "system", "content": "Competitive intelligence analyst."},
        {"role": "user",   "content": (
            f"Search results:\n{competitors}\n\n"
            "Extract REAL companies that build similar products. "
            "Rules: Ignore AI model companies. Ignore unrelated tech companies. "
            "Only include businesses selling similar products."
        )}
    ])

    attempts = state.get("competitor_search_attempts", 0)
    return {
        "competitors": response.competitors,
        "agent_logs": ["Competitors Identified"],
        "competitor_search_attempts": attempts + 1,
        "sources": [
            f"{keywords} top startups 2026",
            f"{keywords} competitors alternatives",
            f"best {industry} companies"
        ]
    }


def should_search_more(state: OracleState) -> str:
    competitors = state.get("competitors") or []
    attempts    = state.get("competitor_search_attempts", 0)
    if len(competitors) < 3 and attempts < 2:
        return "competitor_intel_node"
    return "graveyard_research_node"


def graveyard_research_node(state: OracleState):
    structured_idea = state["structured_idea"]
    keywords = " ".join(structured_idea.keywords[:3])
    industry = structured_idea.industry

    failure_reasons = search_web(f"{keywords} startup failed why")
    lessons         = search_web(f"{industry} startup graveyard lessons")
    postmortem      = search_web(f"failed {keywords} postmortem")
    summ            = failure_reasons + lessons + postmortem

    response = invoke_structured(DeadStartupList, [
        {"role": "system", "content": "Startup failure analyst."},
        {"role": "user",   "content": (
            f"Search results:\n{summ}\n\n"
            "Extract failed startups from these results. "
            "For each: name, what they did, why they failed, and key lesson."
        )}
    ])

    return {
        "dead_startups": response.startups,
        "agent_logs": ["Graveyard Research — done"],
        "sources": [
            f"{keywords} startup failed why",
            f"{industry} startup graveyard lessons",
            f"failed {keywords} postmortem"
        ]
    }


def user_pain_miner_node(state: OracleState):
    structured_idea = state["structured_idea"]
    keywords = " ".join(structured_idea.keywords[:3])
    user    = structured_idea.target_user
    problem = structured_idea.core_problem

    a = search_web(f"site:reddit.com {problem} complaints")
    b = search_web(f"{user} pain points {keywords}")
    c = search_web(f"{keywords} user frustrations reviews")
    d = a + b + c

    response = invoke_structured(UserPainInsights, [
        {"role": "system", "content": "You are a user insight analyst."},
        {"role": "user",   "content": (
            f"Search results:\n{d}\n\n"
            "Extract user insights: complaints, quotes, willingness to pay, etc."
        )}
    ])

    return {
        "user_pain": response,
        "agent_logs": ["User Insights - generated"],
        "sources": [
            f"site:reddit.com {problem} complaints",
            f"{user} pain points {keywords}",
            f"{keywords} user frustrations reviews"
        ]
    }


def market_sizer_node(state: OracleState):
    idea    = state["structured_idea"]
    signals = state["market_signals"]

    response = invoke_structured(MarketSize, [
        {"role": "system", "content": "You are an ex-McKinsey analyst. Always return real dollar figures like '$4.2B' or '$850M'. Never return placeholder text like 'value' or 'N/A'."},
        {"role": "user",   "content": f"""
Startup idea: {idea.value_proposition}
Target user: {idea.target_user}
Monetization: {idea.monetization_model}
Industry: {idea.industry}

Market signals found:
{signals.overall_demand}
Trend: {signals.trend_direction}

Calculate TAM, SAM, SOM using bottom-up math.
- tam: Total Addressable Market as a dollar figure e.g. "$4.2B"
- sam: Serviceable Addressable Market as a dollar figure e.g. "$850M"
- som: Realistically obtainable in 3 years as a dollar figure e.g. "$12M"
- reasoning: Step by step calculation with actual numbers and assumptions
- confidence: high / medium / low
"""}
    ])

    return {
        "market_size": response,
        "agent_logs": ["Market Size - generated"]
    }


def moat_detector_node(state: OracleState):
    structured_idea = state["structured_idea"]
    user_pain       = state["user_pain"]
    competitors     = state["competitors"]

    try:
        comp_summary = "\n".join([
            f"- {c.name}: strengths={c.strengths}, weaknesses={c.weaknesses}"
            for c in competitors[:5]
        ])
    except Exception:
        comp_summary = "No competitor data available"

    response = invoke_structured(MoatAnalysis, [
        {"role": "system", "content": "You are a competitive strategy expert."},
        {"role": "user",   "content": (
            f"Startup: {structured_idea.value_proposition}, "
            f"Solution: {structured_idea.proposed_solution}, "
            f"Competitors: {comp_summary}, "
            f"User workaround: {user_pain.most_common_workaround}. "
            "Evaluate moat potential — switching costs, network effects, data advantage."
        )}
    ])

    return {
        "moat_analysis": response,
        "agent_logs": ["Moat Detection — done"]
    }


def bull_agent_node(state: OracleState):
    structured_idea = state["structured_idea"]
    market_signals  = state["market_signals"]
    market_size     = state["market_size"]
    user_pain       = state["user_pain"]
    moat_analysis   = state["moat_analysis"]

    response = invoke_structured(BullCase, [
        {"role": "system", "content": "You are a positive financial agent who analyses why things may happen in favour of the particular startup."},
        {"role": "user",   "content": (
            f"problem: {structured_idea.core_problem}, "
            f"solution: {structured_idea.proposed_solution}, "
            f"value proposition: {structured_idea.value_proposition}, "
            f"demand: {market_signals.overall_demand}, "
            f"trend: {market_signals.trend_direction}, "
            f"tam: {market_size.tam}, sam: {market_size.sam}, som: {market_size.som}, "
            f"moats: {moat_analysis.potential_moats}, moat verdict: {moat_analysis.verdict}, "
            f"user complaints: {user_pain.top_complaints}, "
            f"willingness to pay: {user_pain.willingness_to_pay}. "
            "All numeric scores (oracle_score, confidence_score, score_breakdown fields) must be integers 0–100."
        )}
    ])

    return {
        "bull_case": response,
        "agent_logs": ["Bull analysis added"]
    }


def bear_agent_node(state: OracleState):
    competitors     = state["competitors"]
    dead_startup    = state["dead_startups"]
    structured_idea = state["structured_idea"]
    market_signals  = state["market_signals"]
    market_size     = state["market_size"]

    try:
        comp_summary = "\n".join([
            f"- {c.name}: strengths={c.strengths}, weaknesses={c.weaknesses}"
            for c in competitors[:5]
        ])
    except Exception:
        comp_summary = "No competitor data available"

    try:
        dead_startup_summary = "\n".join([
            f"{c.name} did {c.what_they_did} and failed because of {c.why_they_failed}"
            for c in dead_startup
        ])
    except Exception:
        dead_startup_summary = "No dead startup data available"

    response = invoke_structured(BearCase, [
        {"role": "system", "content": "You are a critical bear analyst who finds all the flaws in a startup and why it is bound to fail."},
        {"role": "user",   "content": (
            f"problem: {structured_idea.core_problem}, "
            f"solution: {structured_idea.proposed_solution}, "
            f"value proposition: {structured_idea.value_proposition}, "
            f"demand: {market_signals.overall_demand}, "
            f"trend: {market_signals.trend_direction}, "
            f"tam: {market_size.tam}, sam: {market_size.sam}, som: {market_size.som}, "
            f"competitor strengths/weaknesses: {comp_summary}. "
            f"Failed startups in similar domain: {dead_startup_summary}. "
            "Identify common failure patterns with the current startup. "
            "All numeric scores (oracle_score, confidence_score, score_breakdown fields) must be integers 0–100."
        )}
    ])

    return {
        "bear_case": response,
        "agent_logs": ["Bear analysis added"]
    }


def judge_verdict_node(state: OracleState):
    bear = state["bear_case"]
    bull = state["bull_case"]

    response = invoke_structured(JudgeVerdict, [
        {"role": "system", "content": "You are an experienced VC partner who has seen 1000 pitches. Review both bull and bear arguments and deliver a fair, evidence-based verdict."},
        {"role": "user",   "content": f"Bullish analysis: {bull}\n\nBearish analysis: {bear}\n\nDeliver your verdict."}
    ])

    return {
        "judge_verdict": response,
        "agent_logs": ["Judge verdict added"]
    }


def mvp_plan_node(state: OracleState):
    structured_idea = state["structured_idea"]
    judge_verdict   = state["judge_verdict"]
    user_pain       = state["user_pain"]
    competitor      = state["competitors"]

    try:
        comp_summary = "\n".join([
            f"- {c.name}: strengths={c.strengths}, weaknesses={c.weaknesses}"
            for c in competitor[:5]
        ])
    except Exception:
        comp_summary = "No competitor data available"

    response = invoke_structured(MVPPlan, [
        {"role": "system", "content": "You are a pragmatic CTO who ruthlessly prioritizes things."},
        {"role": "user",   "content": (
            f"Idea: {structured_idea}, "
            f"user pain points: {user_pain.top_complaints}, "
            f"competitor summary: {comp_summary}, "
            f"final verdict: {judge_verdict}"
        )}
    ])

    return {
        "mvp_plan": response,
        "agent_logs": ["MVP plan added"]
    }


def final_report_node(state: OracleState):
    structured_idea = state["structured_idea"]
    market_size     = state["market_size"]
    judge_verdict   = state["judge_verdict"]
    bull_case       = state["bull_case"]
    bear_case       = state["bear_case"]
    moat_analysis   = state["moat_analysis"]
    user_pain       = state["user_pain"]

    response = invoke_structured(OracleReport, [
        {"role": "system", "content": "You are a senior VC partner writing an internal investment memo."},
        {"role": "user",   "content": (
            f"structured idea: {structured_idea}, "
            f"market size: {market_size}, "
            f"verdict: {judge_verdict}, "
            f"bull analysis: {bull_case}, "
            f"bear analysis: {bear_case}, "
            f"moat analysis: {moat_analysis}, "
            f"user pain insights: {user_pain}. "
            "Generate a comprehensive report. "
            "All numeric scores (oracle_score, confidence_score, score_breakdown fields) must be integers 0–100."
        )}
    ])

    return {
        "oracle_report": response,
        "agent_logs": ["Oracle report added"]
    }


def sync_node(state: OracleState) -> dict:
    return {}