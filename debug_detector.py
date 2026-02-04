from app.models.detector import VoiceDetector
import os

path = "/Users/rishitguha/Downloads/luvvoice.com-20260203-FSzSWI.mp3"

print("Initializing Detector in isolation...")
detector = VoiceDetector()

print(f"Running detection on {path}...")
try:
    with open(path, "rb") as f:
        audio_bytes = f.read()
        
    result = detector.detect_fraud(audio_bytes)
    
    print("\n--- RESULTS ---")
    print(f"Classification: {result['classification']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Physics: Jitter={result.get('pitch_jitter')}Hz, Std={result.get('pitch_std')}Hz")
    print(f"Pitch Score: {result.get('pitch_human_score')}")
    print(f"Debug Probs: {result.get('debug_probs')}")
    print(f"Heuristic Score: {result.get('heuristic_score')}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
