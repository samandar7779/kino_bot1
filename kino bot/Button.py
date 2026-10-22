from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


# Majburiy kanallarga a'zo bo'lish tugmalari
def subscription_markup(channels: list) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    for ch in channels:
        name = ch.get("name", "📢 Kanalga a'zo bo'lish")
        url = ch.get("url", "")
        markup.add(InlineKeyboardButton(text=name, url=url))

    # Obunani tekshirish tugmasi
    check_btn = InlineKeyboardButton(text="✅ A'zo bo'ldim (Tekshirish)", callback_data="check_sub")
    markup.add(check_btn)
    return markup


# Bosh menyu tugmalari (Reply Keyboard)
def main_menu_markup() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    b1 = KeyboardButton(text="🏠 Start")
    b2 = KeyboardButton(text="🎞 Kinolar bazasi")
    b3 = KeyboardButton(text="👑 Admin")
    b4 = KeyboardButton(text="ℹ️ Help")
    markup.add(b1, b2, b3, b4)
    return markup


# Kinolar bazasi kanaliga o'tish tugmasi
def kinolar_bazasi_markup() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton(
        text="🎬 Kanalga o'tish",
        url="https://t.me/kinolar_to"
    )
    markup.add(btn)
    return markup


# Admin bilan bog'lanish tugmasi
def admin_contact_markup() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton(text="📩 @abay_pg", url="https://t.me/abay_pg")
    markup.add(btn)
    return markup


# Admin boshqaruv paneli tugmalari
def admin_menu_markup() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    b1 = InlineKeyboardButton(text="➕ Kino qo'shish", callback_data="admin_add_movie")
    b2 = InlineKeyboardButton(text="🗑 Kino o'chirish", callback_data="admin_del_movie")
    b3 = InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")
    b4 = InlineKeyboardButton(text="📢 Xabar yuborish", callback_data="admin_broadcast")
    markup.add(b1, b2, b3, b4)
    return markup



