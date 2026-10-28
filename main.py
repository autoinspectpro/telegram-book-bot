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

# Твой реальный Telegram ID
ADMIN_ID = 8718115810

# Название файла книги, который должен лежать в репозитории GitHub
BOOK_FILENAME = "kniga_telegram_bots_i_sayty_s_nulya.docx"

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
        "   💰 Ціна: 175 грн\n",
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
        "Сума: 175 грн (приклад)\n\n"
        "📌 Після оплати надішліть скріншот або квитанцію сюди в чат, "
        "і після перевірки ви отримаєте книгу!",
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.message()
async def forward_to_admin(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        return
    
    await message.answer("⏳ Дякуємо! Ваша квитанція отримана. Адміністратор перевіряє її, і незабаром надішле книгу.")
    
    # Текст с информацией о клиенте
    user_info = (
        f"📥 **Нова квитанція від покупця!**\n"
        f"👤 Ім'я: {message.from_user.full_name}\n"
        f"🔗 Юзернейм: @{message.from_user.username or 'немає'}\n"
        f"🆔 ID: {message.from_user.id}"
    )
    
    # Кнопка подтверждения с зашитым ID покупателя
    confirm_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Підтвердити і надіслати книгу", callback_data=f"send_book_{message.from_user.id}")]
        ]
    )
    
    # Отправляем админу текст с инфой и кнопкой
    await bot.send_message(chat_id=ADMIN_ID, text=user_info, parse_mode="Markdown")
    
    # Пересылаем саму квитанцию (скриншот/фото/документ)
    await message.forward(chat_id=ADMIN_ID)
    
    # Отправляем админу отдельное сообщение с кнопкой подтверждения
    await bot.send_message(
        chat_id=ADMIN_ID, 
        text=f"Натисніть кнопку нижче, щоб надіслати книгу користувачу (ID: {message.from_user.id}):", 
        reply_markup=confirm_keyboard
    )

# Обработка нажатия на кнопку подтверждения админом
@dp.callback_query(F.data.startswith("send_book_"))
async def confirm_and_send_book(callback: types.CallbackQuery):
    # Достаем ID покупателя из callback_data
    buyer_id = int(callback.data.split("_")[2])
    
    try:
        # Проверяем, существует ли файл книги
        if not os.path.exists(BOOK_FILENAME):
            await callback.answer("❌ Помилка: файл книги не знайдено на сервері!", show_alert=True)
            return

        # Отправляем файл покупателю
        book_file = FSInputFile(BOOK_FILENAME)
        await bot.send_document(
            chat_id=buyer_id,
            document=book_file,
            caption="🎉 **Оплату підтверджено!** Ось ваша електронна книга. Дякуємо за покупку! 🚀",
            parse_mode="Markdown"
        )
        
        # Уведомляем админа об успехе
        await callback.message.edit_text(f"✅ Книгу успішно надіслано покупцю (ID: {buyer_id})! Виконано.")
        await callback.answer("Книгу надіслано!")
        
    except Exception as e:
        await callback.answer(f"❌ Помилка при відправці: {e}", show_alert=True)

async def main():
    print("Бот запущено!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
