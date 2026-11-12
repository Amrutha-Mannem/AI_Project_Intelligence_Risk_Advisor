from fastapi import APIRouter
from app.models.chat import ChatQuery, ChatResponse
from app.deps import assistant

router = APIRouter(prefix="/api/chat", tags=["Conversational Assistant"])


@router.post("/query", response_model=ChatResponse)
async def chat_query(req: ChatQuery):
    return assistant.answer_query(req)
