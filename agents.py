from schemas import *
from tools import search_web
from langchain_openai import ChatOpenAI
from config import NVIDIA_API_KEY, NVIDIA_BASE_URL, NVIDIA_MODEL
import json, re, queue as _q, threading

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



_progress_queue = _q.Queue()

def _emit(event: str):
    _progress_queue.put(event)

def reset_progress():
    while True:
        try:
            _progress_queue.get_nowait()
        except _q.Empty:
            break

# ── Schema helpers ────────────────────────────────────────────────────────────

def _resolve_refs(obj, defs):
    if isinstance(obj, dict):
        if "$ref" in obj:
            ref_name = obj["$ref"].split("/")[-1]
            return _resolve_refs(defs.get(ref_name, obj), defs)
        return {k: _resolve_refs(v, defs) for k, v in obj.items() if k != "$defs"}
    if isinstance(obj, list):
        return [_resolve_refs(i, defs) for i in obj]
    return obj

def _schema_prompt(schema_class) -> str:
    raw = schema_class.model_json_schema()
    defs = raw.get("$defs", {})
    resolved = _resolve_refs(raw, defs)
    return (
        "You MUST respond with ONLY a valid JSON object — no markdown fences, "
        "no explanation, no extra text. Raw JSON only.\n"
        f"Schema:\n{json.dumps(resolved, indent=2)}"
    )

def _clean_json(text: str) -> str:
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    text = text.strip()
    start = min(
        (text.find(c) for c in ["{", "["] if text.find(c) != -1),
        default=0
    )
    return text[start:]

def _safe_search(query: str) -> str:
    try:
        result = search_web(query)
        if not result or len(result.strip()) < 30:
            return f"No search results found for: {query}. Use your training knowledge."
        return result
    except Exception as e:
        return f"Search failed ({e}). Use your training knowledge to answer."

def invoke_structured(schema_class, messages):
    messages = [dict(m) for m in messages]
    schema_hint = _schema_prompt(schema_class)
    messages[-1]["content"] += f"\n\n{schema_hint}"
    for m in messages:
        if m.get("role") == "system":
            m["content"] += " Always respond with raw JSON only — no markdown, no prose."
            break
    res = model.invoke(messages)
    text = _clean_json(res.content.strip())
    try:
        return schema_class.model_validate(json.loads(text))
    except Exception:
        retry_messages = messages + [
            {"role": "assistant", "content": res.content},
            {"role": "user", "content": (
                "Your response was not valid JSON. Convert it into a valid JSON object "
                f"matching this schema exactly. Raw JSON only, no markdown:\n{schema_hint}"
            )}
        ]
        res2 = model.invoke(retry_messages)
        text2 = _clean_json(res2.content.strip())
        try:
            return schema_class.model_validate(json.loads(text2))
        except Exception as e:
            raise ValueError(
                f"[invoke_structured] Failed after retry for {schema_class.__name__}: {e}\n"
                f"Raw output:\n{text2[:400]}"
            )

# ── Fallback factories ────────────────────────────────────────────────────────

def _fallback_market_signals():
    return MarketSignals(
        signals=[], overall_demand="Market data unavailable.",
        search_volume_estimate="Unknown", trend_direction="stable",
        key_insight="Insufficient data to assess market demand."
    )

def _fallback_user_pain():
    return UserPainInsights(
        top_complaints=["Data unavailable"], reddit_quotes=[],
        willingness_to_pay="Unknown", most_common_workaround="Unknown",
        emotional_intensity="medium"
    )

def _fallback_market_size():
    return MarketSize(tam="N/A", sam="N/A", som="N/A",
        reasoning="Insufficient data.", confidence="low")

def _fallback_moat():
    return MoatAnalysis(
        potential_moats=[], moat_strength="none",
        switching_costs="Unknown", network_effects="Unknown",
        data_advantage="Unknown", verdict="Insufficient data to assess moat."
    )

def _fallback_bull():
    return BullCase(main_thesis="Bull case unavailable.", top_arguments=[], confidence_score=50)

def _fallback_bear():
    return BearCase(main_thesis="Bear case unavailable.", top_arguments=[],
        confidence_score=50, fatal_flaw="Analysis unavailable.")

