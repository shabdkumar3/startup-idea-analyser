from graph import app
import streamlit as st

st.set_page_config(page_title="Startup Oracle", page_icon="🔮", layout="wide")


#  GLOBAL CSS

st.markdown("""
<style>
body { font-family: 'Inter', sans-serif; }

.stat-card {
    background: #1a1a2e; border: 1px solid #2d2d4e;
    border-radius: 14px; padding: 20px 24px; margin-bottom: 12px;
}
.stat-card .label { font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
.stat-card .value { font-size: 28px; font-weight: 700; color: #fff; word-break: break-word; }
.stat-card .sub   { font-size: 13px; color: #aaa; margin-top: 6px; }

.score-big {
    font-size: 64px; font-weight: 800; line-height: 1;
    background: linear-gradient(135deg, #a78bfa, #60a5fa);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.verdict-badge {
    display: inline-block; padding: 10px 28px; border-radius: 50px;
    font-size: 20px; font-weight: 800; letter-spacing: 2px; margin-top: 8px;
}
.verdict-build { background: linear-gradient(135deg,#065f46,#10b981); color:#d1fae5; }
.verdict-pivot { background: linear-gradient(135deg,#78350f,#f59e0b); color:#fef3c7; }
.verdict-kill  { background: linear-gradient(135deg,#7f1d1d,#ef4444); color:#fee2e2; }

.score-row { margin-bottom: 14px; }
.score-row .score-label { display:flex; justify-content:space-between; font-size:13px; color:#ccc; margin-bottom:5px; }
.score-bar-bg   { background:#2d2d4e; border-radius:6px; height:10px; overflow:hidden; }
.score-bar-fill { height:10px; border-radius:6px; transition:width 0.6s ease; }

.info-card { background:#0f172a; border:1px solid #1e293b; border-radius:12px; padding:18px 20px; margin-bottom:10px; }
.info-card h4 { color:#94a3b8; font-size:11px; text-transform:uppercase; letter-spacing:1.2px; margin:0 0 8px 0; }
.info-card p  { color:#f1f5f9; font-size:17px; font-weight:600; margin:0; word-break:break-word; }

.comp-card { background:#111827; border:1px solid #1f2937; border-radius:14px; padding:20px; margin-bottom:14px; }
.comp-card .comp-name { font-size:18px; font-weight:700; color:#f9fafb; }
.comp-card .comp-type { font-size:13px; color:#6b7280; margin-bottom:12px; }
.comp-card .meta-row  { display:flex; gap:20px; flex-wrap:wrap; margin-bottom:12px; }
.comp-card .meta-item { font-size:13px; color:#9ca3af; }
.comp-card .meta-item span { color:#e5e7eb; font-weight:500; }
.pill-green { background:#064e3b; color:#6ee7b7; border-radius:6px; padding:3px 10px; font-size:12px; display:inline-block; margin:3px; }
.pill-red   { background:#450a0a; color:#fca5a5; border-radius:6px; padding:3px 10px; font-size:12px; display:inline-block; margin:3px; }

.grave-card { background:#1c1917; border-left:4px solid #dc2626; border-radius:10px; padding:18px 20px; margin-bottom:14px; }
.grave-card .grave-name { font-size:17px; font-weight:700; color:#fef2f2; }
.grave-card .grave-year { font-size:12px; color:#9ca3af; }
.grave-why    { background:#2d1515; border-radius:8px; padding:10px 14px; margin:10px 0; color:#fca5a5; font-size:14px; }
.grave-lesson { background:#14291f; border-radius:8px; padding:10px 14px; color:#6ee7b7; font-size:14px; }

.quote-card { background:#1e1b4b; border-left:4px solid #818cf8; border-radius:10px; padding:14px 18px; margin-bottom:10px; font-style:italic; color:#c7d2fe; font-size:15px; word-break:break-word; }

.complaint-row { display:flex; align-items:flex-start; gap:12px; padding:12px 16px; background:#1f1f1f; border-radius:10px; margin-bottom:8px; color:#e5e7eb; font-size:14px; }
.complaint-num { background:#374151; color:#9ca3af; border-radius:50%; width:26px; height:26px; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:700; flex-shrink:0; }

.insight-card { background:#1a1a2e; border-radius:12px; padding:20px; text-align:center; margin-top:10px; }
.insight-card .ic-label { font-size:11px; color:#888; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px; }
.insight-card .ic-val   { font-size:15px; color:#e2e8f0; font-weight:600; word-break:break-word; line-height:1.5; }

.debate-bull { background:#052e16; border:1px solid #15803d; border-radius:14px; padding:20px; height:100%; }
.debate-bear { background:#2d0000; border:1px solid #991b1b; border-radius:14px; padding:20px; height:100%; }
.debate-title  { font-size:20px; font-weight:800; margin-bottom:6px; }
.debate-thesis { font-size:14px; color:#d1fae5; margin-bottom:14px; font-style:italic; }
.debate-bear .debate-thesis { color:#fecaca; }
.arg-row { padding:10px 0; border-bottom:1px solid rgba(255,255,255,0.06); }
.arg-row:last-child { border:none; }
.arg-text { font-size:14px; color:#f1f5f9; font-weight:600; margin-bottom:3px; }
.arg-ev   { font-size:12px; color:#94a3b8; }
.strength-badge { font-size:11px; padding:2px 8px; border-radius:20px; display:inline-block; margin-left:6px; }
.str-strong { background:#1e3a2f; color:#6ee7b7; }
.str-medium { background:#2e2a15; color:#fde68a; }
.str-weak   { background:#2d1515; color:#fca5a5; }
.fatal-box  { background:#4c0519; border:1px solid #9f1239; border-radius:10px; padding:14px 18px; margin-top:14px; color:#fda4af; font-size:14px; }

.judge-card { background:#1e1b4b; border:1px solid #4338ca; border-radius:14px; padding:22px; margin-top:20px; }
.pivot-box { background:#2d2006; border-left:3px solid #f59e0b; border-radius:8px; padding:12px 16px; margin-top:12px; color:#fde68a; font-size:14px; }
.cond-box  { background:#0c1f3d; border-left:3px solid #3b82f6; border-radius:8px; padding:12px 16px; margin-top:10px; color:#93c5fd; font-size:14px; }

.feature-col { background:#111827; border-radius:12px; padding:18px; }
.feature-col h4 { font-size:13px; text-transform:uppercase; letter-spacing:1px; margin-bottom:14px; }
.feature-item { background:#1f2937; border-radius:8px; padding:10px 14px; margin-bottom:8px; font-size:14px; color:#e5e7eb; }
.stack-pill { background:#1e3a5f; color:#93c5fd; border-radius:8px; padding:6px 14px; font-size:13px; font-weight:600; display:inline-block; margin:4px; }

.report-block { background:#0f172a; border:1px solid #1e293b; border-radius:12px; padding:20px 24px; margin-bottom:14px; }
.report-block .rb-label { font-size:11px; color:#64748b; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px; }
.report-block .rb-text  { font-size:15px; color:#e2e8f0; line-height:1.6; word-break:break-word; }

.pipeline-step { padding:8px 14px; border-radius:8px; margin-bottom:6px; font-size:14px; }
.step-done    { background:#052e16; color:#6ee7b7; }
.step-running { background:#1e1b4b; color:#a5b4fc; }
</style>
""", unsafe_allow_html=True)


