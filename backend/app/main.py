from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router
app= FastAPI(title="AI Learning Assistant API",
    description="Backend powered by FastAPI and LangChain",
    version="1.0.0"
    )
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(router)

@app.get("/")
def home():
    return {
        "message": "AI Learning Assistant API is running"
    }
