import os

# --- 自動下載模型 ---
def download_model_if_needed():
    print("=== [DEBUG] 進入 download_model_if_needed ===")
    import gdown
    MODEL_ID = "17CrR9ZCQ6FOg2F4P1x5qaryUzSZAkb2S"
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_DIR = os.path.join(BASE_DIR, "models")
    MODEL_PATH = os.path.join(MODEL_DIR, "best.pt")
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"MODEL_DIR: {MODEL_DIR}")
    print(f"MODEL_PATH: {MODEL_PATH}")
    os.makedirs(MODEL_DIR, exist_ok=True)
    if not os.path.exists(MODEL_PATH):
        print("Downloading YOLO model from Google Drive...")
        url = f"https://drive.google.com/uc?id={MODEL_ID}"
        try:
            gdown.download(url, MODEL_PATH, quiet=False)
            print("Download complete.")
        except Exception as e:
            print(f"Download failed: {e}")
    else:
        print("Model already exists.")

download_model_if_needed()

from flask import Flask
from flask_cors import CORS
from models import db
from routes.auth import auth_bp
from routes.users import users_bp
from routes.food import food_bp
from routes.profile import profile_bp

app = Flask(__name__)

# 用絕對路徑指定資料庫
db_path = os.path.join(os.path.dirname(__file__), 'database', 'USERS_nutrition.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
CORS(app)

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(food_bp, url_prefix='/food')
app.register_blueprint(profile_bp, url_prefix='/api')



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)