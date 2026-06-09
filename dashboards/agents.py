"""Dashboard 3 — AI Agents Panel"""
import streamlit as st
import json
from placement_ai.dashboards.api_client import api_get, api_post

AGENTS = [
    {"id":"program-impact","name":"📊 Skill Program Impact","desc":"Causal inference ROI analysis","endpoint":"/api/agents/program-impact","method":"get"},
    {"id":"salary-intelligence","name":"💰 Salary Intelligence","desc":"KMeans salary cluster analysis","endpoint":"/api/agents/salary-intelligence","method":"get"},
    {"id":"benchmarking","name":"📈 Benchmarking","desc":"Cross-department comparison","endpoint":"/api/agents/benchmarking","method":"get"},
    {"id":"recruiter-intelligence","name":"🏢 Recruiter Intelligence","desc":"Company hiring patterns","endpoint":"/api/agents/recruiter-intelligence","method":"get"},
    {"id":"curriculum","name":"📚 Curriculum Optimization","desc":"Module add/remove recommendations","endpoint":"/api/agents/curriculum-optimization","method":"get"},
]

def show():
    st.title("🤖 AI Agents Panel")
    st.markdown("*10 CrewAI Agents powered by Groq Llama 3 — llama-3.1-8b-instant*")

    st.info("💡 **Agents 1,4,5,8** require a Student ID — use the Student Analysis page\n\n**Agents 2,3,7,9,6** run on full dataset — click Run below")

    for agent in AGENTS:
        with st.expander(f"{agent['name']} — {agent['desc']}"):
            if st.button(f"▶ Run {agent['name']}", key=f"btn_{agent['id']}"):
                with st.spinner(f"Running {agent['name']}..."):
                    if agent["method"] == "get":
                        result = api_get(agent["endpoint"])
                    else:
                        result = api_post(agent["endpoint"])

                    if result:
                        if "analysis" in result:
                            st.markdown("**📋 AI Analysis:**")
                            st.markdown(result["analysis"])
                        if "program_scores" in result:
                            st.markdown("**📊 Program Scores:**")
                            for p in result["program_scores"][:5]:
                                st.write(f"• {p['program']}: Placement uplift +{p['placement_uplift_pct']}%, ROI: {p['roi_score']}")
                        if "department_rankings" in result:
                            st.markdown("**🏛️ Department Rankings:**")
                            for i, d in enumerate(result["department_rankings"]):
                                st.write(f"{i+1}. {d['department']}: {d['avg_readiness']}/100")
                        if "salary_clusters" in result:
                            st.markdown("**💰 Salary Clusters:**")
                            for c in result["salary_clusters"]:
                                st.write(f"• {c['cluster']}: ₹{c['avg_salary']/100000:.1f}L — {c['demand']} demand")
                        if st.checkbox("📄 View Raw JSON", key=f"raw_{id(result)}"):
                            st.json(result)
                    else:
                        st.error("Backend not connected. Start uvicorn first.")

    st.divider()
    st.subheader("🎯 Student-Specific Agents")
    student_id = st.number_input("Enter Student ID", min_value=1, value=1, step=1)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("👤 Student Intelligence"):
            with st.spinner("Analyzing..."):
                result = api_post(f"/api/agents/student-intelligence/{student_id}")
                if result:
                    st.metric("Readiness Score", f"{result.get('readiness_score',0)}/100")
                    st.metric("Risk Level", result.get("risk_level","Unknown"))
                    st.markdown(result.get("analysis",""))

    with col2:
        if st.button("🚨 Intervention Plan"):
            with st.spinner("Planning..."):
                result = api_get(f"/api/agents/intervention/{student_id}")
                if result:
                    st.warning(f"Risk: {result.get('risk_level','Unknown')}")
                    for action in result.get("immediate_actions",[]):
                        st.write(action)

    with col3:
        target_role = st.selectbox("Target Role", ["Software Engineer","Data Scientist","ML Engineer","DevOps Engineer","Full Stack Developer","AI Engineer"])
        if st.button("🔍 Skill Gap Analysis"):
            student = api_get(f"/api/students/{student_id}")
            if student:
                with st.spinner("Analyzing skill gaps..."):
                    result = api_post("/api/agents/skill-gap", {"skills": student.get("skills",[]), "target_role": target_role})
                    if result:
                        st.metric("Match %", f"{result.get('match_percentage',0)}%")
                        st.markdown("**Missing Skills:**")
                        for skill in result.get("missing_skills",[]):
                            st.error(f"❌ {skill}")
                        st.markdown(result.get("roadmap",""))
