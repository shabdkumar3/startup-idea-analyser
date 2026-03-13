from pydantic import BaseModel,Field
from typing import TypedDict, Optional, Annotated, Literal
import operator
class MarketSignal(BaseModel):
    signal:str = Field(description="What is the demand signal?")
    source:str = Field(description="Where was this found?")
    strength:Literal["strong", "medium", "weak"]=Field(description="How strong is this signal?")


class MarketSignals(BaseModel):
    signals:list[MarketSignal] = Field(description="...")
    overall_demand:str  = Field(description="1-2 sentence demand summary")
    search_volume_estimate:str  = Field(description="Estimated monthly search volume")
    trend_direction:Literal["growing", "stable", "declining"] = Field(description="trend direction prediction")
    key_insight:str =Field(description="Single most important market insight")


class StartupIdea(BaseModel):
    target_user :str  = Field(description="Who is the primary user?")
    core_problem :str  = Field(description="What exact problem are they facing?")
    proposed_solution: str = Field(description="How does this startup solve it?")
    industry: str = Field(description="Which industry/vertical?")
    keywords :list[str] = Field(description="5-7 search keywords for research")
    value_proposition: str  =Field(description="One-line value proposition")
    monetization_model: str  = Field(description="How will this make money?")


class Competitor(BaseModel):
    name:str = Field(description="Company Name")
    product_type:str = Field(description="What do they sell")
    pricing:str =Field(description="Pricing Model/range")
    target_user:str= Field(description="who they serve")
    strengths:list[str]=Field(description="Top 3 Stengths")
    weaknesses: list[str]= Field(description="Top 3 weaknesses / gaps")
    funding:str=Field("Unknown",description="Funding Raised")


class DeadStartup(BaseModel):
    name:str = Field(description="Startup Name")
    what_they_did:str = Field(description="What was their idea?")
    why_they_failed:str = Field(description="Root cause of failure")
    lesson:str=Field(description="Key lesson for new founders")
    year_died:str=Field("Unknown",description="Year they shut down")



class DebateArgument(BaseModel):
    argument: str = Field(description="The argument being made")
    evidence: str = Field(description="Evidence supporting the argument")
    strength: Literal["strong", "medium", "weak"] = Field(description="Strength of this argument")


class ScoreBreakdown(BaseModel):
    problem_severity: int = Field(description="Score 0-100")
    market_size: int = Field(description="Score 0-100")
    defensibility: int = Field(description="Score 0-100")
    monetization: int = Field(description="Score 0-100")
    execution_complexity: int = Field(description="Score 0-100")
    founder_fit: int = Field(description="Score 0-100")




class UserPainInsights(BaseModel):
    top_complaints: list[str] = Field(description="Top 5 real user complaints")
    reddit_quotes: list[str] = Field(description="3-5 verbatim quotes from real users")
    willingness_to_pay: str = Field(description="Would they pay? How much?")
    most_common_workaround: str = Field(description="What users currently use instead")
    emotional_intensity: Literal["high", "medium", "low"] = Field(
        description="How strongly users hate this problem"
    )


class MarketSize(BaseModel):
    tam: str = Field(description="Total Addressable Market e.g. '$4.2B'")
    sam: str = Field(description="Serviceable Addressable Market")
    som: str = Field(description="Serviceable Obtainable Market for 3 years")
    reasoning: str = Field(description="Step-by-step calculation logic")
    confidence: Literal["high", "medium", "low"]


class MoatAnalysis(BaseModel):
    potential_moats: list[str] = Field(description="Possible defensibility factors")
    moat_strength: Literal["strong", "medium", "weak", "none"]
    switching_costs: str = Field(description="How hard it is for users to leave")
    network_effects: str = Field(description="Does value grow with more users?")
    data_advantage: str = Field(description="Will the company accumulate unique data?")
    verdict: str = Field(description="One-line moat verdict")


class BullCase(BaseModel):
    main_thesis: str = Field(description="Why this startup will succeed")
    top_arguments: list[DebateArgument]
    confidence_score: int = Field(description="Confidence score 0-100")


class BearCase(BaseModel):
    main_thesis: str = Field(description="Why this startup may fail")
    top_arguments: list[DebateArgument]
    confidence_score: int = Field(description="Confidence score 0-100")
    fatal_flaw: str = Field(description="The biggest killer risk")


class JudgeVerdict(BaseModel):
    verdict: Literal["BUILD IT", "PIVOT", "KILL IT"]
    reasoning: str = Field(description="Why the judge ruled this way")
    bull_wins: list[str] = Field(description="Bull arguments that held up")
    bear_wins: list[str] = Field(description="Bear arguments that held up")
    pivot_suggestion: str = Field(description="If pivot, what exactly to change")
    conditions_to_build: str = Field(description="Conditions required for success")


class MVPPlan(BaseModel):
    must_have_features: list[str]
    nice_to_have_features: list[str]
    must_not_build: list[str]
    tech_stack: list[str]
    timeline_weeks: int
    first_milestone: str
    success_metric: str
    first_100_users_plan: str


class OracleReport(BaseModel):
    oracle_score: int = Field(description="Overall score 0-100")
    score_breakdown: ScoreBreakdown
    verdict: Literal["BUILD IT", "PIVOT", "KILL IT"]
    one_line_summary: str
    positioning_statement: str
    gtm_strategy: str = Field(description="Go-to-market strategy")
    investor_pitch_angle: str
    sources: list[str]

class OracleState(TypedDict):
    raw_idea                    : str
    structured_idea             : Optional[StartupIdea]
    market_signals              : Optional[MarketSignals]
    competitors                 : Optional[list[Competitor]]
    dead_startups               : Optional[list[DeadStartup]]
    user_pain                   : Optional[UserPainInsights]
    market_size                 : Optional[MarketSize]
    moat_analysis               : Optional[MoatAnalysis]
    bull_case                   : Optional[BullCase]
    bear_case                   : Optional[BearCase]
    judge_verdict               : Optional[JudgeVerdict]
    mvp_plan                    : Optional[MVPPlan]
    oracle_report               : Optional[OracleReport]
    agent_logs                  : Annotated[list[str], operator.add]
    sources                     : Annotated[list[str], operator.add]
    competitor_search_attempts  : int


class DeadStartupList(BaseModel):
    startups: list[DeadStartup]

class CompetitorList(BaseModel):
    competitors: list[Competitor]