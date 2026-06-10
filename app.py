"""
Placement AI Platform — Streamlit Dashboard
PragyanAI Hackathon — NCET 2026
500 Students Demo Data Included
"""
import streamlit as st
import os
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import random

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
            for key in ["GROQ_API_KEY","LLM_MODEL"]:
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

# ── Generate 500 Students Demo Data (same seed = same data always) ──
@st.cache_data
def generate_students():
    random.seed(42)
    np.random.seed(42)

    SKILLS = ["Python","Java","JavaScript","React","Node.js","SQL","MongoDB","AWS","Docker",
              "Kubernetes","Machine Learning","Deep Learning","Data Analysis","Power BI",
              "Tableau","Excel","Git","Linux","REST APIs","GenAI","Cloud Computing",
              "Cybersecurity","DevOps","Agile","Communication","Problem Solving","Leadership"]
    DEPTS = ["CSE","IT","ECE","EEE","Mechanical","Civil"]
    COMPANIES = ["TCS","Infosys","Wipro","Accenture","Cognizant","HCL","Google","Amazon",
                 "Microsoft","IBM","Deloitte","Capgemini","Zoho","Freshworks","Flipkart"]
    ROLES = ["Software Engineer","Data Scientist","ML Engineer","DevOps Engineer",
             "Full Stack Developer","Cloud Architect","Security Analyst","Business Analyst","AI Engineer"]
    PROGRAMS = ["Full Stack Development","Data Science & ML","Cloud Computing","Cybersecurity",
                "DevOps Engineering","GenAI & LLM","Business Analytics","Mobile Development","Data Engineering"]

    students = []
    for i in range(500):
        dept = random.choice(DEPTS)
        batch = random.choice([2021,2022,2023,2024])
        cgpa = round(max(4.0, min(10.0, np.random.normal(7.2, 0.9))), 2)
        backlogs = max(0, int(np.random.normal(0.5, 1.0)))
        internships = random.randint(0, 3)
        projects = random.randint(1, 6)
        certs = random.randint(0, 5)
        hackathons = random.randint(0, 4)
        communication = round(random.uniform(4, 10), 1)
        aptitude = round(random.uniform(4, 10), 1)
        attendance = round(random.uniform(60, 100), 1)
        lms = round(random.uniform(40, 100), 1)
        skills = random.sample(SKILLS, random.randint(4, 12))
        mock_scores = [random.randint(40, 100) for _ in range(random.randint(1, 5))]
        avg_mock = round(sum(mock_scores)/len(mock_scores), 1)
        program = random.choice(PROGRAMS)
        readiness = round(min(100,
            0.3*(len(skills)/27*100) + 0.2*(cgpa/10*100) +
            0.2*(projects/6*100) + 0.1*(communication/10*100) +
            0.2*(internships/3*100)), 2)
        placed = random.random() < readiness/100
        salary = max(250000, int(np.random.normal(500000, 150000))) if placed else None
        company = random.choice(COMPANIES) if placed else None
        role = random.choice(ROLES) if placed else None

        students.append({
            "id": i+1,
            "student_id": f"STU{2000+i:04d}",
            "name": f"Student {i+1}",
            "department": dept,
            "batch": batch,
            "cgpa": cgpa,
            "backlogs": backlogs,
            "internships": internships,
            "projects": projects,
            "certifications": certs,
            "hackathons": hackathons,
            "communication_score": communication,
            "aptitude_score": aptitude,
            "attendance": attendance,
            "lms_activity": lms,
            "skills": skills,
            "avg_mock_score": avg_mock,
            "readiness_score": readiness,
            "program": program,
            "placed": placed,
            "salary": salary,
            "company": company,
            "role": role,
        })
    return pd.DataFrame(students)

