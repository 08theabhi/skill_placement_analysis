# 🎓 Placement AI Platform
## Skill Program Impact on Placement Analysis Platform
### Multi-Agentic AI + RAG + Placement Intelligence Ecosystem
**PragyanAI Hackathon — NCET 2026**

---

## 📁 Folder Structure (Exact Spec Match)
```
placement_ai/
├── agents/       # CrewAI 10-agent system
├── prediction/   # XGBoost + LightGBM + SHAP + Prophet
├── rag/          # LangChain + ChromaDB + BGE embeddings
├── dashboards/   # 6 Streamlit pages
├── embeddings/   # BGE utilities
├── analytics/    # ROI + benchmarking
├── chatbot/      # RAG chatbot logic
├── api/          # FastAPI endpoints
├── reports/      # Generated reports
├── datasets/     # Data generators
├── utils/        # Config, DB models
├── app.py        # Streamlit entry point
└── seed.py       # Database seeder
```

## ⚡ Local Setup
```bash
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
copy .env.example .env   # Edit and add GROQ_API_KEY
python seed.py
uvicorn placement_ai.api.main:app --reload --port 8000
streamlit run app.py
```

## 🛠️ Tech Stack
| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit + Plotly |
| Backend | FastAPI |
| Agents | CrewAI + Groq Llama 3 |
| ML | XGBoost + LightGBM + SHAP + Prophet |
| RAG | LangChain + ChromaDB + BGE |
| DB | PostgreSQL |
