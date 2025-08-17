import requests
import os

def send_telegram_notification(order_details):
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID', 'YOUR_CHAT_ID')
    
    message = f"Новый заказ №{order_details['id']}\n"
    message += f"Клиент: {order_details['username']}\n"
    message += f"Телефон: {order_details['phone']}\n"
    message += f"Адрес: {order_details['address']}\n"
    message += f"Сумма: {order_details['total_price']} TJS\n\n"
    message += "Состав заказа:\n"
    
    for product in order_details['products']:
        message += f"- {product['name']} x {product['quantity']} = {product['price'] * product['quantity']} TJS\n"
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    
    response = requests.post(url, data=payload)
    return response.json()