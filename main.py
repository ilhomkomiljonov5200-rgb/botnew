import random
import datetime
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import db


# ================= CONFIG =================
TOKEN = "8524570791:AAHJu5HRzz9Kv6MOHxOTSJutgjDytdi_o4s"
ADMIN_ID = 5321852973
# ==========================================


bot = Bot(TOKEN)
dp = Dispatcher()


# =================================================
# 🔥 100+ RANDOM CHECK MESSAGES
# =================================================

check_messages = [
    "Nimalar qilyapsan 🙂",
    "Kuning qanday o‘tyapti?",
    "Bandmisan hozir?",
    "Charchamadingmi?",
    "Kayfiyating yaxshimi?",
    "Nimalar bilan bandsan?",
    "Bugun rejalaring qanday?",
    "Hammasi joyidami?",
    "Dam oldingmi?",
    "Ishlar qalay?",
    "Hozir nima qilyapsan?",
    "Biror qiziq narsa bo‘ldimi bugun?",
    "Bugun nimani uddalading?",
    "Kichkina tanaffus qildingmi?",
    "Choy ichdingmi ☕",
    "Suv ichishni unutma 😄",
    "Bugun kuldingmi?",
    "Stress qilmayapsanmi?",
    "O‘zingga vaqt ajratdingmi?",
    "Bugun kayfiyat qanday?",
] * 6


evening_messages = [
    "Kechqurun nimalar bilan bandsan?",
    "Bugungi kun qanday o‘tdi?",
    "Dam olyapsanmi?",
    "Bugun nimadan xursand bo‘lding?",
    "Hali uxlamadingmi 😄",
    "Bugun o‘zing uchun nima qilding?"
]


# =================================================
# DAILY MESSAGES
# =================================================

messages = [
    "Bugun o‘zingni ortiqcha qiynama 🙂",
    "Tabassuming kayfiyatni ko‘taradi 😊",
    "Ko‘p ishlama, biroz dam ol.",
    "Sog‘lig‘ing hamma narsadan muhimroq.",
    "Sen bilan gaplashish yoqimli.",
    "Bugun o‘zingga vaqt ajrat.",
    "Shunchaki yaxshi odamsan 🙂",
    "Hayot sekin yashalganda chiroyliroq.",
    "Bugun hammasi joyiga tushadi.",
    "Seni eslaydigan do‘sting bor 🙂"
]


special_messages = [
    "Bugun shunchaki aytgim keldi — sen yaxshi insonsan ⭐",
    "Tasodifan tanishganmiz, lekin yaxshi odam bo‘lib chiqding 🙂",
    "Hayotimga iliqlik olib kirgan kam sonli insonlardan birisan.",
    "Bugungi maxsus eslatma: sen yetarlisan va qadrlisan."
]


random_messages = [
    "Kichkina tanaffus qil ☕",
    "Biror qo‘shiq eshit 🎧",
    "Bugun suv ko‘proq ich 😄",
    "Ortiqcha stress qilma",
    "Hayot oddiy narsalarda go‘zal"
]


# =================================================
# BUTTON
# =================================================

gift_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text="🎁 Qo‘shimcha sovg‘a olish",
            url="https://t.me/ilhom_komiljonov"
        )]
    ]
)


waiting_answer = set()
waiting_support = set()   # 🔥 /zerikdim uchun qo‘shildi
streaks = {}


# =================================================
# HELPERS
# =================================================

def time_prefix():
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return "☀️ Xayrli tong!\n\n"
    elif 18 <= hour:
        return "🌙 Yaxshi dam ol!\n\n"
    return ""


# =================================================
# START
# =================================================

@dp.message(Command("start"))
async def start(msg: Message):
    await db.add_user(msg.from_user.id)
    await msg.answer("💌 Daily Caring Bot ishga tushdi 🙂", reply_markup=gift_kb)


# =================================================
# RANDOM
# =================================================

@dp.message(Command("random"))
async def random_cmd(msg: Message):
    await msg.answer(random.choice(random_messages), reply_markup=gift_kb)


# =================================================
# 🔥 ZERIKDIM (YANGI)
# =================================================

@dp.message(Command("zerikdim"))
async def bored(msg: Message):

    waiting_support.add(msg.from_user.id)

    await msg.answer(
        "😄 Zerikdingmi?\n\n"
        "Nima bo‘ldi, yoz.\nMen senga yordam beraman 🙂",
        reply_markup=gift_kb
    )


# =================================================
# TODAY (daily sovg‘a)
# =================================================

@dp.message(Command("today"))
async def today(msg: Message):

    uid = msg.from_user.id
    today_date = str(datetime.date.today())
    last = await db.get_last_date(uid)

    if uid not in streaks:
        streaks[uid] = 0

    if last == today_date:
        await msg.answer("Bugungi sovg‘a allaqachon ochilgan 🙂")
        return

    if random.randint(1, 5) == 1:
        text = "⭐ Maxsus sovg‘a!\n\n" + random.choice(special_messages)
    else:
        text = random.choice(messages)

    streaks[uid] += 1
    await db.update_date(uid)

    waiting_answer.add(uid)

    await msg.answer(
        f"{time_prefix()}💌 Kunlik sovg‘a:\n\n{text}\n\n🔥 Streak: {streaks[uid]} kun\n\n"
        "🧠 Bugun nima qilding?",
        reply_markup=gift_kb
    )


# =================================================
# FORWARD ANSWERS
# =================================================

@dp.message(F.text)
async def forward_answers(msg: Message):

    if msg.text.startswith("/"):
        return

    uid = msg.from_user.id

    # daily javob
    if uid in waiting_answer:
        waiting_answer.remove(uid)
        await bot.forward_message(ADMIN_ID, msg.chat.id, msg.message_id)
        await msg.answer("Kuning qanday o'tishidan qat’iy nazar doim kulib yur🙂")
        return

    # zerikdim javobi
    if uid in waiting_support:
        waiting_support.remove(uid)
        await bot.forward_message(ADMIN_ID, msg.chat.id, msg.message_id)
        await msg.answer("Tushundim 🙂 Tez orada yozaman.")


# =================================================
# AUTO TASKS
# =================================================

async def send_daily():
    users = await db.get_all_users()
    for (uid,) in users:
        await bot.send_message(uid, "💌 Bugungi sovg‘a tayyor 🙂 /today ni bos", reply_markup=gift_kb)


async def send_check():
    users = await db.get_all_users()
    for (uid,) in users:
        waiting_answer.add(uid)
        await bot.send_message(uid, random.choice(check_messages), reply_markup=gift_kb)


async def send_evening():
    users = await db.get_all_users()
    for (uid,) in users:
        waiting_answer.add(uid)
        await bot.send_message(uid, "🌙 " + random.choice(evening_messages), reply_markup=gift_kb)


# =================================================
# MAIN
# =================================================

async def main():
    await db.init_db()

    scheduler = AsyncIOScheduler()

    scheduler.add_job(send_daily, "cron", hour=9, minute=0)
    scheduler.add_job(send_check, "interval", hours=6)
    scheduler.add_job(send_evening, "cron", hour=21, minute=0)

    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
