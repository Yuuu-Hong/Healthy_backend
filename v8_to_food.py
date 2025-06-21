import cv2
import sqlite3
import numpy as np
from ultralytics import YOLO
import os

class FoodDetectionSystem:
    def __init__(self, model_path, database_path):
        self.model_path = model_path
        self.database_path = database_path
        self.model = None
        self.load_model()
        self.check_database_structure()

    def load_model(self):
        try:
            self.model = YOLO(self.model_path)
            print(f"✅ 模型載入成功: {self.model_path}")
        except Exception as e:
            print(f"❌ 模型載入失敗: {e}")
            raise

    def check_database_structure(self):
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"📊 資料庫中的表格: {[table[0] for table in tables]}")
            try:
                cursor.execute("PRAGMA table_info(Food);")
                columns = cursor.fetchall()
                print(f"📋 Food表格欄位: {[col[1] for col in columns]}")
            except:
                print("⚠️ 請確認資料庫中有正確的食物營養表格")
            conn.close()
        except Exception as e:
            print(f"❌ 資料庫連接失敗: {e}")
            raise

    def detect_food(self, image_path, confidence_threshold=0.5):
        try:
            results = self.model(image_path)
            detected_foods = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        confidence = float(box.conf[0])
                        if confidence >= confidence_threshold:
                            class_id = int(box.cls[0])
                            class_name = self.model.names[class_id]
                            x1, y1, x2, y2 = box.xyxy[0].tolist()
                            detected_foods.append({
                                'class_name': class_name,
                                'confidence': confidence,
                                'bbox': [x1, y1, x2, y2],
                                'class_id': class_id
                            })
            return detected_foods
        except Exception as e:
            print(f"❌ 食物辨識失敗: {e}")
            return []

    def get_nutrition_info(self, food_name):
        """
        從資料庫獲取食物營養資訊
        """
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            query = """
            SELECT [food_name], [calories], [protein], [fat], [carbohydrates], [sugars], [cholesterol]
            FROM Food
            WHERE LOWER([food_name]) LIKE LOWER(?)
            """
            cursor.execute(query, (f'%{food_name}%',))
            result = cursor.fetchone()
            conn.close()
            if result:
                return {
                    'name': result[0],
                    'calories': result[1],
                    'protein': result[2],
                    'fat': result[3],
                    'carbohydrates': result[4],
                    'sugar': result[5],
                    'cholesterol': result[6]
                }
            else:
                return None
        except Exception as e:
            print(f"❌ 營養資訊查詢失敗: {e}")
            return None

    def process_image(self, image_path, confidence_threshold=0.5):
        print(f"🔍 正在處理圖片: {image_path}")
        detected_foods = self.detect_food(image_path, confidence_threshold)
        if not detected_foods:
            print("❌ 未辨識到任何食物")
            return {'detected_foods': [], 'nutrition_info': []}
        print(f"✅ 辨識到 {len(detected_foods)} 種食物")
        nutrition_info_list = []
        for food in detected_foods:
            print(f"📊 查詢 {food['class_name']} 的營養資訊...")
            nutrition = self.get_nutrition_info(food['class_name'])
            nutrition_info_list.append(nutrition)
            if nutrition:
                print(f"✅ 找到 {nutrition['name']} 的營養資訊")
            else:
                print(f"⚠️ 未找到 {food['class_name']} 的營養資訊")
        return {
            'detected_foods': detected_foods,
            'nutrition_info': nutrition_info_list
        }

    def get_total_nutrition(self, nutrition_info_list):
        total_nutrition = {
            'total_calories': 0,
            'total_protein': 0,
            'total_fat': 0,
            'total_carbs': 0,
            'total_sugar': 0,
            'total_cholesterol': 0
        }
        for nutrition in nutrition_info_list:
            if nutrition:
                total_nutrition['total_calories'] += nutrition.get('calories', 0) or 0
                total_nutrition['total_protein'] += nutrition.get('protein', 0) or 0
                total_nutrition['total_fat'] += nutrition.get('fat', 0) or 0
                total_nutrition['total_carbs'] += nutrition.get('carbohydrates', 0) or 0
                total_nutrition['total_sugar'] += nutrition.get('sugar', 0) or 0
                total_nutrition['total_cholesterol'] += nutrition.get('cholesterol', 0) or 0
        return total_nutrition

    def close(self):
        # 不再需要 self.conn
        print("📊 資料庫連接已關閉")

# 使用範例
def main():
    model_path = r"D:\Healthy_website\flask-fullstack-app\backend\models\best.pt"
    database_path = r"D:\Healthy_website\flask-fullstack-app\backend\database\food_data.db"
    try:
        food_system = FoodDetectionSystem(model_path, database_path)
        image_path =  r"C:\Users\USER\OneDrive\圖片\food_test\rice2.jpg" # 替換為實際圖片路徑
        if os.path.exists(image_path):
            results = food_system.process_image(image_path, confidence_threshold=0.5)
            detected_foods = results['detected_foods']
            nutrition_info_list = results['nutrition_info']

            # 1. 辨識出來的食物
            print("\n辨識出來的食物：")
            for food in detected_foods:
                print(f"- {food['class_name']} (信心度: {food['confidence']:.2f})")

            # 2. 個別食物的營養資訊
            print("\n個別食物的營養資訊：")
            for nutrition in nutrition_info_list:
                if nutrition:
                    print(f"{nutrition['name']}:")
                    print(f"  卡路里: {nutrition['calories']} kcal")
                    print(f"  蛋白質: {nutrition['protein']} g")
                    print(f"  脂肪: {nutrition['fat']} g")
                    print(f"  碳水化合物: {nutrition['carbohydrates']} g")
                    print(f"  糖: {nutrition['sugar']} g")
                    print(f"  膽固醇: {nutrition['cholesterol']} mg")
                else:
                    print("查無此食物營養資訊")

            # 3. 所有營養資訊的總和
            total_nutrition = food_system.get_total_nutrition(nutrition_info_list)
            print("\n所有營養資訊總和：")
            print(f"總卡路里: {total_nutrition['total_calories']:.1f} kcal")
            print(f"總蛋白質: {total_nutrition['total_protein']:.1f} g")
            print(f"總脂肪: {total_nutrition['total_fat']:.1f} g")
            print(f"總碳水化合物: {total_nutrition['total_carbs']:.1f} g")
            print(f"總糖: {total_nutrition['total_sugar']:.1f} g")
            print(f"總膽固醇: {total_nutrition['total_cholesterol']:.1f} mg")
        else:
            print(f"❌ 圖片檔案不存在: {image_path}")
            print("請提供正確的測試圖片路徑")
        food_system.close()
    except Exception as e:
        print(f"❌ 系統初始化失敗: {e}")

if __name__ == "__main__":
    main()