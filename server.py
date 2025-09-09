import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# ---------------------------
# Токен Telegram-бота
# ---------------------------
API_TOKEN = "7974895632:AAGB3h8gzFPS0paoowUELBZIaM3X4MekWWs"

# ---------------------------
# Создаем бота и диспетчер
# ---------------------------
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ---------------------------
# Хэндлер на /start
# ---------------------------
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    # Кнопка с Web App
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(
                text="Открыть мини-апп",
                web_app=WebAppInfo(url="https://rezerv-jsnp.onrender.com/")
            )]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "Нажми кнопку ниже, чтобы открыть мини-апп:",
        reply_markup=keyboard
    )

# ---------------------------
# Запуск бота
# ---------------------------
async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
