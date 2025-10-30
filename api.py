import os
import re
import pickle
import pathlib
import zipfile
from typing import List, Optional

import gdown
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sklearn.ensemble import RandomForestClassifier

# -------------------- Model Download & Extraction --------------------
MODELS_DIR = pathlib.Path("trained_models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_FILES = {
    "email_model.pkl.zip": "1DXNw2o7x_sg_rQP1SYCyFUrqfwlZcgpe",
    "email_vectorizer.pkl.zip": "1-GeQFYkqf3nq0-xBdHYYagTqPidvU-_S",
    "url_model.pkl.zip": "1Isdoe_udMTBpEdlvNr2hSn1oQk4m6wG_",
}

def download_models_from_drive():
    """Download model files from Google Drive if not present"""
    for filename, file_id in MODEL_FILES.items():
        filepath = MODELS_DIR / filename
        if not filepath.exists():
            print(f"[Dual-AI] Downloading {filename}...")
            url = f"https://drive.google.com/uc?id={file_id}"
            try:
                gdown.download(url, str(filepath), quiet=False)
                print(f"[Dual-AI] ✓ Downloaded {filename}")
            except Exception as e:
                print(f"[Dual-AI] ✗ Failed to download {filename}: {e}")

def extract_models():
    """Extract ZIP files if needed"""
    EXPECTED_PKLS = {
        "email_model.pkl": MODELS_DIR / "email_model.pkl",
        "email_vectorizer.pkl": MODELS_DIR / "email_vectorizer.pkl",
        "url_model.pkl": MODELS_DIR / "url_model.pkl",
    }
    
    for zip_name, pkl_name in [
        ("email_model.pkl.zip", "email_model.pkl"),
        ("email_vectorizer.pkl.zip", "email_vectorizer.pkl"),
        ("url_model.pkl.zip", "url_model.pkl"),
    ]:
        zip_path = MODELS_DIR / zip_name
        pkl_path = MODELS_DIR / pkl_name
        if zip_path.exists() and not pkl_path.exists():
            print(f"[Dual-AI] Extracting {zip_name}...")
            try:
                with zipfile.ZipFile(zip_path, "r") as z:
                    z.extractall(MODELS_DIR)
                print(f"[Dual-AI] ✓ Extracted {pkl_name}")
            except Exception as e:
                print(f"[Dual-AI] ✗ Failed to extract {zip_name}: {e}")

# Run downloads and extraction at startup
download_models_from_drive()
extract_models()

# -------------------- Models & Registry --------------------
class ModelRegistry:
    email_model: Optional[object] = None
    email_vectorizer: Optional[object] = None
    url_model: Optional[RandomForestClassifier] = None
    feature_names: Optional[List[str]] = None

def try_load_email_model() -> None:
    model_path = MODELS_DIR / "email_model.pkl"
    vectorizer_path = MODELS_DIR / "email_vectorizer.pkl"
    if model_path.exists() and vectorizer_path.exists():
        with open(model_path, "rb") as f:
            ModelRegistry.email_model = pickle.load(f)
        with open(vectorizer_path, "rb") as f:
            ModelRegistry.email_vectorizer = pickle.load(f)
        print("[Dual-AI] ✓ Email model loaded")

def load_url_model() -> None:
    url_pkl = MODELS_DIR / "url_model.pkl"
    if url_pkl.exists():
        with open(url_pkl, "rb") as f:
            ModelRegistry.url_model = pickle.load(f)
        ModelRegistry.feature_names = [
            "UsingIP", "LongURL", "ShortURL", "Symbol@", "HTTPS", "Redirecting//"
        ]
        print("[Dual-AI] ✓ URL model loaded")

def extract_url_features(url: str) -> List[int]:
    feature_names = ModelRegistry.feature_names
    if feature_names is None:
        raise HTTPException(status_code=500, detail="URL feature names not initialized")
    features = [0] * len(feature_names)

    def set_feat(name: str, value: int) -> None:
        if name in feature_names:
            idx = feature_names.index(name)
            features[idx] = value

    ip_pattern = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    set_feat("UsingIP", 1 if re.search(ip_pattern, url) else -1)
    set_feat("LongURL", 1 if len(url) > 75 else -1)
    set_feat("ShortURL", 1 if any(d in url for d in ["bit.ly", "tinyurl", "t.co", "goo.gl"]) else -1)
    set_feat("Symbol@", 1 if "@" in url else -1)
    set_feat("HTTPS", 1 if url.lower().startswith("https") else -1)
    set_feat("Redirecting//", 1 if url.count("//") > 1 else -1)

    return features

