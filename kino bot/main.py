import time
import telebot
from telebot import types
import database as db
import Button

BOT_TOKEN = "8543927305:AAFMZICK47R142NBK8jQdz3Rt2mfFx4MCpo"

ADMINS = [7618611292]

CHANNELS = [
    {
        "name": "🎬 Bizning Kanal",
        "id": "-1003896833204",
        "url": "https://t.me/Kino_0629"
    }
]

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

db.init_db()


def is_admin(user_id: int) -> bool:
    return user_id in ADMINS


def check_sub(user_id: int) -> bool:
    if not CHANNELS:
        return True

    for channel in CHANNELS:

        try:

            member = bot.get_chat_member(
                channel["id"],
                user_id
            )

            print(
                f"User: {user_id} | "
                f"Channel: {channel['id']} | "
                f"Status: {member.status}"
            )

            if member.status in ["left", "kicked"]:
                return False

        except Exception as e:

            print(
                f"Obunani tekshirishda xatolik: {e}"
            )

            return False

    return True


def send_to_channel(message: types.Message):
    try:

        bot.forward_message(
            chat_id=CHANNELS[0]["id"],
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )

        print(
            f"Kanalga yuborildi: "
            f"{message.from_user.id}"
        )

    except Exception as e:

        print(
            f"Kanalga yuborishda xatolik: {e}"
        )


@bot.message_handler(commands=["start"])
def start_handler(message: types.Message):
    user_id = message.from_user.id

    db.add_user(
        user_id,
        message.from_user.username,
        message.from_user.first_name
    )

    if not check_sub(user_id):
        bot.send_message(
            message.chat.id,
            "👋 <b>Assalomu alaykum!</b>\n\n"
            "Botdan foydalanish uchun kanalga a'zo bo'ling "
            "va <b>«A'zo bo'ldim»</b> tugmasini bosing:",
            reply_markup=Button.subscription_markup(CHANNELS)
        )

        return

    bot.send_message(
        message.chat.id,
        f"👋 Assalomu alaykum, "
        f"<b>{message.from_user.first_name}</b>!\n\n"
        "🎬 <b>Kino Botga xush kelibsiz!</b>\n"
        "Kino yuklab olish uchun uning <b>kodini</b> "
        "(masalan: <code>1</code>, <code>25</code>) yuboring.",
        reply_markup=Button.main_menu_markup()
    )


@bot.message_handler(commands=["cancel"])
def cancel_handler(message: types.Message):
    bot.send_message(
        message.chat.id,
        "❌ Jarayon bekor qilindi."
    )


@bot.message_handler(commands=["admin"])
def admin_handler(message: types.Message):
    if not is_admin(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "⛔ Siz admin emassiz!"
        )

        return

    bot.send_message(
        message.chat.id,
        "👑 <b>Admin boshqaruv paneli:</b>",
        reply_markup=Button.admin_menu_markup()
    )


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call: types.CallbackQuery):
    user_id = call.from_user.id

    if call.data == "check_sub":

        if check_sub(user_id):

            bot.answer_callback_query(
                call.id,
                "✅ Obuna tasdiqlandi!"
            )

            bot.edit_message_text(
                "✅ <b>Obuna tasdiqlandi!</b>\n\n"
                "Endi kino kodini yuborishingiz mumkin:",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )

            bot.send_message(
                call.message.chat.id,
                "👇 <b>Quyidagi tugmalar orqali:</b>",
                reply_markup=Button.main_menu_markup()
            )

        else:

            bot.answer_callback_query(
                call.id,
                "❌ Hali kanalga a'zo bo'lmagansiz!",
                show_alert=True
            )

    elif call.data == "admin_stats":

        if not is_admin(user_id):
            return

        bot.answer_callback_query(call.id)

        u_count = db.get_users_count()
        m_count = db.get_movies_count()

        bot.send_message(
            call.message.chat.id,
            f"📊 <b>Statistika:</b>\n\n"
            f"👤 Foydalanuvchilar: <b>{u_count}</b> ta\n"
            f"🎬 Kinolar: <b>{m_count}</b> ta",
            reply_markup=Button.admin_menu_markup()
        )

    elif call.data == "admin_add_movie":

        if not is_admin(user_id):
            return

        bot.answer_callback_query(call.id)

        msg = bot.send_message(
            call.message.chat.id,
            "📹 <b>Kino videosini yuboring:</b>\n"
            "<i>(Bekor qilish: /cancel)</i>"
        )

        bot.register_next_step_handler(
            msg,
            step_movie_file
        )

    elif call.data == "admin_del_movie":

        if not is_admin(user_id):
            return

        bot.answer_callback_query(call.id)

        msg = bot.send_message(
            call.message.chat.id,
            "🗑 <b>O'chirmoqchi bo'lgan kino kodini kiriting:</b>\n"
            "<i>(Bekor qilish: /cancel)</i>"
        )

        bot.register_next_step_handler(
            msg,
            step_movie_delete
        )

    elif call.data == "admin_broadcast":

        if not is_admin(user_id):
            return

        bot.answer_callback_query(call.id)

        msg = bot.send_message(
            call.message.chat.id,
            "📢 <b>Yubormoqchi bo'lgan xabaringizni yuboring:</b>\n"
            "<i>(Bekor qilish: /cancel)</i>"
        )

        bot.register_next_step_handler(
            msg,
            step_broadcast
        )


