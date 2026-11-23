
RESUME_DATA = {
    "profile": {
        "name": "Ishaan Maheshwari",
        "headline": "B.Tech Computer Science & Engineering | Applied AI Engineering",
        "summary": (
            "Computer Science undergraduate focused on applied AI engineering "
            "and empirical model evaluation. Built RAG, tool-calling, and "
            "persistent memory systems; fine-tuned and benchmarked language "
            "models through controlled experiments, reproducible evaluations, "
            "and documented failure analysis."
        ),
    },

    "education": [
        {
            "degree": "B.Tech, Computer Science and Engineering",
            "institution": "ABES Engineering College",
            "expected_graduation": "May 2029",
            "cgpa": "9.3 / 10",
        }
    ],

    "skills": {
        "programming_languages": [
            "Python",
            "C++",
        ],
        "ai_ml": [
            "RAG",
            "LLMs",
            "Embeddings",
            "Semantic Retrieval",
            "Prompt Engineering",
            "LLM Evaluation",
            "Tool Calling",
            "LoRA",
            "DoRA",
        ],
        "frameworks_and_libraries": [
            "PyTorch",
            "Hugging Face Transformers",
            "PEFT",
            "LangChain",
            "Sentence Transformers",
            "FAISS",
            "Pydantic",
        ],
        "backend_and_data": [
            "FastAPI",
            "REST APIs",
            "SQLAlchemy",
            "SQLite",
            "Groq API",
        ],
        "frontend_and_tools": [
            "React",
            "TypeScript",
            "Cytoscape.js",
            "Git",
            "GitHub",
        ],
    },

    "projects": [
        {
            "name": "MemoryMesh — Conflict-Aware AI Memory Engine",
            "type": "Independent Project",
            "technologies": [
                "Python",
                "FastAPI",
                "Groq",
                "Sentence Transformers",
                "SQLAlchemy",
                "SQLite",
                "React",
                "TypeScript",
                "Cytoscape.js",
            ],
            "description": (
                "A persistent memory engine that extracts structured facts "
                "from natural language, retrieves semantically related "
                "memories, and supports conversational querying."
            ),
            "contributions": [
                (
                    "Built a persistent memory engine that extracts "
                    "structured facts from natural language, retrieves "
                    "semantically related memories, and supports "
                    "conversational querying through a FastAPI backend."
                ),
                (
                    "Implemented LLM-based comparison to classify duplicate, "
                    "superseding, coexisting, conflicting, and unrelated "
                    "memories; separated semantic judgment from deterministic "
                    "resolution and database state changes."
                ),
                (
                    "Developed a React knowledge-graph and memory-management "
                    "interface; evaluated resolution across 25 scenarios, "
                    "with 21 passing (84%), and analyzed four "
                    "judgment-sensitive supersession cases."
                ),
            ],
            "evidence": [
                "Persistent memory extraction and retrieval",
                "LLM-based memory comparison and conflict classification",
                "Deterministic resolution and database state management",
                "25 evaluation scenarios with 21 passing (84%)",
                "React knowledge-graph interface",
            ],
        },

        {
            "name": "LoRA vs. DoRA: A Rank-8 Case Study on Text-to-SQL",
            "type": "Independent Project",
            "technologies": [
                "PyTorch",
                "PEFT",
                "Hugging Face Transformers",
            ],
            "description": (
                "A controlled comparison of rank-8 LoRA and DoRA fine-tuning "
                "on Qwen2.5-1.5B for Spider text-to-SQL."
            ),
            "contributions": [
                (
                    "Compared rank-8 LoRA and DoRA fine-tuning on "
                    "Qwen2.5-1.5B for Spider text-to-SQL, using identical "
                    "hyperparameters and execution accuracy on 300 "
                    "held-out examples."
                ),
                (
                    "Repeated experiments across three seeds; per-example "
                    "agreement (89.7%) and query-complexity analysis showed "
                    "the accuracy gap was indistinguishable from training noise."
                ),
                (
                    "Measured a reproducible ~10-16% lower DoRA training "
                    "throughput across seeds and traced the cost to "
                    "per-step weight-norm computation; published methodology, "
                    "results, and reproducible evaluation tooling."
                ),
            ],
            "evidence": [
                "LoRA and DoRA fine-tuning",
                "Qwen2.5-1.5B",
                "Spider text-to-SQL benchmark",
                "300 held-out examples",
                "Experiments across three seeds",
                "89.7% per-example agreement",
                "~20% lower DoRA training throughput",
                "Reproducible evaluation tooling",
            ],
        },

        {
            "name": "RAG & Agentic AI System",
            "type": "Independent Project",
            "technologies": [
                "Python",
                "LangChain",
                "Sentence Transformers",
                "FAISS",
                "Groq",
                "FastAPI",
            ],
            "description": (
                "A modular retrieval-augmented generation and tool-calling "
                "system built from first principles and later migrated to LangChain."
            ),
            "contributions": [
                (
                    "Built modular RAG and tool-calling workflows from "
                    "first principles using Sentence Transformers and FAISS, "
                    "then migrated the architecture to LangChain."
                ),
                (
                    "Created a gold-question evaluation pipeline with "
                    "LLM-as-judge scoring for correctness, grounding, "
                    "hallucination, and completeness; used regression "
                    "tests to assess iterations."
                ),
                (
                    "Implemented and evaluated a prompt-injection guardrail "
                    "and exposed the system through a FastAPI REST API "
                    "with structured request logging."
                ),
            ],
            "evidence": [
                "Modular RAG architecture",
                "Semantic retrieval using Sentence Transformers and FAISS",
                "Tool-calling workflows",
                "LangChain migration",
                "LLM-as-judge evaluation",
                "Correctness, grounding, hallucination, and completeness metrics",
                "Prompt-injection guardrail",
                "FastAPI REST API and request logging",
            ],
        },
    ],

    # No professional experience or certifications are listed
    # in the source resume.
    "experience": [],

    "certifications": [],

    # Project evaluation results are already represented
    # in the relevant project contributions.
    "achievements": [],
}
