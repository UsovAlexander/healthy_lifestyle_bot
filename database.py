import aiosqlite
import json
from datetime import datetime

DB_PATH = "healthy_lifestyle_bot.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                weight REAL,
                height REAL,
                age INTEGER,
                activity_minutes INTEGER,
                city TEXT,
                gender TEXT DEFAULT 'male',
                calorie_goal REAL,
                water_goal REAL,
                logged_water REAL DEFAULT 0,
                logged_calories REAL DEFAULT 0,
                burned_calories REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS water_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS food_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                food_name TEXT,
                calories REAL,
                grams REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS workout_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                workout_type TEXT,
                duration_minutes INTEGER,
                burned_calories REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = await cursor.fetchone()
        return dict(user) if user else None

async def create_or_update_user(user_data: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        user_id = user_data['user_id']
        
        cursor = await db.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        exists = await cursor.fetchone()
        
        if exists:
            update_fields = []
            values = []
            for key, value in user_data.items():
                if key != 'user_id':
                    update_fields.append(f"{key} = ?")
                    values.append(value)
            values.append(user_id)
            
            query = f"UPDATE users SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?"
            await db.execute(query, values)
        else:
            columns = ', '.join(user_data.keys())
            placeholders = ', '.join(['?'] * len(user_data))
            query = f"INSERT INTO users ({columns}) VALUES ({placeholders})"
            await db.execute(query, list(user_data.values()))
        
        await db.commit()

async def log_water(user_id: int, amount: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO water_logs (user_id, amount) VALUES (?, ?)",
            (user_id, amount)
        )
        
        await db.execute(
            "UPDATE users SET logged_water = logged_water + ? WHERE user_id = ?",
            (amount, user_id)
        )
        
        await db.commit()

async def log_food(user_id: int, food_name: str, calories: float, grams: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO food_logs (user_id, food_name, calories, grams) VALUES (?, ?, ?, ?)",
            (user_id, food_name, calories, grams)
        )
        
        await db.execute(
            "UPDATE users SET logged_calories = logged_calories + ? WHERE user_id = ?",
            (calories, user_id)
        )
        
        await db.commit()

async def log_workout(user_id: int, workout_type: str, duration: int, burned_calories: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO workout_logs (user_id, workout_type, duration_minutes, burned_calories) VALUES (?, ?, ?, ?)",
            (user_id, workout_type, duration, burned_calories)
        )
        
        await db.execute(
            "UPDATE users SET burned_calories = burned_calories + ? WHERE user_id = ?",
            (burned_calories, user_id)
        )
        
        await db.commit()

async def reset_daily_logs():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET logged_water = 0, logged_calories = 0, burned_calories = 0")
        await db.commit()