from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas import AnalyzeRequest, AnalysisResponse
from app.services.llm_service import analyze_transcript
from app.core.config import settings


router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalyzeRequest) -> AnalysisResponse:
    try:
        return await analyze_transcript(
            transcript=request.transcript,
            provider=request.provider,
            model=request.model,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc


@router.get("/providers")
async def providers_info() -> dict:
    return {
        "gemini_configured": bool(settings.gemini_api_key and not settings.gemini_api_key.startswith("PASTE_")),
        "groq_configured": bool(settings.groq_api_key and not settings.groq_api_key.startswith("PASTE_")),
        "openai_configured": bool(settings.openai_api_key and not settings.openai_api_key.startswith("PASTE_")),
        "preferred_provider": settings.llm_provider,
    }