def analyze_url_with_model(url: str):
    if ModelRegistry.url_model is None:
        raise HTTPException(status_code=500, detail="URL model not initialized")
    feats = extract_url_features(url)
    pred = int(ModelRegistry.url_model.predict([feats])[0])
    proba = ModelRegistry.url_model.predict_proba([feats])[0]
    return {
        "prediction": "legitimate" if pred == 1 else "phishing",
        "probabilities": {"phishing": float(proba[0]), "legitimate": float(proba[1])},
        "features_used": ModelRegistry.feature_names,
    }

def analyze_email_with_model(text: str):
    if ModelRegistry.email_model is None or ModelRegistry.email_vectorizer is None:
        raise HTTPException(status_code=503, detail="Email model not available")
    tfidf = ModelRegistry.email_vectorizer.transform([text])
    pred = int(ModelRegistry.email_model.predict(tfidf)[0])
    proba = ModelRegistry.email_model.predict_proba(tfidf)[0]
    return {
        "prediction": "phishing" if pred == 1 else "legitimate",
        "probabilities": {"legitimate": float(proba[0]), "phishing": float(proba[1])},
    }

# -------------------- Schemas --------------------
class URLRequest(BaseModel):
    url: str = Field(..., example="https://example.com")

class EmailRequest(BaseModel):
    text: str = Field(..., example="Dear user, verify your account...")

class DualRequest(BaseModel):
    text: str = Field(..., example="Email body with links")

# -------------------- App & CORS --------------------
app = FastAPI(title="Dual AI Phishing Detector API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- Startup --------------------
@app.on_event("startup")
def _startup() -> None:
    try_load_email_model()
    load_url_model()
    print("[Dual-AI] API ready ✓")

# -------------------- CORS Preflight Handler --------------------
@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    return {}

# -------------------- Endpoints --------------------
@app.get("/")
def root():
    return {
        "service": "Dual AI Phishing Detector API",
        "version": "1.0.0",
        "email_model": bool(ModelRegistry.email_model),
        "url_model": bool(ModelRegistry.url_model),
    }

@app.get("/healthz")
def healthz():
    return {
        "status": "ok",
        "email_model": bool(ModelRegistry.email_model),
        "url_model": bool(ModelRegistry.url_model)
    }

@app.post("/predict/url")
def predict_url(req: URLRequest):
    return analyze_url_with_model(req.url)

@app.post("/predict/email")
def predict_email(req: EmailRequest):
    return analyze_email_with_model(req.text)

@app.post("/predict/dual")
def predict_dual(req: DualRequest):
    url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    urls = re.findall(url_pattern, req.text)

    email_result = None
    try:
        email_result = analyze_email_with_model(req.text)
    except HTTPException:
        pass

    url_results = [analyze_url_with_model(u) for u in urls] if urls else []
    overall = "safe"
    if any(r["prediction"] == "phishing" for r in url_results):
        overall = "phishing"
    if email_result and email_result["prediction"] == "phishing":
        overall = "phishing"

    return {
        "overall": overall,
        "email": email_result,
        "urls_found": urls,
        "url_analyses": url_results,
    }

# Chrome extension compatibility endpoint
@app.post("/predict")
def predict_extension(req: EmailRequest):
    text = (req.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    # Try email model first
    if ModelRegistry.email_model is not None and ModelRegistry.email_vectorizer is not None:
        try:
            res = analyze_email_with_model(text)
            label = 1 if res["prediction"] == "phishing" else 0
            phishing_prob = float(res["probabilities"].get("phishing", 0.0))
            return {"label": label, "phishing_probability": phishing_prob}
        except Exception as e:
            print(f"[Dual-AI] Email model error: {e}")

    # Fallback to URL detection if email model not available
    url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    urls = re.findall(url_pattern, text)
    
    if ModelRegistry.url_model is not None and urls:
        try:
            probs = []
            for u in urls:
                res = analyze_url_with_model(u)
                probs.append(float(res["probabilities"]["phishing"]))
            phishing_prob = max(probs) if probs else 0.0
            label = 1 if phishing_prob >= 0.5 else 0
            return {"label": label, "phishing_probability": phishing_prob}
        except Exception as e:
            print(f"[Dual-AI] URL model error: {e}")

    # If neither model works, return safe with 0 probability
    return {"label": 0, "phishing_probability": 0.0}
