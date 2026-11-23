
from __future__ import annotations

from multiprocessing import context
import re
import os
from collections import defaultdict, deque
from functools import lru_cache
from threading import Lock
from time import monotonic
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from pydantic import BaseModel, Field

from .knowledge import retrieve
from .jd_matcher import analyze_job_description

load_dotenv()

app = FastAPI(
    title="I Portfolio API",
    version="1.0.0",
    description="Grounded portfolio assistant API",
)

_request_times: dict[str, deque[float]] = defaultdict(deque)
_rate_lock = Lock()

origins = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# ---------------------------------------------------------------------
# Request and response models
# ---------------------------------------------------------------------

class HistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=2000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[HistoryMessage] = Field(default_factory=list, max_length=8)


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


class JDMatchRequest(BaseModel):
    job_description: str = Field(
        min_length=50,
        max_length=12000,
    )


# ---------------------------------------------------------------------
# Groq client
# ---------------------------------------------------------------------

@lru_cache(maxsize=1)
def get_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="The AI assistant is not configured yet. Add GROQ_API_KEY to the backend environment.",
        )

    return Groq(api_key=api_key)


# ---------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------

@app.get("/api/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "I Portfolio API",
    }


# ---------------------------------------------------------------------
# Portfolio chatbot
# ---------------------------------------------------------------------

@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, request: Request) -> ChatResponse:

    # Lightweight per-process abuse guard.
    client_ip = request.client.host if request.client else "unknown"
    now = monotonic()

    with _rate_lock:
        recent = _request_times[client_ip]

        while recent and now - recent[0] > 60:
            recent.popleft()

        if len(recent) >= 20:
            raise HTTPException(
                status_code=429,
                detail="Too many questions in a short period. Please wait a minute and try again.",
            )

        recent.append(now)

    # Detect greetings so previous topics don't contaminate retrieval.
    is_greeting = bool(
        re.fullmatch(
            r"(?:hi|hello|hey|heya|yo|good morning|good afternoon|good evening)"
            r"(?:\s+(?:there|chatbot|ishaan))?[!.?,\s]*",
            payload.message.strip(),
            re.IGNORECASE,
        )
    )

    # Retrieve only for the current question.
    # Do not pull old topics into unrelated questions.
    sources = [] if is_greeting else retrieve(payload.message)

    context = "\n\n".join(
        f"[{item['title']}]\n{item['content']}"
        for item in sources
    )

    
    system_prompt = f"""You are Ask Ishaan, the AI assistant on Ishaan Maheshwari's personal portfolio.

Your job is to answer visitors' questions about Ishaan's background, projects,
technical skills, experiments, and documented work.

PERSONALITY:
- Sound natural, conversational, and approachable.
- Speak like a developer discussing his own work.
- Be confident but never boastful or overly enthusiastic.
- Avoid robotic language, corporate wording, and repetitive openings.

RESPONSE STYLE:
- Be concise by default. Most answers should be 2-3 sentences.
- Answer the exact question without explaining every related detail.
- For simple questions, give a direct answer.
- For project questions, briefly explain what the project does and its main idea.
- Mention technologies, architecture, metrics, or implementation details only
  when relevant to the question.
- Use bullets only when listing multiple items genuinely improves clarity.
- Expand when the visitor explicitly asks for details, an explanation,
  a comparison, or how something works.
- Don't repeat information or add unnecessary introductions and conclusions.
- Always finish your final sentence and complete your thought.
- Never end with an unfinished sentence, dangling bullet, or incomplete explanation.
- Prefer a shorter complete answer over a longer answer that risks being cut off.
- Do not start explaining additional details if there isn't enough room to finish.
- For broad questions like "What is X?", give a brief overview in 1-2 sentences.
- Do not list the full technology stack or implementation details unless asked.
- Treat the visitor's question as the limit of what needs explaining.

ACCURACY:
- Use the portfolio context as the source of truth about Ishaan.
- Never invent features, technologies, metrics, results, responsibilities,
  dates, or experience.
- If something isn't documented, say so naturally rather than guessing.
- Distinguish actual project implementations from general technical explanations.
- Never present assumptions as facts.

CONVERSATION:
- Use previous messages to understand follow-up questions.
- Don't repeat a project introduction when answering a follow-up.
- Interpret short questions using the conversation context.
- Don't let unrelated earlier topics influence the current answer.

PORTFOLIO CONTEXT:
{context if context else "No directly relevant portfolio information was retrieved. Be transparent and do not guess."}
"""


    # Don't feed old conversation into a greeting.
    messages = [
        {"role": "system", "content": system_prompt}
    ]

    if not is_greeting:
        for item in payload.history[-6:]:
            messages.append({
                "role": item.role,
                "content": item.content,
            })

    messages.append({
        "role": "user",
        "content": payload.message,
    })

    try:
        completion = get_client().chat.completions.create(
            model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
            messages=messages,
            temperature=0.45,
            max_completion_tokens=300,
        )

        answer = (
            completion.choices[0].message.content
            or "I couldn't produce an answer just now. Please try again."
        )

        return ChatResponse(
            answer=answer.strip(),
            sources=[item["title"] for item in sources],
        )

    except HTTPException:
        raise

    except Exception as exc:
        print(f"Groq request failed: {type(exc).__name__}")

        raise HTTPException(
            status_code=502,
            detail="The AI provider could not complete the request. Please try again shortly.",
        ) from exc


# ---------------------------------------------------------------------
# AI-powered Job Description Matcher
# ---------------------------------------------------------------------

@app.post("/api/jd-match")
def jd_match(payload: JDMatchRequest) -> dict:

    try:
        result = analyze_job_description(
            job_description=payload.job_description,
            client=get_client(),
            model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        )

        return result

    except HTTPException:
        raise

    except ValueError as exc:
        print(f"JD matcher validation failed: {type(exc).__name__}")

        raise HTTPException(
            status_code=502,
            detail="The JD analysis could not be completed reliably. Please try again.",
        ) from exc

    except Exception as exc:
        print(f"JD matcher failed: {type(exc).__name__}")

        raise HTTPException(
            status_code=502,
            detail="The AI provider could not complete the JD analysis. Please try again shortly.",
        ) from exc
