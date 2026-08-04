# 🐦 RAVEN AI

### Enterprise Knowledge Platform powered by Retrieval-Augmented Generation (RAG) & Machine Learning

Transform PDF documents into an intelligent knowledge archive using semantic search, local Large Language Models, and offline machine learning.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![React](https://img.shields.io/badge/React-Frontend-61DAFB)
![LangChain](https://img.shields.io/badge/LangChain-RAG-success)
![ChromaDB](https://img.shields.io/badge/ChromaDB-VectorDB-orange)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black)
![Machine Learning](https://img.shields.io/badge/ML-Linear%20SVM-red)

---

# 📖 Overview

RAVEN AI is an enterprise knowledge platform that enables users to upload PDF documents, organize them intelligently, and interact with them using natural language.

Instead of relying on keyword search, RAVEN AI combines:

- Retrieval-Augmented Generation (RAG)
- Semantic Search
- Local Large Language Models (Ollama + Qwen)
- Offline Machine Learning

to deliver grounded, citation-backed answers while automatically classifying uploaded documents into enterprise document categories.

Unlike traditional chatbots, every answer is generated only after retrieving relevant document passages from the knowledge base.

---

# ✨ Features

## 📄 Intelligent Document Processing

- Upload PDF documents
- Automatic PDF parsing
- Intelligent text chunking
- Semantic vector indexing
- Persistent ChromaDB storage
- Automatic document categorization
- Knowledge archive
- Delete documents
- Automatic vector cleanup

---

## 🤖 AI-Powered Question Answering

- Retrieval-Augmented Generation (RAG)
- Semantic Search
- Local Ollama (Qwen 3)
- LangChain Retrieval Pipeline
- Context-aware grounded responses
- Source citations
- Similarity-based retrieval
- Hallucination-resistant responses

---

## 🧠 Machine Learning Document Classification

Every uploaded document is automatically classified using an offline supervised Machine Learning pipeline.

Categories:

- Finance
- HR
- Legal
- Research
- Resume
- Technical

Pipeline:

PDF

↓

Extract Text

↓

Preprocess Text

↓

TF-IDF Vectorization

↓

Linear SVM

↓

Category Prediction

The classifier runs completely offline without any LLM.

---

## 🎨 Modern User Experience

- React + Tailwind UI
- Enterprise archive theme
- Category badges
- Archive filtering
- Scrollable archive
- Scrollable citations
- Loading indicators
- Error handling
- Confirmation dialogs
- Responsive layout

---

# 🖼 Screenshots

## Home

> <img width="2602" height="1514" alt="image" src="https://github.com/user-attachments/assets/fb73a0dc-d905-4fd3-95eb-f651f5606429" />


---

## Delete Document

> <img width="2940" height="1606" alt="image" src="https://github.com/user-attachments/assets/e5cb9a8f-ea4b-4616-a4b5-8cf60d754060" />


---

## Ask Questions

> <img width="2936" height="1610" alt="image" src="https://github.com/user-attachments/assets/40ef389c-d299-44b5-814f-fd29059a8326" />


---

## Document Classification

> <img width="1024" height="1300" alt="image" src="https://github.com/user-attachments/assets/65f7d122-2a4e-40c5-a3b0-4b4bf63ad428" />


---

## Citation-backed Response

> <img width="1848" height="720" alt="image" src="https://github.com/user-attachments/assets/b6fc4b5b-b491-473b-ba2c-287c6f0b3a1f" />


---

# 🏗 System Architecture

```text
                    React Frontend
                           │
                           ▼
                    FastAPI Backend
                           │
      ┌────────────────────┼────────────────────┐
      │                    │                    │
      ▼                    ▼                    ▼
PDF Processing      LangChain RAG        ML Classifier
      │                    │                    │
      ▼                    ▼                    ▼
Text Extraction     Semantic Search      TF-IDF + SVM
      │                    │
      ▼                    ▼
Chunking          ChatOllama (Qwen)
      │                    │
      └────────────┬───────┘
                   ▼
              ChromaDB
            Vector Database
```

---

# 🧠 RAG Pipeline

```text
Upload PDF
      │
      ▼
Extract Text
      │
      ▼
Chunk Document
      │
      ▼
Generate Embeddings
      │
      ▼
Store in ChromaDB

──────────────────────────────

User Question
      │
      ▼
Generate Query Embedding
      │
      ▼
Retrieve Relevant Chunks
      │
      ▼
Build Context
      │
      ▼
LangChain + Ollama
      │
      ▼
Grounded Response
      │
      ▼
Supporting Citations
```

---

# 🤖 ML Classification Pipeline

```text
Upload PDF
      │
      ▼
Extract Text
      │
      ▼
Text Preprocessing
      │
      ▼
TF-IDF Vectorizer
      │
      ▼
Linear SVM
      │
      ▼
Predicted Category
      │
      ▼
Store Metadata
      │
      ▼
Display Category Badge
```

---

# 📊 Model Evaluation

Three supervised machine learning models were evaluated.

| Model | Validation Accuracy | Validation Weighted F1 |
|--------|--------------------:|-----------------------:|
| Logistic Regression | 97.7% | 97.7% |
| **Linear SVM** | **100%** | **100%** |
| XGBoost | 90.7% | 90.6% |

Final untouched hold-out test performance:

- Accuracy: **93.8%**
- Weighted F1 Score: **93.3%**

Linear SVM was selected as the production classifier because it generalized best on sparse TF-IDF document features.

---

# 🛠 Tech Stack

## Backend

- FastAPI
- Python
- LangChain
- ChromaDB
- Ollama
- PyMuPDF
- Uvicorn

---

## Frontend

- React
- Vite
- Tailwind CSS

---

## AI

- LangChain
- Ollama
- Qwen 3
- ChromaDB
- Sentence Transformers

---

## Machine Learning

- Scikit-learn
- Linear SVM
- TF-IDF
- Joblib

---

# 📂 Project Structure

```text
the-raven-ai/

├── app/
├── frontend/
├── ml/
│   ├── models/
│   ├── scripts/
│   ├── train.py
│   ├── evaluate.py
│   └── predict.py
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
|--------|----------|-------------|
| POST | /documents/upload | Upload document |
| GET | /documents | List documents |
| DELETE | /documents/{filename} | Delete document |
| POST | /documents/search | Semantic search |

---

## Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /chat | Ask questions |

---

# 🚀 Getting Started

## Clone

```bash
git clone https://github.com/TejasTomar28/the-raven-ai.git
cd the-raven-ai
```

---

## Backend

```bash
python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
```

---

## Install Ollama

```bash
ollama pull qwen3:4b

ollama serve
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

---

## Backend

```bash
uvicorn app.main:app --reload
```

Swagger:

```
http://localhost:8000/docs
```

---

# 💡 End-to-End Workflow

```text
Upload PDF

↓

Extract Text

↓

ML Classification

↓

Generate Embeddings

↓

Store Chunks in ChromaDB

↓

Ask Question

↓

Retrieve Relevant Chunks

↓

Generate Grounded Answer

↓

Display Supporting Citations
```

---

# 🔒 Why RAG?

Unlike traditional chatbots, RAVEN AI does not rely solely on the LLM's internal knowledge.

Instead, it retrieves relevant document passages before generating an answer.

Benefits:

- Grounded responses
- Explainable citations
- Reduced hallucinations
- Enterprise-ready knowledge retrieval

---

# 🔮 Future Improvements

- Multi-user workspaces
- Authentication & Authorization
- Streaming responses
- Hybrid keyword + semantic retrieval
- OCR support for scanned PDFs
- Docker Compose
- Kubernetes deployment
- Cloud deployment
- Role-based access control

---

# 👨‍💻 Author

**Tejas Tomar**

Software Engineering Student

Delhi Technological University (DTU)

Backend Development • Artificial Intelligence • Machine Learning • Distributed Systems

