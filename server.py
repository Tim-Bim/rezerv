import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
import os

API_TOKEN = "7974895632:AAGB3h8gzFPS0paoowUELBZIaM3X4MekWWs"


bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: Message):
    keyboard = {
        "keyboard": [[{"text": "Открыть мини-апп"}]],
        "resize_keyboard": True
    }
    await message.answer("Нажми кнопку ниже, чтобы открыть мини-апп:", reply_markup=keyboard)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
