import requests
import json
import time

# List of samples (approximate ground truth)
# Note: These are public URLs. If any 404, the script handles it.
SAMPLES = [
    # --- HUMAN / REAL ---
    {
        "url": "https://upload.wikimedia.org/wikipedia/commons/4/40/Turing_test.ogg", 
        "label": "Human", 
        "lang": "en",
        "description": "English Human Speech (Wikipedia)"
    },
    {
        "url": "https://upload.wikimedia.org/wikipedia/commons/8/83/Kalam_speaking.ogg",
        "label": "Human",
        "lang": "en/hi", # APJ Abdul Kalam
        "description": "Indian Accent Human Speech"
    },
    {
         "url": "https://librivox.org/uploads/tests/test_mp3_128kbps.mp3",
         "label": "Human",
         "lang": "en",
         "description": "Librivox Audiobook Record"
    },

    # --- AI / FAKE ---
    # Common TTS samples
    {
        "url": "https://www2.cs.uic.edu/~mT/dataset/wav/s1.wav",
        "label": "AI",
        "lang": "en",
        "description": "Old TTS Synthesis"
    },
    # Using a known deepfake/TTS example if available publicly and stable
    {
        "url": "https://github.com/microsoft/Azure-Speech-Service-Wrapper/raw/master/samples/en-US-JessaNeural.mp3",
        # NOTE: This is Microsoft Neural TTS. 
        # Deepfake detectors "should" catch this, but high-quality TTS is hard.
        "label": "AI",
        "lang": "en",
        "description": "Microsoft Neural TTS"
    }
]

API_URL = "http://localhost:8000/detect"
HEADERS = {"x-api-key": "demo_key_123"}

def run_benchmark():
    print(f"Running Benchmark on {len(SAMPLES)} samples...")
    print("-" * 60)
    print(f"{'Description':<30} | {'True Label':<10} | {'Pred Label':<10} | {'Conf':<6} | {'Status'}")
    print("-" * 60)

    correct = 0
    total = 0

    for sample in SAMPLES:
        try:
            payload = {"audio_url": sample["url"]}
            response = requests.post(API_URL, json=payload, headers=HEADERS, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                pred_label = result.get("classification")
                conf = result.get("confidence")
                
                # Check correctness
                is_correct = (pred_label == sample["label"])
                status = "✅ PASS" if is_correct else "❌ FAIL"
                if is_correct:
                    correct += 1
                
                print(f"{sample['description']:<30} | {sample['label']:<10} | {pred_label:<10} | {conf:<6} | {status}")
                total += 1
            else:
                error_msg = response.text[:50] # truncated
                print(f"{sample['description']:<30} | {sample['label']:<10} | {'ERROR':<10} | {'N/A':<6} | {response.status_code} - {error_msg}")
                
        except Exception as e:
            print(f"{sample['description']:<30} | {sample['label']:<10} | {'ERROR':<10} | {'N/A':<6} | {str(e)[:20]}")

    print("-" * 60)
    if total > 0:
        print(f"Accuracy: {correct}/{total} ({correct/total*100:.1f}%)")
    else:
        print("No samples processed successfully.")

if __name__ == "__main__":
    # Ensure server is running? 
    # We assume server is running on localhost:8000
    try:
        run_benchmark()
    except KeyboardInterrupt:
        print("\nBenchmark stopped.")
