import random


ITEMS = [
    ("🪵 چوب ساده", "Common"),
    ("🗡 شمشیر آهنی", "Uncommon"),
    ("💎 کریستال آبی", "Rare"),
    ("👑 تاج پادشاهی", "Epic"),
    ("🐉 تخم اژدها", "Legendary"),
    ("🌑 قلب سایه", "Mythic"),
]


def get_random_item():
    return random.choice(ITEMS)
