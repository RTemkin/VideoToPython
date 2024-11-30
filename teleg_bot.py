from telebot import types
import telebot

token='7593173531:AAEELEnidKCwI7bHV5pnRiOfFNoZPkqQ86w'
bot=telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_dice(message.chat.id)
    bot.send_message(message.chat.id,'Hello World!')

@bot.message_handler(commands=["info"])
def info_func(message):
    keyboard = types.InlineKeyboardMarkup()
    url_batton = types.InlineKeyboardButton(text="Перейти на Yandex", url="https://ya.ru/")
    keyboard.add(url_batton)
    bot.send_message(message.chat.id,"Перейди в поисковик, нажав на кнопку", reply_markup=keyboard)

@bot.message_handler(content_types=['text'])
def repeat_all_messages(message):
    bot.send_message(message.chat.id,message.text)

if __name__=='__main__':
    bot.infinity_polling()

