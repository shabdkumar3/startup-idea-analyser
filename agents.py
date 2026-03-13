from schemas import *
from tools import search_web
from langchain_openai import ChatOpenAI
from config import NVIDIA_API_KEY, NVIDIA_BASE_URL, NVIDIA_MODEL

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
def decompose_idea_node(state: OracleState) -> dict:
        raw_idea = state["raw_idea"]   
        
        result = model.with_structured_output(StartupIdea).invoke([
            {"role": "system", "content": "You are a sharp startup analyst. Decompose the founder's idea into precise structured components. Be specific — no vague answers."},
            {"role": "user",   "content": f"Startup idea: {raw_idea}"}
        ])
        
        return {
            "structured_idea": result,                          
            "agent_logs": ["Idea Decomposer — done"]         
        }
def market_research_node(state: OracleState):
    structured_idea= state["structured_idea"]
    keywords = " ".join(structured_idea.keywords[:3])
    market_size= search_web(f"{keywords} market size 2026")
    growth_trend= search_web(f"{keywords} industry growth trends")
    demand = search_web(f"{structured_idea.industry} market demand")
    results = market_size+growth_trend+demand
    response= model.with_structured_output(MarketSignals).invoke([
    {"role": "system", "content": "You are a market research analyst"},
    {"role": "user",   "content": f"Search results:\n{results}\n\nExtract market signals."}
])
    return{
        "market_signals": response,
        "agent_logs": ["Market Research — done"],        
        "sources": [keywords,structured_idea.industry ]    
    }

def competitor_intel_node(state: OracleState):
    structured_idea= state["structured_idea"]
    keywords = " ".join(structured_idea.keywords[:3])
    industry= structured_idea.industry
    top_startups= search_web(f"{keywords} top startups 2026")
    competitor_alternatives= search_web(f"{keywords} competitors alternatives")
    top_companies=search_web(f"best {industry} companies")
    competitors= top_companies+top_startups+competitor_alternatives
    response= model.with_structured_output(CompetitorList).invoke(
        [
            {"role": "system", "content": "Competitive intelligence analyst."},
            {"role": "user",   "content": f"Search results:\n{competitors}\n\nExtract REAL companies that build similar products.Rules:- Ignore AI model companies- Ignore unrelated tech companies- Only include businesses selling similar products ."}
        ]
    )
    attempts = state.get("competitor_search_attempts", 0)
    return {
        "competitors": response.competitors,
        "agent_logs":["Competitors Identified"],
        "competitor_search_attempts": attempts + 1,
        "sources": [f"{keywords} top startups 2026", f"{keywords} competitors alternatives", f"best {industry} companies"]
    }
def should_search_more(state: OracleState) -> str:
    competitors = state.get("competitors") or []
    attempts    = state.get("competitor_search_attempts", 0)
    
    if len(competitors) < 3 and attempts < 2:
        return "competitor_intel_node"   
    return "graveyard_research_node"     

def graveyard_research_node(state:OracleState):
    structured_idea= state["structured_idea"]
    keywords = " ".join(structured_idea.keywords[:3])
    industry= structured_idea.industry
    failure_reasons= search_web(f"{keywords} startup failed why")
    lessons=search_web(f"{industry} startup graveyard lessons")
    postmortem= search_web(f"failed {keywords} postmortem")
    summ= failure_reasons+lessons+postmortem
    response= model.with_structured_output(DeadStartupList).invoke(
        [
            {"role": "system", "content": "startup failure analyst"},
            {"role": "user",   "content": f"Search results:\n{summ}\n\nExtract failed startups from these results. For each: name, what they did, why they failed, and key lesson."}
        ]
    )
    return {
    "dead_startups": response.startups,
    "agent_logs": ["Graveyard Research — done"],
    "sources": [f"{keywords} startup failed why", f"{industry} startup graveyard lessons", f"failed {keywords} postmortem"]
}

def user_pain_miner_node(state:OracleState):
    structured_idea= state["structured_idea"]
    keywords = " ".join(structured_idea.keywords[:3])
    user= structured_idea.target_user
    problem= structured_idea.core_problem
    a=search_web(f"site:reddit.com {problem} complaints")
    b=search_web(f"{user} pain points {keywords}")
    c=search_web(f"{keywords} user frustrations reviews")
    d=a+b+c
    e= model.with_structured_output(UserPainInsights).invoke([
            {"role": "system", "content": "you are a user insight analyst"},
            {"role": "user",   "content": f"Search results:\n{d}\n\nExtract user insights from these , tell about complaints, quotes, willing to pay etc"}
        ])
    return{
        "user_pain":e,
        "agent_logs":["User Insights - generated"],
        "sources": [
    f"site:reddit.com {problem} complaints",
    f"{user} pain points {keywords}",
    f"{keywords} user frustrations reviews"
]
    }

def market_sizer_node(state:OracleState):
    idea= state["structured_idea"]
    signals= state["market_signals"]
    response = model.with_structured_output(MarketSize).invoke([
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
        ]
         
    )
    return {
        "market_size" :  response,
        "agent_logs" : ["Market Size - genearted"]
    }


def moat_detector_node(state:OracleState):
    structured_idea= state["structured_idea"]
    user_pain=state["user_pain"]
    competitors=state["competitors"]
    try:
        comp_summary = "\n".join([
        f"- {c.name}: strengths={c.strengths}, weaknesses={c.weaknesses}"
        for c in competitors[:5]
    ])
    except:
        comp_summary = "No competitor data available" 
        

    response= model.with_structured_output(MoatAnalysis).invoke(
        [{"role":"system", "content":"you are a competitive strategy expert"},
         {"role":"user", "content":f"Startup: {structured_idea.value_proposition}, Solution: {structured_idea.proposed_solution},Competitors:{comp_summary} and User workaround: {user_pain.most_common_workaround} . Now Evaluate moat potential — switching costs, network effects, data advantage."}])
    
    return {
    "moat_analysis": response,
    "agent_logs": ["Moat Detection — done"]
}

