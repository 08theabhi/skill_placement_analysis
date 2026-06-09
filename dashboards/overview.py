"""Dashboard 1 — Overview: Placement Success Dashboard"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from placement_ai.dashboards.api_client import api_get

def show():
    st.title("📊 Placement Intelligence Overview")
    st.markdown("*AI-Powered Placement Analytics — PragyanAI Hackathon NCET 2026*")

    overview = api_get("/api/analytics/overview")
    if not overview:
        st.error("❌ Backend not connected. Start: `uvicorn placement_ai.api.main:app --reload --port 8000`")
        st.info("📌 Running in demo mode with sample data")
        overview = {"total_students":500,"placed_students":321,"placement_rate":64.2,"avg_ctc":503000,"avg_cgpa":7.2,"avg_readiness":62.5}

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 Total Students", f"{overview.get('total_students',0):,}")
    col2.metric("✅ Placed", f"{overview.get('placed_students',0):,}", f"{overview.get('placement_rate',0)}%")
    col3.metric("💰 Avg CTC", f"₹{overview.get('avg_ctc',0)/100000:.2f}L")
    col4.metric("📊 Avg Readiness", f"{overview.get('avg_readiness',0):.1f}/100")

    st.divider()

    depts = api_get("/api/analytics/departments")
    programs = api_get("/api/analytics/programs")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏛️ Department Performance")
        if depts:
            fig = px.bar(depts, x="department", y="avg_readiness", color="avg_readiness",
                color_continuous_scale="viridis", title="Avg Readiness Score by Department")
            fig.update_layout(plot_bgcolor="#0f1629", paper_bgcolor="#0a0e1a",
                font_color="#e2e8f0", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            demo = [{"department":"CSE","avg_readiness":72},{"department":"IT","avg_readiness":68},
                    {"department":"ECE","avg_readiness":61},{"department":"EEE","avg_readiness":58},
                    {"department":"Mechanical","avg_readiness":52},{"department":"Civil","avg_readiness":49}]
            fig = px.bar(demo, x="department", y="avg_readiness", color="avg_readiness",
                color_continuous_scale="viridis", title="Avg Readiness Score by Department")
            fig.update_layout(plot_bgcolor="#0f1629", paper_bgcolor="#0a0e1a", font_color="#e2e8f0")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📚 Skill Program ROI")
        if programs:
            fig = px.scatter(programs, x="completion_rate", y="industry_relevance",
                size="hours", hover_name="name", color="avg_feedback_score",
                title="Program: Completion Rate vs Industry Relevance")
            fig.update_layout(plot_bgcolor="#0f1629", paper_bgcolor="#0a0e1a", font_color="#e2e8f0")
            st.plotly_chart(fig, use_container_width=True)
        else:
            demo_programs = [
                {"name":"GenAI & LLM","completion_rate":0.88,"industry_relevance":9.5,"hours":150,"avg_feedback_score":4.8},
                {"name":"DevOps","completion_rate":0.82,"industry_relevance":8.8,"hours":220,"avg_feedback_score":4.5},
                {"name":"Full Stack","completion_rate":0.79,"industry_relevance":8.2,"hours":200,"avg_feedback_score":4.3},
                {"name":"Data Science","completion_rate":0.85,"industry_relevance":9.0,"hours":240,"avg_feedback_score":4.6},
            ]
            fig = px.scatter(demo_programs, x="completion_rate", y="industry_relevance",
                size="hours", hover_name="name", color="avg_feedback_score",
                title="Program: Completion Rate vs Industry Relevance")
            fig.update_layout(plot_bgcolor="#0f1629", paper_bgcolor="#0a0e1a", font_color="#e2e8f0")
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("📈 Placement Trend by Skill Program")
    skill_data = {"GenAI":82,"DevOps":78,"Cloud":75,"Data Science":72,"Full Stack":70,"Cybersecurity":67,"Analytics":64}
    fig = go.Figure(go.Bar(x=list(skill_data.keys()), y=list(skill_data.values()),
        marker_color=["#00d4ff","#7c3aed","#10b981","#f59e0b","#ef4444","#ec4899","#06b6d4"]))
    fig.update_layout(plot_bgcolor="#0f1629", paper_bgcolor="#0a0e1a",
        font_color="#e2e8f0", title="Placement Rate by Skill Program (%)")
    st.plotly_chart(fig, use_container_width=True)
