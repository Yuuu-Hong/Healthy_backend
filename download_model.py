# filepath: backend/download_model.py
import os
import gdown

MODEL_ID = "17CrR9ZCQ6FOg2F4P1x5qaryUzSZAkb2S"
MODEL_PATH = os.path.join("models", "best.pt")
os.makedirs("models", exist_ok=True)

if not os.path.exists(MODEL_PATH):
    print("Downloading YOLO model from Google Drive...")
    url = f"https://drive.google.com/uc?id={MODEL_ID}"
    gdown.download(url, MODEL_PATH, quiet=False)
    print("Download complete.")
else:
    print("Model already exists.")