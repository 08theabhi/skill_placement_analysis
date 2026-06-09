"""Dashboard 5 — RAG Chatbot: LangChain + ChromaDB + BGE Embeddings"""
import streamlit as st
from placement_ai.dashboards.api_client import api_post

SAMPLE_QUESTIONS = [
    "Which skills improve salary most?",
    "Am I placement ready?",
    "Which companies fit my profile?",
    "Which program improved placement most?",
    "Why did placements drop?",
    "Which department performs best?",
    "What is the ROI of AI programs?",
    "Which skills should I learn for GenAI roles?",
]

def show():
    st.title("💬 RAG Placement Chatbot")
    st.markdown("*LangChain + ChromaDB + BGE Embeddings — Powered by Groq Llama 3*")

    st.info("🤖 Ask anything about placements, skills, programs, or career guidance")

    # Sample questions
    st.markdown("**💡 Try these questions:**")
    cols = st.columns(4)
    for i, q in enumerate(SAMPLE_QUESTIONS[:8]):
        if cols[i%4].button(q, key=f"q_{i}"):
            st.session_state["chat_input"] = q

    st.divider()

    # Chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
        else:
            with st.chat_message("assistant"):
                st.write(msg["content"])

    # Input
    question = st.chat_input("Ask about placements, skills, career guidance...")

    # Handle button clicks
    if "chat_input" in st.session_state and st.session_state.chat_input:
        question = st.session_state.chat_input
        st.session_state.chat_input = ""

    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                result = api_post("/api/chatbot/ask", {"question": question})
                if result:
                    answer = result.get("answer", "Unable to answer at this time.")
                    sources = result.get("sources", [])
                    st.write(answer)
                    if sources:
                        st.caption(f"📚 Sources: {', '.join(sources)}")
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                else:
                    msg = "❌ Backend not connected. Start: `uvicorn placement_ai.api.main:app --reload --port 8000`"
                    st.error(msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": msg})

    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()
