from pydantic import BaseModel, Field, field_validator
from typing import TypedDict, Optional, Annotated, Literal
import operator, re

def _norm_lower(v, options, default):
    if not isinstance(v, str):
        return default
    v = v.strip().lower()
    if v in options:
        return v
    for o in options:
        if o in v or v in o:
            return o
    return default

def _norm_upper_verdict(v):
    if not isinstance(v, str):
        return "PIVOT"
    v = v.strip().upper()
    if "BUILD" in v:
        return "BUILD IT"
    if "KILL" in v or "DEAD" in v or "DIE" in v:
        return "KILL IT"
    if "PIVOT" in v:
        return "PIVOT"
    return "PIVOT"

def _coerce_score(v):
    if isinstance(v, bool):
        return 50
    if isinstance(v, (int, float)):
        return max(0, min(100, int(v)))
    if isinstance(v, str):
        m = re.search(r'\d+', v)
        if m:
            return max(0, min(100, int(m.group())))
    return 50


class MarketSignal(BaseModel):
    signal: str = Field("N/A", description="What is the demand signal?")
    source: str = Field("N/A", description="Where was this found?")
    strength: Literal["strong", "medium", "weak"] = Field("medium", description="How strong is this signal?")

    @field_validator("strength", mode="before")
    @classmethod
    def norm_strength(cls, v):
        return _norm_lower(v, ["strong", "medium", "weak"], "medium")


class MarketSignals(BaseModel):
    signals: list[MarketSignal] = Field(default_factory=list, description="...")
    overall_demand: str = Field("Unknown", description="1-2 sentence demand summary")
    search_volume_estimate: str = Field("Unknown", description="Estimated monthly search volume")
    trend_direction: Literal["growing", "stable", "declining"] = Field("stable", description="trend direction")
    key_insight: str = Field("Insufficient data", description="Single most important market insight")

    @field_validator("trend_direction", mode="before")
    @classmethod
    def norm_trend(cls, v):
        if not isinstance(v, str):
            return "stable"
        v = v.strip().lower()
        if v in ["growing", "stable", "declining"]:
            return v
        if any(w in v for w in ["grow", "increas", "up", "ris"]):
            return "growing"
        if any(w in v for w in ["declin", "decreas", "down", "fall", "shrink"]):
            return "declining"
        return "stable"

    @field_validator("signals", mode="before")
    @classmethod
    def coerce_signals_list(cls, v):
        if isinstance(v, dict):
            return [v]
        return v if isinstance(v, list) else []


class StartupIdea(BaseModel):
    target_user: str = Field("General users", description="Who is the primary user?")
    core_problem: str = Field("Unknown problem", description="What exact problem are they facing?")
    proposed_solution: str = Field("Unknown solution", description="How does this startup solve it?")
    industry: str = Field("Technology", description="Which industry/vertical?")
    keywords: list[str] = Field(default_factory=list, description="5-7 search keywords for research")
    value_proposition: str = Field("N/A", description="One-line value proposition")
    monetization_model: str = Field("Subscription", description="How will this make money?")

    @field_validator("keywords", mode="before")
    @classmethod
    def coerce_keywords(cls, v):
        if isinstance(v, str):
            return [v]
        return v if isinstance(v, list) else []


class Competitor(BaseModel):
    name: str = Field("Unknown", description="Company Name")
    product_type: str = Field("Unknown", description="What do they sell")
    pricing: str = Field("Unknown", description="Pricing Model/range")
    target_user: str = Field("Unknown", description="who they serve")
    strengths: list[str] = Field(default_factory=list, description="Top 3 Strengths")
    weaknesses: list[str] = Field(default_factory=list, description="Top 3 weaknesses / gaps")
    funding: str = Field("Unknown", description="Funding Raised")

    @field_validator("strengths", "weaknesses", mode="before")
    @classmethod
    def coerce_str_list(cls, v):
        if isinstance(v, str):
            return [v]
        return v if isinstance(v, list) else []


class DeadStartup(BaseModel):
    name: str = Field("Unknown", description="Startup Name")
    what_they_did: str = Field("Unknown", description="What was their idea?")
    why_they_failed: str = Field("Unknown", description="Root cause of failure")
    lesson: str = Field("Unknown", description="Key lesson for new founders")
    year_died: str = Field("Unknown", description="Year they shut down")