#  HELPERS
def get(obj, *keys, default="N/A"):
    for key in keys:
        if obj is None: return default
        try:
            obj = obj.get(key) if isinstance(obj, dict) else getattr(obj, key, None)
        except Exception:
            return default
    return obj if obj is not None else default

def get_list(obj, key, default=None):
    val = get(obj, key, default=None)
    if val is None: return default or []
    return val if isinstance(val, list) else (default or [])

def sbadge(s):
    s = str(s).lower()
    cls = {"strong":"str-strong","medium":"str-medium","weak":"str-weak"}.get(s,"str-weak")
    return f'<span class="strength-badge {cls}">{s}</span>'

NODE_MESSAGES = {
    "decompose":   "🧠 Decomposing your idea",
    "research":    "📊 Researching the market",
    "competitor":  "⚔️ Finding competitors",
    "graveyard":   "💀 Digging the graveyard",
    "user_pain":   "😤 Mining user pain points",
    "market_size": "💰 Calculating market size",
    "moat":        "🛡️ Detecting moat potential",
    "bullish":     "🐂 Building bull case",
    "bearish":     "🐻 Building bear case",
    "verdict":     "⚖️ Judge is deciding",
    "mvp":         "🚀 Planning MVP",
    "report":      "📝 Writing final report",
}


