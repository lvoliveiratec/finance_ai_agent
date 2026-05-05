import logging
import os
import re
from typing import Any

from fastapi import FastAPI, Request
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from finance_ai_agent.agent import root_agent


APP_NAME = os.getenv("ADK_APP_NAME", "finance_ai_agent")
MAX_QUESTIONS_PER_MESSAGE = int(os.getenv("MAX_QUESTIONS_PER_MESSAGE", "5"))

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Finance AI Chat Adapter")
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)


def _extract_chat_text(payload: dict[str, Any]) -> str:
    return payload.get("message", {}).get("argumentText") or payload.get("message", {}).get("text") or ""


def _extract_user_id(payload: dict[str, Any]) -> str:
    user = payload.get("user") or payload.get("message", {}).get("sender", {})
    return user.get("email") or user.get("name") or "anonymous"


def _extract_session_id(payload: dict[str, Any], user_id: str) -> str:
    space = payload.get("space") or payload.get("message", {}).get("space", {})
    thread = payload.get("message", {}).get("thread", {})
    space_name = space.get("name", "space")
    thread_name = thread.get("name", "thread")
    raw_session = f"{user_id}:{space_name}:{thread_name}"
    return raw_session.replace("/", "_").replace(":", "_")


def _split_questions(text: str) -> list[str]:
    normalized = text.strip()
    if not normalized:
        return []

    lines = [
        re.sub(r"^\s*[-*\d.)]+\s*", "", line).strip()
        for line in normalized.splitlines()
        if line.strip()
    ]

    if len(lines) > 1:
        return lines

    parts = [part.strip() for part in re.split(r"(?<=\?)\s+", normalized) if part.strip()]
    return parts or [normalized]


async def _ensure_session(user_id: str, session_id: str) -> None:
    try:
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )
    except Exception:
        # A sessao pode ja existir no processo atual.
        logging.debug("Session already exists or could not be created", exc_info=True)


async def _ask_agent(user_id: str, session_id: str, text: str) -> str:
    await _ensure_session(user_id, session_id)

    content = types.Content(
        role="user",
        parts=[types.Part(text=text)],
    )

    final_parts: list[str] = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
    ):
        if not getattr(event, "content", None):
            continue
        for part in event.content.parts or []:
            if getattr(part, "text", None):
                final_parts.append(part.text)

    if not final_parts:
        return "Nao consegui gerar uma resposta para essa pergunta."

    return final_parts[-1]


async def _ask_agent_for_message(user_id: str, session_id: str, text: str) -> str:
    questions = _split_questions(text)

    if len(questions) <= 1:
        return await _ask_agent(user_id=user_id, session_id=session_id, text=text)

    if len(questions) > MAX_QUESTIONS_PER_MESSAGE:
        return (
            f"Recebi {len(questions)} perguntas na mesma mensagem. "
            f"Para manter a resposta confiavel, envie no maximo {MAX_QUESTIONS_PER_MESSAGE} perguntas por vez."
        )

    answers: list[str] = []
    for index, question in enumerate(questions, start=1):
        child_session_id = f"{session_id}_q{index}"
        answer = await _ask_agent(user_id=user_id, session_id=child_session_id, text=question)
        answers.append(f"Pergunta {index}: {question}\n{answer.strip()}")

    return "\n\n".join(answers)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/")
async def google_chat_webhook(request: Request) -> dict[str, str]:
    payload = await request.json()
    event_type = payload.get("type")

    if event_type == "ADDED_TO_SPACE":
        return {"text": "Ola. Sou o agente financeiro da POC. Pode me perguntar sobre receita, despesa, orcado e fornecedores."}

    text = _extract_chat_text(payload).strip()
    if not text:
        return {"text": "Envie uma pergunta financeira para eu consultar os dados da POC."}

    user_id = _extract_user_id(payload)
    session_id = _extract_session_id(payload, user_id)

    try:
        answer = await _ask_agent_for_message(user_id=user_id, session_id=session_id, text=text)
        return {"text": answer}
    except Exception:
        logging.exception("Erro ao processar mensagem do Google Chat")
        return {"text": "Tive um erro ao consultar os dados financeiros. Verifique os logs do Cloud Run."}


@app.post("/google-chat")
async def google_chat_webhook_alias(request: Request) -> dict[str, str]:
    return await google_chat_webhook(request)