def _fallback_verdict():
    return JudgeVerdict(
        verdict="PIVOT", reasoning="Insufficient data for a full verdict.",
        bull_wins=[], bear_wins=[],
        pivot_suggestion="Gather more market data before proceeding.",
        conditions_to_build="More research required."
    )

def _fallback_mvp():
    return MVPPlan(
        must_have_features=["Core feature set TBD"], nice_to_have_features=[],
        must_not_build=[], tech_stack=["TBD"], timeline_weeks=12,
        first_milestone="MVP launch", success_metric="User acquisition",
        first_100_users_plan="Direct outreach"
    )

def _fallback_report(verdict_obj=None):
    v = getattr(verdict_obj, "verdict", "PIVOT") if verdict_obj else "PIVOT"
    return OracleReport(
        oracle_score=50, score_breakdown=ScoreBreakdown(), verdict=v,
        one_line_summary="Analysis partially completed due to data limitations.",
        positioning_statement="N/A", gtm_strategy="N/A",
        investor_pitch_angle="N/A", sources=[]
    )

# ── Agents ────────────────────────────────────────────────────────────────────

def decompose_idea_node(state: OracleState) -> dict:
    _emit("START:decompose")
    try:
        result = invoke_structured(StartupIdea, [
            {"role": "system", "content": "You are a sharp startup analyst. Decompose the founder's idea into precise structured components. Be specific — no vague answers."},
            {"role": "user",   "content": f"Startup idea: {state['raw_idea']}"}
        ])
        _emit("DONE:decompose")
        return {"structured_idea": result, "agent_logs": ["Idea Decomposer — done"]}
    except Exception as e:
        _emit("DONE:decompose")
        return {
            "structured_idea": StartupIdea(
                target_user="General users",
                core_problem=state.get("raw_idea", "Unknown"),
                proposed_solution="Unknown", industry="Technology",
                keywords=state.get("raw_idea", "startup").split()[:5],
                value_proposition=state.get("raw_idea", "N/A"),
                monetization_model="Subscription"
            ),
            "agent_logs": [f"Idea Decomposer — fallback ({str(e)[:60]})"]
        }

def market_research_node(state: OracleState):
    _emit("START:research")
    try:
        idea = state.get("structured_idea")
        if not idea:
            _emit("DONE:research")
            return {"market_signals": _fallback_market_signals(), "agent_logs": ["Market Research — skipped"], "sources": []}
        keywords = " ".join((idea.keywords or ["startup"])[:3])
        results = _safe_search(f"{keywords} {idea.industry} market size growth trends 2026")
        response = invoke_structured(MarketSignals, [
            {"role": "system", "content": "You are a market research analyst."},
            {"role": "user",   "content": f"Search results:\n{results}\n\nExtract market signals."}
        ])
        _emit("DONE:research")
        return {
            "market_signals": response,
            "agent_logs": ["Market Research — done"],
            "sources": [f"{keywords} {idea.industry} market size growth trends 2026"]
        }
    except Exception as e:
        _emit("DONE:research")
        return {"market_signals": _fallback_market_signals(),
                "agent_logs": [f"Market Research — fallback ({str(e)[:60]})"], "sources": []}

def competitor_intel_node(state: OracleState):
    _emit("START:competitor")
    try:
        idea = state.get("structured_idea")
        if not idea:
            _emit("DONE:competitor")
            return {"competitors": [], "agent_logs": ["Competitors — skipped"],
                    "competitor_search_attempts": 1, "sources": []}
        keywords = " ".join((idea.keywords or ["startup"])[:3])
        industry = idea.industry or "Technology"
        results = _safe_search(f"{keywords} top competitors startups alternatives {industry}")
        response = invoke_structured(CompetitorList, [
            {"role": "system", "content": "Competitive intelligence analyst."},
            {"role": "user",   "content": (
                f"Search results:\n{results}\n\n"
                "Extract REAL companies that build similar products. "
                "Ignore AI model companies. Only include businesses selling similar products."
            )}
        ])
        attempts = state.get("competitor_search_attempts", 0)
        _emit("DONE:competitor")
        return {
            "competitors": response.competitors,
            "agent_logs": ["Competitors Identified"],
            "competitor_search_attempts": attempts + 1,
            "sources": [f"{keywords} top competitors startups alternatives {industry}"]
        }
    except Exception as e:
        attempts = state.get("competitor_search_attempts", 0)
        _emit("DONE:competitor")
        return {"competitors": [], "agent_logs": [f"Competitor Intel — fallback ({str(e)[:60]})"],
                "competitor_search_attempts": attempts + 1, "sources": []}

