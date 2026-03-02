import streamlit as st
import google.generativeai as genai
import json
import time
from datetime import datetime

st.set_page_config(
    page_title="JobHunt Agent Orchestrator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg:       #05060a;
    --s1:       #0d0f18;
    --s2:       #131622;
    --border:   #1c2035;
    --accent:   #7c6af7;
    --accent2:  #f7c26a;
    --green:    #4dffb4;
    --red:      #ff5f6d;
    --blue:     #4dc8ff;
    --text:     #d0d5f0;
    --muted:    #4a5070;
    --glow:     rgba(124,106,247,0.25);
}

*, html, body, [class*="css"] {
    font-family: 'Syne', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
    box-sizing: border-box;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--s1) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Headings */
h1 { font-size: 2.2rem !important; font-weight: 800 !important; letter-spacing: -1px !important; color: white !important; }
h2, h3 { font-weight: 700 !important; color: var(--text) !important; }

/* Inputs */
textarea, input[type="text"], input[type="number"] {
    background: var(--s2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 14px !important;
}
textarea:focus, input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--glow) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), #5b4de0) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important; font-size: 14px !important;
    letter-spacing: 0.5px !important; padding: 10px 22px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px var(--glow) !important;
}

/* Agent card */
.agent-card {
    background: var(--s1);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 22px;
    margin: 8px 0;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s;
}
.agent-card.running { border-color: var(--accent); box-shadow: 0 0 20px var(--glow); }
.agent-card.done    { border-color: var(--green); }
.agent-card.idle    { border-color: var(--border); }
.agent-card.error   { border-color: var(--red); }

.agent-title {
    font-weight: 700; font-size: 15px; letter-spacing: 0.5px;
    margin-bottom: 4px;
}
.agent-desc { font-size: 13px; color: var(--muted); font-family: 'DM Mono', monospace; }
.agent-status {
    position: absolute; top: 18px; right: 18px;
    font-size: 11px; font-weight: 700; letter-spacing: 2px;
    text-transform: uppercase; font-family: 'DM Mono', monospace;
}
.status-idle    { color: var(--muted); }
.status-running { color: var(--accent); animation: pulse 1.2s infinite; }
.status-done    { color: var(--green); }
.status-error   { color: var(--red); }

@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

/* Output box */
.output-box {
    background: var(--s2);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 0 10px 10px 0;
    padding: 18px 22px;
    margin: 10px 0;
    font-family: 'DM Mono', monospace;
    font-size: 13px;
    line-height: 1.7;
}
.output-box.green { border-left-color: var(--green); }
.output-box.yellow { border-left-color: var(--accent2); }
.output-box.blue { border-left-color: var(--blue); }
.output-box.red { border-left-color: var(--red); }

