from flask import Blueprint, request, jsonify
import sqlite3
import os
from datetime import datetime

profile_bp = Blueprint('profile', __name__)
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'USERS_nutrition.db')

@profile_bp.route('/profile/<username>', methods=['GET'])
def get_profile(username):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    user_id = user[0]
    cursor.execute("SELECT age, gender, height, weight, activity FROM user_profile WHERE user_id=?", (user_id,))
    profile = cursor.fetchone()
    conn.close()
    if profile:
        return jsonify({'age': profile[0], 'gender': profile[1], 'height': profile[2], 'weight': profile[3], 'activity': profile[4]})
    else:
        return jsonify({'error': 'Profile not found'}), 404

@profile_bp.route('/profile/<username>', methods=['POST'])
def set_profile(username):
    data = request.json
    age = data.get('age')
    gender = data.get('gender')
    height = data.get('height')
    weight = data.get('weight')
    activity = data.get('activity')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    user_id = user[0]
    cursor.execute("SELECT id FROM user_profile WHERE user_id=?", (user_id,))
    exists = cursor.fetchone()
    if exists:
        cursor.execute("""
            UPDATE user_profile SET age=?, gender=?, height=?, weight=?, activity=?, updated_at=?
            WHERE user_id=?
        """, (age, gender, height, weight, activity, datetime.now(), user_id))
    else:
        cursor.execute("""
            INSERT INTO user_profile (user_id, age, gender, height, weight, activity)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, age, gender, height, weight, activity))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Profile saved'})