def should_search_more(state: OracleState) -> str:
    competitors = state.get("competitors") or []
    attempts = state.get("competitor_search_attempts", 0)
    if len(competitors) < 3 and attempts < 2:
        return "competitor_intel_node"
    return "graveyard_research_node"

def graveyard_research_node(state: OracleState):
    _emit("START:graveyard")
    try:
        idea = state.get("structured_idea")
        if not idea:
            _emit("DONE:graveyard")
            return {"dead_startups": [], "agent_logs": ["Graveyard — skipped"], "sources": []}
        keywords = " ".join((idea.keywords or ["startup"])[:3])
        industry = idea.industry or "Technology"
        summ = _safe_search(f"failed {keywords} {industry} startup graveyard lessons postmortem")
        response = invoke_structured(DeadStartupList, [
            {"role": "system", "content": "Startup failure analyst."},
            {"role": "user",   "content": (
                f"Search results:\n{summ}\n\n"
                "Extract failed startups. For each: name, what they did, why they failed, key lesson."
            )}
        ])
        _emit("DONE:graveyard")
        return {
            "dead_startups": response.startups,
            "agent_logs": ["Graveyard Research — done"],
            "sources": [f"failed {keywords} {industry} startup graveyard lessons postmortem"]
        }
    except Exception as e:
        _emit("DONE:graveyard")
        return {"dead_startups": [], "agent_logs": [f"Graveyard Research — fallback ({str(e)[:60]})"], "sources": []}

def user_pain_miner_node(state: OracleState):
    _emit("START:user_pain")
    try:
        idea = state.get("structured_idea")
        if not idea:
            _emit("DONE:user_pain")
            return {"user_pain": _fallback_user_pain(), "agent_logs": ["User Pain — skipped"], "sources": []}
        keywords = " ".join((idea.keywords or ["startup"])[:3])
        d = _safe_search(f"{idea.target_user} {keywords} complaints pain points frustrations")
        response = invoke_structured(UserPainInsights, [
            {"role": "system", "content": "You are a user insight analyst."},
            {"role": "user",   "content": f"Search results:\n{d}\n\nExtract user insights: complaints, quotes, willingness to pay, etc."}
        ])
        _emit("DONE:user_pain")
        return {
            "user_pain": response,
            "agent_logs": ["User Insights — generated"],
            "sources": [f"{idea.target_user} {keywords} complaints pain points frustrations"]
        }
    except Exception as e:
        _emit("DONE:user_pain")
        return {"user_pain": _fallback_user_pain(),
                "agent_logs": [f"User Pain Miner — fallback ({str(e)[:60]})"], "sources": []}

def market_sizer_node(state: OracleState):
    _emit("START:market_size")
    try:
        idea = state.get("structured_idea")
        signals = state.get("market_signals") or _fallback_market_signals()
        if not idea:
            _emit("DONE:market_size")
            return {"market_size": _fallback_market_size(), "agent_logs": ["Market Sizer — skipped"]}
        response = invoke_structured(MarketSize, [
            {"role": "system", "content": "You are an ex-McKinsey analyst. Always return real dollar figures. Never return placeholder text."},
            {"role": "user",   "content": f"""
Startup idea: {idea.value_proposition}
Target user: {idea.target_user}
Monetization: {idea.monetization_model}
Industry: {idea.industry}
Market signals: {signals.overall_demand}
Trend: {signals.trend_direction}

Calculate TAM, SAM, SOM using bottom-up math.
- tam: Total Addressable Market e.g. "$4.2B"
- sam: Serviceable Addressable Market e.g. "$850M"
- som: Realistically obtainable in 3 years e.g. "$12M"
- reasoning: Step by step calculation
- confidence: high / medium / low
"""}
        ])
        _emit("DONE:market_size")
        return {"market_size": response, "agent_logs": ["Market Size — generated"]}
    except Exception as e:
        _emit("DONE:market_size")
        return {"market_size": _fallback_market_size(),
                "agent_logs": [f"Market Sizer — fallback ({str(e)[:60]})"]}

