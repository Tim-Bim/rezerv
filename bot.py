from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo
from aiogram.filters import Command
import asyncio
import os
TOKEN = os.getenv("8241120054:AAEYyOEq61QiX4EYfVzue7sIKOHbAUHN4Qg")


API_TOKEN = "8241120054:AAEYyOEq61QiX4EYfVzue7sIKOHbAUHN4Qg"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(
                text="Открыть мини-апп",
                web_app=WebAppInfo(url="https://fascinating-stroopwafel-e24651.netlify.app/")
            )]
        ],
        resize_keyboard=True
    )
    await message.answer("Нажми кнопку ниже, чтобы открыть мини-апп:", reply_markup=keyboard)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