#  HEADER
if "result" not in st.session_state:
    st.session_state.result = None

st.markdown("""
<div style="text-align:center; padding:20px 0 10px 0;">
  <div style="font-size:52px;">🔮</div>
  <div style="font-size:38px; font-weight:900; background:linear-gradient(135deg,#a78bfa,#60a5fa);
       -webkit-background-clip:text; -webkit-text-fill-color:transparent;">STARTUP ORACLE</div>
  <div style="color:#6b7280; font-size:15px; margin-top:4px;">Give me your startup idea — I'll tell you if it'll live or die.</div>
</div>
""", unsafe_allow_html=True)
st.divider()

idea = st.text_area("Describe your startup idea", height=80,
    placeholder="e.g. Uber for dogs | AI therapist for Gen Z | B2B SaaS for restaurant inventory")

if st.button("⚡ Analyze with Oracle", type="primary", use_container_width=True):
    if not idea.strip():
        st.warning("Please enter an idea first!")
    else:
        st.session_state.result = None
        import threading, time

        result_holder, error_holder = {}, {}

        def run_pipeline():
            try:
                result_holder["data"] = app.invoke({
                    "raw_idea": idea, "agent_logs": [],
                    "sources": [], "competitor_search_attempts": 0
                })
            except Exception as e:
                error_holder["err"] = e

        thread = threading.Thread(target=run_pipeline)
        thread.start()

        progress_box = st.empty()
        node_msgs = list(NODE_MESSAGES.values())
        step = 0

        while thread.is_alive():
            html = "".join([f'<div class="pipeline-step step-done">✅ {node_msgs[i]}</div>' for i in range(step)])
            if step < len(node_msgs):
                html += f'<div class="pipeline-step step-running">⚡ {node_msgs[step]} ...</div>'
            progress_box.markdown(html, unsafe_allow_html=True)
            time.sleep(3)
            if step < len(node_msgs) - 1:
                step += 1

        thread.join()

        if "err" in error_holder:
            st.error(f"Pipeline error: {error_holder['err']}")
            st.stop()

        done_html = "".join([f'<div class="pipeline-step step-done">✅ {log}</div>'
                             for log in result_holder["data"].get("agent_logs", [])])
        progress_box.markdown(done_html, unsafe_allow_html=True)
        st.session_state.result = result_holder["data"]
        st.success("✅ Analysis complete!")


