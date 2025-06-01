import telebot
from telebot import types
import os
import random

TOKEN = '7618568984:AAGbduDv2pnUGHaT2uxigKYa4gydkkmN1-k'
bot = telebot.TeleBot(TOKEN)

MEMES_FOLDER = 'pictures'
TEXTS_FILE = 'fun.txt'
RESPONSES = [
    "Какая смешная шутка!",
    "Ахаххахаххахахаххахахха!",
    "Хорошая шутка, посмеялся!",
    "😂😂😂",
    "Лол, это было смешно!",
    "Я запомню эту шутку!"
]

user_last_message = {}

def create_main_keyboard():
    """Создает основную клавиатуру с выбором действий"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton('➕ Мем')
    btn2 = types.KeyboardButton('📄 Анекдот')
    markup.add(btn1, btn2)
    return markup

def create_feedback_keyboard():
    """Создает клавиатуру для оценки контента"""
    markup = types.InlineKeyboardMarkup()
    like = types.InlineKeyboardButton(text='👍 Лайк', callback_data='like')
    dislike = types.InlineKeyboardButton(text='👎 Дизлайк', callback_data='dislike')
    markup.add(like, dislike)
    return markup

def offer_services(chat_id):
    """Предлагает пользователю выбрать следующее действие"""
    bot.send_message(
        chat_id,
        "Что хочешь сделать дальше?",
        reply_markup=create_main_keyboard()
    )

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        f'Привет, {message.from_user.first_name}!\n'
        '• Нажми "➕ Мем", и я пришлю тебе мем.\n'
        '• Нажми "📄 Анекдот", чтобы получить случайное сообщение.\n'
        '• Или просто напиши мне что-нибудь смешное!',
        reply_markup=create_main_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == '➕ Мем')
def send_meme(message):
    if not os.path.exists(MEMES_FOLDER):
        bot.send_message(message.chat.id, 'Папка с мемами не найдена!')
        offer_services(message.chat.id)
        return
    
    memes = [f for f in os.listdir(MEMES_FOLDER) if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    if not memes:
        bot.send_message(message.chat.id, 'В папке нет мемов!')
        offer_services(message.chat.id)
        return
    
    random_meme = random.choice(memes)
    meme_path = os.path.join(MEMES_FOLDER, random_meme)
    
    with open(meme_path, 'rb') as photo:
        msg = bot.send_photo(
            message.chat.id, 
            photo, 
            reply_markup=create_feedback_keyboard()
        )
        user_last_message[message.chat.id] = {
            'type': 'meme', 
            'file': random_meme, 
            'message_id': msg.message_id
        }

@bot.message_handler(func=lambda message: message.text == '📄 Анекдот')
def send_random_text(message):
    try:
        with open(TEXTS_FILE, 'r', encoding='utf-8') as f:
            texts = [line.strip() for line in f.readlines() if line.strip()]
        
        if not texts:
            bot.reply_to(message, "Файл с текстами пуст!")
            offer_services(message.chat.id)
            return
        
        random_text = random.choice(texts)
        msg = bot.reply_to(
            message, 
            random_text, 
            reply_markup=create_feedback_keyboard()
        )
        user_last_message[message.chat.id] = {
            'type': 'text', 
            'content': random_text, 
            'message_id': msg.message_id
        }
    except Exception as e:
        bot.reply_to(message, f"Ошибка при чтении файла: {e}")
        offer_services(message.chat.id)

@bot.callback_query_handler(func=lambda call: True)
def handle_feedback(call):
    chat_id = call.message.chat.id
    
    if call.data == 'like':
        bot.send_message(chat_id, "Я рада что тебе понравилось! 😊")
    elif call.data == 'dislike':
        bot.send_message(chat_id, "Грустно что тебе не понравилось. Попробуй еще посмотреть. 😔")
    
    try:
        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=None
        )
    except:
        pass
    
    offer_services(chat_id)

@bot.message_handler(func=lambda message: True)
def echo_message(message):
    if message.text.startswith('/') or message.text in ['➕ Мем', '📄 Анекдот']:
        return
    
    random_response = random.choice(RESPONSES)
    bot.reply_to(message, random_response)
    offer_services(message.chat.id)

if __name__ == '__main__':
    print('Бот запущен!')
    bot.infinity_polling()