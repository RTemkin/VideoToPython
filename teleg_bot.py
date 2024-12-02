from telebot import types
import telebot

token='7593173531:AAEELEnidKCwI7bHV5pnRiOfFNoZPkqQ86w'
bot=telebot.TeleBot(token)
my_chat_id = 517481295

@bot.message_handler(commands=['start'])

def start_message(message):
    bot.send_dice(message.chat.id)
    #bot.send_message(message.chat.id, str(message.chat.id))
    #bot.send_message(message.chat.id,'Hello World!')
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True )
    batton1 = types.KeyboardButton(text="Услуги")
    batton2 = types.KeyboardButton(text="О компании")
    batton3 = types.KeyboardButton(text="Оставить заявку")
    keyboard.add(batton1,batton2,batton3)
    bot.send_message(message.chat.id,"Приветствие компании", reply_markup=keyboard)

#@bot.message_handler(commands=["info"])
def info_func(message):
    keyboard = types.InlineKeyboardMarkup()
    url_batton = types.InlineKeyboardButton(text="Перейти на Yandex", url="https://ya.ru/")
    keyboard.add(url_batton)
    bot.send_message(message.chat.id,"Перейди в поисковик, нажав на кнопку", reply_markup=keyboard)

def send_request(message):
    mes=f'Новая заявка:{message.text}'
    bot.send_message(my_chat_id,mes)
    bot.send_message(message.chat.id,'Заявка в обработке')

def send_servive(message):
    bot.send_message(message.chat.id, '1. Составить отчет')
    bot.send_message(message.chat.id, '2. Оплатить налоги')
    bot.send_message(message.chat.id, '3. Рассчитать бюджет')

# @bot.message_handler(commands=["menu"])
# def menu(message):
#     keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True )
#     batton_phone = types.KeyboardButton(text="Отправить номер тел", request_contact=True)
#     batton_geo = types.KeyboardButton(text="Оnправить местоположение", request_location=True)
#     keyboard.add(batton_phone,batton_geo)
#     bot.send_message(message.chat.id,"отправь номер или местоположение", reply_markup=keyboard)

@bot.message_handler(content_types=['text'])
def repeat_all_messages(message):
    if message.text.lower() =='о компании':
        info_func(message)
    #bot.send_message(message.chat.id,message.text)
    if message.text.lower() =='оcтавить заявку':
        bot.send_message(message.chat.id,'Рады сотрудничать, оставте конакты')
        bot.register_next_step_handler(message,send_request)
    if message.text.lower() =='услуги':
        send_servive(message)

if __name__=='__main__':
    bot.infinity_polling()

