from aiogram import Router
from aiogram.types.message import Message
from aiogram.filters import Command


router = Router()


@router.message(Command("test"))
async def user_info(message: Message):
    await message.answer(text=f"ваш телеграм айди: @{message.from_user.username}")