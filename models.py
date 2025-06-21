from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(255), nullable=False)  # 新增這一行
    created_at = db.Column(db.DateTime)
    def __repr__(self):
        return f'<User {self.username}>'

class Meal(db.Model):
    __tablename__ = 'meals'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    meal_time = db.Column(db.DateTime)
    meal_type = db.Column(db.String(50))

class FoodIntake(db.Model):
    __tablename__ = 'food_intake'
    id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey('meals.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    food_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float)
    calories = db.Column(db.Float)
    protein = db.Column(db.Float)
    fat = db.Column(db.Float)
    carbohydrate = db.Column(db.Float)
    sugar = db.Column(db.Float)
    cholesterol = db.Column(db.Float)