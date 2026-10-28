import asyncio
import os
import logging
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Помилка: BOT_TOKEN не знайдено")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def get_main_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📚 Каталог книг", callback_data="catalog")],
            [InlineKeyboardButton(text="ℹ️ Про автора / Бот", callback_data="about")]
        ]
    )

def get_book_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Купити (Тест)", callback_data="buy_book")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="catalog")]
        ]
    )

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Вітаємо, {message.from_user.first_name}! 👋\n\n"
        "Ласкаво просимо до нашого магазину електронних книг.\n"
        "Оберіть потрібний розділ у меню нижче:",
        reply_markup=get_main_keyboard()
    )

@dp.callback_query(F.data == "catalog")
async def show_catalog(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📖 **Наші електронні книги:**\n\n"
        "1. **«Успішний старт у Telegram»**\n"
        "   Покроковий гайд по запуску.\n"
        "   💰 Ціна: 150 грн\n",
        parse_mode="Markdown",
        reply_markup=get_book_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "about")
async def show_about(callback: types.CallbackQuery):
    back_kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]]
    )
    await callback.message.edit_text(
        "ℹ️ **Про наш сервіс**\n\n"
        "Тут ви можете придбати авторські електронні книги.",
        parse_mode="Markdown",
        reply_markup=back_kb
    )
    await callback.answer()

@dp.callback_query(F.data == "back_main")
async def back_main(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Вітаємо! Оберіть розділ:",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "buy_book")
async def process_buy(callback: types.CallbackQuery):
    await callback.message.answer(
        "💳 **Реквізити для оплати:**\n\n"
        "Номер картки А-Банк: `4323 3450 4950 5424`\n"
        "Отримувач: Богдан П.\n"
        "Сума: 150 грн (приклад)\n\n"
        "📌 Після оплати надішліть скріншот або квитанцію сюди в чат, "
        "і ми надішлемо вам книгу вручну!",
        parse_mode="Markdown"
    )
    await callback.answer()



async def main():
    print("Бот запущено!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