class DebateArgument(BaseModel):
    argument: str = Field("N/A", description="The argument being made")
    evidence: str = Field("N/A", description="Evidence supporting the argument")
    strength: Literal["strong", "medium", "weak"] = Field("medium", description="Strength of this argument")

    @field_validator("strength", mode="before")
    @classmethod
    def norm_strength(cls, v):
        return _norm_lower(v, ["strong", "medium", "weak"], "medium")


class ScoreBreakdown(BaseModel):
    problem_severity: int = Field(50, description="Score 0-100")
    market_size: int = Field(50, description="Score 0-100")
    defensibility: int = Field(50, description="Score 0-100")
    monetization: int = Field(50, description="Score 0-100")
    execution_complexity: int = Field(50, description="Score 0-100")
    founder_fit: int = Field(50, description="Score 0-100")

    @field_validator("problem_severity", "market_size", "defensibility",
                     "monetization", "execution_complexity", "founder_fit", mode="before")
    @classmethod
    def coerce_score(cls, v):
        return _coerce_score(v)


class UserPainInsights(BaseModel):
    top_complaints: list[str] = Field(default_factory=list, description="Top 5 real user complaints")
    reddit_quotes: list[str] = Field(default_factory=list, description="3-5 verbatim quotes from real users")
    willingness_to_pay: str = Field("Unknown", description="Would they pay? How much?")
    most_common_workaround: str = Field("Unknown", description="What users currently use instead")
    emotional_intensity: Literal["high", "medium", "low"] = Field("medium", description="How strongly users hate this problem")

    @field_validator("emotional_intensity", mode="before")
    @classmethod
    def norm_intensity(cls, v):
        return _norm_lower(v, ["high", "medium", "low"], "medium")

    @field_validator("top_complaints", "reddit_quotes", mode="before")
    @classmethod
    def coerce_str_list(cls, v):
        if isinstance(v, str):
            return [v]
        return v if isinstance(v, list) else []


class MarketSize(BaseModel):
    tam: str = Field("N/A", description="Total Addressable Market e.g. '$4.2B'")
    sam: str = Field("N/A", description="Serviceable Addressable Market")
    som: str = Field("N/A", description="Serviceable Obtainable Market for 3 years")
    reasoning: str = Field("N/A", description="Step-by-step calculation logic")
    confidence: Literal["high", "medium", "low"] = Field("low")

    @field_validator("confidence", mode="before")
    @classmethod
    def norm_confidence(cls, v):
        return _norm_lower(v, ["high", "medium", "low"], "low")


class MoatAnalysis(BaseModel):
    potential_moats: list[str] = Field(default_factory=list, description="Possible defensibility factors")
    moat_strength: Literal["strong", "medium", "weak", "none"] = Field("none")
    switching_costs: str = Field("Unknown", description="How hard it is for users to leave")
    network_effects: str = Field("Unknown", description="Does value grow with more users?")
    data_advantage: str = Field("Unknown", description="Will the company accumulate unique data?")
    verdict: str = Field("Insufficient data", description="One-line moat verdict")

    @field_validator("moat_strength", mode="before")
    @classmethod
    def norm_moat(cls, v):
        return _norm_lower(v, ["strong", "medium", "weak", "none"], "none")

    @field_validator("potential_moats", mode="before")
    @classmethod
    def coerce_moats_list(cls, v):
        if isinstance(v, str):
            return [v]
        return v if isinstance(v, list) else []


class BullCase(BaseModel):
    main_thesis: str = Field("N/A", description="Why this startup will succeed")
    top_arguments: list[DebateArgument] = Field(default_factory=list)
    confidence_score: int = Field(50, description="Confidence score 0-100")

    @field_validator("confidence_score", mode="before")
    @classmethod
    def coerce_score(cls, v):
        return _coerce_score(v)

    @field_validator("top_arguments", mode="before")
    @classmethod
    def coerce_args_list(cls, v):
        if isinstance(v, dict):
            return [v]
        return v if isinstance(v, list) else []


class BearCase(BaseModel):
    main_thesis: str = Field("N/A", description="Why this startup may fail")
    top_arguments: list[DebateArgument] = Field(default_factory=list)
    confidence_score: int = Field(50, description="Confidence score 0-100")
    fatal_flaw: str = Field("N/A", description="The biggest killer risk")

    @field_validator("confidence_score", mode="before")
    @classmethod
    def coerce_score(cls, v):
        return _coerce_score(v)

    @field_validator("top_arguments", mode="before")
    @classmethod
    def coerce_args_list(cls, v):
        if isinstance(v, dict):
            return [v]
        return v if isinstance(v, list) else []


