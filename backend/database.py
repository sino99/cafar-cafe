import sqlite3
import hashlib
import json
import os
from datetime import datetime
from flask import json

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Создание таблицы пользователей
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE NOT NULL,
                 phone TEXT NOT NULL,
                 password TEXT NOT NULL,
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Создание таблицы товаров
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 description TEXT,
                 image TEXT,
                 price REAL NOT NULL,
                 available BOOLEAN DEFAULT 1,
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Создание таблицы заказов
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER NOT NULL,
                 products TEXT NOT NULL,
                 total_price REAL NOT NULL,
                 address TEXT NOT NULL,
                 phone TEXT NOT NULL,
                 status TEXT DEFAULT 'Новый',
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                 FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    # Создание администратора по умолчанию
    admin_password = hashlib.sha256("12345678910".encode()).hexdigest()
    try:
        c.execute("INSERT INTO users (username, phone, password) VALUES (?, ?, ?)", 
                 ("Safari", "+992000000000", admin_password))
    except sqlite3.IntegrityError:
        pass
    
    # Добавление тестовых товаров, если таблица пуста
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        sample_products = [
            ("Комбо Бургер 5 в 1", "1 Чикенбургер, 125гр картошка фри, 250гр микс, 1шт соус на выбор, 1 кола или Фанта 0.5", "1.jpg", 52.0, 1),
            ("Комбо 3 в 1", "1 Чикенбургер, 125гр картошка фри, 1 Кола или Фанта 0.5", "2.jpg", 27.0, 1),
            ("Фри с сосиской и соусом", "150гр Картофель фри, 2шт сосиска и 2 вида соуса на выбор", "8.jpg", 15.0, 1),
            ("Баскет ножки 1КГ", "Маленькие куриные ножки в хрустящей панировке. Средней остроты", "9.jpg", 85.0, 1),
            ("ЧикенБургер", "Бургер с куриными стрипсами", "20.jpg", 17.0, 1),
            ("Хот-дог SaFar", "Хот-дог с сочной сосиской и соусом", "28.jpg", 15.0, 1),
            ("Coca Cola 0.5", "Газированный напиток", "napitok_coca-cola_0_5_l_p_b_kazahstan.jpg", 6.0, 1)
        ]
        c.executemany("INSERT INTO products (name, description, image, price, available) VALUES (?, ?, ?, ?, ?)", sample_products)
    
    conn.commit()
    conn.close()

def get_user_by_username(username):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def create_user(username, phone, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, phone, password) VALUES (?, ?, ?)", 
                 (username, phone, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_all_products():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    products = c.fetchall()
    conn.close()
    return products

def create_order(user_id, products, total_price, address, phone):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    products_json = json.dumps(products)
    c.execute("INSERT INTO orders (user_id, products, total_price, address, phone) VALUES (?, ?, ?, ?, ?)",
              (user_id, products_json, total_price, address, phone))
    conn.commit()
    order_id = c.lastrowid
    conn.close()
    return order_id

def get_all_orders():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""SELECT orders.*, users.username 
                 FROM orders 
                 JOIN users ON orders.user_id = users.id 
                 ORDER BY orders.created_at DESC""")
    orders = c.fetchall()
    conn.close()
    return orders

def get_product_by_id(product_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = c.fetchone()
    conn.close()
    return product

def save_product(product_id, name, description, price, available, image=None):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    try:
        if product_id:
            # Обновление существующего товара
            if image:
                c.execute("""UPDATE products 
                             SET name = ?, description = ?, price = ?, available = ?, image = ?
                             WHERE id = ?""",
                          (name, description, price, available, image, product_id))
            else:
                c.execute("""UPDATE products 
                             SET name = ?, description = ?, price = ?, available = ?
                             WHERE id = ?""",
                          (name, description, price, available, product_id))
        else:
            # Создание нового товара
            if image:
                c.execute("""INSERT INTO products (name, description, price, available, image)
                             VALUES (?, ?, ?, ?, ?)""",
                          (name, description, price, available, image))
            else:
                c.execute("""INSERT INTO products (name, description, price, available)
                             VALUES (?, ?, ?, ?)""",
                          (name, description, price, available))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Ошибка сохранения товара: {e}")
        return False
    finally:
        conn.close()

def delete_product(product_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    try:
        # Сначала получим информацию о товаре для удаления изображения
        c.execute("SELECT image FROM products WHERE id = ?", (product_id,))
        image_file = c.fetchone()[0]
        
        # Удаляем товар из БД
        c.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        
        # Удаляем изображение, если оно есть
        if image_file:
            try:
                image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'images', image_file)
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                print(f"Ошибка удаления изображения: {e}")
        
        return True
    except Exception as e:
        print(f"Ошибка удаления товара: {e}")
        return False
    finally:
        conn.close()

# Дополнительные функции для админ-панели
def get_order_by_id(order_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""SELECT orders.*, users.username 
                 FROM orders 
                 JOIN users ON orders.user_id = users.id 
                 WHERE orders.id = ?""", (order_id,))
    order = c.fetchone()
    conn.close()
    
    if order:
        return {
            'id': order[0],
            'user_id': order[1],
            'products': json.loads(order[2]),
            'total_price': order[3],
            'address': order[4],
            'phone': order[5],
            'status': order[6],
            'created_at': order[7],
            'username': order[8]
        }
    return None

# Добавить в database.py
def get_user_orders(user_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""
        SELECT id, created_at, total_price, status 
        FROM orders 
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,))
    orders = c.fetchall()
    conn.close()
    return [{
        'id': o[0],
        'date': o[1],
        'total_price': o[2],
        'status': o[3]
    } for o in orders]

def get_user_profile(user_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT username, phone FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    
    if user:
        return {
            'username': user[0],
            'phone': user[1],
            'orders': get_user_orders(user_id)
        }
    return None

def update_order_status(order_id, status):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    try:
        c.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Ошибка обновления статуса заказа: {e}")
        return False
    finally:
        conn.close()