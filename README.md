# 🐦 The Raven AI

> **Ask Your Organization Anything.**

The Raven AI is an AI-powered Enterprise Knowledge Platform that enables users to search, understand, and interact with organisational documents using **Retrieval-Augmented Generation (RAG)** and **Large Language Models (LLMs)**.

Instead of manually browsing through hundreds of documents, users can ask natural language questions and receive context-aware, citation-backed answers generated from their knowledge base.

---

# ✨ Features

- 📄 Upload enterprise PDF documents
- 🔍 Semantic document search using vector embeddings
- 🤖 AI-powered question answering using Retrieval-Augmented Generation (RAG)
- 📚 Citation-backed responses grounded in uploaded documents
- 📝 AI-generated document summaries
- 🔐 Secure JWT-based authentication
- 🌐 RESTful APIs for document management and AI interactions

---

# 🏗️ System Architecture

```
                        Client / Postman
                               │
                          REST APIs
                               │
                               ▼
                    +----------------------+
                    |    Spring Boot API   |
                    +----------+-----------+
                               │
                               ▼
                     Python AI Service
                               │
                +--------------+--------------+
                |                             |
                ▼                             ▼
        PDF Text Extraction           Query Processing
                │                             │
                ▼                             ▼
         Document Chunking          Semantic Retrieval
                │                             │
                ▼                             ▼
Sentence Transformer Embeddings      Relevant Context
                │                             │
                +-------------+---------------+
                              │
                              ▼
                          ChromaDB
                              │
                              ▼
                 OpenAI / Ollama (Qwen)
                              │
                              ▼
               Citation-backed AI Response
```

---

# 🚀 Tech Stack

## Backend

- Java
- Spring Boot
- Spring Security
- JWT Authentication
- REST APIs

## AI & Machine Learning

- Python
- LangChain
- ChromaDB
- Sentence Transformers
- OpenAI API / Ollama (Qwen)

## Documentation

- Swagger / OpenAPI

---

# ⚙️ Workflow

### 1. Document Upload

Users upload PDF documents through the platform.

### 2. Document Processing

The AI service extracts text from uploaded PDFs and divides the content into meaningful chunks.

### 3. Embedding Generation

Each text chunk is converted into vector embeddings using Sentence Transformers.

### 4. Semantic Indexing

Embeddings are stored in ChromaDB to enable semantic similarity search.

### 5. Query Processing

When a user asks a question, the query is converted into an embedding and matched against the indexed document chunks.

### 6. AI Response Generation

The retrieved document chunks are provided to the Large Language Model using Retrieval-Augmented Generation (RAG), producing context-aware and citation-backed answers.

---

# 📂 Project Structure

```
the-raven-ai
│
├── backend/
│
├── ml-service/
│
├── docs/
│   ├── architecture/
│   ├── api/
│   └── screenshots/
│
├── README.md
├── docker-compose.yml
└── LICENSE
```

---

# 🔐 Authentication

- JWT Authentication
- Secure REST APIs
- Protected AI endpoints

---

# 📖 API Documentation

Swagger UI is available after running the Spring Boot application.

```
http://localhost:8080/swagger-ui/index.html
```

---

# 🎯 Core Capabilities

- Enterprise document understanding
- Semantic document retrieval
- AI-powered question answering
- Citation-backed responses
- Document summarisation
- Explainable RAG pipeline

---

# 💡 Motivation

Modern organisations generate a vast amount of knowledge in reports, manuals, policies, and technical documentation. Traditional keyword-based search often struggles to retrieve relevant information from these documents.

The Raven AI addresses this challenge by combining semantic search, Retrieval-Augmented Generation (RAG), and Large Language Models to transform static organisational documents into an intelligent knowledge assistant.

---

# 🔮 Future Enhancements

- Support for DOCX and PPTX documents
- Multi-document conversations
- Conversation history
- Hybrid Search (Semantic + Keyword)
- Streaming AI responses
- Source highlighting inside documents

---

# 👨‍💻 Author

**Tejas Tomar**

Software Engineering Undergraduate  
Delhi Technological University (DTU)
