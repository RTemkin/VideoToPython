import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InputFile, FSInputFile
from aiogram.filters import Command

# VideoToPython_bot Replace with your bot token and group ID
API_TOKEN = '7535382168:AAHLnaloofQO4xGpSoiXqAdOYL3-3Ip9COM'  # Замените на токен вашего бота
CHAT_ID = '-1002496545090'  # Замените на ID вашей группы (отрицательный для групп)
IMAGE_PATH = 'D:/VideoToPython/аватары для бота/42c964feae1311ef81cf929d34e956e8.png'  

bot = Bot(token=API_TOKEN)
dp = Dispatcher() 

@dp.message(Command('sendphoto'))
async def send_photo_command(message: types.Message): #Use types.Message for clarity
    try:
        #Use InputFile to wrap the file object
        photo = FSInputFile(IMAGE_PATH)  
        await bot.send_photo(chat_id=CHAT_ID, photo=photo, caption='Here is your photo!')
        await message.reply("Photo sent successfully!")
    except FileNotFoundError:
        await message.reply(f"Error: Image file not found. Please check the path: {IMAGE_PATH}")
    except Exception as e:
        await message.reply(f"An error occurred: {type(e).__name__} - {e}")


async def main():
    print('Бот работает...')
    await dp.start_polling(bot)

if __name__ == '__main__':  # Исправлено на '__name__ == "__main__"'
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот остановлен')

