# filepath: backend/download_model.py
import os
import sys
import gdown

MODEL_ID = "17CrR9ZCQ6FOg2F4P1x5qaryUzSZAkb2S"

# 取得專案根目錄
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "best.pt")

os.makedirs(MODEL_DIR, exist_ok=True)

if not os.path.exists(MODEL_PATH):
    print("Downloading YOLO model from Google Drive...")
    url = f"https://drive.google.com/uc?id={MODEL_ID}"
    try:
        gdown.download(url, MODEL_PATH, quiet=False)
        print("Download complete.")
    except Exception as e:
        print(f"Download failed: {e}")
        sys.exit(1)
else:
    print("Model already exists.")