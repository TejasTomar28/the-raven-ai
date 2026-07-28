<div align="center">

# 🐦 RAVEN AI

### Enterprise Knowledge Platform powered by Retrieval-Augmented Generation (RAG)

Transform PDF documents into an intelligent knowledge archive using semantic search, vector embeddings, and local Large Language Models.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![React](https://img.shields.io/badge/React-19-61DAFB)
![LangChain](https://img.shields.io/badge/LangChain-RAG-orange)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_DB-purple)
![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black)

</div>

---

# 📖 Overview

RAVEN AI is an enterprise-grade **Retrieval-Augmented Generation (RAG)** platform that converts PDF documents into an intelligent knowledge archive.

Instead of searching documents using keywords, users can ask questions in natural language. RAVEN AI retrieves the most relevant document passages using semantic search and generates grounded responses using a locally running Large Language Model.

Every answer is backed by the retrieved source passages, improving transparency and reducing hallucinations.

---

# ✨ Features

## Document Management

- Upload PDF documents
- Automatic document parsing
- Intelligent text chunking
- Persistent vector indexing
- Knowledge archive
- Delete uploaded documents
- Automatic vector cleanup

---

## AI-Powered Question Answering

- Semantic retrieval using embeddings
- Context-aware answers
- Retrieval-Augmented Generation (RAG)
- Local LLM using Ollama
- Grounded responses
- Source passage citations
- Similarity-based retrieval

---

## User Experience

- Modern React interface
- Enterprise-inspired archive theme
- Scrollable knowledge archive
- Scrollable citation panel
- Loading indicators
- Error handling
- Responsive layout
- Confirmation dialogs

---

# 🖼 Screenshots

## Home Interface

> <img width="2888" height="1604" alt="image" src="https://github.com/user-attachments/assets/bea53e42-785d-480b-a025-93843ad0aa6d" />


---

## Upload Documents

> <img width="2850" height="1534" alt="image" src="https://github.com/user-attachments/assets/a1a0e2a3-1489-42d5-b33d-535c612369cb" />


---

## Ask Questions

> <img width="2826" height="1602" alt="image" src="https://github.com/user-attachments/assets/540dd0ba-31d1-43e4-a008-ed43bfe80781" />


---

## Grounded Response

> <img width="1762" height="982" alt="image" src="https://github.com/user-attachments/assets/dfb91c04-a5fe-42d9-9b64-3d151fa3ee89" />


---

# 🏗 System Architecture

```
                ┌────────────────────┐
                │    React Frontend  │
                └─────────┬──────────┘
                          │
                  REST API Calls
                          │
                ┌─────────▼──────────┐
                │      FastAPI       │
                └─────────┬──────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
 PDF Processing     LangChain RAG     Document APIs
        │                 │
        ▼                 ▼
 Text Chunking      Semantic Retrieval
        │                 │
        ▼                 ▼
 Embeddings       ChatOllama (LLM)
        │                 │
        └─────────┬───────┘
                  ▼
             ChromaDB
          Vector Database
```

---

# 🧠 RAG Pipeline

```
                Upload PDF
                     │
                     ▼
            Extract Document Text
                     │
                     ▼
              Chunk Document
                     │
                     ▼
         Generate Embeddings
                     │
                     ▼
      Store Vectors in ChromaDB
                     │
──────────────────────────────────────────────
                     │
                User Question
                     │
                     ▼
        Generate Question Embedding
                     │
                     ▼
      Retrieve Relevant Chunks
                     │
                     ▼
        Build Context Prompt
                     │
                     ▼
     LangChain + Ollama (LLM)
                     │
                     ▼
      Grounded AI Response
                     │
                     ▼
    Return Supporting Citations
```

---

# 🛠 Tech Stack

## Backend

- FastAPI
- Python
- LangChain
- ChromaDB
- Ollama
- PyPDF
- Uvicorn

---

## Frontend

- React
- Vite
- Tailwind CSS

---

## AI Stack

- LangChain
- Ollama
- Qwen 3 (Local LLM)
- ChromaDB
- Sentence Transformers

---

# 📂 Project Structure

```
the-raven-ai/
│
├── app/
│   ├── api/
│   ├── core/
│   ├── langchain/
│   ├── models/
│   ├── rag/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── layouts/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── styles/
│   │   └── utils/
│   │
│   └── package.json
│
├── uploads/
├── data/
├── requirements.txt
└── README.md
```

---

# 🔌 REST API

## Documents

| Method | Endpoint | Description |
|----------|----------|-------------|
| POST | `/documents/upload` | Upload PDF |
| GET | `/documents` | List uploaded documents |
| DELETE | `/documents/{filename}` | Delete document |
| POST | `/documents/search` | Semantic search |
| GET | `/documents/{filename}/text` | Extracted text |
| GET | `/documents/{filename}/chunks` | Document chunks |

---

## Chat

| Method | Endpoint | Description |
|----------|----------|-------------|
| POST | `/chat` | Ask questions using RAG |

---

# 🚀 Getting Started

## 1. Clone Repository

```bash
git clone https://github.com/TejasTomar28/the-raven-ai.git

cd the-raven-ai
```

---

## 2. Backend Setup

Create virtual environment

```bash
python -m venv .venv
```

Activate

### Windows

```bash
.venv\Scripts\activate
```

### macOS / Linux

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## 3. Install Ollama

Install Ollama

https://ollama.com

Pull the model

```bash
ollama pull qwen3:4b
```

Start Ollama

```bash
ollama serve
```

---

## 4. Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

---

## 5. Run Backend

```bash
uvicorn app.main:app --reload
```

Swagger UI

```
http://localhost:8000/docs
```

---

# 💡 Example Workflow

1. Upload PDF documents

↓

2. Documents are parsed and chunked

↓

3. Embeddings are generated

↓

4. Chunks are stored inside ChromaDB

↓

5. Ask questions in natural language

↓

6. Relevant chunks are retrieved

↓

7. LangChain sends context to Ollama

↓

8. Receive grounded AI response

↓

9. Inspect supporting source passages

---

# 🔒 Why RAG?

Unlike traditional chatbots, RAVEN AI does not rely solely on the LLM's internal knowledge.

Instead, it retrieves relevant document passages before generating an answer, making responses:

- More accurate
- Explainable
- Grounded in uploaded documents
- Less prone to hallucinations

---

# 🔮 Future Improvements

- Document classification
- Category-based archive
- Authentication & user accounts
- Multi-user knowledge spaces
- Streaming AI responses
- Hybrid keyword + semantic search
- Cloud deployment
- Docker Compose
- Kubernetes deployment
- Role-based access control

---

# 👨‍💻 Author

**Tejas Tomar**

Software Engineering Student  
Delhi Technological University (DTU)

Backend Development • Artificial Intelligence • Distributed Systems


