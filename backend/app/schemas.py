from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    # Identifies the conversation. The frontend creates it and sends it every time,
    # so the backend knows whose memory to use.
    session_id: str = Field(min_length=1, max_length=100)


class ChatResponse(BaseModel):
    answer: str