#  RESULTS
if st.session_state.result:
    r = st.session_state.result

    oracle_report = r.get("oracle_report")
    judge_verdict = r.get("judge_verdict")
    market_size   = r.get("market_size")
    competitors   = r.get("competitors") or []
    dead_startups = r.get("dead_startups") or []
    user_pain     = r.get("user_pain")
    bull_case     = r.get("bull_case")
    bear_case     = r.get("bear_case")
    mvp_plan      = r.get("mvp_plan")
    moat_analysis = r.get("moat_analysis")

    st.divider()

    # ── Hero Row ──
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        score = get(oracle_report, "oracle_score", default=0)
        try: score = int(score)
        except: score = 0
        c = "#10b981" if score >= 65 else "#f59e0b" if score >= 40 else "#ef4444"
        st.markdown(f"""
        <div class="stat-card" style="border-color:{c}55; text-align:center;">
          <div class="label">Oracle Score</div>
          <div style="font-size:64px; font-weight:800; color:{c}; line-height:1;">{score}</div>
          <div class="sub">out of 100</div>
          <div style="background:#1e293b; border-radius:8px; height:8px; margin-top:12px; overflow:hidden;">
            <div style="background:{c}; height:8px; width:{score}%; border-radius:8px;"></div>
          </div>
        </div>""", unsafe_allow_html=True)

    with col2:
        verdict = get(oracle_report, "verdict", default="N/A")
        vcls  = {"BUILD IT":"verdict-build","PIVOT":"verdict-pivot","KILL IT":"verdict-kill"}.get(verdict,"")
        vemoji= {"BUILD IT":"✅","PIVOT":"🔄","KILL IT":"❌"}.get(verdict,"")
        st.markdown(f"""
        <div class="stat-card" style="text-align:center;">
          <div class="label">Verdict</div>
          <div style="margin-top:14px;"><span class="verdict-badge {vcls}">{verdict} {vemoji}</span></div>
        </div>""", unsafe_allow_html=True)

    with col3:
        summary = get(oracle_report, "one_line_summary", default="")
        pitch   = get(oracle_report, "investor_pitch_angle", default="")
        st.markdown(f"""
        <div class="stat-card">
          <div class="label">One-Line Summary</div>
          <div style="font-size:16px; color:#e2e8f0; font-weight:600; margin-bottom:12px; line-height:1.5;">{summary}</div>
          <div class="label" style="margin-top:4px;">Investor Pitch Angle</div>
          <div style="font-size:13px; color:#94a3b8; line-height:1.5;">{pitch}</div>
        </div>""", unsafe_allow_html=True)

    # ── Score Breakdown ──
    sb = get(oracle_report, "score_breakdown", default=None)
    if sb:
        st.markdown("### 📊 Score Breakdown")
        metrics = [
            ("🔥 Problem Severity",  "problem_severity"),
            ("💰 Market Size",       "market_size"),
            ("🛡️ Defensibility",    "defensibility"),
            ("💳 Monetization",      "monetization"),
            ("⚙️ Exec Complexity",   "execution_complexity"),
            ("🎯 Founder Fit",       "founder_fit"),
        ]
        left, right = st.columns(2)
        for i, (label, key) in enumerate(metrics):
            val = get(sb, key, default=0)
            try: val = int(val)
            except: val = 0
            bar_c = "#10b981" if val >= 65 else "#f59e0b" if val >= 40 else "#ef4444"
            (left if i % 2 == 0 else right).markdown(f"""
            <div class="score-row">
              <div class="score-label"><span>{label}</span><span style="color:{bar_c}; font-weight:700;">{val}/100</span></div>
              <div class="score-bar-bg"><div class="score-bar-fill" style="width:{val}%; background:{bar_c};"></div></div>
            </div>""", unsafe_allow_html=True)

    st.divider()

    # TABS 
    tabs = st.tabs(["📈 Market", "⚔️ Competitors", "💀 Graveyard", "😤 User Pain", "🐂🐻 Debate", "🚀 MVP", "📝 Full Report"])

    # TAB 0 — Market
    with tabs[0]:
        if market_size:
            st.markdown("#### 💰 Market Size Breakdown")
            c1, c2, c3 = st.columns(3)
            for col, lbl, key, clr in [
                (c1,"TAM — Total Addressable","tam","#a78bfa"),
                (c2,"SAM — Serviceable","sam","#60a5fa"),
                (c3,"SOM — Obtainable (3yr)","som","#34d399"),
            ]:
                col.markdown(f"""
                <div class="info-card" style="border-color:{clr}55; text-align:center;">
                  <h4>{lbl}</h4><p style="color:{clr}; font-size:22px;">{get(market_size,key)}</p>
                </div>""", unsafe_allow_html=True)

            reasoning  = get(market_size, "reasoning", default="")
            confidence = get(market_size, "confidence", default="")
            if reasoning:
                conf_c = {"high":"#10b981","medium":"#f59e0b","low":"#ef4444"}.get(str(confidence).lower(),"#94a3b8")
                st.markdown(f"""
                <div class="report-block" style="margin-top:16px;">
                  <div class="rb-label">📐 Analyst Reasoning &nbsp;·&nbsp;
                    Confidence: <span style="color:{conf_c}; font-weight:700;">{str(confidence).upper()}</span>
                  </div>
                  <div class="rb-text">{reasoning}</div>
                </div>""", unsafe_allow_html=True)

            if moat_analysis:
                st.markdown("#### 🛡️ Moat Analysis")

                moat_strength = str(get(moat_analysis,"moat_strength",default="weak")).lower()
                ms_cfg = {
                    "strong": ("#10b981","#052e16","💪 STRONG MOAT","High defensibility — hard to replicate"),
                    "medium": ("#f59e0b","#2d1f00","⚠️ MEDIUM MOAT","Some defensibility but needs shoring up"),
                    "weak":   ("#ef4444","#450a0a","🚨 WEAK MOAT","Easy to copy — urgently needs a moat"),
                    "none":   ("#6b7280","#1f2937","❌ NO MOAT",  "Completely open to competition"),
                }
                ms_clr, ms_bg, ms_label, ms_sub = ms_cfg.get(moat_strength, ms_cfg["weak"])

                # Moat strength banner
                st.markdown(f"""
                <div style="background:{ms_bg}; border:1px solid {ms_clr}55; border-radius:12px;
                     padding:14px 22px; margin-bottom:18px; display:flex; align-items:center; gap:16px;">
                  <div style="font-size:28px;">🛡️</div>
                  <div>
                    <div style="font-size:18px; font-weight:800; color:{ms_clr};">{ms_label}</div>
                    <div style="font-size:13px; color:#9ca3af; margin-top:2px;">{ms_sub}</div>
                  </div>
                </div>""", unsafe_allow_html=True)

                # 3 moat factor cards
                def clean_moat_text(text):
                    """Convert raw single-word model values to readable sentences"""
                    mapping = {
                        "low":          "Minimal — easy for users to switch away",
                        "low_moderate": "Below average — some friction but not enough",
                        "moderate":     "Moderate — some friction exists for users",
                        "medium":       "Moderate — some friction exists for users",
                        "high":         "Strong — users face real costs to leave",
                        "none":         "None — users can switch freely at any time",
                        "yes":          "Present — grows stronger with more users",
                        "no":           "Absent — no network effects observed",
                    }
                    cleaned = str(text).strip().lower().replace(" ", "_")
                    return mapping.get(cleaned, str(text))  # fallback to original if not matched

                def moat_card(icon, title, text, color):
                    display_text = clean_moat_text(text)
                    t = str(text).strip().lower()
                    # Detect strength — check raw value first, then keywords in display text
                    if t in ["high","strong"] or any(w in t for w in ["high","strong","significant","deep"]):
                        strength_lbl, s_clr = "HIGH", "#10b981"
                    elif t in ["low","none","no"] or any(w in t for w in ["low","none","minimal","absent","no "]):
                        strength_lbl, s_clr = "LOW", "#ef4444"
                    else:
                        strength_lbl, s_clr = "MEDIUM", "#f59e0b"
                    dot = f'<span style="background:{s_clr}; border-radius:50%; width:8px; height:8px; display:inline-block; margin-right:6px;"></span>'
                    return f"""
                    <div style="background:#0d1117; border:1px solid {color}44; border-radius:14px;
                         padding:18px 20px; height:100%;">
                      <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
                        <span style="font-size:22px;">{icon}</span>
                        <span style="font-size:12px; color:#94a3b8; text-transform:uppercase; letter-spacing:1px; font-weight:600;">{title}</span>
                      </div>
                      <div style="font-size:14px; color:#cbd5e1; line-height:1.6; margin-bottom:12px;">{display_text}</div>
                      <div style="font-size:11px; color:#6b7280;">{dot}<span style="color:{s_clr}; font-weight:700;">{strength_lbl}</span></div>
                    </div>"""

                m1, m2, m3 = st.columns(3)
                m1.markdown(moat_card("🔒","Switching Costs", get(moat_analysis,"switching_costs"), "#818cf8"), unsafe_allow_html=True)
                m2.markdown(moat_card("🌐","Network Effects",  get(moat_analysis,"network_effects"),  "#34d399"), unsafe_allow_html=True)
                m3.markdown(moat_card("🗄️","Data Advantage",  get(moat_analysis,"data_advantage"),   "#fb923c"), unsafe_allow_html=True)

                # Potential moats as pills
                potential = get_list(moat_analysis,"potential_moats")
                if potential:
                    st.markdown("<br>", unsafe_allow_html=True)
                    pills = "".join([f'<span style="background:#1e3a5f; color:#93c5fd; border-radius:20px; padding:5px 14px; font-size:13px; display:inline-block; margin:4px;">🔹 {m}</span>' for m in potential])
                    st.markdown(f"""
                    <div style="background:#0d1117; border:1px solid #1e293b; border-radius:12px; padding:16px 20px;">
                      <div style="font-size:11px; color:#64748b; text-transform:uppercase; letter-spacing:1px; margin-bottom:10px;">⚡ Potential Moats to Build</div>
                      <div>{pills}</div>
                    </div>""", unsafe_allow_html=True)

                # Verdict bar
                vt = get(moat_analysis,"verdict",default="")
                if vt:
                    st.markdown(f"""
                    <div style="background:#1e1b4b; border-left:4px solid #818cf8; border-radius:0 10px 10px 0;
                         padding:14px 18px; margin-top:12px;">
                      <div style="font-size:11px; color:#818cf8; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">⚖️ Moat Verdict</div>
                      <div style="font-size:14px; color:#c7d2fe; line-height:1.6;">{vt}</div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.info("Market size data not available.")

    # TAB 1 — Competitors
    with tabs[1]:
        if competitors:
            st.markdown(f"#### ⚔️ {len(competitors)} Competitors Found")
            for c in competitors:
                name = get(c,"name",default="Unknown")
                s_pills = "".join([f'<span class="pill-green">✓ {s}</span>' for s in get_list(c,"strengths")])
                w_pills = "".join([f'<span class="pill-red">✗ {w}</span>'   for w in get_list(c,"weaknesses")])
                st.markdown(f"""
                <div class="comp-card">
                  <div class="comp-name">🏢 {name}</div>
                  <div class="comp-type">{get(c,"product_type",default="")}</div>
                  <div class="meta-row">
                    <div class="meta-item">💳 Pricing: <span>{get(c,"pricing")}</span></div>
                    <div class="meta-item">👤 Target: <span>{get(c,"target_user")}</span></div>
                    <div class="meta-item">💰 Funding: <span>{get(c,"funding")}</span></div>
                  </div>
                  <div style="margin-bottom:8px;"><b style="color:#94a3b8; font-size:12px;">STRENGTHS</b><br>{s_pills or "—"}</div>
                  <div><b style="color:#94a3b8; font-size:12px;">WEAKNESSES</b><br>{w_pills or "—"}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No competitor data found.")

    # TAB 2 — Graveyard
    with tabs[2]:
        if dead_startups:
            st.markdown(f"#### 💀 {len(dead_startups)} Failed Startups — Learn From Their Graves")
            for d in dead_startups:
                name   = get(d,"name",default="Unknown")
                year   = get(d,"year_died",default="Unknown")
                did    = get(d,"what_they_did",default="")
                why    = get(d,"why_they_failed",default="")
                lesson = get(d,"lesson",default="")
                st.markdown(f"""
                <div class="grave-card">
                  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <span class="grave-name">💀 {name}</span>
                    <span class="grave-year">Died: {year}</span>
                  </div>
                  <div style="font-size:14px; color:#d1d5db; margin-bottom:8px;">{did}</div>
                  {"<div class='grave-why'>⚠️ <b>Why they failed:</b> " + why + "</div>" if why else ""}
                  {"<div class='grave-lesson'>💡 <b>Key Lesson:</b> " + lesson + "</div>" if lesson else ""}
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No graveyard data found.")

    # TAB 3 — User Pain
    with tabs[3]:
        if user_pain:
            intensity  = str(get(user_pain,"emotional_intensity",default="medium")).lower()
            complaints = get_list(user_pain,"top_complaints")
            quotes     = get_list(user_pain,"reddit_quotes")
            wtp        = get(user_pain,"willingness_to_pay",default="")
            workaround = get(user_pain,"most_common_workaround",default="")

            cfg = {
                "high":  ("🔥 HIGH PAIN — Users are desperate for a solution","#ef4444","#450a0a"),
                "medium":("⚠️ MEDIUM PAIN — Annoying but manageable",          "#f59e0b","#2d1f00"),
                "low":   ("😐 LOW PAIN — Nice-to-have territory",              "#60a5fa","#0c1f3d"),
            }
            lbl, clr, bg = cfg.get(intensity,("UNKNOWN","#94a3b8","#1f2937"))
            st.markdown(f"""
            <div style="background:{bg}; border:1px solid {clr}55; border-radius:12px; padding:14px 20px; margin-bottom:20px;">
              <span style="font-size:18px; color:{clr}; font-weight:800;">{lbl}</span>
            </div>""", unsafe_allow_html=True)

            if complaints:
                st.markdown("#### 😤 Top Complaints")
                for i, c in enumerate(complaints, 1):
                    st.markdown(f"""
                    <div class="complaint-row">
                      <div class="complaint-num">{i}</div><div>{c}</div>
                    </div>""", unsafe_allow_html=True)

            if quotes:
                st.markdown("#### 💬 Real User Quotes")
                for q in quotes:
                    st.markdown(f'<div class="quote-card">"{q}"</div>', unsafe_allow_html=True)

            if wtp or workaround:
                st.markdown("#### 💡 Key Insights")
                ic1, ic2 = st.columns(2)
                if wtp:
                    ic1.markdown(f"""
                    <div class="insight-card">
                      <div class="ic-label">💳 Willingness to Pay</div>
                      <div class="ic-val">{wtp}</div>
                    </div>""", unsafe_allow_html=True)
                if workaround:
                    ic2.markdown(f"""
                    <div class="insight-card">
                      <div class="ic-label">🔧 Current Workaround</div>
                      <div class="ic-val">{workaround}</div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.info("User pain data not available.")

    # TAB 4 — Debate
    with tabs[4]:
        if bull_case or bear_case:
            col1, col2 = st.columns(2)
            with col1:
                if bull_case:
                    bscore = get(bull_case,"confidence_score",default=0)
                    thesis = get(bull_case,"main_thesis",default="")
                    args_html = "".join([f"""
                    <div class="arg-row">
                      <div class="arg-text">{get(a,"argument")}{sbadge(get(a,"strength"))}</div>
                      <div class="arg-ev">{get(a,"evidence")}</div>
                    </div>""" for a in get_list(bull_case,"top_arguments")])
                    st.markdown(f"""
                    <div class="debate-bull">
                      <div class="debate-title">🐂 BULL CASE
                        <span style="font-size:13px; color:#6ee7b7; font-weight:400; margin-left:8px;">{bscore}/100 confidence</span>
                      </div>
                      <div class="debate-thesis">{thesis}</div>
                      {args_html}
                    </div>""", unsafe_allow_html=True)

            with col2:
                if bear_case:
                    bscore = get(bear_case,"confidence_score",default=0)
                    thesis = get(bear_case,"main_thesis",default="")
                    fatal  = get(bear_case,"fatal_flaw",default="")
                    args_html = "".join([f"""
                    <div class="arg-row">
                      <div class="arg-text">{get(a,"argument")}{sbadge(get(a,"strength"))}</div>
                      <div class="arg-ev">{get(a,"evidence")}</div>
                    </div>""" for a in get_list(bear_case,"top_arguments")])
                    st.markdown(f"""
                    <div class="debate-bear">
                      <div class="debate-title">🐻 BEAR CASE
                        <span style="font-size:13px; color:#fca5a5; font-weight:400; margin-left:8px;">{bscore}/100 confidence</span>
                      </div>
                      <div class="debate-thesis">{thesis}</div>
                      {args_html}
                      {"<div class='fatal-box'>☠️ <b>Fatal Flaw:</b> " + fatal + "</div>" if fatal else ""}
                    </div>""", unsafe_allow_html=True)

            if judge_verdict:
                reasoning = get(judge_verdict,"reasoning",default="")
                pivot     = get(judge_verdict,"pivot_suggestion",default="")
                cond      = get(judge_verdict,"conditions_to_build",default="")
                verdict_v = get(judge_verdict,"verdict",default="")
                vcls2 = {"BUILD IT":"verdict-build","PIVOT":"verdict-pivot","KILL IT":"verdict-kill"}.get(verdict_v,"")
                st.markdown(f"""
                <div class="judge-card">
                  <div style="display:flex; align-items:center; gap:14px; margin-bottom:14px; flex-wrap:wrap;">
                    <span style="font-size:20px; font-weight:800; color:#e0e7ff;">⚖️ Judge's Verdict</span>
                    <span class="verdict-badge {vcls2}" style="font-size:14px; padding:6px 18px;">{verdict_v}</span>
                  </div>
                  <div style="font-size:14px; color:#c7d2fe; line-height:1.7; margin-bottom:8px;">{reasoning}</div>
                  {"<div class='pivot-box'>🔄 <b>Pivot Suggestion:</b> " + pivot + "</div>" if pivot else ""}
                  {"<div class='cond-box'>🎯 <b>Conditions to Build:</b> " + cond + "</div>" if cond else ""}
                </div>""", unsafe_allow_html=True)
        else:
            st.info("Debate data not available.")

    # TAB 5 — MVP
    with tabs[5]:
        if mvp_plan:
            c1, c2, c3 = st.columns(3)
            for col, title, key, clr in [
                (c1,"✅ Must Have",      "must_have_features",   "#10b981"),
                (c2,"💡 Nice to Have",  "nice_to_have_features","#60a5fa"),
                (c3,"❌ Do NOT Build",  "must_not_build",        "#ef4444"),
            ]:
                items = get_list(mvp_plan, key)
                items_html = "".join([f'<div class="feature-item" style="border-left:3px solid {clr};">{f}</div>' for f in items])
                col.markdown(f"""
                <div class="feature-col">
                  <h4 style="color:{clr};">{title}</h4>
                  {items_html or '<div style="color:#6b7280; font-size:13px;">None</div>'}
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            m1, m2 = st.columns(2)
            timeline = get(mvp_plan,"timeline_weeks",default="")
            metric   = get(mvp_plan,"success_metric",default="")
            plan     = get(mvp_plan,"first_100_users_plan",default="")
            milestone= get(mvp_plan,"first_milestone",default="")
            stack    = get_list(mvp_plan,"tech_stack")

            if timeline:
                m1.markdown(f"""<div class="info-card" style="text-align:center;">
                  <h4>⏱️ Timeline</h4><p style="color:#a78bfa;">{timeline} weeks</p></div>""", unsafe_allow_html=True)
            if metric:
                m2.markdown(f"""<div class="info-card" style="text-align:center;">
                  <h4>🎯 Success Metric</h4><p style="font-size:14px; color:#34d399;">{metric}</p></div>""", unsafe_allow_html=True)
            if milestone:
                st.markdown(f"""<div class="report-block"><div class="rb-label">🏁 First Milestone</div>
                  <div class="rb-text">{milestone}</div></div>""", unsafe_allow_html=True)
            if plan:
                st.markdown(f"""<div class="report-block" style="border-color:#60a5fa44;">
                  <div class="rb-label">🚀 First 100 Users Plan</div>
                  <div class="rb-text">{plan}</div></div>""", unsafe_allow_html=True)
            if stack:
                pills = "".join([f'<span class="stack-pill">{s}</span>' for s in stack])
                st.markdown(f"""<div class="report-block"><div class="rb-label">🛠️ Tech Stack</div>
                  <div style="margin-top:8px;">{pills}</div></div>""", unsafe_allow_html=True)
        else:
            st.info("MVP plan not available.")

    # TAB 6 — Full Report
    with tabs[6]:
        if oracle_report:
            pos = get(oracle_report,"positioning_statement",default="")
            gtm = get(oracle_report,"gtm_strategy",default="")
            for lbl, val, clr in [
                ("📌 Positioning Statement", pos,  "#a78bfa"),
                ("📣 Go-to-Market Strategy", gtm,  "#60a5fa"),
            ]:
                if val:
                    st.markdown(f"""
                    <div class="report-block" style="border-color:{clr}44;">
                      <div class="rb-label" style="color:{clr};">{lbl}</div>
                      <div class="rb-text">{val}</div>
                    </div>""", unsafe_allow_html=True)

        with st.expander("📚 Sources Used"):
            for s in r.get("sources", []): st.write(f"- {s}")
        with st.expander("🤖 Agent Execution Log"):
            for log in r.get("agent_logs", []): st.write(f"- {log}")

        st.download_button("⬇️ Download Full Report (JSON)", data=str(r),
                           file_name="oracle_report.json", mime="application/json")