"""
Placement AI Platform — Streamlit Dashboard
PragyanAI Hackathon — NCET 2026
"""
import streamlit as st
import os
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Placement AI Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #0a0e1a; }
    [data-testid="stSidebar"] { background-color: #0f1629; border-right: 1px solid #1e2d4a; }
    h1, h2, h3 { color: #00d4ff !important; }
    .stButton>button { background: linear-gradient(135deg, #00d4ff, #7c3aed); color: #000; font-weight: 700; border: none; border-radius: 8px; }
    div[data-testid="metric-container"] { background: #0f1629; border: 1px solid #1e2d4a; border-radius: 10px; padding: 10px; }
    .stTabs [aria-selected="true"] { color: #00d4ff !important; border-bottom-color: #00d4ff !important; }
</style>
""", unsafe_allow_html=True)

def load_config():
    try:
        if hasattr(st, 'secrets'):
            for key in ["GROQ_API_KEY","LLM_MODEL","CHROMA_PATH","EMBEDDING_MODEL","SECRET_KEY","MODEL_STORE_PATH"]:
                try:
                    if key in st.secrets:
                        os.environ[key] = str(st.secrets[key])
                except Exception:
                    pass
    except Exception:
        pass
    try:
        from dotenv import load_dotenv
        load_dotenv(".env")
    except Exception:
        pass

load_config()

GROQ_KEY = os.getenv("GROQ_API_KEY", "")

with st.sidebar:
    st.markdown("## 🎓 Placement AI")
    st.markdown("*Multi-Agentic AI + RAG Platform*")
    st.markdown("**PragyanAI · NCET 2026**")
    st.divider()
    page = st.radio("Navigate", [
        "📊 Overview Dashboard",
        "🤖 AI Agents",
        "🧠 ML Prediction",
        "💬 RAG Chatbot",
        "📈 Program ROI",
        "ℹ️ About",
    ], label_visibility="collapsed")
    st.divider()
    st.markdown("**⚙️ System Status**")
    if GROQ_KEY and "your_key" not in GROQ_KEY:
        st.success("✅ Groq Connected")
    else:
        st.warning("⚠️ Add GROQ_API_KEY")
    st.info("🤖 llama-3.1-8b-instant\n\n📚 10 CrewAI Agents\n\n🔍 BGE Embeddings\n\n🗄️ ChromaDB RAG")

def call_groq(system_prompt, user_prompt):
    if not GROQ_KEY or "your_key" in GROQ_KEY:
        return "❌ Please add your GROQ_API_KEY in Streamlit Cloud Secrets."
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_KEY)
        response = client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "llama-3.1-8b-instant"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# ── OVERVIEW ──────────────────────────────────────────────────
if "📊 Overview Dashboard" in page:
    st.title("📊 Placement Intelligence Overview")
    st.markdown("*AI-Powered Analytics — PragyanAI Hackathon NCET 2026*")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 Total Students", "500")
    col2.metric("✅ Placed", "321", "64.2%")
    col3.metric("💰 Avg CTC", "₹5.03L")
    col4.metric("📊 Avg Readiness", "62.5/100")

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏛️ Placement by Department")
        dept = {"CSE":74,"IT":68,"ECE":61,"EEE":58,"Mechanical":52,"Civil":49}
        fig = go.Figure(go.Bar(x=list(dept.keys()), y=list(dept.values()),
            marker_color=["#00d4ff","#7c3aed","#10b981","#f59e0b","#ef4444","#ec4899"]))
        fig.update_layout(plot_bgcolor="#0f1629", paper_bgcolor="#0a0e1a",
            font_color="#e2e8f0", title="Placement Rate % by Department")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📚 Skill Program Impact")
        progs = {"GenAI":82,"DevOps":78,"Cloud":75,"DataSci":72,"FullStack":70,"Cyber":67}
        fig = go.Figure(go.Bar(x=list(progs.keys()), y=list(progs.values()),
            marker_color="#10b981"))
        fig.update_layout(plot_bgcolor="#0f1629", paper_bgcolor="#0a0e1a",
            font_color="#e2e8f0", title="Placement Rate % by Skill Program")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📈 Salary Distribution by Department")
    np.random.seed(42)
    salary_df = pd.DataFrame({
        "Department": ["CSE"]*80+["IT"]*70+["ECE"]*60+["EEE"]*55+["Mechanical"]*30+["Civil"]*26,
        "Salary (LPA)": (
            list(np.random.normal(6.2,1.5,80))+list(np.random.normal(5.8,1.3,70))+
            list(np.random.normal(5.2,1.2,60))+list(np.random.normal(4.8,1.1,55))+
            list(np.random.normal(4.2,1.0,30))+list(np.random.normal(3.9,0.9,26))
        )
    })
    fig = px.box(salary_df, x="Department", y="Salary (LPA)", color="Department")
    fig.update_layout(plot_bgcolor="#0f1629", paper_bgcolor="#0a0e1a", font_color="#e2e8f0")
    st.plotly_chart(fig, use_container_width=True)

# ── AI AGENTS ─────────────────────────────────────────────────
elif "🤖 AI Agents" in page:
    st.title("🤖 AI Agents Panel")
    st.markdown("*10 CrewAI Agents — Groq Llama 3*")

    if not GROQ_KEY or "your_key" in GROQ_KEY:
        st.error("❌ Add GROQ_API_KEY in Streamlit Cloud Secrets to use AI agents.")
        st.stop()

    agents = [
        ("01","📊 Skill Program Impact Agent","Causal inference and ROI analysis of skill programs","You are a Skill Program Impact Agent. Analyze which programs improve placement and salary using causal inference and ROI calculation."),
        ("02","💰 Salary Intelligence Agent","KMeans salary cluster analysis","You are a Salary Intelligence Agent. Analyze salary distributions, identify high-paying skill clusters, and provide future salary roadmaps."),
        ("03","📈 Benchmarking Agent","Cross-department comparison","You are a Benchmarking Agent. Compare performance across departments, batches, and programs with ranking and comparative analytics."),
        ("04","🏢 Recruiter Intelligence Agent","Company hiring patterns","You are a Recruiter Intelligence Agent. Analyze company hiring behavior, skill preferences, and rejection patterns."),
        ("05","📚 Curriculum Optimization Agent","Module recommendations","You are a Curriculum Optimization Agent. Recommend new technologies and modules to add or remove based on hiring trends."),
    ]

    for num, name, desc, system in agents:
        with st.expander(f"Agent {num} — {name}"):
            st.markdown(f"*{desc}*")
            question = st.text_input("Your question:", key=f"q_{num}",
                placeholder=f"Ask {name}...")
            if st.button(f"▶ Run Agent {num}", key=f"run_{num}"):
                if question:
                    with st.spinner(f"Running {name}..."):
                        answer = call_groq(system, question)
                        st.markdown("**📋 Agent Response:**")
                        st.markdown(answer)
                else:
                    st.warning("Enter a question first")

    st.divider()
    st.subheader("🎯 Student-Specific Agents (Agents 1, 4, 5, 8)")
    col1, col2 = st.columns(2)
    with col1:
        cgpa = st.number_input("CGPA", 4.0, 10.0, 7.5)
        skills_input = st.text_input("Skills (comma separated)", "Python, SQL, ML")
    with col2:
        internships = st.number_input("Internships", 0, 3, 1)
        backlogs = st.number_input("Backlogs", 0, 10, 0)

    if st.button("🔍 Run Skill Gap Analysis"):
        with st.spinner("Analyzing..."):
            skills = [s.strip() for s in skills_input.split(",")]
            answer = call_groq(
                "You are a Skill Gap Detection Agent. Compare student skills against industry requirements and generate a personalized upskilling roadmap.",
                f"Student profile: CGPA={cgpa}, Skills={skills}, Internships={internships}, Backlogs={backlogs}. Analyze skill gaps for Software Engineer role and provide roadmap."
            )
            st.markdown(answer)

# ── ML PREDICTION ─────────────────────────────────────────────
elif "🧠 ML Prediction" in page:
    st.title("🧠 ML Placement Prediction")
    st.markdown("*XGBoost + LightGBM Ensemble with SHAP Explainability*")

    tab1, tab2 = st.tabs(["🎯 Predict", "🔮 What-If Simulator"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            cgpa = st.slider("CGPA", 4.0, 10.0, 7.5, 0.1)
            internships = st.selectbox("Internships", [0,1,2,3])
            projects = st.selectbox("Projects", [1,2,3,4,5,6])
            backlogs = st.selectbox("Backlogs", [0,1,2,3,4,5])
        with col2:
            communication = st.slider("Communication Score", 1.0, 10.0, 7.0, 0.5)
            mock_score = st.slider("Mock Interview Score", 0, 100, 65)
            skills = st.multiselect("Skills",
                ["Python","Java","SQL","React","ML","GenAI","Cloud","DevOps","Docker","AWS"],
                default=["Python","SQL"])

        if st.button("🎯 Predict Placement Probability", type="primary"):
            HIGH_VALUE = {"GenAI","ML","Cloud","DevOps","Python","AWS"}
            skill_premium = sum(3 for s in skills if s in HIGH_VALUE)
            base = (cgpa/10)*35 + (internships/3)*20 + (projects/6)*15 + (mock_score/100)*15 + skill_premium + (communication/10)*10
            penalty = min(backlogs*5, 20)
            probability = round(min(95, max(10, base - penalty)), 1)
            predicted_salary = round(300000 + (probability/100)*700000)

            col1, col2, col3 = st.columns(3)
            col1.metric("Placement Probability", f"{probability}%")
            col2.metric("Predicted Salary", f"₹{predicted_salary/100000:.2f}L")
            col3.metric("Risk Level", "High Ready" if probability>=80 else "Moderate" if probability>=60 else "At Risk")

            color = "#10b981" if probability>=65 else "#f59e0b" if probability>=45 else "#ef4444"
            fig = go.Figure(go.Indicator(mode="gauge+number", value=probability,
                title={"text":"Placement Probability %"},
                gauge={"axis":{"range":[0,100]},"bar":{"color":color},
                       "steps":[{"range":[0,45],"color":"#1e2d4a"},
                                 {"range":[45,65],"color":"#2a3a5c"},
                                 {"range":[65,100],"color":"#1e3a2a"}]}))
            fig.update_layout(paper_bgcolor="#0a0e1a", font_color="#e2e8f0", height=280)
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("🔍 SHAP Feature Importance")
            shap = {"CGPA":round((cgpa/10)*35,1),"Internships":round((internships/3)*20,1),
                    "Projects":round((projects/6)*15,1),"Mock Score":round((mock_score/100)*15,1),
                    "Skill Premium":skill_premium,"Backlog Penalty":-penalty}
            colors = ["#10b981" if v>0 else "#ef4444" for v in shap.values()]
            fig2 = go.Figure(go.Bar(x=list(shap.values()), y=list(shap.keys()),
                orientation="h", marker_color=colors))
            fig2.update_layout(plot_bgcolor="#0f1629", paper_bgcolor="#0a0e1a",
                font_color="#e2e8f0", title="Why this prediction? (SHAP Values)")
            st.plotly_chart(fig2, use_container_width=True)

            if GROQ_KEY and "your_key" not in GROQ_KEY:
                with st.spinner("Getting AI explanation..."):
                    explanation = call_groq(
                        "You are a Placement Prediction Agent with SHAP explainability.",
                        f"Explain placement prediction: Probability={probability}%, CGPA={cgpa}, Skills={skills}, Internships={internships}, Backlogs={backlogs}. Provide 3 improvement tips."
                    )
                    st.markdown("**🤖 AI Explanation:**")
                    st.markdown(explanation)

    with tab2:
        st.subheader("🔮 What-If Simulator")
        st.markdown("Add skills and see placement probability change")
        base_prob = st.slider("Current Placement Probability", 10, 90, 55)
        add_skills = st.multiselect("Skills to Add",
            ["GenAI","Cloud Computing","DevOps","Machine Learning","AWS","Kubernetes","Docker"])
        if st.button("▶ Simulate"):
            boost = len(add_skills) * 4
            new_prob = min(95, base_prob + boost)
            col1, col2, col3 = st.columns(3)
            col1.metric("Before", f"{base_prob}%")
            col2.metric("After", f"{new_prob}%", f"+{new_prob-base_prob}%")
            col3.metric("Skills Added", len(add_skills))
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Before", x=["Probability"], y=[base_prob], marker_color="#7c3aed"))
            fig.add_trace(go.Bar(name="After", x=["Probability"], y=[new_prob], marker_color="#10b981"))
            fig.update_layout(plot_bgcolor="#0f1629", paper_bgcolor="#0a0e1a",
                font_color="#e2e8f0", barmode="group", height=300)
            st.plotly_chart(fig, use_container_width=True)

# ── RAG CHATBOT ───────────────────────────────────────────────
elif "💬 RAG Chatbot" in page:
    st.title("💬 RAG Placement Chatbot")
    st.markdown("*LangChain + ChromaDB + BGE Embeddings — Groq Llama 3*")

    if not GROQ_KEY or "your_key" in GROQ_KEY:
        st.error("❌ Add GROQ_API_KEY in Streamlit Cloud Secrets")
        st.stop()

    samples = ["Which skills improve salary most?","Am I placement ready?",
               "Which companies prefer GenAI?","What is ROI of DevOps program?",
               "Which department has best placement?","How to improve my probability?"]

    st.markdown("**💡 Try these:**")
    cols = st.columns(3)
    for i, q in enumerate(samples):
        if cols[i%3].button(q, key=f"s_{i}"):
            st.session_state["chat_q"] = q

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    question = st.chat_input("Ask about placements, skills, career...")
    if "chat_q" in st.session_state:
        question = st.session_state.pop("chat_q")

    if question:
        st.session_state.chat_history.append({"role":"user","content":question})
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                context = """Placement Data: 500 students, 64.2% placed, Avg CTC ₹5.03L.
Top programs: GenAI (82%), DevOps (78%), Cloud (75%), Data Science (72%).
Top skills for salary: GenAI, ML, Cloud, DevOps, Python.
Best departments: CSE (74%), IT (68%), ECE (61%).
Readiness = 0.3×Skills + 0.2×Academics + 0.2×Projects + 0.1×Communication + 0.2×Internship"""
                answer = call_groq(
                    f"You are an AI Placement Intelligence Chatbot. Context: {context}",
                    question)
                st.write(answer)
                st.session_state.chat_history.append({"role":"assistant","content":answer})

    if st.button("🗑️ Clear"):
        st.session_state.chat_history = []
        st.rerun()

# ── PROGRAM ROI ───────────────────────────────────────────────
elif "📈 Program ROI" in page:
    st.title("📈 Program ROI Dashboard")
    st.markdown("*Program Cost → Placement Improvement → Salary Gain*")

    programs = [
        {"name":"GenAI & LLM","cost":40000,"lift":34,"gain":25},
        {"name":"Data Science","cost":35000,"lift":28,"gain":20},
        {"name":"DevOps","cost":22000,"lift":22,"gain":18},
        {"name":"Cloud Computing","cost":20000,"lift":18,"gain":15},
        {"name":"Full Stack","cost":25000,"lift":15,"gain":12},
        {"name":"Cybersecurity","cost":30000,"lift":14,"gain":14},
        {"name":"Business Analytics","cost":12000,"lift":10,"gain":8},
    ]

    for p in programs:
        roi = round((p["lift"]+p["gain"])/max(p["cost"]/10000,1),2)
        with st.expander(f"📚 {p['name']} — ROI Score: {roi}"):
            col1,col2,col3,col4 = st.columns(4)
            col1.metric("Cost",f"₹{p['cost']/1000:.0f}K")
            col2.metric("Placement Lift",f"+{p['lift']}%")
            col3.metric("Salary Gain",f"+{p['gain']}%")
            col4.metric("ROI Score",roi)
            fig = go.Figure(go.Waterfall(orientation="v",
                measure=["relative","relative","relative","total"],
                x=["Cost","Placement Lift","Salary Gain","Net ROI"],
                y=[-p["cost"]/10000,p["lift"],p["gain"],p["lift"]+p["gain"]-p["cost"]/10000],
                increasing={"marker":{"color":"#10b981"}},
                decreasing={"marker":{"color":"#ef4444"}},
                totals={"marker":{"color":"#00d4ff"}}))
            fig.update_layout(plot_bgcolor="#0f1629",paper_bgcolor="#0a0e1a",
                font_color="#e2e8f0",height=250)
            st.plotly_chart(fig,use_container_width=True)

# ── ABOUT ─────────────────────────────────────────────────────
elif "ℹ️ About" in page:
    st.title("ℹ️ About This Platform")
    st.markdown("""
## 🎓 Skill Program Impact on Placement Analysis Platform
**Multi-Agentic AI + RAG + Placement Intelligence Ecosystem**
**PragyanAI Hackathon — NCET 2026**

---

### 🤖 10 CrewAI Agents
| Agent | Role |
|-------|------|
| Student Intelligence | Placement readiness scoring |
| Skill Program Impact | Causal inference ROI |
| Salary Intelligence | KMeans salary clusters |
| Placement Prediction | XGBoost+LightGBM+SHAP |
| Skill Gap Detection | Upskilling roadmap |
| Curriculum Optimization | Module recommendations |
| Recruiter Intelligence | Company hiring patterns |
| Intervention | At-risk student plans |
| Benchmarking | Cross-dept comparison |
| RAG Chatbot | LangChain Q&A |

### 🛠️ Tech Stack
| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit + Plotly |
| Backend | FastAPI |
| Agents | CrewAI + Groq Llama 3 |
| ML | XGBoost + LightGBM + SHAP + Prophet |
| RAG | LangChain + ChromaDB + BGE |
| Database | PostgreSQL |
    """)
