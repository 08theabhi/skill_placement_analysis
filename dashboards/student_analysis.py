"""Dashboard 2 — Student Analysis"""
import streamlit as st
import plotly.graph_objects as go
from placement_ai.dashboards.api_client import api_get, api_post

def show():
    st.title("👤 Student Analysis")
    st.markdown("*Individual student placement readiness and AI Career Twin*")

    col1, col2 = st.columns([1, 3])
    with col1:
        student_id = st.number_input("Student ID", min_value=1, value=1, step=1)
        search = st.button("🔍 Analyze Student")

    if search:
        student = api_get(f"/api/students/{student_id}")
        if not student:
            st.error(f"Student ID {student_id} not found. Run seed.py first.")
            return

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("CGPA", student.get("cgpa"))
        col2.metric("Readiness", f"{student.get('readiness_score',0):.1f}/100")
        col3.metric("Skills", len(student.get("skills",[])))
        col4.metric("Internships", student.get("internships",0))

        st.subheader(f"👤 {student.get('name')} — {student.get('department')} ({student.get('batch')})")

        risk = student.get("readiness_score",0)
        if risk >= 80: st.success("🟢 High Ready — Strong placement candidate")
        elif risk >= 60: st.warning("🟡 Moderate — Needs skill improvement")
        elif risk >= 40: st.error("🟠 At Risk — Requires intervention")
        else: st.error("🔴 Critical — Immediate action needed")

        col1, col2 = st.columns(2)
        with col1:
            score_breakdown = {
                "Skills (30%)": round(0.3*(len(student.get("skills",[]))/27*100),1),
                "Academics (20%)": round(0.2*(student.get("cgpa",0)/10*100),1),
                "Projects (20%)": round(0.2*(student.get("projects",0)/6*100),1),
                "Communication (10%)": round(0.1*(student.get("communication_score",0)/10*100),1),
                "Internship (20%)": round(0.2*(student.get("internships",0)/3*100),1),
            }
            fig = go.Figure(go.Bar(
                x=list(score_breakdown.values()), y=list(score_breakdown.keys()),
                orientation="h", marker_color=["#00d4ff","#7c3aed","#10b981","#f59e0b","#ef4444"]))
            fig.update_layout(plot_bgcolor="#0f1629", paper_bgcolor="#0a0e1a",
                font_color="#e2e8f0", title="Readiness Score Breakdown")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**🛠️ Skills**")
            skills = student.get("skills",[])
            for sk in skills:
                st.markdown(f"✅ {sk}")

        st.subheader("🤖 AI Agent Analysis")
        with st.spinner("Running Student Intelligence Agent..."):
            result = api_post(f"/api/agents/student-intelligence/{student_id}")
            if result:
                st.markdown(result.get("analysis","No analysis available"))

        st.subheader("🚨 Intervention Plan")
        with st.spinner("Running Intervention Agent..."):
            result = api_get(f"/api/agents/intervention/{student_id}")
            if result:
                actions = result.get("immediate_actions",[])
                if actions:
                    for action in actions:
                        st.warning(action)
                st.markdown(result.get("detailed_plan",""))