/* Progress step */
.step-row {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 0; border-bottom: 1px solid var(--border);
    font-size: 14px;
}
.step-num {
    width: 28px; height: 28px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 700; flex-shrink: 0;
    font-family: 'DM Mono', monospace;
}
.step-num.done    { background: var(--green); color: #000; }
.step-num.running { background: var(--accent); color: #fff; }
.step-num.pending { background: var(--border); color: var(--muted); }

/* Stat pill */
.stat-pill {
    display: inline-flex; align-items: center; gap: 8px;
    background: var(--s2); border: 1px solid var(--border);
    border-radius: 100px; padding: 6px 16px;
    font-family: 'DM Mono', monospace; font-size: 13px;
    margin: 3px;
}
.stat-val { font-size: 20px; font-weight: 700; color: var(--accent); }

/* Tag */
.tag {
    display: inline-block;
    background: rgba(124,106,247,0.15);
    border: 1px solid rgba(124,106,247,0.35);
    border-radius: 6px; padding: 3px 10px;
    font-size: 12px; font-family: 'DM Mono', monospace;
    color: var(--accent); margin: 2px;
}
.tag-green { background: rgba(77,255,180,0.1); border-color: rgba(77,255,180,0.3); color: var(--green); }
.tag-yellow { background: rgba(247,194,106,0.1); border-color: rgba(247,194,106,0.3); color: var(--accent2); }
.tag-blue { background: rgba(77,200,255,0.1); border-color: rgba(77,200,255,0.3); color: var(--blue); }
.tag-red { background: rgba(255,95,109,0.1); border-color: rgba(255,95,109,0.3); color: var(--red); }

/* Section label */
.slbl {
    font-size: 10px; font-weight: 700; letter-spacing: 3px;
    text-transform: uppercase; color: var(--muted);
    border-bottom: 1px solid var(--border); padding-bottom: 6px;
    margin: 20px 0 12px;
}

/* Metric */
.mbox {
    background: var(--s1); border: 1px solid var(--border);
    border-radius: 10px; padding: 16px; text-align: center;
}
.mval { font-size: 30px; font-weight: 800; color: var(--accent); font-family: 'DM Mono', monospace; }
.mlbl { font-size: 10px; letter-spacing: 2px; text-transform: uppercase; color: var(--muted); margin-top: 4px; }

/* Selectbox */
[data-baseweb="select"] > div {
    background: var(--s2) !important; border-color: var(--border) !important;
}

/* Expander */
[data-testid="stExpander"] {
    background: var(--s1) !important; border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

#MainMenu, footer, .stDeployButton { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════
DEFAULTS = {
    "api_key_set": False,
    "profile": {},
    "results": {},          # agent_id -> output text
    "agent_status": {},     # agent_id -> idle/running/done/error
    "run_log": [],          # chronological log entries
    "orchestration_done": False,
    "final_plan": None,
    "resume_text": None,
    "cover_letter": None,
    "tracker": [],
    "total_runs": 0,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════
# AGENT DEFINITIONS
# ══════════════════════════════════════════════════════════
AGENTS = [
    {
        "id": "profile_analyst",
        "name": "🧠 Profile Analyst",
        "role": "Analyse candidate's background, extract key skills, identify strengths & gaps",
        "color": "accent",
    },
    {
        "id": "market_researcher",
        "name": "🔍 Market Researcher",
        "role": "Research current job market, in-demand roles, salary ranges, top hiring companies",
        "color": "blue",
    },
    {
        "id": "job_matcher",
        "name": "🎯 Job Matcher",
        "role": "Match candidate profile to best-fit roles with fit scores and reasoning",
        "color": "green",
    },
    {
        "id": "resume_agent",
        "name": "📄 Resume Optimizer",
        "role": "Rewrite and optimise CV/resume for ATS and human readers for target roles",
        "color": "yellow",
    },
    {
        "id": "cover_letter_agent",
        "name": "✍️ Cover Letter Writer",
        "role": "Generate tailored, compelling cover letters for top-matched positions",
        "color": "accent",
    },
    {
        "id": "linkedin_agent",
        "name": "💼 LinkedIn Optimizer",
        "role": "Optimise LinkedIn headline, summary, and skills section for recruiter discovery",
        "color": "blue",
    },
    {
        "id": "outreach_agent",
        "name": "📧 Outreach Strategist",
        "role": "Write cold outreach templates to recruiters and hiring managers",
        "color": "green",
    },
    {
        "id": "interview_agent",
        "name": "🎤 Interview Coach",
        "role": "Prepare likely interview questions with tailored STAR-method answers",
        "color": "yellow",
    },
    {
        "id": "action_planner",
        "name": "🗺️ Action Planner",
        "role": "Create a day-by-day 30-day job hunt sprint plan with daily tasks",
        "color": "accent",
    },
]

COLOR_MAP = {
    "accent": ("rgba(124,106,247,0.15)", "rgba(124,106,247,0.4)"),
    "blue":   ("rgba(77,200,255,0.1)",  "rgba(77,200,255,0.35)"),
    "green":  ("rgba(77,255,180,0.1)",  "rgba(77,255,180,0.3)"),
    "yellow": ("rgba(247,194,106,0.1)", "rgba(247,194,106,0.3)"),
}

def log(msg, level="info"):
    ts = datetime.now().strftime("%H:%M:%S")
    emoji = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌", "running": "⚙️"}.get(level, "•")
    st.session_state.run_log.append(f"`{ts}` {emoji} {msg}")

def run_agent(model, agent_id, prompt):
    st.session_state.agent_status[agent_id] = "running"
    log(f"Agent **{agent_id}** started", "running")
    try:
        response = model.generate_content(prompt)
        result = response.text.strip()
        st.session_state.results[agent_id] = result
        st.session_state.agent_status[agent_id] = "done"
        log(f"Agent **{agent_id}** completed ({len(result)} chars)", "success")
        return result
    except Exception as e:
        st.session_state.agent_status[agent_id] = "error"
        log(f"Agent **{agent_id}** failed: {e}", "error")
        return f"ERROR: {e}"

def build_base_context(p):
    return f"""
CANDIDATE PROFILE:
Name: {p.get('name','Not provided')}
Current Title: {p.get('title','Not provided')}
Years of Experience: {p.get('years',0)}
Target Role(s): {p.get('target_roles','Not specified')}
Location: {p.get('location','Not specified')}
Open to Remote: {p.get('remote','Not specified')}
Skills: {p.get('skills','Not provided')}
Education: {p.get('education','Not provided')}
Industry Background: {p.get('industry','Not provided')}
Salary Expectation: {p.get('salary','Not specified')}
Urgency: {p.get('urgency','ASAP')}
Key Achievements: {p.get('achievements','Not provided')}
Current Resume Summary: {p.get('resume_summary','Not provided')}
""".strip()


# ══════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🎯 JobHunt AI")
    st.markdown("**Multi-Agent Orchestrator**")
    st.markdown("---")

    api_key = st.text_input("Gemini API Key", type="password", placeholder="AIza...")
    if api_key:
        st.session_state.api_key_set = True
        st.session_state._api_key = api_key
        st.markdown('<span class="tag-green">● API Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="tag-red">● No API Key</span>', unsafe_allow_html=True)

    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["🚀 Orchestrate", "📋 Results", "📊 Tracker", "📜 Run Log"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    total = st.session_state.total_runs
    done = sum(1 for v in st.session_state.agent_status.values() if v == "done")
    st.markdown(f"""
    <div class="mbox" style="margin-bottom:8px">
        <div class="mval">{done}/{len(AGENTS)}</div>
        <div class="mlbl">Agents Done</div>
    </div>
    <div class="mbox">
        <div class="mval">{total}</div>
        <div class="mlbl">Total Runs</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔄 Reset All", use_container_width=True):
        for k, v in DEFAULTS.items():
            st.session_state[k] = v if not isinstance(v, (dict, list)) else type(v)()
        st.rerun()


# ══════════════════════════════════════════════════════════
# PAGE: ORCHESTRATE
# ══════════════════════════════════════════════════════════
if "Orchestrate" in page:
    st.markdown("# 🎯 JOB HUNT AGENT ORCHESTRATOR")
    st.markdown(
        '<span class="tag">9 Specialized Agents</span>'
        '<span class="tag-blue">Parallel + Sequential</span>'
        '<span class="tag-green">End-to-End Automation</span>',
        unsafe_allow_html=True
    )

    # ── Profile Form ──
    st.markdown('<div class="slbl">Your Profile</div>', unsafe_allow_html=True)

    with st.form("profile_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            name = st.text_input("Full Name *")
            title = st.text_input("Current / Last Job Title *")
            years = st.number_input("Years of Experience", 0, 50, 3)
        with c2:
            target_roles = st.text_input("Target Role(s) *", placeholder="e.g. Data Engineer, ML Engineer")
            location = st.text_input("Location *", placeholder="e.g. London, UK / Remote")
            remote = st.selectbox("Work Preference", ["Open to all", "Remote only", "Hybrid", "On-site only"])
        with c3:
            salary = st.text_input("Salary Expectation", placeholder="e.g. £60k–£80k / $120k")
            industry = st.text_input("Industry Background", placeholder="e.g. FinTech, Healthcare, SaaS")
            urgency = st.selectbox("Urgency", ["ASAP (days)", "Within 2 weeks", "Within a month", "Flexible"])

        skills = st.text_area("Key Skills *", placeholder="Python, SQL, dbt, Spark, AWS, Tableau, communication…", height=70)
        education = st.text_input("Education", placeholder="e.g. BSc Computer Science, UCL, 2019")
        achievements = st.text_area("Top 3–5 Achievements", placeholder="e.g. Reduced pipeline latency by 60%, led team of 5 engineers, launched product used by 200k users…", height=70)
        resume_summary = st.text_area("Paste Current Resume / LinkedIn Summary (optional but recommended)", height=100, placeholder="Paste your existing resume text here for best results…")

        submitted = st.form_submit_button("⚡ LAUNCH ALL AGENTS", use_container_width=True)

    if submitted:
        errors = []
        if not name: errors.append("Name")
        if not title: errors.append("Current Title")
        if not target_roles: errors.append("Target Roles")
        if not skills: errors.append("Skills")
        if not location: errors.append("Location")
        if errors:
            st.error(f"⚠️ Please fill in: {', '.join(errors)}")
        elif not st.session_state.api_key_set:
            st.error("⚠️ Please enter your Gemini API Key in the sidebar.")
        else:
            profile = {
                "name": name, "title": title, "years": years,
                "target_roles": target_roles, "location": location, "remote": remote,
                "salary": salary, "industry": industry, "urgency": urgency,
                "skills": skills, "education": education,
                "achievements": achievements, "resume_summary": resume_summary,
            }
            st.session_state.profile = profile
            st.session_state.results = {}
            st.session_state.agent_status = {a["id"]: "idle" for a in AGENTS}
            st.session_state.run_log = []
            st.session_state.orchestration_done = False
            st.session_state.total_runs += 1

            genai.configure(api_key=st.session_state._api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            ctx = build_base_context(profile)

            # ── PROGRESS UI ──
            progress_placeholder = st.empty()
            status_placeholder = st.empty()

            PIPELINE = [
                # Stage 1 – parallel intel gathering
                [("profile_analyst", f"""You are a career consultant. Analyse this candidate profile in depth.

{ctx}

Provide:
1. **Core Strengths** (top 5 with evidence)
2. **Skills Gap Analysis** (missing skills for target roles)
3. **Unique Value Proposition** (2–3 sentences, memorable)
4. **Positioning Strategy** (how to stand out in the market)
5. **Red Flags to Address** (gaps, job-hopping, etc.)
6. **Quick Wins** (3 things they can do TODAY to improve employability)

Be brutally honest and specific. Format with clear headers."""),

                ("market_researcher", f"""You are a job market analyst. Research the current market for:

Target Role(s): {target_roles}
Location: {location}
Remote Preference: {remote}

Provide:
1. **Market Demand** (hot vs cold, growth trend)
2. **Top 15 Hiring Companies** right now in this space (with why they're hiring)
3. **Salary Ranges** (junior/mid/senior breakdown)
4. **Most In-Demand Skills** (rank top 10)
5. **Job Boards to Prioritise** (ranked by effectiveness for this role)
6. **Best Time to Apply** and application volume tips
7. **Insider Tips** (what hiring managers actually look for)

Be specific with numbers and company names.""")],

                # Stage 2 – depends on stage 1
                [("job_matcher", f"""You are a talent matching specialist.

{ctx}

MARKET INTELLIGENCE:
{st.session_state.results.get('market_researcher','Pending')}

PROFILE ANALYSIS:
{st.session_state.results.get('profile_analyst','Pending')}

Generate:
1. **Top 10 Specific Job Titles** to apply for (with fit score 0–100 and reasoning)
2. **Top 5 Specific Companies** to target with application strategy per company
3. **Niche Opportunities** they might be overlooking
4. **Titles to AVOID** (why they'd be rejected)
5. **Pivot Opportunities** if they want adjacent roles

Format as a ranked list with scores.""")],

                # Stage 3 – all parallel document generation
                [("resume_agent", f"""You are an expert ATS resume writer and career coach.

{ctx}

JOB MATCH INTELLIGENCE:
{st.session_state.results.get('job_matcher','Pending')}

Rewrite their resume optimised for: {target_roles}

Produce:
1. **ATS-Optimised Professional Summary** (3–4 punchy sentences)
2. **Skills Section** (categorised, keyword-rich for ATS)
3. **Rewritten Experience Bullets** (STAR format, quantified, action verbs — at least 8 bullets)
4. **Key ATS Keywords** to include (list of 20)
5. **Resume Structure Advice** (order, length, format tips)
6. **What to Remove** from current resume

Make it compelling to both ATS and human recruiters."""),

                ("linkedin_agent", f"""You are a LinkedIn optimisation expert.

{ctx}

TARGET ROLES: {target_roles}

Produce a complete LinkedIn makeover:
1. **Headline** (3 variations, keyword-rich, <120 chars each)
2. **About Section** (full rewrite, 2000 chars, story-driven, keywords woven in)
3. **Skills Section** (top 20 skills to list in priority order)
4. **Featured Section** ideas (what to showcase)
5. **Connection Strategy** (who to connect with, how many per day)
6. **Content Strategy** (what to post to attract recruiters)
7. **Profile Completeness Checklist** (10 items)

Make the headline irresistible to recruiters."""),

                ("cover_letter_agent", f"""You are a master cover letter writer.

{ctx}

TOP TARGET ROLE: {target_roles.split(',')[0].strip() if target_roles else 'Target Role'}

PROFILE STRENGTHS:
{st.session_state.results.get('profile_analyst','Pending')}

Write 2 complete cover letters:

COVER LETTER 1 — "The Storyteller" (narrative, personal, memorable)
COVER LETTER 2 — "The Achiever" (data-driven, results-focused, punchy)

Each letter should be 300–400 words, ready to send with minor personalisation.
Include [COMPANY NAME] and [HIRING MANAGER] placeholders."""),

                ("outreach_agent", f"""You are a headhunting and outreach expert.

{ctx}

TARGET COMPANIES from job match:
{st.session_state.results.get('job_matcher','Pending')[:500] if st.session_state.results.get('job_matcher') else 'Various target companies'}

Write 5 outreach templates:
1. **Cold LinkedIn DM to Recruiter** (under 150 words)
2. **Cold LinkedIn DM to Hiring Manager** (under 200 words)
3. **Cold Email to Recruiter** (with subject line)
4. **Follow-Up Message** after applying (LinkedIn or email)
5. **Referral Request** to existing connection

For each: include subject line (if email), the full message, and a note on when/how to personalise.
Make them feel human, not templated.""")],

                # Stage 4 – final synthesis
                [("interview_agent", f"""You are a top interview coach.

{ctx}

TARGET ROLE: {target_roles}

Prepare the candidate for interviews:
1. **Top 15 Most Likely Interview Questions** for {target_roles}
2. **STAR Answer Templates** for top 5 behavioural questions (tailored to their background)
3. **Technical Questions** to expect (and how to approach them)
4. **Questions to ASK the Interviewer** (5 impressive questions)
5. **Salary Negotiation Script** (word-for-word for their expectation: {salary})
6. **Common Mistakes** to avoid in interviews for this role
7. **30-60-90 Day Plan** to pitch in final rounds

Make answers specific to their actual experience."""),

                ("action_planner", f"""You are a strategic career coach. Create an aggressive, realistic job hunt action plan.

{ctx}

MARKET INTELLIGENCE: {st.session_state.results.get('market_researcher','')[:300]}
JOB MATCHES: {st.session_state.results.get('job_matcher','')[:300]}
URGENCY: {urgency}

Create a **30-Day Job Hunt Sprint Plan**:

WEEK 1 – Foundation (Days 1–7): Setup, resume, LinkedIn, profiles
WEEK 2 – Launch (Days 8–14): Start applying, outreach begins
WEEK 3 – Scale (Days 15–21): Interviews, networking, follow-ups
WEEK 4 – Close (Days 22–30): Final rounds, negotiations, decision

For each week provide:
- Daily task list (specific, actionable, time-boxed)
- Target numbers (applications/day, outreach/day, etc.)
- Key milestones
- Mindset tips

End with a **Success Metrics Dashboard** (what good looks like each week).""")],
            ]

            # Run pipeline stage by stage
            total_agents = len(AGENTS)
            completed = 0

            for stage_idx, stage in enumerate(PIPELINE):
                stage_name = ["Intel Gathering", "Role Matching", "Document Generation", "Final Prep"][stage_idx]
                status_placeholder.markdown(f"**⚙️ Stage {stage_idx+1}/4 — {stage_name}** ({len(stage)} agent{'s' if len(stage)>1 else ''} running)")

                for agent_id, prompt in stage:
                    st.session_state.agent_status[agent_id] = "running"

                for agent_id, prompt in stage:
                    run_agent(model, agent_id, prompt)
                    completed += 1
                    progress_placeholder.progress(completed / total_agents, text=f"Completed {completed}/{total_agents} agents")

            # Final synthesis
            status_placeholder.markdown("**⚙️ Synthesizing master plan…**")
            synthesis_prompt = f"""You are a chief career strategist. Synthesise ALL the agent outputs below into a single executive summary.

{ctx}

OUTPUTS AVAILABLE:
- Profile Analysis: {st.session_state.results.get('profile_analyst','')[:400]}
- Market Research: {st.session_state.results.get('market_researcher','')[:400]}
- Job Matches: {st.session_state.results.get('job_matcher','')[:400]}
- Action Plan: {st.session_state.results.get('action_planner','')[:400]}

Create a **Master Job Hunt Brief** with:
1. **Executive Summary** (3 sentences: who they are, what they want, why they'll get it)
2. **The #1 Priority Action** to take TODAY
3. **Top 3 Roles to Apply For This Week** (specific job titles + companies)
4. **Critical Success Factors** (top 5 things that will determine success)
5. **Timeline Prediction** (realistic timeline to first offer given urgency: {urgency})
6. **The Winning Strategy** in 1 paragraph

Keep it concise, motivating, and actionable."""

            genai.configure(api_key=st.session_state._api_key)
            synth_model = genai.GenerativeModel("gemini-2.5-flash")
            synth_resp = synth_model.generate_content(synthesis_prompt)
            st.session_state.final_plan = synth_resp.text

            st.session_state.orchestration_done = True
            progress_placeholder.progress(1.0, text="✅ All agents complete!")
            status_placeholder.success("🎉 Orchestration complete! Go to **Results** page.")
            log("Full orchestration completed", "success")

    # ── Agent Status Grid ──
    if st.session_state.agent_status:
        st.markdown('<div class="slbl">Agent Pipeline Status</div>', unsafe_allow_html=True)
        cols = st.columns(3)
        for i, agent in enumerate(AGENTS):
            status = st.session_state.agent_status.get(agent["id"], "idle")
            bg, border = COLOR_MAP.get(agent["color"], COLOR_MAP["accent"])
            status_css = f"status-{status}"
            card_css = f"agent-card {status}"
            status_label = {"idle": "IDLE", "running": "RUNNING…", "done": "DONE", "error": "ERROR"}.get(status, "IDLE")

            with cols[i % 3]:
                st.markdown(f"""
                <div class="{card_css}" style="background:{bg};border-color:{border}">
                    <div class="agent-status {status_css}">{status_label}</div>
                    <div class="agent-title">{agent['name']}</div>
                    <div class="agent-desc">{agent['role']}</div>
                </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# PAGE: RESULTS
# ══════════════════════════════════════════════════════════
elif "Results" in page:
    st.markdown("# 📋 AGENT RESULTS")

    if not st.session_state.results:
        st.info("No results yet. Run the orchestrator first.")
    else:
        # Master Plan first
        if st.session_state.final_plan:
            st.markdown("## 🗺️ Master Job Hunt Brief")
            st.markdown('<div class="output-box">', unsafe_allow_html=True)
            st.markdown(st.session_state.final_plan)
            st.markdown('</div>', unsafe_allow_html=True)
            st.download_button(
                "📥 Download Master Brief",
                data=st.session_state.final_plan,
                file_name="job_hunt_master_brief.md",
                mime="text/markdown",
                use_container_width=True
            )
            st.markdown("---")

        # Individual agent results
        color_class = {"accent": "", "blue": "blue", "green": "green", "yellow": "yellow"}
        for agent in AGENTS:
            aid = agent["id"]
            result = st.session_state.results.get(aid)
            if not result:
                continue
            cc = color_class.get(agent["color"], "")
            with st.expander(f"{agent['name']}  ·  {len(result.splitlines())} lines", expanded=False):
                st.markdown(f'<div class="output-box {cc}">', unsafe_allow_html=True)
                st.markdown(result)
                st.markdown('</div>', unsafe_allow_html=True)
                st.download_button(
                    f"📥 Download {agent['name'].split(' ',1)[1]}",
                    data=result,
                    file_name=f"{aid}.md",
                    mime="text/markdown",
                    key=f"dl_{aid}"
                )

        # Combined download
        if len(st.session_state.results) >= 3:
            st.markdown("---")
            all_text = f"# JOB HUNT COMPLETE PACKAGE\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            if st.session_state.final_plan:
                all_text += f"## MASTER BRIEF\n{st.session_state.final_plan}\n\n---\n\n"
            for agent in AGENTS:
                r = st.session_state.results.get(agent["id"])
                if r:
                    all_text += f"## {agent['name'].upper()}\n{r}\n\n---\n\n"
            st.download_button(
                "📦 Download Complete Job Hunt Package (.md)",
                data=all_text,
                file_name="job_hunt_complete_package.md",
                mime="text/markdown",
                use_container_width=True
            )


# ══════════════════════════════════════════════════════════
# PAGE: TRACKER
# ══════════════════════════════════════════════════════════
elif "Tracker" in page:
    st.markdown("# 📊 APPLICATION TRACKER")
    st.caption("Track your applications manually while the agents do the strategy work")

    with st.form("add_application"):
        st.markdown('<div class="slbl">Add Application</div>', unsafe_allow_html=True)
        tc1, tc2, tc3 = st.columns(3)
        with tc1:
            t_company = st.text_input("Company *")
            t_role = st.text_input("Role *")
        with tc2:
            t_status = st.selectbox("Status", ["Applied", "Phone Screen", "Interview", "Final Round", "Offer", "Rejected", "Ghosted"])
            t_date = st.date_input("Date Applied", value=datetime.today())
        with tc3:
            t_salary = st.text_input("Salary Offered", placeholder="e.g. £65k")
            t_notes = st.text_input("Notes", placeholder="Recruiter name, source, etc.")

        if st.form_submit_button("➕ Add Application", use_container_width=True):
            if t_company and t_role:
                st.session_state.tracker.append({
                    "company": t_company, "role": t_role,
                    "status": t_status, "date": str(t_date),
                    "salary": t_salary, "notes": t_notes
                })
                st.success(f"Added: {t_role} @ {t_company}")
                st.rerun()

    tracker = st.session_state.tracker
    if tracker:
        # Stats
        st.markdown('<div class="slbl">Pipeline Stats</div>', unsafe_allow_html=True)
        statuses = [t["status"] for t in tracker]
        sc1, sc2, sc3, sc4, sc5 = st.columns(5)
        sc1.markdown(f'<div class="mbox"><div class="mval">{len(tracker)}</div><div class="mlbl">Total</div></div>', unsafe_allow_html=True)
        sc2.markdown(f'<div class="mbox"><div class="mval">{statuses.count("Interview") + statuses.count("Final Round")}</div><div class="mlbl">Interviews</div></div>', unsafe_allow_html=True)
        sc3.markdown(f'<div class="mbox"><div class="mval">{statuses.count("Offer")}</div><div class="mlbl">Offers</div></div>', unsafe_allow_html=True)
        sc4.markdown(f'<div class="mbox"><div class="mval">{statuses.count("Rejected")}</div><div class="mlbl">Rejected</div></div>', unsafe_allow_html=True)
        interview_rate = round((statuses.count("Interview") + statuses.count("Final Round") + statuses.count("Offer")) / len(tracker) * 100) if tracker else 0
        sc5.markdown(f'<div class="mbox"><div class="mval">{interview_rate}%</div><div class="mlbl">Interview Rate</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="slbl">Applications</div>', unsafe_allow_html=True)
        STATUS_COLOR = {
            "Applied": "tag", "Phone Screen": "tag-blue", "Interview": "tag-yellow",
            "Final Round": "tag-yellow", "Offer": "tag-green", "Rejected": "tag-red", "Ghosted": "tag-red"
        }
        for i, app in enumerate(reversed(tracker)):
            sc = STATUS_COLOR.get(app["status"], "tag")
            with st.expander(f"**{app['role']}** @ {app['company']}  |  {app['date']}", expanded=False):
                st.markdown(
                    f'<span class="{sc}">{app["status"]}</span> '
                    f'{"  <span class=\"tag-blue\">" + app["salary"] + "</span>" if app["salary"] else ""} '
                    f'{"  <span style=\"color:var(--muted);font-size:13px;\">" + app["notes"] + "</span>" if app["notes"] else ""}',
                    unsafe_allow_html=True
                )
                if st.button("🗑️ Remove", key=f"rm_{i}"):
                    actual_idx = len(tracker) - 1 - i
                    st.session_state.tracker.pop(actual_idx)
                    st.rerun()
    else:
        st.info("No applications tracked yet. Add your first one above!")


# ══════════════════════════════════════════════════════════
# PAGE: RUN LOG
# ══════════════════════════════════════════════════════════
elif "Log" in page:
    st.markdown("# 📜 ORCHESTRATION RUN LOG")
    if not st.session_state.run_log:
        st.info("No runs yet.")
    else:
        for entry in st.session_state.run_log:
            st.markdown(entry)
        if st.button("Clear Log"):
            st.session_state.run_log = []
            st.rerun()
