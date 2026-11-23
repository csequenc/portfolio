
"""Curated public portfolio facts and semantic retrieval for Ask Ishaan."""

from __future__ import annotations

from functools import lru_cache

import numpy as np

from .embeddings import embed_texts


KNOWLEDGE: list[dict[str, str | list[str]]] = [
    {
        "id": "profile",
        "title": "Profile and education",
        "keywords": [
            "ishaan", "profile", "education", "college",
            "cgpa", "graduation", "about"
        ],
        "content": (
            "Ishaan Maheshwari is a Computer Science and Engineering undergraduate "
            "pursuing a B.Tech at ABES Engineering College. His expected graduation "
            "date is May 2029, and his reported CGPA is 9.3/10. His primary focus is "
            "applied AI engineering and empirical evaluation of machine learning "
            "systems. His documented projects include MemoryMesh, a conflict-aware "
            "AI memory engine; a RAG and Agentic AI System; and a controlled "
            "LoRA vs. DoRA fine-tuning study."
        ),
    },
    {
        "id": "memorymesh-overview",
        "title": "MemoryMesh - project overview",
        "keywords": [
            "memorymesh", "memory", "persistent memory",
            "ai memory", "facts"
        ],
        "content": (
            "MemoryMesh is a conflict-aware AI memory engine designed to extract "
            "structured facts from natural-language input, retrieve semantically "
            "related memories, and support conversational querying. It focuses on "
            "handling information that changes over time or contains contradictions, "
            "rather than treating every newly extracted fact as an unrelated entry. "
            "The backend uses Python and FastAPI, with Groq for LLM-based comparison, "
            "SQLAlchemy and SQLite for persistence, and Sentence Transformers for "
            "semantic retrieval. Its interface uses React, TypeScript, and Cytoscape.js. "
            "Repository: https://github.com/csequenc/MemoryMesh"
        ),
    },
    {
        "id": "memorymesh-resolution",
        "title": "MemoryMesh - comparison and conflict resolution",
        "keywords": [
            "memorymesh", "duplicate", "superseding",
            "coexisting", "conflicting", "resolution"
        ],
        "content": (
            "MemoryMesh uses LLM-based comparison to classify relationships between "
            "memories. The supported relationship categories are duplicate, "
            "superseding, coexisting, conflicting, and unrelated. The system separates "
            "semantic judgment from deterministic resolution and database state "
            "changes. The LLM determines how two pieces of information relate; "
            "deterministic application logic handles the resulting resolution and "
            "persistence operations. This separation keeps semantic interpretation "
            "distinct from changes to stored memory."
        ),
    },
    {
        "id": "memorymesh-evaluation",
        "title": "MemoryMesh - evaluation and results",
        "keywords": [
            "memorymesh", "evaluation", "testing",
            "scenarios", "accuracy", "results"
        ],
        "content": (
            "MemoryMesh was evaluated across 25 scenarios, with 21 passing, "
            "corresponding to an 84% pass rate. The evaluation also involved analysis "
            "of four judgment-sensitive supersession cases. The project includes "
            "a React-based knowledge-graph and memory-management interface. "
            "The reported evaluation result is 21 passing scenarios out of 25; "
            "it should not be interpreted as a general production accuracy guarantee."
        ),
    },
    {
        "id": "lora-dora-overview",
        "title": "LoRA vs DoRA - experimental setup",
        "keywords": [
            "lora", "dora", "fine tuning", "finetuning",
            "qwen", "spider", "text to sql"
        ],
        "content": (
            "The LoRA vs. DoRA project is a controlled rank-8 fine-tuning study "
            "for text-to-SQL generation. It compares Low-Rank Adaptation (LoRA) "
            "and Weight-Decomposed Low-Rank Adaptation (DoRA) on Qwen2.5-1.5B "
            "using the Spider text-to-SQL benchmark. Both methods were evaluated "
            "using identical hyperparameters and execution accuracy on 300 "
            "held-out examples. Experiments were repeated across three random seeds. "
            "The implementation uses PyTorch, Hugging Face Transformers, and PEFT."
        ),
    },
    {
        "id": "lora-dora-results",
        "title": "LoRA vs DoRA - findings and performance",
        "keywords": [
            "lora", "dora", "agreement", "throughput",
            "training", "benchmark", "results"
        ],
        "content": (
            "The LoRA vs. DoRA experiments reported 89.7% per-example agreement. "
            "The observed accuracy difference between the methods was "
            "indistinguishable from training noise in the experiments. DoRA had "
            "approximately 10-16% lower training throughput. The additional cost was "
            "traced to per-step weight-norm computation. The study emphasizes "
            "controlled comparisons, multiple random seeds, execution-based "
            "evaluation, and analysis of the practical trade-offs between the methods. "
            "It does not establish that one method is universally more accurate."
        ),
    },
    {
        "id": "rag-agent-overview",
        "title": "RAG and Agentic AI system - architecture",
        "keywords": [
            "rag", "agent", "agentic", "retrieval",
            "faiss", "langchain", "tool calling"
        ],
        "content": (
            "The RAG and Agentic AI System combines retrieval-augmented generation "
            "with tool-calling workflows. Its initial implementation was built "
            "modularly using Sentence Transformers for embeddings and FAISS for "
            "similarity-based retrieval. The architecture was later migrated to "
            "LangChain. The project uses Groq for language-model interaction and "
            "FastAPI to expose functionality through a REST API. "
            "Repository: https://github.com/csequenc/ai-rag-agent. "
            "The project description should not be interpreted as a separate "
            "autonomous agent platform or a claim that it executes arbitrary tasks."
        ),
    },
    {
        "id": "rag-agent-evaluation",
        "title": "RAG and Agentic AI system - evaluation and safeguards",
        "keywords": [
            "rag", "evaluation", "hallucination", "grounding",
            "guardrail", "prompt injection", "testing"
        ],
        "content": (
            "The RAG and Agentic AI System includes a gold-question evaluation "
            "pipeline using LLM-as-judge scoring. Its evaluation dimensions include "
            "correctness, grounding, hallucination, and completeness. Regression "
            "tests are used to assess changes across iterations. The system also "
            "implements and evaluates a prompt-injection guardrail. Its FastAPI "
            "REST API includes structured request logging. These components support "
            "systematic evaluation of response quality and safer handling of "
            "untrusted input."
        ),
    },
    {
        "id": "skills",
        "title": "Technical skills and technologies",
        "keywords": [
            "skills", "python", "c++", "pytorch",
            "transformers", "faiss", "react",
            "typescript", "technologies"
        ],
        "content": (
            "Ishaan's documented technical skills are grouped as follows. "
            "Programming: Python and C++. "
            "AI and ML: RAG, LLMs, embeddings, semantic retrieval, prompt "
            "engineering, LLM evaluation, tool calling, LoRA, and DoRA. "
            "Libraries: PyTorch, Hugging Face Transformers, PEFT, LangChain, "
            "Sentence Transformers, FAISS, and Pydantic. "
            "Backend: FastAPI, REST APIs, SQLAlchemy, SQLite, and Groq API. "
            "Frontend and tools: React, TypeScript, Cytoscape.js, Git, and GitHub. "
            "These are documented skills, not a ranked assessment of proficiency."
        ),
    },
    {
        "id": "contact",
        "title": "Contact and professional links",
        "keywords": [
            "contact", "email", "linkedin", "github", "reach", "connect"
        ],
        "content": (
            "GitHub: https://github.com/csequenc. "
            "LinkedIn: https://linkedin.com/in/maheshwari-ishaan. "
            "Email: ishaan.maheshwari.07@gmail.com."
        ),
    },
]