def step_movie_file(message: types.Message):
    if message.text == "/cancel":
        bot.send_message(
            message.chat.id,
            "❌ Bekor qilindi."
        )

        return

    if message.video:

        file_id = message.video.file_id
        file_type = "video"

    elif message.document:

        file_id = message.document.file_id
        file_type = "document"

    else:

        msg = bot.send_message(
            message.chat.id,
            "❌ Video yoki fayl yuboring "
            "(yoki /cancel):"
        )

        bot.register_next_step_handler(
            msg,
            step_movie_file
        )

        return

    msg = bot.send_message(
        message.chat.id,
        "🔢 Ushbu kino uchun <b>kod</b> kiriting "
        "(masalan: <code>101</code>):"
    )

    bot.register_next_step_handler(
        msg,
        step_movie_code,
        file_id,
        file_type
    )


def step_movie_code(
        message: types.Message,
        file_id: str,
        file_type: str
):
    if message.text == "/cancel":
        bot.send_message(
            message.chat.id,
            "❌ Bekor qilindi."
        )

        return

    if not message.text or not message.text.isdigit():
        msg = bot.send_message(
            message.chat.id,
            "❌ Kod faqat raqam bo'lishi kerak! "
            "Qaytadan kiriting:"
        )

        bot.register_next_step_handler(
            msg,
            step_movie_code,
            file_id,
            file_type
        )

        return

    code = int(message.text)

    msg = bot.send_message(
        message.chat.id,
        "📝 Kino nomi/tavsifini kiriting "
        "(yoki <code>/skip</code> yozing):"
    )

    bot.register_next_step_handler(
        msg,
        step_movie_caption,
        code,
        file_id,
        file_type
    )


def step_movie_caption(
        message: types.Message,
        code: int,
        file_id: str,
        file_type: str
):
    if message.text == "/cancel":
        bot.send_message(
            message.chat.id,
            "❌ Bekor qilindi."
        )

        return

    caption = (
        ""
        if message.text == "/skip"
        else (message.text or "")
    )

    if db.add_movie(
            code,
            file_id,
            file_type,
            caption
    ):

        bot.send_message(
            message.chat.id,
            f"✅ <b>Kino saqlandi!</b>\n\n"
            f"🆔 Kodi: <code>{code}</code>",
            reply_markup=Button.admin_menu_markup()
        )

    else:

        bot.send_message(
            message.chat.id,
            "❌ Saqlashda xatolik yuz berdi.",
            reply_markup=Button.admin_menu_markup()
        )


def step_movie_delete(message: types.Message):
    if message.text == "/cancel":
        bot.send_message(
            message.chat.id,
            "❌ Bekor qilindi."
        )

        return

    if not message.text or not message.text.isdigit():
        msg = bot.send_message(
            message.chat.id,
            "❌ Raqamli kod kiriting:"
        )

        bot.register_next_step_handler(
            msg,
            step_movie_delete
        )

        return

    code = int(message.text)

    if db.delete_movie(code):

        bot.send_message(
            message.chat.id,
            f"✅ <code>{code}</code> kodli kino o'chirildi!",
            reply_markup=Button.admin_menu_markup()
        )

    else:

        bot.send_message(
            message.chat.id,
            f"❌ <code>{code}</code> kodli kino topilmadi.",
            reply_markup=Button.admin_menu_markup()
        )


def step_broadcast(message: types.Message):
    if message.text == "/cancel":
        bot.send_message(
            message.chat.id,
            "❌ Bekor qilindi."
        )

        return

    users = db.get_all_users()

    status_msg = bot.send_message(
        message.chat.id,
        f"⏳ {len(users)} ta foydalanuvchiga yuborilmoqda..."
    )

    sent = 0
    failed = 0

    for user_id in users:

        try:

            bot.copy_message(
                chat_id=user_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )

            sent += 1

            time.sleep(0.04)

        except Exception:

            failed += 1

    bot.edit_message_text(
        f"📢 <b>Yakunlandi!</b>\n\n"
        f"✅ Yetkazildi: <b>{sent}</b>\n"
        f"❌ Yetib bormadi: <b>{failed}</b>",
        chat_id=status_msg.chat.id,
        message_id=status_msg.message_id
    )


