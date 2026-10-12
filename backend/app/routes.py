import logging

from fastapi import APIRouter, HTTPException

from app.schemas import ChatResponse, QuestionRequest
from app.services.llm_services import LLMServiceError, get_answer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["AI Assistant"])


@router.post("/ask", response_model=ChatResponse)
def ask_question(request: QuestionRequest):
    try:
        answer = get_answer(request.question)
    except LLMServiceError as error:
        # Configuration problem (missing .env values...)
        logger.error("LLM configuration error: %s", error)
        raise HTTPException(status_code=500, detail=str(error))
    except Exception:
        # Network problem, invalid API key, rate limit...
        logger.exception("LLM request failed")
        raise HTTPException(
            status_code=502,
            detail="The AI service failed to answer. Check the backend terminal for details.",
        )

    return ChatResponse(answer=answer)