from langgraph.graph import StateGraph, END, START
from schemas import OracleState
from agents import *

graph = StateGraph(OracleState)

graph.add_node("decompose",  decompose_idea_node)
graph.add_node("competitor", competitor_intel_node)
graph.add_node("research",   market_research_node)
graph.add_node("graveyard",  graveyard_research_node)
graph.add_node("sync",       sync_node)
graph.add_node("user_pain",  user_pain_miner_node)
graph.add_node("market_size",market_sizer_node)
graph.add_node("moat",       moat_detector_node)
graph.add_node("bullish",    bull_agent_node)
graph.add_node("bearish",    bear_agent_node)
graph.add_node("verdict",    judge_verdict_node)
graph.add_node("mvp",        mvp_plan_node)
graph.add_node("report",     final_report_node)

graph.add_edge(START, "decompose")
graph.add_edge("decompose", "research")
graph.add_edge("decompose", "competitor")
graph.add_edge("decompose", "graveyard")

graph.add_conditional_edges(
    "competitor",
    should_search_more,
    {
        "competitor_intel_node":   "competitor",
        "graveyard_research_node": "sync"
    }
)

graph.add_edge("research",  "sync")
graph.add_edge("graveyard", "sync")

graph.add_edge("sync",        "user_pain")
graph.add_edge("user_pain",   "market_size")
graph.add_edge("market_size", "moat")
graph.add_edge("moat",        "bullish")
graph.add_edge("moat",        "bearish")
graph.add_edge("bullish",     "verdict")
graph.add_edge("bearish",     "verdict")
graph.add_edge("verdict",     "mvp")
graph.add_edge("mvp",         "report")
graph.add_edge("report",      END)

app = graph.compile()