# Minimum cosine similarity for retrieved records.
MIN_SIMILARITY = 0.15


def _record_text(item: dict) -> str:
    """Build the text representation embedded for each knowledge record."""
    return f"{item['title']}. {item['content']}"


@lru_cache(maxsize=1)
def _knowledge_vectors() -> np.ndarray:
    """Generate and cache normalized embeddings for all knowledge records."""
    texts = [_record_text(item) for item in KNOWLEDGE]

    vectors = embed_texts(texts)

    if vectors.shape[0] != len(KNOWLEDGE):
        raise RuntimeError(
            "Knowledge embedding count does not match the number of records."
        )

    return vectors


def retrieve(
    question: str,
    limit: int = 5,
) -> list[dict[str, str | list[str]]]:
    """Retrieve the most relevant portfolio records using cosine similarity."""

    question = question.strip()

    if not question or limit <= 0:
        return []

    question_vector = embed_texts([question])[0]
    knowledge_vectors = _knowledge_vectors()

    # Embeddings are L2-normalized, so dot product gives cosine similarity.
    similarities = knowledge_vectors @ question_vector

    ranked_indices = np.argsort(similarities)[::-1]

    results: list[dict[str, str | list[str]]] = []

    for index in ranked_indices:
        score = float(similarities[index])

        if score < MIN_SIMILARITY:
            continue

        results.append(KNOWLEDGE[int(index)])

        if len(results) >= limit:
            break

    return results
