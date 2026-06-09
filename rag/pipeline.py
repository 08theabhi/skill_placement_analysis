"""
RAG Pipeline — LangChain + ChromaDB + BGE Embeddings
Implements Agent 10: RAG Chatbot Agent
"""
import os
import json
from typing import List, Dict
from placement_ai.utils.config import settings

def get_rag_pipeline():
    try:
        from langchain_groq import ChatGroq
        from langchain_chroma import Chroma
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.runnables import RunnablePassthrough
        try:
            from langchain_community.embeddings import HuggingFaceBgeEmbeddings
        except ImportError:
            from langchain.embeddings import HuggingFaceEmbeddings as HuggingFaceBgeEmbeddings

        embeddings = HuggingFaceBgeEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        os.makedirs(settings.CHROMA_PATH, exist_ok=True)
        vectorstore = Chroma(
            collection_name=settings.CHROMA_COLLECTION,
            embedding_function=embeddings,
            persist_directory=settings.CHROMA_PATH
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        llm = ChatGroq(groq_api_key=settings.GROQ_API_KEY, model_name=settings.LLM_MODEL, temperature=0.2)

        prompt = ChatPromptTemplate.from_template("""You are an AI Placement Intelligence Assistant.
Use the following context from the placement database to answer the question accurately.

Context:
{context}

Question: {question}

Provide a helpful, data-driven answer. Be specific with numbers and percentages when available.""")

        chain = (
            {"context": retriever | (lambda docs: "\n\n".join(d.page_content for d in docs)),
             "question": RunnablePassthrough()}
            | prompt | llm | StrOutputParser()
        )
        return chain, vectorstore, embeddings
    except Exception as e:
        return None, None, None

def ingest_data(students: List[Dict], placements: List[Dict], programs: List[Dict]):
    try:
        _, vectorstore, embeddings = get_rag_pipeline()
        if vectorstore is None:
            return {"status": "error", "message": "RAG pipeline not available"}
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain_core.documents import Document
        docs = []
        for s in students[:100]:
            text = f"Student {s.get('name','Unknown')} from {s.get('department')} batch {s.get('batch')}. CGPA: {s.get('cgpa')}. Skills: {', '.join(s.get('skills',[]))}. Readiness: {s.get('readiness_score',0):.1f}/100. Internships: {s.get('internships',0)}."
            docs.append(Document(page_content=text, metadata={"type":"student","id":str(s.get("id",""))}))
        for p in placements[:50]:
            text = f"Placement record: Student placed at {p.get('company_name','Unknown')} as {p.get('role','Unknown')} with salary ₹{p.get('salary',0):,}."
            docs.append(Document(page_content=text, metadata={"type":"placement"}))
        for prog in programs:
            text = f"Skill program: {prog.get('name')} covers {', '.join(prog.get('skills_covered',[]))}. Duration: {prog.get('duration_weeks')} weeks. Cost: ₹{prog.get('cost',0):,}. Completion rate: {prog.get('completion_rate',0)*100:.0f}%."
            docs.append(Document(page_content=text, metadata={"type":"program"}))
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        splits = splitter.split_documents(docs)
        vectorstore.add_documents(splits)
        return {"status": "success", "documents_ingested": len(splits)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def query_rag(question: str) -> str:
    try:
        chain, _, _ = get_rag_pipeline()
        if chain is None:
            from placement_ai.agents.crew import agent_rag_chatbot
            result = agent_rag_chatbot(question)
            return result.get("answer", "Unable to answer at this time.")
        return chain.invoke(question)
    except Exception as e:
        from placement_ai.agents.crew import agent_rag_chatbot
        result = agent_rag_chatbot(question)
        return result.get("answer", f"Error: {str(e)}")
