from flask import Blueprint, request, jsonify
import os
import sqlite3
from datetime import datetime
from v8_to_food import FoodDetectionSystem

food_bp = Blueprint('food', __name__)

# 設定專案根目錄（自動偵測，不寫死路徑）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 使用相對路徑取得模型與資料庫
model_path = os.path.join(BASE_DIR, "models", "best.pt")
database_path = os.path.join(BASE_DIR, "database", "food_data.db")
food_system = FoodDetectionSystem(model_path, database_path)

# 取得正確的資料庫絕對路徑
db_path = os.path.join(BASE_DIR, 'database', 'USERS_nutrition.db')

@food_bp.route('/upload', methods=['POST'])
def upload_food():
    photo = request.files.get('photo')
    username = request.form.get('username')
    if not photo or not username:
        return jsonify({'error': '缺少照片或用戶資訊'}), 400

    # 儲存圖片到本地（雲端建議改用雲端儲存服務，如 S3，這裡暫用 uploads 目錄）
    save_dir = os.path.join(BASE_DIR, 'uploads')
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, photo.filename)
    photo.save(save_path)

    # 呼叫 YOLO+資料庫推論
    results = food_system.process_image(save_path, confidence_threshold=0.5)
    detected_foods = results['detected_foods']
    nutrition_info_list = results['nutrition_info']
    total_nutrition = food_system.get_total_nutrition(nutrition_info_list)

    # 儲存辨識結果到 USERS_nutrition.db
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. 查 User_ID
    cursor.execute("SELECT ID FROM users WHERE username=?", (username,))
    user_row = cursor.fetchone()
    if not user_row:
        conn.close()
        return jsonify({'error': '找不到用戶'}), 400
    user_id = user_row[0]

    # 2. 新增一筆 Meals
    meal_time = datetime.now()
    hour = meal_time.hour
    minute = meal_time.minute

    # 判斷餐別
    if (hour == 4 and minute >= 1) or (5 <= hour < 11) or (hour == 11 and minute == 0):
        meal_type = "breakfast"
    elif (hour == 11 and minute >= 1) or (12 <= hour < 15) or (hour == 15 and minute == 0):
        meal_type = "lunch"
    elif (hour == 15 and minute >= 1) or (16 <= hour < 22) or (hour == 22 and minute == 0):
        meal_type = "dinner"
    else:
        meal_type = "midnight snack"

    cursor.execute("INSERT INTO meals (User_ID, Meal_Time, Meal_Type) VALUES (?, ?, ?)", (user_id, meal_time, meal_type))
    meal_id = cursor.lastrowid

    # 3. 寫入 Food Intake Table
    for info in nutrition_info_list:
        if info:
            cursor.execute("""
                INSERT INTO food_intake (
                    Meal_ID, User_ID, Food_Name, [calories], [protein], [fat],
                    [carbohydrate], [sugar], [cholesterol]
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                meal_id,
                user_id,
                info['name'],
                info['calories'],
                info['protein'],
                info['fat'],
                info['carbohydrates'],
                info['sugar'],
                info['cholesterol']
            ))
    conn.commit()
    conn.close()

    return jsonify({
        'detected_foods': detected_foods,
        'nutrition_info': nutrition_info_list,
        'total_nutrition': total_nutrition
    })

@food_bp.route('/summary/<username>', methods=['GET'])
def get_today_summary(username):
    db_path = os.path.join(BASE_DIR, 'database', 'USERS_nutrition.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    user_id = user[0]
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute("""
        SELECT SUM(fi.calories), SUM(fi.protein), SUM(fi.fat), SUM(fi.carbohydrate), SUM(fi.sugar), SUM(fi.cholesterol)
        FROM food_intake fi
        JOIN meals m ON fi.meal_id = m.id
        WHERE m.user_id=? AND DATE(m.meal_time)=?
    """, (user_id, today))
    row = cursor.fetchone()
    conn.close()
    result = {
        'tdee': row[0] or 0,
        'protein': row[1] or 0,
        'fat': row[2] or 0,
        'carb': row[3] or 0,
        'sugar': row[4] or 0,
        'cholesterol': row[5] or 0
    }
    return jsonify(result)

@food_bp.route('/today_foods/<username>', methods=['GET'])
def get_today_foods(username):
    db_path = os.path.join(BASE_DIR, 'database', 'USERS_nutrition.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    user_id = user[0]
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute("""
        SELECT fi.food_name, fi.amount, fi.calories, fi.protein, fi.fat, fi.carbohydrate, fi.sugar, fi.cholesterol, m.meal_time
        FROM food_intake fi
        JOIN meals m ON fi.meal_id = m.id
        WHERE m.user_id=? AND DATE(m.meal_time)=?
        ORDER BY m.meal_time DESC
    """, (user_id, today))
    rows = cursor.fetchall()
    conn.close()
    foods = [
        {
            'food_name': row[0],
            'amount': row[1],
            'calories': row[2],
            'protein': row[3],
            'fat': row[4],
            'carb': row[5],
            'sugar': row[6],
            'cholesterol': row[7],
            'meal_time': row[8]
        }
        for row in rows
    ]
    return jsonify(foods)

@food_bp.route('/history/<username>', methods=['GET'])
def get_history(username):
    db_path = os.path.join(BASE_DIR, 'database', 'USERS_nutrition.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return jsonify([])

    user_id = user[0]
    cursor.execute("""
        SELECT fi.food_name, fi.amount, fi.calories, fi.protein, fi.fat, fi.carbohydrate, fi.sugar, fi.cholesterol, m.meal_time
        FROM food_intake fi
        JOIN meals m ON fi.meal_id = m.id
        WHERE m.user_id=?
        ORDER BY m.meal_time DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    foods = [
        {
            'food_name': row[0],
            'amount': row[1],
            'calories': row[2],
            'protein': row[3],
            'fat': row[4],
            'carb': row[5],
            'sugar': row[6],
            'cholesterol': row[7],
            'meal_time': row[8]
        }
        for row in rows
    ]
    return jsonify(foods)
