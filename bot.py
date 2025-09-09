import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo
from aiogram.filters import Command
import os

API_TOKEN = os.getenv("API_TOKEN")  # добавь в Render
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot=bot)

@dp.message(Command("start"))
async def start_command(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(
                text="Открыть мини-апп",
                web_app=WebAppInfo(url="https://rezerv-jsnp.onrender.com/?v=2")  # сброс кеша
            )]
        ],
        resize_keyboard=True
    )
    await message.answer("Нажми кнопку ниже, чтобы открыть мини-апп:", reply_markup=keyboard)

async def main():
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
