import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import Command

# ----------------- Вставь сюда токен напрямую -----------------
API_TOKEN = "7974895632:AAGB3h8gzFPS0paoowUELBZIaM3X4MekWWs"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot=bot)

@dp.message(Command("start"))
async def start_command(message: types.Message):
    # Кнопка для мини-апп
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="Открыть мини-апп",
                    web_app=WebAppInfo(url="https://rezerv-jsnp.onrender.com/?v=2")  # версионный параметр для сброса кеша
                )
            ]
        ],
        resize_keyboard=True
    )
    await message.answer("Нажми кнопку ниже, чтобы открыть мини-апп:", reply_markup=keyboard)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
