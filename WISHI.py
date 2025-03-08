import telebot
from telebot import types
from pymongo import MongoClient

API_TOKEN = '6803057775:AAHGhUOaHuZJGBXFQbhuBZBBhEPAU9KgNG8'
bot = telebot.TeleBot(API_TOKEN, parse_mode='Markdown')  # Використовуємо Markdown

# Підключення до MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['wishlist_db']  # Назва вашої бази даних
wishlist_collection = db['wishlists']  # Колекція для зберігання вішлістів
users_collection = db['users']  # Колекція для зберігання користувачів

class Wish:
    def __init__(self, item):
        self.item = item

    def __str__(self):
        return self.item

class WishListBot:
    def __init__(self):
        pass

    def add_wish(self, user_id, item):
        wishlist = {
            "user_id": user_id,
            "item": item
        }
        wishlist_collection.insert_one(wishlist)
        return "Бажання додане!"

    def view_wishes(self, user_id):
        wishes = wishlist_collection.find({"user_id": user_id})
        wish_list = [wish['item'] for wish in wishes]
        if not wish_list:
            return "Ваш вішліст порожній."
        formatted_list = [self.format_wish(item) for item in wish_list]
        return "\n".join(formatted_list)

    def format_wish(self, wish):
        if wish.startswith("http"):
            return f"[Посилання]({wish})"
        return wish

    def get_wishes(self, user_id):
        return [wish['item'] for wish in wishlist_collection.find({"user_id": user_id})]

    def delete_wish(self, user_id, item):
        result = wishlist_collection.delete_one({"user_id": user_id, "item": item})
        if result.deleted_count > 0:
            return "Бажання видалено!"
        return "Бажання не знайдене у вашому вішлісті."

    def add_user(self, user):
        user_data = {
            "user_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name
        }
        users_collection.update_one({"user_id": user.id}, {"$set": user_data}, upsert=True)

    def find_user_by_username(self, username):
        return users_collection.find_one({"username": username})

    def find_user_by_id(self, user_id):
        return users_collection.find_one({"user_id": user_id})

    def get_user_id(self, username):
        user = self.find_user_by_username(username)
        if user:
            return user['user_id']
        return None

wish_bot = WishListBot()

user_states = {}

def create_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('/add')
    btn2 = types.KeyboardButton('/view')
    btn3 = types.KeyboardButton('/delete')
    btn4 = types.KeyboardButton('/view_user')
    btn5 = types.KeyboardButton('/my_id')
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    wish_bot.add_user(message.from_user)
    markup = create_menu()
    bot.reply_to(message, "Ласкаво просимо до Wishi! Створи свій вішліст і дізнайся, що бажають твої друзі.", reply_markup=markup)

@bot.message_handler(commands=['add'])
def initiate_add_item(message):
    user_states[message.from_user.id] = 'adding_item'
    bot.reply_to(message, "Будь ласка, введіть бажання, яке хочете додати.")

@bot.message_handler(commands=['delete'])
def initiate_delete_item(message):
    user_id = message.from_user.id
    wishes = wish_bot.get_wishes(user_id)
    
    if not wishes:
        bot.reply_to(message, "У вас поки немає бажань.")
        return
    
    markup = types.InlineKeyboardMarkup()
    for wish in wishes:
        markup.add(types.InlineKeyboardButton(wish, callback_data=f"delete:{wish}"))
    
    bot.reply_to(message, "Виберіть бажання, яке хочете видалити:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete:"))
def handle_delete_callback(call):
    item = call.data.split(":")[1]
    user_id = call.from_user.id
    response = wish_bot.delete_wish(user_id, item)
    bot.answer_callback_query(call.id, response)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=response)

@bot.message_handler(commands=['view_user'])
def initiate_view_user_wishlist(message):
    user_states[message.from_user.id] = 'viewing_user_wishlist'
    bot.reply_to(message, "Будь ласка, введіть нік або ID користувача. Приклад: @username або 123456789")

@bot.message_handler(func=lambda message: message.from_user.id in user_states)
def handle_user_input(message):
    state = user_states.get(message.from_user.id)
    
    if state == 'adding_item':
        item = message.text.strip()
        response = wish_bot.add_wish(message.from_user.id, item)
        bot.reply_to(message, response)
    
    elif state == 'viewing_user_wishlist':
        query = message.text.strip()
        if query.isdigit():
            user = wish_bot.find_user_by_id(int(query))
        else:
            if query.startswith('@'):
                query = query[1:]  # Видаляємо символ '@'
            user = wish_bot.find_user_by_username(query)
        
        if user:
            response = wish_bot.view_wishes(user['user_id'])
        else:
            response = "Користувача не знайдено."
        bot.reply_to(message, response)
    
    user_states.pop(message.from_user.id, None)  # Очистити стан після обробки

@bot.message_handler(commands=['view'])
def view_items(message):
    response = wish_bot.view_wishes(message.from_user.id)
    bot.reply_to(message, response)

rand_var = 10


@bot.message_handler(commands=['my_id'])
def get_my_id(message):
    user_id = message.from_user.id
    user = wish_bot.find_user_by_id(user_id)
    if user:
        response = f"Ваш ID: {user['user_id']}"
    else:
        response = "Вашого користувача не знайдено в базі даних."
    bot.reply_to(message, response)

if __name__ == '__main__':
    bot.polling(none_stop=True)
