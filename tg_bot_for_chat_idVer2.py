import telebot

# VideoToPython_bot
BOT_TOKEN = '7535382168:AAHLnaloofQO4xGpSoiXqAdOYL3-3Ip9COM'  # Замените на свой токен бота
bot = telebot.TeleBot(BOT_TOKEN)

GROUP_CHAT_ID = '517481295'

# Путь к файлу с изображением. Замените на ваш путь.
PHOTO_PATH = 'D:/VideoToPython/аватары для бота/42c964feae1311ef81cf929d34e956e8.png'  # Например: 'images/my_photo.jpg'


@bot.message_handler(commands=['sendphoto'])
def send_photo(message):
    try:
        with open(PHOTO_PATH, 'rb') as photo:
            bot.send_photo(GROUP_CHAT_ID, photo, caption="Это фото из моего Python приложения!")
            bot.reply_to(message, "Фото отправлено!")
    except FileNotFoundError:
        bot.reply_to(message, "Фото не найдено!")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")


bot.polling()