def moat_detector_node(state: OracleState):
    _emit("START:moat")
    try:
        idea = state.get("structured_idea")
        user_pain = state.get("user_pain") or _fallback_user_pain()
        competitors = state.get("competitors") or []
        if not idea:
            _emit("DONE:moat")
            return {"moat_analysis": _fallback_moat(), "agent_logs": ["Moat Detection — skipped"]}
        try:
            comp_summary = "\n".join([
                f"- {c.name}: strengths={c.strengths}, weaknesses={c.weaknesses}"
                for c in competitors[:5]
            ]) or "No competitor data available"
        except Exception:
            comp_summary = "No competitor data available"
        response = invoke_structured(MoatAnalysis, [
            {"role": "system", "content": "You are a competitive strategy expert."},
            {"role": "user",   "content": (
                f"Startup: {idea.value_proposition}, Solution: {idea.proposed_solution}, "
                f"Competitors: {comp_summary}, User workaround: {user_pain.most_common_workaround}. "
                "Evaluate moat potential — switching costs, network effects, data advantage."
            )}
        ])
        _emit("DONE:moat")
        return {"moat_analysis": response, "agent_logs": ["Moat Detection — done"]}
    except Exception as e:
        _emit("DONE:moat")
        return {"moat_analysis": _fallback_moat(),
                "agent_logs": [f"Moat Detection — fallback ({str(e)[:60]})"]}

def bull_agent_node(state: OracleState):
    _emit("START:bullish")
    try:
        idea = state.get("structured_idea")
        signals = state.get("market_signals") or _fallback_market_signals()
        size = state.get("market_size") or _fallback_market_size()
        pain = state.get("user_pain") or _fallback_user_pain()
        moat = state.get("moat_analysis") or _fallback_moat()
        if not idea:
            _emit("DONE:bullish")
            return {"bull_case": _fallback_bull(), "agent_logs": ["Bull Agent — skipped"]}
        response = invoke_structured(BullCase, [
            {"role": "system", "content": "You are a bull-case analyst finding reasons a startup will succeed."},
            {"role": "user",   "content": (
                f"problem: {idea.core_problem}, solution: {idea.proposed_solution}, "
                f"value prop: {idea.value_proposition}, demand: {signals.overall_demand}, "
                f"trend: {signals.trend_direction}, tam: {size.tam}, sam: {size.sam}, som: {size.som}, "
                f"moats: {moat.potential_moats}, moat verdict: {moat.verdict}, "
                f"user complaints: {pain.top_complaints}, willingness to pay: {pain.willingness_to_pay}. "
                "All numeric scores must be integers 0–100."
            )}
        ])
        _emit("DONE:bullish")
        return {"bull_case": response, "agent_logs": ["Bull analysis added"]}
    except Exception as e:
        _emit("DONE:bullish")
        return {"bull_case": _fallback_bull(), "agent_logs": [f"Bull Agent — fallback ({str(e)[:60]})"]}

def bear_agent_node(state: OracleState):
    _emit("START:bearish")
    try:
        idea = state.get("structured_idea")
        signals = state.get("market_signals") or _fallback_market_signals()
        size = state.get("market_size") or _fallback_market_size()
        competitors = state.get("competitors") or []
        dead = state.get("dead_startups") or []
        if not idea:
            _emit("DONE:bearish")
            return {"bear_case": _fallback_bear(), "agent_logs": ["Bear Agent — skipped"]}
        try:
            comp_summary = "\n".join([
                f"- {c.name}: strengths={c.strengths}, weaknesses={c.weaknesses}"
                for c in competitors[:5]
            ]) or "No competitor data"
        except Exception:
            comp_summary = "No competitor data"
        try:
            dead_summary = "\n".join([
                f"{c.name} did {c.what_they_did} and failed because {c.why_they_failed}"
                for c in dead
            ]) or "No dead startup data"
        except Exception:
            dead_summary = "No dead startup data"
        response = invoke_structured(BearCase, [
            {"role": "system", "content": "You are a bear-case analyst finding all the flaws in a startup."},
            {"role": "user",   "content": (
                f"problem: {idea.core_problem}, solution: {idea.proposed_solution}, "
                f"value prop: {idea.value_proposition}, demand: {signals.overall_demand}, "
                f"trend: {signals.trend_direction}, tam: {size.tam}, sam: {size.sam}, som: {size.som}, "
                f"competitor strengths/weaknesses: {comp_summary}. "
                f"Failed startups in similar domain: {dead_summary}. "
                "All numeric scores must be integers 0–100."
            )}
        ])
        _emit("DONE:bearish")
        return {"bear_case": response, "agent_logs": ["Bear analysis added"]}
    except Exception as e:
        _emit("DONE:bearish")
        return {"bear_case": _fallback_bear(), "agent_logs": [f"Bear Agent — fallback ({str(e)[:60]})"]}

