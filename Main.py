import asyncio
import os
import random
import time

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

import database
from items import get_random_item


load_dotenv()


TOKEN = os.getenv("BOT_TOKEN")


bot = Bot(TOKEN)

dp = Dispatcher()


COOLDOWN = 300

active_items = {}



@dp.message(Command("start"))
async def start(message: Message):

    await database.add_group(
        message.chat.id
    )

    await message.reply(
        "🐶 Hop Bot فعال شد!"
    )



@dp.message(lambda m: m.text == "هاپ هاپ")
async def hop(message: Message):

    user = message.from_user
    chat = message.chat.id

    data = await database.get_user(
        user,
        chat
    )

    now = int(time.time())


    if now - data[4] < COOLDOWN:

        remain = COOLDOWN - (now - data[4])

        await message.reply(
            f"⏳ {remain//60} دقیقه صبر کن"
        )

        return


    await database.give_hop(
        user,
        chat
    )


    await message.reply(
        "🐶 هاپ هاپ!\n"
        "💎 +1 Hop Point"
    )



@dp.message(Command("hop"))
async def my_score(message: Message):

    data = await database.get_user(
        message.from_user,
        message.chat.id
    )

    await message.reply(
        f"💎 Hop Point:\n{data[3]}"
    )



@dp.message(Command("bag"))
async def bag(message: Message):

    items = await database.get_inventory(
        message.from_user.id
    )


    if not items:

        await message.reply(
            "🎒 کیف خالی است"
        )

        return


    text="🎒 کیف تو:\n\n"


    for item in items:

        text += f"{item[0]} | {item[1]}\n"


    await message.reply(text)



async def spawn_item():

    while True:

        await asyncio.sleep(3600)


        for chat_id in list(active_items.keys()):

            item, rarity = get_random_item()

            active_items[chat_id] = (
                item,
                rarity
            )


            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                    InlineKeyboardButton(
                        text="🎁 بردار",
                        callback_data="take"
                    )
                    ]
                ]
            )


            await bot.send_message(
                chat_id,
                f"🎁 آیتم ظاهر شد!\n\n"
                f"{item}\n"
                f"⭐ {rarity}\n\n"
                f"شانس گرفتن: 50٪",
                reply_markup=kb
            )



@dp.callback_query(lambda c: c.data=="take")
async def take(call: CallbackQuery):

    chat = call.message.chat.id


    if chat not in active_items:

        await call.answer(
            "چیزی نیست"
        )

        return


    if random.randint(1,100) > 50:

        await call.message.answer(
            "💨 شانس نیاوردی"
        )

        return


    item, rarity = active_items.pop(chat)


    await database.add_item(
        call.from_user.id,
        item,
        rarity
    )


    await call.message.answer(
        f"🎉 {call.from_user.first_name}\n\n"
        f"گرفتی:\n"
        f"{item}\n"
        f"⭐ {rarity}"
    )



async def main():

    await database.init_db()

    asyncio.create_task(
        spawn_item()
    )

    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())
