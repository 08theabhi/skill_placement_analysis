"""
Placement AI Platform — Streamlit Dashboard
Main entry point: streamlit run app.py
PragyanAI Hackathon — NCET 2026
"""
import streamlit as st
import os

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
    .stSelectbox > div > div { background-color: #0f1629; }
</style>
""", unsafe_allow_html=True)

# Load config from Streamlit secrets or .env
def load_config():
    try:
        if hasattr(st, 'secrets'):
            for key in ["GROQ_API_KEY","LLM_MODEL","DATABASE_URL","SYNC_DATABASE_URL",
                        "CHROMA_PATH","EMBEDDING_MODEL","SECRET_KEY","MODEL_STORE_PATH","API_URL"]:
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

# Sidebar
with st.sidebar:
    st.markdown("## 🎓 Placement AI")
    st.markdown("*Multi-Agentic AI + RAG Platform*")
    st.markdown("**PragyanAI · NCET 2026**")
    st.divider()

    page = st.radio("🗺️ Navigate", [
        "📊 Overview Dashboard",
        "👤 Student Analysis",
        "🤖 AI Agents",
        "🧠 ML Prediction",
        "💬 RAG Chatbot",
        "📈 Program ROI",
    ], label_visibility="collapsed")

    st.divider()
    st.markdown("**⚙️ System Status**")

    api_url = os.getenv("API_URL", "http://localhost:8000")
    try:
        import httpx
        r = httpx.get(f"{api_url}/health", timeout=2)
        if r.status_code == 200:
            st.success("✅ Backend Online")
        else:
            st.warning("⚠️ Backend Offline")
    except Exception:
        st.warning("⚠️ Backend Offline")

    groq_key = os.getenv("GROQ_API_KEY","")
    if groq_key and "your_key" not in groq_key:
        st.success("✅ Groq Connected")
    else:
        st.error("❌ Add GROQ_API_KEY to .env")

    st.info("🤖 llama-3.1-8b-instant\n\n📚 10 CrewAI Agents\n\n🔍 BGE Embeddings\n\n🗄️ ChromaDB RAG")

# Page routing
if "📊 Overview Dashboard" in page:
    from placement_ai.dashboards.overview import show
    show()
elif "👤 Student Analysis" in page:
    from placement_ai.dashboards.student_analysis import show
    show()
elif "🤖 AI Agents" in page:
    from placement_ai.dashboards.agents import show
    show()
elif "🧠 ML Prediction" in page:
    from placement_ai.dashboards.ml_prediction import show
    show()
elif "💬 RAG Chatbot" in page:
    from placement_ai.dashboards.chatbot import show
    show()
elif "📈 Program ROI" in page:
    from placement_ai.dashboards.program_roi import show
    show()
