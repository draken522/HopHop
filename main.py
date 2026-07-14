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

from keep_alive import keep_alive

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
            f"⏳ هنوز {remain//60} دقیقه باید صبر کنی"
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
        f"🐾 امتیاز تو:\n\n"
        f"💎 {data[3]} Hop Point"
    )





@dp.message(Command("bag"))
async def bag(message: Message):

    items = await database.get_inventory(
        message.from_user.id
    )


    if not items:

        await message.reply(
            "🎒 کیف تو خالی است"
        )

        return


    text = "🎒 آیتم‌های تو:\n\n"


    for item in items:

        text += (
            f"{item[0]}\n"
            f"⭐ {item[1]}\n\n"
        )


    await message.reply(text)





async def spawn_item():

    while True:

        await asyncio.sleep(3600)


        # فعلا فقط برای گروه‌هایی که ثبت شده‌اند

        async with database.aiosqlite.connect(database.DB) as db:

            cursor = await db.execute(
                "SELECT chat_id FROM groups"
            )

            groups = await cursor.fetchall()



        for group in groups:

            chat_id = group[0]


            item, rarity = get_random_item()


            active_items[chat_id] = (
                item,
                rarity
            )


            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🎁 بردار",
                            callback_data="take_item"
                        )
                    ]
                ]
            )


            await bot.send_message(
                chat_id,
                f"""
🎁 آیتم جدید ظاهر شد!

{item}

⭐ درجه:
{rarity}

🎯 شانس گرفتن: 50٪
""",
                reply_markup=keyboard
            )





@dp.callback_query(lambda c: c.data == "take_item")
async def take_item(call: CallbackQuery):

    chat_id = call.message.chat.id


    if chat_id not in active_items:

        await call.answer(
            "❌ آیتمی وجود ندارد"
        )

        return



    chance = random.randint(1,100)


    if chance > 50:

        await call.message.answer(
            f"💨 {call.from_user.first_name} شانس نیاورد!"
        )

        return



    item, rarity = active_items.pop(
        chat_id
    )


    await database.add_item(
        call.from_user.id,
        item,
        rarity
    )


    await call.message.answer(
        f"""
🎉 {call.from_user.first_name}

آیتم را گرفتی:

{item}

⭐ {rarity}
"""
    )





async def main():

    await database.init_db()


    asyncio.create_task(
        spawn_item()
    )


    await dp.start_polling(bot)





if __name__ == "__main__":

    keep_alive()

    asyncio.run(main())