class JudgeVerdict(BaseModel):
    verdict: Literal["BUILD IT", "PIVOT", "KILL IT"] = Field("PIVOT")
    reasoning: str = Field("N/A", description="Why the judge ruled this way")
    bull_wins: list[str] = Field(default_factory=list)
    bear_wins: list[str] = Field(default_factory=list)
    pivot_suggestion: str = Field("N/A", description="If pivot, what exactly to change")
    conditions_to_build: str = Field("N/A", description="Conditions required for success")

    @field_validator("verdict", mode="before")
    @classmethod
    def norm_verdict(cls, v):
        return _norm_upper_verdict(v)

    @field_validator("bull_wins", "bear_wins", mode="before")
    @classmethod
    def coerce_str_list(cls, v):
        if isinstance(v, str):
            return [v]
        return v if isinstance(v, list) else []


class MVPPlan(BaseModel):
    must_have_features: list[str] = Field(default_factory=list)
    nice_to_have_features: list[str] = Field(default_factory=list)
    must_not_build: list[str] = Field(default_factory=list)
    tech_stack: list[str] = Field(default_factory=list)
    timeline_weeks: int = Field(12)
    first_milestone: str = Field("N/A")
    success_metric: str = Field("N/A")
    first_100_users_plan: str = Field("N/A")

    @field_validator("timeline_weeks", mode="before")
    @classmethod
    def coerce_timeline(cls, v):
        if isinstance(v, (int, float)):
            return max(1, int(v))
        if isinstance(v, str):
            m = re.search(r'\d+', v)
            if m:
                return max(1, int(m.group()))
        return 12

    @field_validator("must_have_features", "nice_to_have_features",
                     "must_not_build", "tech_stack", mode="before")
    @classmethod
    def coerce_str_list(cls, v):
        if isinstance(v, str):
            return [v]
        return v if isinstance(v, list) else []


class OracleReport(BaseModel):
    oracle_score: int = Field(50, description="Overall score 0-100")
    score_breakdown: ScoreBreakdown = Field(default_factory=ScoreBreakdown)
    verdict: Literal["BUILD IT", "PIVOT", "KILL IT"] = Field("PIVOT")
    one_line_summary: str = Field("N/A")
    positioning_statement: str = Field("N/A")
    gtm_strategy: str = Field("N/A", description="Go-to-market strategy")
    investor_pitch_angle: str = Field("N/A")
    sources: list[str] = Field(default_factory=list)

    @field_validator("oracle_score", mode="before")
    @classmethod
    def coerce_score(cls, v):
        return _coerce_score(v)

    @field_validator("verdict", mode="before")
    @classmethod
    def norm_verdict(cls, v):
        return _norm_upper_verdict(v)

    @field_validator("sources", mode="before")
    @classmethod
    def coerce_str_list(cls, v):
        if isinstance(v, str):
            return [v]
        return v if isinstance(v, list) else []

    @field_validator("score_breakdown", mode="before")
    @classmethod
    def coerce_breakdown(cls, v):
        if v is None:
            return ScoreBreakdown()
        return v


class OracleState(TypedDict):
    raw_idea: str
    structured_idea: Optional[StartupIdea]
    market_signals: Optional[MarketSignals]
    competitors: Optional[list[Competitor]]
    dead_startups: Optional[list[DeadStartup]]
    user_pain: Optional[UserPainInsights]
    market_size: Optional[MarketSize]
    moat_analysis: Optional[MoatAnalysis]
    bull_case: Optional[BullCase]
    bear_case: Optional[BearCase]
    judge_verdict: Optional[JudgeVerdict]
    mvp_plan: Optional[MVPPlan]
    oracle_report: Optional[OracleReport]
    agent_logs: Annotated[list[str], operator.add]
    sources: Annotated[list[str], operator.add]
    competitor_search_attempts: int


class DeadStartupList(BaseModel):
    startups: list[DeadStartup] = Field(default_factory=list)

    @field_validator("startups", mode="before")
    @classmethod
    def coerce_list(cls, v):
        if isinstance(v, dict):
            return [v]
        return v if isinstance(v, list) else []


class CompetitorList(BaseModel):
    competitors: list[Competitor] = Field(default_factory=list)

    @field_validator("competitors", mode="before")
    @classmethod
    def coerce_list(cls, v):
        if isinstance(v, dict):
            return [v]
        return v if isinstance(v, list) else []