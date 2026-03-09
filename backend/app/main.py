"""
SAGE FastAPI application.

Run:
    uvicorn app.main:app --reload --port 8000
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)

from app.routers.agent import router as agent_router
from app.routers.submissions import router as submissions_router

app = FastAPI(
    title="SAGE — AI Governance & Evaluation API",
    version="1.0.0",
    description="Backend for the SAGE agentic evaluation assistant.",
)

# Allow the Vite dev server and production build
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent_router)
app.include_router(submissions_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "SAGE"}
