"""Dashboard 4 — ML Prediction: XGBoost + LightGBM + SHAP + Prophet"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from placement_ai.dashboards.api_client import api_get, api_post

SKILLS_LIST = ["Python","Java","JavaScript","React","Node.js","SQL","MongoDB","AWS","Docker",
               "Kubernetes","Machine Learning","Deep Learning","Data Analysis","Power BI",
               "Tableau","Excel","Git","Linux","REST APIs","GenAI","Cloud Computing",
               "Cybersecurity","DevOps","Agile","Communication","Problem Solving","Leadership"]

def show():
    st.title("🧠 ML Prediction Pipeline")
    st.markdown("*XGBoost + LightGBM Ensemble with SHAP Explainability*")

    tab1, tab2, tab3, tab4 = st.tabs(["🏋️ Train Models", "🎯 Predict & Explain", "🔮 What-If Simulator", "📈 Trend Forecast"])

    with tab1:
        st.subheader("Train ML Models on Student Dataset")
        st.info("This trains XGBoost + LightGBM models on all 500 students with SHAP explainability.")
        if st.button("🚀 Start Training", type="primary"):
            with st.spinner("Training XGBoost + LightGBM on 500 students..."):
                result = api_post("/api/ml/train")
                if result:
                    if result.get("status") == "success":
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Students Trained", result.get("students_trained",0))
                        col2.metric("XGBoost AUC", result.get("xgb_auc",0))
                        col3.metric("Ensemble AUC", result.get("ensemble_auc",0))
                        st.success("✅ Models trained successfully!")
                    else:
                        st.error(result.get("message","Training failed"))
                else:
                    st.error("Backend not connected.")

    with tab2:
        st.subheader("Predict Placement Probability with SHAP")
        student_id = st.number_input("Student ID (1-500)", min_value=1, max_value=500, value=1)
        if st.button("🎯 Predict Placement"):
            with st.spinner("Running prediction..."):
                result = api_get(f"/api/ml/predict/{student_id}")
                if result:
                    prob = result.get("placement_probability", 0)
                    label = result.get("prediction_label","Unknown")
                    salary = result.get("predicted_salary",0)

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Placement Probability", f"{prob}%")
                    col2.metric("Prediction", label)
                    col3.metric("Predicted Salary", f"₹{salary/100000:.2f}L")

                    color = "#10b981" if prob >= 65 else "#f59e0b" if prob >= 45 else "#ef4444"
                    fig = go.Figure(go.Indicator(mode="gauge+number",
                        value=prob, title={"text":"Placement Probability %"},
                        gauge={"axis":{"range":[0,100]},
                               "bar":{"color":color},
                               "steps":[{"range":[0,45],"color":"#1e2d4a"},
                                        {"range":[45,65],"color":"#2a3a5c"},
                                        {"range":[65,100],"color":"#1e3a2a"}]}))
                    fig.update_layout(paper_bgcolor="#0a0e1a", font_color="#e2e8f0", height=280)
                    st.plotly_chart(fig, use_container_width=True)

                    shap_factors = result.get("shap_top_factors",[])
                    if shap_factors:
                        st.subheader("🔍 SHAP Feature Importance (Why this prediction?)")
                        features = [f["feature"] for f in shap_factors]
                        impacts = [f["impact"] for f in shap_factors]
                        colors = ["#10b981" if v > 0 else "#ef4444" for v in impacts]
                        fig2 = go.Figure(go.Bar(x=impacts, y=features, orientation="h", marker_color=colors))
                        fig2.update_layout(plot_bgcolor="#0f1629", paper_bgcolor="#0a0e1a",
                            font_color="#e2e8f0", title="Positive = helps placement, Negative = hurts")
                        st.plotly_chart(fig2, use_container_width=True)

                    if "explanation" in result:
                        st.markdown("**🤖 AI Explanation:**")
                        st.markdown(result["explanation"])
                else:
                    st.error("Backend not connected or student not found.")

    with tab3:
        st.subheader("🔮 What-If Placement Simulator")
        st.markdown("*Add skills and see how placement probability changes*")
        student_id_sim = st.number_input("Student ID for simulation", min_value=1, value=1, key="sim_id")
        add_skills = st.multiselect("Skills to Add", SKILLS_LIST)

        if st.button("▶ Run Simulation") and add_skills:
            student = api_get(f"/api/students/{student_id_sim}")
            if student:
                orig_result = api_get(f"/api/ml/predict/{student_id_sim}")
                orig = orig_result.get("placement_probability", 50) if orig_result else 50

                new_skills = list(set(student.get("skills",[]) + add_skills))
                student["skills"] = new_skills
                from placement_ai.agents.crew import agent_placement_prediction
                new_result = agent_placement_prediction(student)
                new_prob = new_result.get("placement_probability", orig)

                col1, col2, col3 = st.columns(3)
                col1.metric("Before", f"{orig}%")
                col2.metric("After Adding Skills", f"{new_prob}%", f"+{new_prob-orig:.1f}%")
                col3.metric("Skills Added", len(add_skills))

                fig = go.Figure()
                fig.add_trace(go.Bar(name="Before", x=["Placement Probability"], y=[orig], marker_color="#7c3aed"))
                fig.add_trace(go.Bar(name="After", x=["Placement Probability"], y=[new_prob], marker_color="#10b981"))
                fig.update_layout(plot_bgcolor="#0f1629", paper_bgcolor="#0a0e1a",
                    font_color="#e2e8f0", barmode="group", height=300,
                    title=f"Impact of adding: {', '.join(add_skills)}")
                st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.subheader("📈 Placement Trend Forecasting (Prophet)")
        st.markdown("*Time series forecasting of future placement trends*")
        if st.button("🔮 Forecast Next 6 Months"):
            with st.spinner("Running Prophet time series model..."):
                result = api_get("/api/ml/forecast")
                if result and result.get("status") == "success":
                    forecast_data = result.get("forecast", [])
                    if forecast_data:
                        df = pd.DataFrame(forecast_data)
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=df["month"], y=df["predicted"],
                            mode="lines+markers", name="Predicted", line=dict(color="#00d4ff", width=2)))
                        fig.update_layout(plot_bgcolor="#0f1629", paper_bgcolor="#0a0e1a",
                            font_color="#e2e8f0", title=f"Placement Forecast — Trend: {result.get('trend','stable').upper()}")
                        st.plotly_chart(fig, use_container_width=True)
                        st.success(f"📊 Trend: {result.get('trend','stable').title()}")
                else:
                    st.info("Prophet not installed or insufficient data. Install with: `pip install prophet`")
