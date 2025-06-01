import telebot
from telebot import types
import os
import random

TOKEN = '7618568984:AAGbduDv2pnUGHaT2uxigKYa4gydkkmN1-k'
bot = telebot.TeleBot(TOKEN)

MEMES_FOLDER = 'pictures'

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton('➕')
    markup.add(btn)
    
    bot.reply_to(
        message,
        f'Привет, {message.from_user.first_name}! Нажми плюсик, и я пришлю тебе мем.',
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == '➕')
def send_meme(message):
    if not os.path.exists(MEMES_FOLDER):
        bot.send_message(message.chat.id, 'Папка с мемами не найдена!')
        return
    
    memes = [f for f in os.listdir(MEMES_FOLDER) if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    if not memes:
        bot.send_message(message.chat.id, 'В папке нет мемов!')
        return
    
    random_meme = random.choice(memes)
    meme_path = os.path.join(MEMES_FOLDER, random_meme)
    
    with open(meme_path, 'rb') as photo:
        bot.send_photo(message.chat.id, photo)

if __name__ == '__main__':
    print('Бот запущен!')
    bot.infinity_polling()