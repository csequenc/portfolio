"""Curated public portfolio facts used as the assistant's grounding context."""

KNOWLEDGE = [
    {
        "id": "profile",
        "title": "Profile and education",
        "keywords": ["ishaan", "profile", "education", "college", "cgpa", "graduation", "about", "degree"],
        "content": (
            "Ishaan Maheshwari is a B.Tech Computer Science and Engineering undergraduate at "
            "ABES Engineering College, expected to graduate in May 2029. His focus is applied AI "
            "engineering and empirical model evaluation. His resume lists a CGPA of 9.3/10."
        ),
    },
    {
        "id": "memorymesh",
        "title": "MemoryMesh",
        "keywords": ["memorymesh", "memory", "conflict", "supersede", "database", "fastapi", "graph", "sqlite", "resolution"],
        "content": (
            "MemoryMesh is a conflict-aware AI memory engine. It extracts structured facts from "
            "natural language, retrieves semantically related memories, and supports conversational "
            "querying through FastAPI. LLM-based comparison classifies duplicate, superseding, "
            "coexisting, conflicting, and unrelated memories. Semantic judgment is separated from "
            "deterministic resolution and database state changes. It was evaluated across 25 scenarios, "
            "with 21 passing (84%). Stack: Python, FastAPI, Groq, Sentence Transformers, SQLAlchemy, "
            "SQLite, React, TypeScript, and Cytoscape.js. Repository: https://github.com/csequenc/MemoryMesh"
        ),
    },
    {
        "id": "lora-dora",
        "title": "LoRA vs. DoRA study",
        "keywords": ["lora", "dora", "fine tuning", "finetuning", "qwen", "spider", "text to sql", "research", "training", "pytorch"],
        "content": (
            "The LoRA vs. DoRA project is a rank-8 case study on text-to-SQL. It compares LoRA and "
            "DoRA fine-tuning on Qwen2.5-1.5B for Spider using identical hyperparameters and execution "
            "accuracy on 300 held-out examples. Experiments were repeated across three seeds. "
            "Per-example agreement was 89.7%; the accuracy gap was indistinguishable from training "
            "noise. DoRA training throughput was approximately 20% lower, traced to per-step weight-norm "
            "computation. Stack: PyTorch, PEFT, and Hugging Face Transformers."
        ),
    },
    {
        "id": "rag-agent",
        "title": "RAG and Agentic AI system",
        "keywords": ["rag", "agent", "agentic", "retrieval", "faiss", "langchain", "groq", "tool calling", "hallucination", "guardrail"],
        "content": (
            "The RAG & Agentic AI System uses Sentence Transformers and FAISS for retrieval-augmented "
            "generation, and tool-calling workflows. It was first built modularly and then migrated to "
            "LangChain. A gold-question evaluation pipeline uses LLM-as-judge scoring for correctness, "
            "grounding, hallucination, and completeness, with regression tests. It includes a "
            "prompt-injection guardrail and a FastAPI REST API with structured request logging. "
            "Stack: Python, LangChain, Sentence Transformers, FAISS, Groq, and FastAPI. "
            "Repository: https://github.com/csequenc/ai-rag-agent"
        ),
    },
    {
        "id": "skills",
        "title": "Technical skills",
        "keywords": ["skills", "python", "c++", "pytorch", "transformers", "faiss", "react", "typescript", "sqlalchemy", "technologies", "tools", "stack"],
        "content": (
            "Languages: Python and C++. AI/ML: RAG, LLMs, embeddings, semantic retrieval, prompt "
            "engineering, LLM evaluation, tool calling, LoRA, and DoRA. Frameworks and libraries: "
            "PyTorch, Hugging Face Transformers, PEFT, LangChain, Sentence Transformers, FAISS, and "
            "Pydantic. Backend and data: FastAPI, REST APIs, SQLAlchemy, SQLite, and Groq API. "
            "Frontend and tools: React, TypeScript, Cytoscape.js, Git, and GitHub."
        ),
    },
    {
        "id": "contact",
        "title": "Contact and links",
        "keywords": ["contact", "email", "linkedin", "github", "reach", "connect"],
        "content": (
            "GitHub: https://github.com/csequenc. LinkedIn: https://linkedin.com/in/maheshwari-ishaan. "
            "Email: ishaan.maheshwari.07@gmail.com."
        ),
    },
]


def retrieve(question: str, limit: int = 3) -> list[dict[str, str]]:
    """Small lexical retriever; the LLM only sees the highest-scoring portfolio notes."""
    import re

    stop_words = {
        "what", "when", "where", "which", "who", "why", "how", "does", "did", "are", "is",
        "was", "were", "the", "and", "for", "with", "from", "about", "tell", "me", "can",
        "you", "your", "his", "her", "this", "that", "have", "has", "had", "please", "explain",
    }
    terms = {term for term in re.findall(r"[a-z0-9+#.-]+", question.lower()) if len(term) > 2 and term not in stop_words}
    scored: list[tuple[int, dict[str, str]]] = []
    for item in KNOWLEDGE:
        searchable = (item["title"] + " " + item["content"]).lower()
        score = sum(3 for keyword in item["keywords"] if keyword in terms)
        score += sum(1 for term in terms if term in searchable)
        if score:
            scored.append((score, item))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in scored[:limit]]
