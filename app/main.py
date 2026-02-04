from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes import router as api_router
from app.models.detector import VoiceDetector

# Lifecycle manager to preload model
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load model on startup
    print("Initializing application...")
    VoiceDetector.get_instance()
    yield
    print("Shutting down...")

app = FastAPI(
    title="AI Voice Detector API",
    description="Hackathon API for detecting AI-generated speech using Wav2Vec2",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(api_router, prefix="")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
