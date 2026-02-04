from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, List
from app.api.auth import verify_api_key
from app.utils.audio import process_audio_input
from app.models.detector import get_detector

router = APIRouter()

class DetectRequest(BaseModel):
    audio_base64: Optional[str] = None
    audio_url: Optional[str] = None
    transcript: Optional[str] = None 
    message: Optional[str] = None

# Hackathon Exact Format
class DetectResponse(BaseModel):
    classification: str       # "AI" | "Human"
    confidence_score: float   # 0.0 - 1.0
    ai_probability: float     # Raw AI probability
    detected_language: str    # e.g. "en", "hi", "ta"
    transcription: str        # Original transcription
    english_translation: str  # English translation
    fraud_keywords: List[str] # List of detected fraud keywords
    overall_risk: str         # "HIGH" | "MEDIUM" | "LOW"
    explanation: str          # Explanation string
    # Diagnostics
    audio_duration_seconds: float       # Duration of processed audio
    num_chunks_processed: int           # Number of 30s chunks
    chunk_ai_probabilities: List[float] # AI probability per chunk
    # Deep Diagnostics
    pitch_human_score: Optional[float] = 0.0
    pitch_std: Optional[float] = 0.0
    pitch_jitter: Optional[float] = 0.0
    smoothness_score: Optional[float] = 0.0
    variance_score: Optional[float] = 0.0
    heuristic_score: Optional[float] = 0.0
    debug_probs: Optional[List[float]] = []
    debug_labels: Optional[dict] = {}

@router.post("/detect", response_model=DetectResponse, dependencies=[Depends(verify_api_key)])
async def detect_voice(request: DetectRequest):
    if not request.audio_base64 and not request.audio_url:
        raise HTTPException(
            status_code=400, 
            detail="Must provide either 'audio_base64' or 'audio_url'"
        )
    
    try:
        audio_array = process_audio_input(request.audio_base64, request.audio_url)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio processing failed: {str(e)}")

    try:
        detector = get_detector()
        result = detector.detect_fraud(audio_array)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
