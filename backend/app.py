from flask import Flask, request, jsonify, session, send_from_directory
from database import get_user_profile, init_db, get_user_by_username, create_user, get_all_products, create_order, get_all_orders
import hashlib
import os
import json
import sqlite3

app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'images')

# Создаем папку для изображений, если её нет
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

init_db()

# Маршруты для HTML-страниц
@app.route('/')
def index():
    return app.send_static_file('html/index.html')

@app.route('/login.html')
def login_page():
    return app.send_static_file('html/login.html')

@app.route('/register.html')
def register_page():
    return app.send_static_file('html/register.html')

@app.route('/admin.html')
def admin_page():
    return app.send_static_file('html/admin.html')

# Обработка статических файлов
@app.route('/<path:path>')
def serve_static(path):
    # Пробуем найти файл в статических ресурсах
    try:
        return app.send_static_file(path)
    except:
        pass
    
    # Если не нашли, пробуем отдать как HTML файл
    if not path.endswith('.html'):
        return app.send_static_file(f'html/{path}.html')
    return app.send_static_file(f'html/{path}')

# API endpoints
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = get_user_by_username(username)
    if not user:
        return jsonify({'success': False, 'message': 'Пользователь не найден'}), 401
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if user[3] != hashed_password:
        return jsonify({'success': False, 'message': 'Неверный пароль'}), 401
    
    session['user_id'] = user[0]
    session['username'] = user[1]
    session['is_admin'] = (user[1] == 'Safari')
    
    return jsonify({
        'success': True,
        'username': user[1],
        'is_admin': session['is_admin']
    })

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    phone = data.get('phone')
    password = data.get('password')
    
    if not username or not phone or not password:
        return jsonify({'success': False, 'message': 'Заполните все поля'}), 400
    
    if create_user(username, phone, password):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Пользователь уже существует'}), 400

@app.route('/api/logout')
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/products')
def products():
    products = get_all_products()
    return jsonify([{
        'id': p[0],
        'name': p[1],
        'description': p[2],
        'image': f"/images/{p[3]}" if p[3] else "",
        'price': p[4],
        'available': bool(p[5])
    } for p in products])

@app.route('/api/order', methods=['POST'])
def create_new_order():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Необходима авторизация'}), 401
    
    data = request.json
    order_id = create_order(
        session['user_id'],
        data['products'],
        data['total_price'],
        data['address'],
        data['phone']
    )
    
    # Отправка в Telegram (заглушка)
    print(f"Заказ #{order_id} создан")
    
    return jsonify({'success': True, 'order_id': order_id})

@app.route('/api/check-auth')
def check_auth():
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'username': session['username'],
            'is_admin': session.get('is_admin', False)
        })
    return jsonify({'authenticated': False})

# Обновить /api/user-profile
@app.route('/api/user-profile')
def user_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_profile = get_user_profile(session['user_id'])
    if user_profile:
        return jsonify(user_profile)
    
    return jsonify({
        'username': session['username'],
        'phone': 'Не указан',
        'orders': []
    })

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Новые маршруты для админки
@app.route('/check-admin-auth')
def check_admin_auth():
    if 'user_id' not in session:
        return jsonify({'is_admin': False}), 401
    
    return jsonify({
        'is_admin': session.get('is_admin', False),
        'username': session.get('username', '')
    })

@app.route('/admin/products')
def admin_products():
    if not session.get('is_admin', False):
        return jsonify({'error': 'Unauthorized'}), 403
    
    products = get_all_products()
    return jsonify([{
        'id': p[0],
        'name': p[1],
        'description': p[2],
        'image': p[3],
        'price': p[4],
        'available': bool(p[5])
    } for p in products])

@app.route('/admin/orders')
def admin_orders():
    if not session.get('is_admin', False):
        return jsonify({'error': 'Unauthorized'}), 403
    
    orders = get_all_orders()
    return jsonify([{
        'id': o[0],
        'user_id': o[1],
        'products': json.loads(o[2]),
        'total_price': o[3],
        'address': o[4],
        'phone': o[5],
        'status': o[6],
        'created_at': o[7],
        'username': o[8]
    } for o in orders])

if __name__ == '__main__':
    app.run(debug=True, port=5000)