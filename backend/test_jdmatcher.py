
import json
import os

from app.main import get_client
from app.jd_matcher import analyze_job_description


# A sample Applied AI Engineering internship description.
# We'll use this to test matching against your actual resume data.
JOB_DESCRIPTION = """
Applied AI Engineering Intern

Responsibilities:
- Build and evaluate LLM-powered applications.
- Develop Retrieval-Augmented Generation (RAG) pipelines.
- Work with embeddings and semantic search.
- Build backend APIs using Python and FastAPI.
- Experiment with language model fine-tuning techniques.
- Evaluate model outputs for correctness and hallucinations.
- Work with PyTorch and Hugging Face Transformers.

Requirements:
- Strong Python programming skills.
- Understanding of LLMs, RAG, and vector databases.
- Familiarity with LangChain or similar frameworks.
- Knowledge of REST APIs and SQL databases.
- Bachelor's degree in Computer Science or a related field.

Preferred:
- Previous industry internship experience.
- Experience deploying AI applications to production.
"""


def main():
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    print(f"Testing JD Matcher with model: {model}")
    print("Sending job description to Groq...\n")

    try:
        result = analyze_job_description(
            job_description=JOB_DESCRIPTION,
            client=get_client(),
            model=model,
        )

        print("=" * 55)
        print("JD MATCHING RESULTS")
        print("=" * 55)

        print(json.dumps(result, indent=2, ensure_ascii=False))

    except Exception as exc:
        print(f"\nTest failed: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
