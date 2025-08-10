# IRCC Chatbot 🤖  
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)  
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red)](https://streamlit.io/)  
[![HuggingFace](https://img.shields.io/badge/🤗-Transformers-yellow)](https://huggingface.co/)  
[![FAISS](https://img.shields.io/badge/Vector%20DB-FAISS-green)](https://faiss.ai/)  

An AI-powered chatbot designed to answer questions about **IRCC (Immigration, Refugees and Citizenship Canada)** guidelines using a **Retrieval-Augmented Generation (RAG)** pipeline.  

This project leverages **FAISS** for vector search, **Sentence Transformers** for embeddings, and **local LLMs** like `google/flan-t5-xl` to provide accurate, source-backed answers directly from an offline knowledge base.  

---

## ✨ Features  
- **Accurate, Source-Based Answers** – Responses are grounded in IRCC official documents.  
- **Hybrid Retrieval** – Semantic search with keyword-based filtering for improved relevance.  
- **Multi-Turn Memory** – Keeps the last few conversation turns for natural interactions.  
- **Local & Free Models** – Works offline using open-source models, no API costs.  
- **Streamlit UI** – User-friendly interface for easy interaction.  
- **Error Handling** – Gracefully handles cases when no relevant data is found.  

---

## 🛠️ Tech Stack  
- **Language Models:** `google/flan-t5-xl` (or alternative local models)  
- **Embeddings:** `all-MiniLM-L6-v2` via `sentence-transformers`  
- **Vector Store:** FAISS (cosine similarity search)  
- **UI:** Streamlit  
- **PDF/Text Processing:** PyMuPDF, LangChain  
- **Additional Tools:** Hugging Face Transformers, NumPy, Torch  

---

## 🚀 Installation  

1️⃣ **Clone the repository**  
```bash
git clone https://github.com/yourusername/ircc-chatbot.git
cd ircc-chatbot
```

2️⃣ **Install dependencies**
```bash
pip install -r requirements.txt
```

3️⃣ **Prepare the knowledge base**
- Place your IRCC-related documents in data folder with pdf and json
- Run all the script
```bash
python scripts/embed_documents.py
python scripts/extract_text_from_json.py
python scripts/extract_text_from_pdf.py
```

4️⃣ **Run the chatbot**
```bash 
streamlit run src/streamlit_app.py
```

---

## 💡 Usage
- Ask any IRCC-related question in the chat.
- The bot retrieves relevant chunks from its knowledge base and formulates an answer.
- If no relevant information is found, it will explicitly say so.
Example:
```bash
You: What is the processing time for a study permit?  
Bot: Based on the provided IRCC guidelines, study permit processing times vary depending on your country. Please refer to the official IRCC website for the most recent updates.
```

---

## 📊 Future Improvements
- Support larger open-source models like Mistral or LLaMA.
- Add streaming responses for faster perceived output.
- Implement better UI with conversation history panel.
- Deploy to Hugging Face Spaces or other cloud platforms.