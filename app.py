import os
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