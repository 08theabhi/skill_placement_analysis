"""Dashboard 6 — Program ROI Dashboard"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from placement_ai.dashboards.api_client import api_get

def show():
    st.title("📈 Program ROI Dashboard")
    st.markdown("*Program Cost → Placement Improvement → Salary Gain*")

    programs = api_get("/api/analytics/programs")
    if not programs:
        programs = [
            {"name":"GenAI & LLM","cost":40000,"completion_rate":0.88,"industry_relevance":9.5,"avg_feedback_score":4.8,"skills_covered":["Python","GenAI","ML"],"duration_weeks":12},
            {"name":"Data Science","cost":35000,"completion_rate":0.85,"industry_relevance":9.0,"avg_feedback_score":4.6,"skills_covered":["Python","ML","SQL"],"duration_weeks":20},
            {"name":"DevOps","cost":22000,"completion_rate":0.82,"industry_relevance":8.8,"avg_feedback_score":4.5,"skills_covered":["Docker","Kubernetes","AWS"],"duration_weeks":18},
            {"name":"Full Stack","cost":25000,"completion_rate":0.79,"industry_relevance":8.2,"avg_feedback_score":4.3,"skills_covered":["React","Node.js","SQL"],"duration_weeks":16},
            {"name":"Cloud Computing","cost":20000,"completion_rate":0.81,"industry_relevance":8.5,"avg_feedback_score":4.4,"skills_covered":["AWS","Docker","Linux"],"duration_weeks":12},
        ]

    st.subheader("💰 Program Investment vs Return")
    placement_lifts = [15, 18, 22, 28, 34, 18, 12][:len(programs)]
    salary_gains = [8, 10, 14, 18, 25, 12, 8][:len(programs)]

    for i, (prog, lift, gain) in enumerate(zip(programs, placement_lifts, salary_gains)):
        cost = prog.get("cost", 0)
        roi = round((lift + gain) / max(cost/10000, 1), 2)
        with st.expander(f"📚 {prog.get('name')} — ROI Score: {roi}"):
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("💸 Program Cost", f"₹{cost/1000:.0f}K")
            col2.metric("📈 Placement Lift", f"+{lift}%")
            col3.metric("💰 Salary Gain", f"+{gain}%")
            col4.metric("🎯 ROI Score", roi)

            fig = go.Figure(go.Waterfall(
                name="ROI Journey", orientation="v",
                measure=["relative","relative","relative","total"],
                x=["Program Cost", "Placement Improvement", "Salary Gain", "Net ROI"],
                y=[-cost/10000, lift, gain, lift+gain-cost/10000],
                connector={"line":{"color":"#1e2d4a"}},
                increasing={"marker":{"color":"#10b981"}},
                decreasing={"marker":{"color":"#ef4444"}},
                totals={"marker":{"color":"#00d4ff"}}
            ))
            fig.update_layout(plot_bgcolor="#0f1629", paper_bgcolor="#0a0e1a",
                font_color="#e2e8f0", height=280, title="Program Cost → Improvement → Gain")
            st.plotly_chart(fig, use_container_width=True)

            st.write(f"**Skills Covered:** {', '.join(prog.get('skills_covered',[]))}")
            st.write(f"**Duration:** {prog.get('duration_weeks')} weeks | **Feedback:** {prog.get('avg_feedback_score',0)}/5")

    st.divider()
    st.subheader("🏆 Program ROI Ranking")
    roi_data = []
    for prog, lift, gain in zip(programs, placement_lifts, salary_gains):
        cost = prog.get("cost", 1)
        roi_data.append({"Program": prog.get("name"), "ROI": round((lift+gain)/max(cost/10000,1),2), "Placement Lift": lift})
    roi_data.sort(key=lambda x: x["ROI"], reverse=True)

    fig = px.bar(roi_data, x="Program", y="ROI", color="ROI",
        color_continuous_scale="viridis", title="ROI Score by Program")
    fig.update_layout(plot_bgcolor="#0f1629", paper_bgcolor="#0a0e1a", font_color="#e2e8f0")
    st.plotly_chart(fig, use_container_width=True)

    with st.spinner("Running Skill Program Impact Agent..."):
        result = api_get("/api/agents/program-impact")
        if result and result.get("analysis"):
            st.subheader("🤖 AI Analysis")
            st.markdown(result["analysis"])
