import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6992175382

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

support_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💬 Написать в поддержку")]
    ],
    resize_keyboard=True
)

admin_messages = {}


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 Привет!\n\n"
        "Это бот поддержки.\n"
        "Нажми кнопку ниже, чтобы связаться с оператором.",
        reply_markup=support_button
    )


@dp.message(F.text == "💬 Написать в поддержку")
async def support(message: Message):
    await message.answer(
        "✍️ Напиши свой вопрос.\n"
        "Я передам его оператору."
    )


@dp.message(F.from_user.id != ADMIN_ID)
async def user_message(message: Message):
    user = message.from_user

    info = (
        "📩 НОВОЕ ОБРАЩЕНИЕ\n\n"
        f"👤 {user.full_name}\n"
        f"🆔 ID: {user.id}\n"
    )

    if user.username:
        info += f"🔗 @{user.username}\n"

    info += "\n💬 Сообщение ниже:"

    await bot.send_message(ADMIN_ID, info)

    copied = await message.copy_to(ADMIN_ID)

    admin_messages[copied.message_id] = user.id

    await message.answer(
        "✅ Сообщение отправлено оператору.\n"
        "Ожидай ответа."
    )


@dp.message(F.from_user.id == ADMIN_ID, F.reply_to_message)
async def admin_reply(message: Message):
    user_id = admin_messages.get(
        message.reply_to_message.message_id
    )

    if not user_id:
        await message.answer(
            "❌ Пользователь не найден.\n"
            "Ответь именно на сообщение пользователя."
        )
        return

    await message.copy_to(user_id)

    await message.answer("✅ Ответ отправлен.")


async def main():
    logging.basicConfig(level=logging.INFO)

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не установлен")

    print("🤖 Бот запущен!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
