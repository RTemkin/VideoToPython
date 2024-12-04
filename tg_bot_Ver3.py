import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import nest_asyncio

nest_asyncio.apply()  # Применяем nest_asyncio

# VideoToPython_bot
bot_token = '7535382168:AAHLnaloofQO4xGpSoiXqAdOYL3-3Ip9COM'  # Замените на свой токен бота
chat_id = '-1002496545090'

# Путь к файлу с изображением. Замените на ваш путь.
image_path = 'D:/VideoToPython/аватары для бота/68091f32ae1311ef88fafeb312a664ad.png'  # Например: 'images/my_photo.jpg'


async def send_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        with open(image_path, 'rb') as photo:
            await context.bot.send_photo(chat_id=chat_id, photo=photo)
        print(f"Изображение отправлено в Telegram: {image_path}")
    except Exception as e:
        print(f"Ошибка отправки изображения в Telegram: {e}")


async def main():
    application = ApplicationBuilder().token(bot_token).build()

    # Добавляем обработчик команды /sendphoto
    application.add_handler(CommandHandler("sendphoto", send_photo))

    # Запускаем бота
    await application.run_polling()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())  # Если вы все еще получаете ошибки, попробуйте использовать этот участок кода