@bot.message_handler(commands=["help"])
def help_handler(message: types.Message):
    bot.send_message(
        message.chat.id,
        "ℹ️ <b>Botdan foydalanish bo'yicha yo'riqnoma:</b>\n\n"
        "🎬 Kino olish uchun uning <b>kodini</b> yuboring "
        "(masalan: <code>1</code>, <code>25</code>).\n\n"
        "🔘 <b>Tugmalar:</b>\n"
        "🏠 <b>Start</b> — bosh menyu\n"
        "🎞 <b>Kinolar bazasi</b> — kinolar kanali\n"
        "👑 <b>Admin</b> — admin bilan bog'lanish\n"
        "ℹ️ <b>Help</b> — ushbu yo'riqnoma\n\n"
        "📩 Boshqa xabar/rasm yuborsangiz — u kanalga yuboriladi.",
        reply_markup=Button.main_menu_markup()
    )


MENU_BUTTONS = {"🏠 Start", "🎞 Kinolar bazasi", "👑 Admin", "ℹ️ Help"}


# Menyu tugmalari bosilganda (kanalga yuborilmasligi uchun)
@bot.message_handler(func=lambda m: m.text in MENU_BUTTONS)
def menu_handler(message: types.Message):
    text = message.text.strip()

    if text == "🏠 Start":
        bot.send_message(
            message.chat.id,
            f"👋 Assalomu alaykum, "
            f"<b>{message.from_user.first_name}</b>!\n\n"
            "🎬 Kino kodini yuboring "
            "(masalan: <code>1</code>, <code>25</code>)."
        )

    elif text == "🎞 Kinolar bazasi":
        bot.send_message(
            message.chat.id,
            "🎞 <b>Kinolar bazasi:</b>\n\n"
            "Barcha kinolar ushbu kanalda joylashgan. "
            "Kerakli kinoni tanlash uchun quyidagi "
            "tugmani bosing:",
            reply_markup=Button.kinolar_bazasi_markup()
        )

    elif text == "👑 Admin":
        bot.send_message(
            message.chat.id,
            "👑 <b>Admin bilan bog'lanish:</b>\n\n"
            "📩 Savol, taklif yoki murojaatlar uchun "
            "quyidagi tugma orqali admina yozing:",
            reply_markup=Button.admin_contact_markup()
        )

    elif text == "ℹ️ Help":
        help_handler(message)


@bot.message_handler(
    content_types=[
        "text",
        "photo",
        "video",
        "document",
        "audio",
        "voice",
        "animation",
        "sticker"
    ]
)
def search_movie_handler(message: types.Message):
    user_id = message.from_user.id

    db.add_user(
        user_id,
        message.from_user.username,
        message.from_user.first_name
    )

    if not check_sub(user_id):
        bot.send_message(
            message.chat.id,
            "⚠️ Kinolarni yuklab olish uchun "
            "avval kanalga a'zo bo'ling:",
            reply_markup=Button.subscription_markup(CHANNELS)
        )

        return

    if message.text:

        text = message.text.strip()

        if text.isdigit():

            code = int(text)

            movie = db.get_movie(code)

            if not movie:
                bot.reply_to(
                    message,
                    f"❌ <b>{code}</b> kodli kino topilmadi!"
                )

                return

            caption_text = (
                f"{movie['caption']}\n\n"
                if movie["caption"]
                else ""
            )

            caption_text += (
                f"🎬 <b>Kino kodi:</b> "
                f"<code>{movie['code']}</code>\n"
                f"🤖 <i>@{bot.get_me().username}</i>"
            )

            try:

                if movie["file_type"] == "video":

                    bot.send_video(
                        message.chat.id,
                        movie["file_id"],
                        caption=caption_text
                    )

                else:

                    bot.send_document(
                        message.chat.id,
                        movie["file_id"],
                        caption=caption_text
                    )

            except Exception as e:

                bot.reply_to(
                    message,
                    f"❌ Yuborishda xatolik: {e}"
                )

            return

        else:

            send_to_channel(message)

            bot.reply_to(
                message,
                "✅ Xabaringiz kanalga yuborildi."
            )

            return

    send_to_channel(message)

    bot.send_message(
        message.chat.id,
        "✅ Yuborildi."
    )


if __name__ == "__main__":
    print("🚀 Bot muvaffaqiyatli ishga tushdi...", flush=True)

    while True:
        try:
            bot.infinity_polling(
                timeout=30,
                long_polling_timeout=20,
                interval=1,
                restart_on_change=False
            )
        except Exception as e:
            print(
                f"⚠️ Ulanish uzildi: {e}\n"
                f"🔁 5 soniyadan so'ng qayta ulaniladi...",
                flush=True
            )
            time.sleep(5)
