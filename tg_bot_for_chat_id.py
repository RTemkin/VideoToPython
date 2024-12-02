import telebot

# VideoToPython_bot
BOT_TOKEN = '7535382168:AAHLnaloofQO4xGpSoiXqAdOYL3-3Ip9COM'  # Замените на свой токен бота
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    print(f"Chat ID: {message.chat.id}")
    bot.reply_to(message, f"Chat ID: {message.chat.id}")

bot.polling()

