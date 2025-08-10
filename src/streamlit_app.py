import streamlit as st
import faiss
import json
import os
import torch
from sentence_transformers import SentenceTransformer
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from pathlib import Path

# -------------------
# Config
# -------------------
#VECTOR_DIR = ".../vector_store"
VECTOR_DIR = Path(__file__).resolve().parent.parent / "vector_store"
EMBED_MODEL = "all-MiniLM-L6-v2"
LOCAL_LLM_MODEL = "google/flan-t5-xl"
MAX_HISTORY_TURNS = 5
TOP_K_RETRIEVAL = 3

# -------------------
# Load FAISS & Metadata
# -------------------
@st.cache_resource
def load_index():
    index = faiss.read_index(os.path.join(VECTOR_DIR, "index.faiss"))
    with open(os.path.join(VECTOR_DIR, "chunks_metadata.json"), "r", encoding="utf-8") as f:
        chunks = json.load(f)
    return index, chunks

# -------------------
# Load Models
# -------------------
@st.cache_resource
def load_models():
    embedder = SentenceTransformer(EMBED_MODEL)
    device = 0 if torch.cuda.is_available() else -1
    tokenizer = AutoTokenizer.from_pretrained(LOCAL_LLM_MODEL)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        LOCAL_LLM_MODEL,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None
    )
    llm_pipe = pipeline("text2text-generation", model=model, tokenizer=tokenizer, device=device)
    return embedder, llm_pipe

# -------------------
# Retrieval
# -------------------
def retrieve_context(query, embedder, index, chunks, top_k=TOP_K_RETRIEVAL):
    query_emb = embedder.encode([query])
    faiss.normalize_L2(query_emb)
    D, I = index.search(query_emb, top_k)
    retrieved = [chunks[i] for i in I[0] if i < len(chunks)]
    if not retrieved:
        return None, []
    context_text = "\n\n".join([f"Source: {c['source']}\n{c['text']}" for c in retrieved])
    return context_text, retrieved

# -------------------
# Answer Generation
# -------------------
def generate_answer(context, question, chat_history, llm_pipe):
    if not context:
        return "❌ I couldn't find any relevant information in my knowledge base."

    history_text = "\n".join([f"User: {h['user']}\nBot: {h['bot']}" for h in chat_history[-MAX_HISTORY_TURNS:]])
    prompt = (
        "You are an AI assistant specializing in answering questions about IRCC guidelines. "
        "Base your answers only on the provided context. If the context does not contain the answer, say so clearly.\n\n"
        f"Context:\n{context}\n\n"
        f"Conversation History:\n{history_text}\n\n"
        f"User: {question}\nBot:"
    )
    output = llm_pipe(prompt, max_new_tokens=300)
    return output[0]["generated_text"].strip()

# -------------------
# Streamlit UI Styling
# -------------------
st.set_page_config(page_title="IRCC Chatbot", page_icon="🤖", layout="centered")
st.markdown("""
    <style>
    .user-bubble {
        background-color: #DCF8C6;
        color: black;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        text-align: right;
        max-width: 80%;
        margin-left: auto;
    }
    .bot-bubble {
        background-color: #F1F0F0;
        color: black;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        text-align: left;
        max-width: 80%;
        margin-right: auto;
    }
    .source-box {
        background-color: #f9f9f9;
        color: black;
        font-size: 1rem;
        font-weight: 600;
        padding: 8px;
        border-radius: 5px;
        margin-top: 3px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 IRCC Immigration Chatbot")
st.caption("💬 Ask about IRCC guidelines — I’ll answer based on my knowledge base.")

# Load resources
index, chunks = load_index()
embedder, llm_pipe = load_models()

# Session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Input
user_input = st.text_input("Your question:", "", placeholder="Type your question and press Enter...")

if st.button("Send") and user_input.strip():
    with st.spinner("Thinking..."):
        context, sources = retrieve_context(user_input, embedder, index, chunks)
        answer = generate_answer(context, user_input, st.session_state.chat_history, llm_pipe)

        st.session_state.chat_history.append({"user": user_input, "bot": answer, "sources": sources})

# Chat history display with bubbles
for chat in st.session_state.chat_history:
    st.markdown(f"<div class='user-bubble'>🧑 {chat['user']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='bot-bubble'>🤖 {chat['bot']}</div>", unsafe_allow_html=True)
    if chat["sources"]:
        with st.expander("📂 Sources"):
            for s in chat["sources"]:
                st.markdown(f"<div class='source-box'>- {s['source']}</div>", unsafe_allow_html=True)

# Clear button
if st.button("🗑️ Clear Conversation"):
    st.session_state.chat_history = []
    st.rerun()