def judge_verdict_node(state: OracleState):
    _emit("START:verdict")
    try:
        bull = state.get("bull_case") or _fallback_bull()
        bear = state.get("bear_case") or _fallback_bear()
        response = invoke_structured(JudgeVerdict, [
            {"role": "system", "content": "You are an experienced VC partner who has seen 1000 pitches. Deliver a fair, evidence-based verdict."},
            {"role": "user",   "content": f"Bullish analysis: {bull}\n\nBearish analysis: {bear}\n\nDeliver your verdict."}
        ])
        _emit("DONE:verdict")
        return {"judge_verdict": response, "agent_logs": ["Judge verdict added"]}
    except Exception as e:
        _emit("DONE:verdict")
        return {"judge_verdict": _fallback_verdict(), "agent_logs": [f"Judge Verdict — fallback ({str(e)[:60]})"]}

def mvp_plan_node(state: OracleState):
    _emit("START:mvp")
    try:
        idea = state.get("structured_idea")
        pain = state.get("user_pain") or _fallback_user_pain()
        verdict = state.get("judge_verdict") or _fallback_verdict()
        competitors = state.get("competitors") or []
        if not idea:
            _emit("DONE:mvp")
            return {"mvp_plan": _fallback_mvp(), "agent_logs": ["MVP Plan — skipped"]}
        try:
            comp_summary = "\n".join([
                f"- {c.name}: strengths={c.strengths}, weaknesses={c.weaknesses}"
                for c in competitors[:5]
            ]) or "No competitor data"
        except Exception:
            comp_summary = "No competitor data"
        response = invoke_structured(MVPPlan, [
            {"role": "system", "content": "You are a pragmatic CTO who ruthlessly prioritizes."},
            {"role": "user",   "content": (
                f"Idea: {idea}, user pain points: {pain.top_complaints}, "
                f"competitor summary: {comp_summary}, final verdict: {verdict}"
            )}
        ])
        _emit("DONE:mvp")
        return {"mvp_plan": response, "agent_logs": ["MVP plan added"]}
    except Exception as e:
        _emit("DONE:mvp")
        return {"mvp_plan": _fallback_mvp(), "agent_logs": [f"MVP Plan — fallback ({str(e)[:60]})"]}

def final_report_node(state: OracleState):
    _emit("START:report")
    try:
        response = invoke_structured(OracleReport, [
            {"role": "system", "content": "You are a senior VC partner writing an internal investment memo."},
            {"role": "user",   "content": (
                f"structured idea: {state.get('structured_idea')}, "
                f"market size: {state.get('market_size') or _fallback_market_size()}, "
                f"verdict: {state.get('judge_verdict') or _fallback_verdict()}, "
                f"bull analysis: {state.get('bull_case') or _fallback_bull()}, "
                f"bear analysis: {state.get('bear_case') or _fallback_bear()}, "
                f"moat analysis: {state.get('moat_analysis') or _fallback_moat()}, "
                f"user pain insights: {state.get('user_pain') or _fallback_user_pain()}. "
                "Generate a comprehensive report. All numeric scores must be integers 0–100."
            )}
        ])
        _emit("DONE:report")
        return {"oracle_report": response, "agent_logs": ["Oracle report added"]}
    except Exception as e:
        _emit("DONE:report")
        return {"oracle_report": _fallback_report(state.get("judge_verdict")),
                "agent_logs": [f"Final Report — fallback ({str(e)[:60]})"]}

def sync_node(state: OracleState) -> dict:
    return {}