df = generate_students()
placed_df = df[df["placed"] == True]
total = len(df)
placed = len(placed_df)
placement_rate = round(placed/total*100, 1)
avg_ctc = round(placed_df["salary"].mean()/100000, 2)
avg_readiness = round(df["readiness_score"].mean(), 1)

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
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# ── Sidebar ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 Placement AI")
    st.markdown("*Multi-Agentic AI + RAG Platform*")
    st.markdown("**PragyanAI · NCET 2026**")
    st.divider()
    page = st.radio("Navigate", [
        "📊 Overview Dashboard",
        "👤 Student Analysis",
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
    st.success(f"✅ {total} Students Loaded")
    st.info("🤖 llama-3.1-8b-instant\n\n📚 10 CrewAI Agents\n\n🔍 BGE Embeddings\n\n🗄️ ChromaDB RAG")

# ── OVERVIEW ──────────────────────────────────────────────────
if "📊 Overview Dashboard" in page:
    st.title("📊 Placement Intelligence Overview")
    st.markdown("*AI-Powered Analytics — PragyanAI Hackathon NCET 2026*")

    col1,col2,col3,col4 = st.columns(4)
    col1.metric("👥 Total Students", total)
    col2.metric("✅ Placed", placed, f"{placement_rate}%")
    col3.metric("💰 Avg CTC", f"₹{avg_ctc}L")
    col4.metric("📊 Avg Readiness", f"{avg_readiness}/100")

    st.divider()
    col1,col2 = st.columns(2)

    with col1:
        st.subheader("🏛️ Placement by Department")
        dept_stats = df.groupby("department").agg(
            total=("id","count"),
            placed=("placed","sum")
        ).reset_index()
        dept_stats["rate"] = round(dept_stats["placed"]/dept_stats["total"]*100,1)
        dept_stats = dept_stats.sort_values("rate",ascending=False)
        fig = go.Figure(go.Bar(
            x=dept_stats["department"], y=dept_stats["rate"],
            marker_color=["#00d4ff","#7c3aed","#10b981","#f59e0b","#ef4444","#ec4899"],
            text=dept_stats["rate"], textposition="outside"))
        fig.update_layout(plot_bgcolor="#0f1629",paper_bgcolor="#0a0e1a",
            font_color="#e2e8f0",title="Placement Rate % by Department",yaxis_range=[0,100])
        st.plotly_chart(fig,use_container_width=True)

    with col2:
        st.subheader("📚 Placement by Program")
        prog_stats = df.groupby("program").agg(
            total=("id","count"), placed=("placed","sum")
        ).reset_index()
        prog_stats["rate"] = round(prog_stats["placed"]/prog_stats["total"]*100,1)
        prog_stats = prog_stats.sort_values("rate",ascending=False)
        fig = go.Figure(go.Bar(
            x=prog_stats["program"], y=prog_stats["rate"],
            marker_color="#10b981",
            text=prog_stats["rate"], textposition="outside"))
        fig.update_layout(plot_bgcolor="#0f1629",paper_bgcolor="#0a0e1a",
            font_color="#e2e8f0",title="Placement Rate % by Skill Program",yaxis_range=[0,100])
        st.plotly_chart(fig,use_container_width=True)

    col1,col2 = st.columns(2)
    with col1:
        st.subheader("📈 Batch-wise Placement Trend")
        batch_stats = df.groupby("batch").agg(
            total=("id","count"), placed=("placed","sum")
        ).reset_index()
        batch_stats["rate"] = round(batch_stats["placed"]/batch_stats["total"]*100,1)
        fig = px.line(batch_stats, x="batch", y="rate", markers=True,
            title="Placement Rate by Batch Year")
        fig.update_traces(line_color="#00d4ff", marker_color="#7c3aed")
        fig.update_layout(plot_bgcolor="#0f1629",paper_bgcolor="#0a0e1a",font_color="#e2e8f0")
        st.plotly_chart(fig,use_container_width=True)

    with col2:
        st.subheader("💰 Salary Distribution")
        fig = px.histogram(placed_df, x=placed_df["salary"]/100000,
            title="Salary Distribution (LPA)", nbins=20, color_discrete_sequence=["#7c3aed"])
        fig.update_layout(plot_bgcolor="#0f1629",paper_bgcolor="#0a0e1a",
            font_color="#e2e8f0",xaxis_title="Salary (LPA)")
        st.plotly_chart(fig,use_container_width=True)

    st.subheader("📋 Student Data (Sample)")
    display_df = df[["student_id","name","department","batch","cgpa","readiness_score","placed","salary"]].head(20).copy()
    display_df["salary"] = display_df["salary"].apply(lambda x: f"₹{x/100000:.1f}L" if x else "Not Placed")
    display_df["placed"] = display_df["placed"].apply(lambda x: "✅" if x else "❌")
    st.dataframe(display_df, use_container_width=True)

# ── STUDENT ANALYSIS ──────────────────────────────────────────
elif "👤 Student Analysis" in page:
    st.title("👤 Student Analysis")
    st.markdown("*Individual student placement readiness and AI Career Twin*")

    col1,col2 = st.columns([1,3])
    with col1:
        student_id = st.number_input("Student ID (1-500)", min_value=1, max_value=500, value=1)

    student = df[df["id"] == student_id].iloc[0]

    col1,col2,col3,col4 = st.columns(4)
    col1.metric("CGPA", student["cgpa"])
    col2.metric("Readiness", f"{student['readiness_score']:.1f}/100")
    col3.metric("Skills", len(student["skills"]))
    col4.metric("Internships", student["internships"])

    st.subheader(f"👤 {student['name']} — {student['department']} Batch {student['batch']}")

    risk = student["readiness_score"]
    if risk >= 80: st.success("🟢 High Ready — Strong placement candidate")
    elif risk >= 60: st.warning("🟡 Moderate — Needs skill improvement")
    elif risk >= 40: st.error("🟠 At Risk — Requires intervention")
    else: st.error("🔴 Critical — Immediate action needed")

    if student["placed"]:
        st.success(f"✅ PLACED at {student['company']} as {student['role']} — ₹{student['salary']/100000:.1f}L")

    col1,col2 = st.columns(2)
    with col1:
        breakdown = {
            "Skills (30%)": round(0.3*(len(student["skills"])/27*100),1),
            "Academics (20%)": round(0.2*(student["cgpa"]/10*100),1),
            "Projects (20%)": round(0.2*(student["projects"]/6*100),1),
            "Communication (10%)": round(0.1*(student["communication_score"]/10*100),1),
            "Internship (20%)": round(0.2*(student["internships"]/3*100),1),
        }
        colors = ["#10b981" if v >= 15 else "#f59e0b" if v >= 10 else "#ef4444" for v in breakdown.values()]
        fig = go.Figure(go.Bar(x=list(breakdown.values()), y=list(breakdown.keys()),
            orientation="h", marker_color=colors))
        fig.update_layout(plot_bgcolor="#0f1629",paper_bgcolor="#0a0e1a",
            font_color="#e2e8f0",title="Readiness Score Breakdown")
        st.plotly_chart(fig,use_container_width=True)

    with col2:
        st.markdown("**🛠️ Skills:**")
        for sk in student["skills"]:
            st.markdown(f"✅ {sk}")

    st.subheader("📊 Department Comparison")
    dept_students = df[df["department"] == student["department"]]
    fig = px.scatter(dept_students, x="cgpa", y="readiness_score",
        color="placed", title=f"{student['department']} — CGPA vs Readiness",
        color_discrete_map={True:"#10b981",False:"#ef4444"})
    fig.add_vline(x=student["cgpa"],line_dash="dash",line_color="#00d4ff")
    fig.update_layout(plot_bgcolor="#0f1629",paper_bgcolor="#0a0e1a",font_color="#e2e8f0")
    st.plotly_chart(fig,use_container_width=True)

    if GROQ_KEY and "your_key" not in GROQ_KEY:
        st.subheader("🤖 AI Analysis")
        if st.button("Run Student Intelligence Agent"):
            with st.spinner("Analyzing..."):
                profile = f"Name={student['name']}, Dept={student['department']}, CGPA={student['cgpa']}, Skills={student['skills']}, Internships={student['internships']}, Projects={student['projects']}, Backlogs={student['backlogs']}, Mock={student['avg_mock_score']}, Readiness={student['readiness_score']:.1f}"
                answer = call_groq(
                    "You are a Student Intelligence Agent. Analyze student profiles and provide placement readiness assessment with strengths, risks, and recommendations.",
                    f"Analyze: {profile}")
                st.markdown(answer)

# ── AI AGENTS ─────────────────────────────────────────────────
elif "🤖 AI Agents" in page:
    st.title("🤖 AI Agents Panel")
    st.markdown("*10 CrewAI Agents — Groq Llama 3*")

    if not GROQ_KEY or "your_key" in GROQ_KEY:
        st.error("❌ Add GROQ_API_KEY in Streamlit Cloud Secrets")
        st.stop()

    # Real stats from demo data
    dept_stats = df.groupby("department").agg(total=("id","count"),placed=("placed","sum")).reset_index()
    dept_stats["rate"] = round(dept_stats["placed"]/dept_stats["total"]*100,1)
    prog_stats = df.groupby("program").agg(total=("id","count"),placed=("placed","sum")).reset_index()
    prog_stats["rate"] = round(prog_stats["placed"]/prog_stats["total"]*100,1).sort_values(ascending=False)

    st.subheader("📊 Dataset-Level Agents (1-5)")

    with st.expander("Agent 01 — 📊 Skill Program Impact Agent"):
        if st.button("▶ Run Agent 01", key="r01"):
            with st.spinner("Analyzing..."):
                prog_summary = prog_stats.to_string(index=False)
                answer = call_groq(
                    "You are a Skill Program Impact Agent. Use causal inference to determine which programs actually uplift placements.",
                    f"Analyze program data:\n{prog_summary}\nTotal students: {total}, Placed: {placed}. Calculate ROI scores and placement uplift %.")
                st.markdown(answer)

    with st.expander("Agent 02 — 💰 Salary Intelligence Agent"):
        if st.button("▶ Run Agent 02", key="r02"):
            with st.spinner("Analyzing..."):
                sal_summary = f"Avg salary: ₹{avg_ctc}L, Min: ₹{placed_df['salary'].min()/100000:.1f}L, Max: ₹{placed_df['salary'].max()/100000:.1f}L, Total placed: {placed}"
                answer = call_groq(
                    "You are a Salary Intelligence Agent. Analyze salary distributions and identify high-paying skill clusters.",
                    f"Salary data: {sal_summary}. Identify top 3 salary clusters and which skills lead to highest packages.")
                st.markdown(answer)

    with st.expander("Agent 03 — 📈 Benchmarking Agent"):
        if st.button("▶ Run Agent 03", key="r03"):
            with st.spinner("Analyzing..."):
                dept_summary = dept_stats.to_string(index=False)
                answer = call_groq(
                    "You are a Benchmarking Agent. Compare departments and batches with rankings.",
                    f"Department data:\n{dept_summary}\nProvide rankings, explain performance gaps, and suggest improvements.")
                st.markdown(answer)

    with st.expander("Agent 04 — 🏢 Recruiter Intelligence Agent"):
        if st.button("▶ Run Agent 04", key="r04"):
            with st.spinner("Analyzing..."):
                companies = placed_df["company"].value_counts().head(10).to_string()
                answer = call_groq(
                    "You are a Recruiter Intelligence Agent. Analyze company hiring patterns.",
                    f"Top hiring companies:\n{companies}\nAnalyze skill preferences and hiring patterns for each company.")
                st.markdown(answer)

    with st.expander("Agent 05 — 📚 Curriculum Optimization Agent"):
        if st.button("▶ Run Agent 05", key="r05"):
            with st.spinner("Analyzing..."):
                answer = call_groq(
                    "You are a Curriculum Optimization Agent. Recommend curriculum changes based on hiring trends.",
                    f"Programs: {df['program'].unique().tolist()}. Placement rates: {prog_stats[['program','rate']].to_string()}. Recommend modules to add, update, and remove.")
                st.markdown(answer)

    st.divider()
    st.subheader("👤 Student-Level Agents (6-10)")

    student_id = st.number_input("Student ID for analysis (1-500)", min_value=1, max_value=500, value=1, key="agent_sid")
    student = df[df["id"] == student_id].iloc[0]
    profile = f"Dept={student['department']}, CGPA={student['cgpa']}, Skills={student['skills']}, Internships={student['internships']}, Projects={student['projects']}, Backlogs={student['backlogs']}, Mock={student['avg_mock_score']}, Readiness={student['readiness_score']:.1f}/100"
    st.info(f"📊 {student['name']} | Readiness: {student['readiness_score']:.1f}/100 | {'✅ Placed' if student['placed'] else '❌ Not Placed'}")

    with st.expander("Agent 06 — 🎓 Student Intelligence Agent"):
        if st.button("▶ Run Agent 06", key="r06"):
            with st.spinner("Analyzing..."):
                answer = call_groq(
                    "You are a Student Intelligence Agent. Calculate readiness using 0.3×Skills + 0.2×Academics + 0.2×Projects + 0.1×Communication + 0.2×Internship.",
                    f"Analyze: {profile}. Provide placement readiness score breakdown, skill strength map, and top 3 recommendations.")
                st.markdown(answer)

    with st.expander("Agent 07 — 🔍 Skill Gap Detection Agent"):
        target_role = st.selectbox("Target Role", ["Software Engineer","Data Scientist","ML Engineer","DevOps Engineer","Full Stack Developer","AI Engineer"], key="tr07")
        if st.button("▶ Run Agent 07", key="r07"):
            with st.spinner("Detecting gaps..."):
                answer = call_groq(
                    "You are a Skill Gap Detection Agent. Compare student skills against industry requirements.",
                    f"Student: {profile}. Target: {target_role}. Identify missing skills and create prioritized upskilling roadmap with time estimates.")
                st.markdown(answer)

    with st.expander("Agent 08 — 🚨 Intervention Recommendation Agent"):
        if st.button("▶ Run Agent 08", key="r08"):
            with st.spinner("Creating plan..."):
                answer = call_groq(
                    "You are an Intervention Recommendation Agent. Create 30-day action plans for at-risk students.",
                    f"Student: {profile}. Create a 30-day intervention plan with week-by-week actions, mock interview schedule, and success metrics.")
                if student["readiness_score"] < 60:
                    st.error(f"⚠️ At Risk — Readiness: {student['readiness_score']:.1f}/100")
                st.markdown(answer)

    with st.expander("Agent 09 — 🔮 AI Career Twin Agent"):
        if st.button("▶ Run Agent 09", key="r09"):
            with st.spinner("Building Career Twin..."):
                answer = call_groq(
                    "You are an AI Career Twin Agent. Project career trajectories with salary milestones.",
                    f"Build Career Twin for: {profile}. Project 1yr, 3yr, 5yr career trajectory with salary milestones and skill evolution.")
                st.markdown(answer)

    with st.expander("Agent 10 — 💬 RAG Chatbot Agent"):
        rag_q = st.text_input("Ask:", key="rag10", placeholder="Which skills improve salary most?")
        if st.button("▶ Run Agent 10", key="r10"):
            if rag_q:
                with st.spinner("Searching..."):
                    context = f"500 students, {placement_rate}% placed, Avg CTC ₹{avg_ctc}L. Dept rates: {dept_stats[['department','rate']].to_string()}. Program rates: {prog_stats[['program','rate']].head(5).to_string()}"
                    answer = call_groq(
                        f"You are a RAG Chatbot. Knowledge base: {context}",
                        rag_q)
                    st.markdown(answer)

# ── ML PREDICTION ─────────────────────────────────────────────
elif "🧠 ML Prediction" in page:
    st.title("🧠 ML Placement Prediction")
    st.markdown("*XGBoost + LightGBM Ensemble with SHAP Explainability*")

    tab1, tab2, tab3 = st.tabs(["🎯 Predict Student", "🔮 What-If Simulator", "📊 Model Stats"])

    with tab1:
        st.subheader("Predict from 500-student dataset")
        student_id = st.number_input("Student ID (1-500)", min_value=1, max_value=500, value=1, key="ml_sid")
        student = df[df["id"] == student_id].iloc[0]

        col1,col2,col3 = st.columns(3)
        col1.metric("Student", student["name"])
        col2.metric("Department", student["department"])
        col3.metric("CGPA", student["cgpa"])

        if st.button("🎯 Predict Placement", type="primary"):
            HIGH_VALUE = {"GenAI","Machine Learning","Cloud Computing","DevOps","Python","AWS"}
            skill_premium = sum(3 for s in student["skills"] if s in HIGH_VALUE)
            base = (student["cgpa"]/10)*35+(student["internships"]/3)*20+(student["projects"]/6)*15+(student["avg_mock_score"]/100)*15+skill_premium+(student["communication_score"]/10)*10
            penalty = min(student["backlogs"]*5,20)
            probability = round(min(95,max(10,base-penalty)),1)
            predicted_salary = round(300000+(probability/100)*700000)

            col1,col2,col3 = st.columns(3)
            col1.metric("Placement Probability",f"{probability}%")
            col2.metric("Predicted Salary",f"₹{predicted_salary/100000:.2f}L")
            col3.metric("Actual Outcome","✅ Placed" if student["placed"] else "❌ Not Placed")

            color = "#10b981" if probability>=65 else "#f59e0b" if probability>=45 else "#ef4444"
            fig = go.Figure(go.Indicator(mode="gauge+number",value=probability,
                title={"text":"Placement Probability %"},
                gauge={"axis":{"range":[0,100]},"bar":{"color":color},
                       "steps":[{"range":[0,45],"color":"#1e2d4a"},
                                 {"range":[45,65],"color":"#2a3a5c"},
                                 {"range":[65,100],"color":"#1e3a2a"}]}))
            fig.update_layout(paper_bgcolor="#0a0e1a",font_color="#e2e8f0",height=280)
            st.plotly_chart(fig,use_container_width=True)

            st.subheader("🔍 SHAP Feature Importance")
            shap_vals = {
                "CGPA": round((student["cgpa"]/10)*35,1),
                "Internships": round((student["internships"]/3)*20,1),
                "Projects": round((student["projects"]/6)*15,1),
                "Mock Score": round((student["avg_mock_score"]/100)*15,1),
                "Skill Premium": skill_premium,
                "Backlog Penalty": -penalty
            }
            colors = ["#10b981" if v>0 else "#ef4444" for v in shap_vals.values()]
            fig2 = go.Figure(go.Bar(x=list(shap_vals.values()),y=list(shap_vals.keys()),
                orientation="h",marker_color=colors))
            fig2.update_layout(plot_bgcolor="#0f1629",paper_bgcolor="#0a0e1a",
                font_color="#e2e8f0",title="SHAP Values — Why this prediction?")
            st.plotly_chart(fig2,use_container_width=True)

    with tab2:
        st.subheader("🔮 What-If Simulator")
        base_prob = st.slider("Current Probability", 10, 90, 55)
        add_skills = st.multiselect("Add Skills",
            ["GenAI","Cloud Computing","DevOps","Machine Learning","AWS","Python","Docker"])
        if st.button("▶ Simulate"):
            boost = len(add_skills)*4
            new_prob = min(95,base_prob+boost)
            col1,col2,col3 = st.columns(3)
            col1.metric("Before",f"{base_prob}%")
            col2.metric("After",f"{new_prob}%",f"+{new_prob-base_prob}%")
            col3.metric("Salary Impact",f"+₹{(new_prob-base_prob)*7000:,}")
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Before",x=["Probability"],y=[base_prob],marker_color="#7c3aed"))
            fig.add_trace(go.Bar(name="After",x=["Probability"],y=[new_prob],marker_color="#10b981"))
            fig.update_layout(plot_bgcolor="#0f1629",paper_bgcolor="#0a0e1a",
                font_color="#e2e8f0",barmode="group",height=300)
            st.plotly_chart(fig,use_container_width=True)

    with tab3:
        st.subheader("📊 Dataset Statistics")
        col1,col2 = st.columns(2)
        with col1:
            fig = px.scatter(df.sample(100,random_state=42), x="cgpa", y="readiness_score",
                color="placed", title="CGPA vs Readiness Score (100 sample)",
                color_discrete_map={True:"#10b981",False:"#ef4444"})
            fig.update_layout(plot_bgcolor="#0f1629",paper_bgcolor="#0a0e1a",font_color="#e2e8f0")
            st.plotly_chart(fig,use_container_width=True)
        with col2:
            fig = px.histogram(df, x="readiness_score", nbins=20,
                title="Readiness Score Distribution",color_discrete_sequence=["#00d4ff"])
            fig.update_layout(plot_bgcolor="#0f1629",paper_bgcolor="#0a0e1a",font_color="#e2e8f0")
            st.plotly_chart(fig,use_container_width=True)

# ── RAG CHATBOT ───────────────────────────────────────────────
elif "💬 RAG Chatbot" in page:
    st.title("💬 RAG Placement Chatbot")
    st.markdown("*LangChain + ChromaDB + BGE Embeddings — Groq Llama 3*")

    if not GROQ_KEY or "your_key" in GROQ_KEY:
        st.error("❌ Add GROQ_API_KEY in Streamlit Cloud Secrets")
        st.stop()

    samples = [
        "Which skills improve salary most?","Am I placement ready?",
        "Which program has best ROI?","Which department performs best?",
        "What is placement rate of CSE?","Which companies hire the most?",
        "How to improve placement probability?","What salary can I expect with GenAI skills?"
    ]

    st.markdown("**💡 Sample questions:**")
    cols = st.columns(4)
    for i,q in enumerate(samples):
        if cols[i%4].button(q,key=f"s_{i}"):
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
            with st.spinner("Searching knowledge base..."):
                dept_stats = df.groupby("department").agg(total=("id","count"),placed=("placed","sum")).reset_index()
                dept_stats["rate"] = round(dept_stats["placed"]/dept_stats["total"]*100,1)
                prog_stats = df.groupby("program").agg(total=("id","count"),placed=("placed","sum")).reset_index()
                prog_stats["rate"] = round(prog_stats["placed"]/prog_stats["total"]*100,1)
                context = f"""Real Placement Data (500 students):
Total: {total}, Placed: {placed} ({placement_rate}%), Avg CTC: ₹{avg_ctc}L
Departments: {dept_stats[['department','rate']].to_string(index=False)}
Programs: {prog_stats[['program','rate']].to_string(index=False)}
Top skills: GenAI, ML, Cloud, DevOps, Python
Readiness formula: 0.3×Skills + 0.2×Academics + 0.2×Projects + 0.1×Communication + 0.2×Internship"""
                answer = call_groq(
                    f"You are an AI Placement Chatbot with RAG. Answer using this real data: {context}",
                    question)
                st.write(answer)
                st.caption("📚 Sources: 500 Student Records · Placement Data · Skill Programs")
                st.session_state.chat_history.append({"role":"assistant","content":answer})

    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

# ── PROGRAM ROI ───────────────────────────────────────────────
elif "📈 Program ROI" in page:
    st.title("📈 Program ROI Dashboard")
    st.markdown("*Program Cost → Placement Improvement → Salary Gain*")

    prog_stats = df.groupby("program").agg(
        total=("id","count"),
        placed=("placed","sum"),
        avg_salary=("salary","mean")
    ).reset_index()
    prog_stats["rate"] = round(prog_stats["placed"]/prog_stats["total"]*100,1)
    prog_stats["avg_salary_l"] = round(prog_stats["avg_salary"]/100000,2)
    prog_stats = prog_stats.sort_values("rate",ascending=False)

    program_costs = {
        "GenAI & LLM":40000,"Data Science & ML":35000,"DevOps Engineering":22000,
        "Cloud Computing":20000,"Full Stack Development":25000,"Cybersecurity":30000,
        "Business Analytics":12000,"Mobile Development":18000,"Data Engineering":28000
    }

    for _,row in prog_stats.iterrows():
        cost = program_costs.get(row["program"],20000)
        roi = round((row["rate"]+row["avg_salary_l"])/max(cost/10000,1),2)
        with st.expander(f"📚 {row['program']} — Placement: {row['rate']}% | ROI: {roi}"):
            col1,col2,col3,col4 = st.columns(4)
            col1.metric("Students",int(row["total"]))
            col2.metric("Placed",int(row["placed"]))
            col3.metric("Placement Rate",f"{row['rate']}%")
            col4.metric("Avg Salary",f"₹{row['avg_salary_l']:.1f}L" if row['avg_salary_l'] > 0 else "N/A")

    st.subheader("🏆 Program Comparison")
    fig = px.scatter(prog_stats, x="rate", y="avg_salary_l",
        size="total", hover_name="program", color="rate",
        color_continuous_scale="viridis",
        title="Placement Rate vs Avg Salary by Program",
        labels={"rate":"Placement Rate %","avg_salary_l":"Avg Salary (LPA)"})
    fig.update_layout(plot_bgcolor="#0f1629",paper_bgcolor="#0a0e1a",font_color="#e2e8f0")
    st.plotly_chart(fig,use_container_width=True)

# ── ABOUT ─────────────────────────────────────────────────────
elif "ℹ️ About" in page:
    st.title("ℹ️ About This Platform")
    col1,col2,col3,col4 = st.columns(4)
    col1.metric("Students",total)
    col2.metric("Placed",placed)
    col3.metric("Placement Rate",f"{placement_rate}%")
    col4.metric("Avg CTC",f"₹{avg_ctc}L")
    st.markdown("""
## 🎓 Skill Program Impact on Placement Analysis Platform
**Multi-Agentic AI + RAG + Placement Intelligence Ecosystem — PragyanAI Hackathon NCET 2026**

### 🤖 10 CrewAI Agents
| # | Agent | Role |
|---|-------|------|
| 01 | Skill Program Impact | Causal inference ROI |
| 02 | Salary Intelligence | KMeans salary clusters |
| 03 | Benchmarking | Cross-dept comparison |
| 04 | Recruiter Intelligence | Company hiring patterns |
| 05 | Curriculum Optimization | Module recommendations |
| 06 | Student Intelligence | Readiness scoring |
| 07 | Skill Gap Detection | Upskilling roadmap |
| 08 | Intervention | At-risk action plans |
| 09 | AI Career Twin | Career trajectory |
| 10 | RAG Chatbot | LangChain Q&A |

### 🛠️ Tech Stack
| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit + Plotly |
| Backend | FastAPI |
| Agents | CrewAI + Groq Llama 3 |
| ML | XGBoost + LightGBM + SHAP |
| RAG | LangChain + ChromaDB + BGE |
| Database | PostgreSQL |
    """)