def bull_agent_node(state:OracleState):
    structured_idea= state["structured_idea"]
    market_signals= state["market_signals"]
    market_size= state["market_size"]
    user_pain= state["user_pain"]
    moat_analysis =state["moat_analysis"] 
    response = model.with_structured_output(BullCase).invoke([
        {"role":"system", "content":"you are a postive financial agent, you analyse on why things may happen in the favpur of the particular startup"},
        {"role":"user","content":f"you have the follwing paramenters : problem : {structured_idea.core_problem}, solution:{structured_idea.proposed_solution}, value proposition:{structured_idea.value_proposition},demand : {market_signals.overall_demand}, trend: {market_signals.trend_direction}, tam :{market_size.tam}, sam :{market_size.sam}, som : {market_size.som}, moats :{moat_analysis.potential_moats}, moat verdict:{moat_analysis.verdict}, now see how user complaints as {user_pain.top_complaints} and their willingnesss to pay {user_pain.willingness_to_pay} may help in growth of the startup. All numeric scores (oracle_score, confidence_score, score_breakdown fields) must be integers from 0 to 100. "}
    ])
    return {
        "bull_case": response,
        "agent_logs":["Bull analysis added"]
    }

def bear_agent_node(state:OracleState):
    competitors= state["competitors"]
    dead_startup = state["dead_startups"]
    structured_idea= state["structured_idea"]
    market_signals= state["market_signals"]
    market_size= state["market_size"]
    try:
        comp_summary = "\n".join([
        f"- {c.name}: strengths={c.strengths}, weaknesses={c.weaknesses}"
        for c in competitors[:5]
    ])
    except:
        comp_summary = "No competitor data available" 
    try:
        dead_startup_summary = "\n".join([
        f"{c.name} did {c.what_they_did} and failed beacuse of {c.why_they_failed}" for c in dead_startup
        ])
    except:
        dead_startup_summary =" No dead starup data available"
    resposne = model.with_structured_output(BearCase).invoke([
        {"role":"system", "content" :" you are a critical bear analyset who finds all the flws ina startup and how they cant survive and are bound to fail"},
        {"role":"user", "content": f"you have the follwing paramenters : problem : {structured_idea.core_problem}, solution:{structured_idea.proposed_solution}, value proposition:{structured_idea.value_proposition},demand : {market_signals.overall_demand}, trend: {market_signals.trend_direction}, tam :{market_size.tam}, sam :{market_size.sam}, som : {market_size.som}, now you have the main festures as strength and weakness  of  competitors but you have to focus more on strengths : {comp_summary}. now reflecting on how startup in similar domain have failed anaylse {dead_startup_summary} and identify things common between dead startups and current soltuion in order to evalute why cureent startup will also fail, All numeric scores (oracle_score, confidence_score, score_breakdown fields) must be integers from 0 to 100."}
    ]
    )

    return{
        "bear_case":resposne,
        "agent_logs":["Bear analysis added"]
    }

def judge_verdict_node(state:OracleState):
    bear = state["bear_case"]
    bull = state["bull_case"]
    response= model.with_structured_output(JudgeVerdict).invoke([
        {"role": "system", "content": "You are an experienced VC partner who has seen 1000 pitches. Review both bull and bear arguments and deliver a fair, evidence-based verdict."},
        {"role":"user", "content":f"analyse both the bullish :{bull} and bearish:{bear} insighnts and based on them , tell your verdict"}
    ])
    return {
        "judge_verdict": response,
        "agent_logs" : ["Judge verdict added"]
    }



def mvp_plan_node(state:OracleState):
    structured_idea= state["structured_idea"]
    judge_verdict= state["judge_verdict"]
    user_pain= state["user_pain"]
    competitor= state["competitors"]
    try:
        comp_summary = "\n".join([
        f"- {c.name}: strengths={c.strengths}, weaknesses={c.weaknesses}"
        for c in competitor[:5]
    ])
    except:
        comp_summary = "No competitor data available" 
    response = model.with_structured_output(MVPPlan).invoke(
        [
            {"role": "system", "content" : "you are a pragmatic CTO who ruthlessly prioritizes things" },
            {"role":"user", "content" : f" so you have the idea as {structured_idea}, you have user pain points: {user_pain.top_complaints}, compititor summary :{comp_summary}, final verdict :{judge_verdict}"}
        ]
    )
    return {
        "mvp_plan": response,
        "agent_logs": ["MVP plan added"]
    }

def final_report_node(state:OracleState):
    structured_idea= state["structured_idea"]
    market_size= state["market_size"]
    judge_verdict=state["judge_verdict"]
    bull_case= state["bull_case"]
    bear_case=state["bear_case"]
    moat_analysis = state ["moat_analysis"]
    user_pain=state["user_pain"]
    response= model.with_structured_output(OracleReport).invoke([{"role":"system","content":"you are a senior VC partner writing internal investment memo"},{"role":"user", "content":f"you are given all the data as structured idea= {structured_idea} , market size :{market_size}, verdict:{judge_verdict}, bull analysis : {bull_case}, bear analysis :{bear_case}, moat analysis :{moat_analysis}, user pain insights :{user_pain}. Now generate a report based on this. All numeric scores (oracle_score, confidence_score, score_breakdown fields) must be integers from 0 to 100."}])
    return {
        "oracle_report": response,
        "agent_logs":["Oracle report added"]
    }

def sync_node(state: OracleState) -> dict:
    return {}