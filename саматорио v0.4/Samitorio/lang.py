# -*- coding: utf-8 -*-
"""Samitorio v0.4 - localization (EN / RU)."""
import core

_lang = "en"

EN = {
    "hud.hp": "HP %d/%d",
    "hud.power": "Power %d/%d kW",
    "hud.wave": "Wave %s",
    "hud.wave_in": "in %ds",
    "hud.wave_active": "ACTIVE!",
    "hud.day": "Day",
    "hud.night": "Night",
    "hud.score": "Score %d",
    "hud.fps": "FPS %d",
    "hud.controls": "[WASD] Move  [LMB] Mine  [E] Inv  [T] Research  [B] Build  [ESC] Menu",
    "hud.controls_build": "[1-9] Select  [R] Rotate  [[ ] / [ ]] Recipe  [LMB] Place  [RMB] Cancel",
    "hud.map": "[M] Map",
    "valid.not_researched": "Not researched",
    "valid.tile_occupied": "Tile occupied",
    "valid.out_of_bounds": "Out of bounds",
    "valid.boulder": "Boulder blocks",
    "valid.no_vein": "No ore deposit",
    "valid.clear": "Clear ground first",
    "valid.missing": "Missing materials",
    "inv.title": "INVENTORY",
    "inv.close": "[E] Close",
    "inv.items": "Items",
    "inv.craft": "Craft",
    "inv.stats": "Stats",
    "inv.equip": "Equip",
    "inv.search": "Type to search...",
    "inv.select": "Select an item",
    "inv.stack": "Stack: %d",
    "inv.recipe": "Recipe",
    "inv.queue": "Crafting Queue",
    "inv.idle": "Idle - click a recipe below",
    "inv.left": "%ds left",
    "inv.craft_recipes": "Hand-craft recipes",
    "inv.craft": "Craft",
    "inv.storage": "Storage",
    "inv.equip_title": "Equipment / Armor Grid",
    "inv.available": "Available:",
    "res.title": "RESEARCH  [T] close",
    "res.ing": "Researching: %s  %.0f%%",
    "res.start": "Start",
    "res.locked": "Locked",
    "menu.title": "SAMITORIO",
    "menu.version": "v0.4",
    "menu.continue": "Continue",
    "menu.new": "New Game",
    "menu.settings": "Settings",
    "menu.quit": "Quit",
    "menu.no_save": "No saved game",
    "pause.resume": "Resume",
    "pause.save": "Save Game",
    "pause.save_menu": "Save & Quit to Menu",
    "pause.quit": "Quit to Desktop",
    "set.title": "SETTINGS",
    "set.lang": "Language",
    "set.sound": "Sound",
    "set.music": "Music",
    "set.sfx_vol": "SFX Volume",
    "set.music_vol": "Music Volume",
    "set.fps": "Show FPS",
    "set.back": "Back",
    "set.on": "On",
    "set.off": "Off",
    "set.seed": "Seed: %d",
    "set.saved": "Game saved",
    "msg.no_save": "There is no saved game yet. Start a new game first.",
    "msg.overwrite": "Auto-save overwritten on exit.",
}

RU = {
    "hud.hp": "ЗД %d/%d",
    "hud.power": "Энергия %d/%d кВт",
    "hud.wave": "Волна %s",
    "hud.wave_in": "через %dс",
    "hud.wave_active": "АТАКА!",
    "hud.day": "День",
    "hud.night": "Ночь",
    "hud.score": "Счёт %d",
    "hud.fps": "FPS %d",
    "hud.controls": "[WASD] Движ.  [ЛКМ] Копать  [E] Инв.  [T] Наука  [B] Стройка  [ESC] Меню",
    "hud.controls_build": "[1-9] Выбор  [R] Поворот  [[ ] / [ ]] Рецепт  [ЛКМ] Ставить  [ПКМ] Отмена",
    "hud.map": "[M] Карта",
    "valid.not_researched": "Не исследовано",
    "valid.tile_occupied": "Тайл занят",
    "valid.out_of_bounds": "За пределами мира",
    "valid.boulder": "Мешает валун",
    "valid.no_vein": "Нет залежи",
    "valid.clear": "Сначала расчисти землю",
    "valid.missing": "Не хватает материалов",
    "inv.title": "ИНВЕНТАРЬ",
    "inv.close": "[E] Закрыть",
    "inv.items": "Предметы",
    "inv.craft": "Крафт",
    "inv.stats": "Хранилище",
    "inv.equip": "Экипировка",
    "inv.search": "Поиск...",
    "inv.select": "Выберите предмет",
    "inv.stack": "Стак: %d",
    "inv.recipe": "Рецепт",
    "inv.queue": "Очередь крафта",
    "inv.idle": "Простой — жмите на рецепт ниже",
    "inv.left": "осталось %dс",
    "inv.craft_recipes": "Ручные рецепты",
    "inv.craft": "Создать",
    "inv.storage": "Хранилище",
    "inv.equip_title": "Экипировка / Слоты брони",
    "inv.available": "Доступно:",
    "res.title": "ИССЛЕДОВАНИЯ  [T] закрыть",
    "res.ing": "Исследуется: %s  %.0f%%",
    "res.start": "Начать",
    "res.locked": "Заблокировано",
    "menu.title": "САМИТОРИО",
    "menu.version": "v0.4",
    "menu.continue": "Продолжить",
    "menu.new": "Новая игра",
    "menu.settings": "Настройки",
    "menu.quit": "Выйти",
    "menu.no_save": "Нет сохранения",
    "pause.resume": "Продолжить",
    "pause.save": "Сохранить игру",
    "pause.save_menu": "Сохранить и в меню",
    "pause.quit": "Выйти на рабочий стол",
    "set.title": "НАСТРОЙКИ",
    "set.lang": "Язык",
    "set.sound": "Звуки",
    "set.music": "Музыка",
    "set.sfx_vol": "Громкость эффектов",
    "set.music_vol": "Громкость музыки",
    "set.fps": "Показывать FPS",
    "set.back": "Назад",
    "set.on": "Вкл",
    "set.off": "Выкл",
    "set.seed": "Сид: %d",
    "set.saved": "Игра сохранена",
    "msg.no_save": "Сохраниений ещё нет — начните новую игру.",
    "msg.overwrite": "Автосохранение перезаписано при выходе.",
}

ITEM_RU = {
    "iron-ore": "Железная руда", "copper-ore": "Медная руда",
    "coal": "Уголь", "stone": "Камень", "uranium-ore": "Урановая руда",
    "oil": "Нефть", "sulfur": "Сера", "calcite": "Кальцит",
    "scrap": "Металлолом", "rare-ore": "Редкая руда",
    "tungsten-ore": "Вольфрамовая руда", "cryo-ore": "Крио-кристалл",
    "wood": "Древесина", "iron-plate": "Железная плита",
    "copper-plate": "Медная плита", "steel-plate": "Стальная плита",
    "stone-brick": "Каменный блок", "iron-gear-wheel": "Железная шестерня",
    "iron-stick": "Железный прут", "copper-cable": "Медный провод",
    "electronic-circuit": "Электронная схема", "advanced-circuit": "Продвинутая схема",
    "processing-unit": "Процессор", "plastic-bar": "Пластик",
    "battery": "Батарея", "automation-science-pack": "Колба: автоматика",
    "logistic-science-pack": "Колба: логистика", "military-science-pack": "Колба: военная",
    "chemical-science-pack": "Колба: химия", "production-science-pack": "Колба: производство",
    "utility-science-pack": "Колба: средства производства",
    "conveyor-belt": "Конвейерная лента", "fast-belt": "Быстрая лента",
    "inserter": "Вставщик", "fast-inserter": "Быстрый вставщик",
    "gun-turret": "Пулемётная турель", "laser-turret": "Лазерная турель",
    "wall": "Каменная стена", "lamp": "Лампа", "rail": "Рельса",
    "firearm-magazine": "Патроны", "iron-armor": "Железная броня",
    "heavy-armor": "Тяжёлая броня", "power-armor": "Силовая броня",
    "exoskeleton": "Экзоскелет", "night-vision": "Ночное зрение",
    "energy-shield": "Энергощит", "solar-panel": "Солнечная панель",
    "coal-gen": "Котёл", "laser-beam": "Лазерный луч",
}

TECH_NAME_RU = {
    "automation": "Автоматика", "logistics": "Логистика",
    "steel-proc": "Выплавка стали", "electricity": "Электричество",
    "turrets": "Турели", "advanced": "Продвинутые схемы",
    "military": "Военная техника", "railways": "Железные дороги",
}

TECH_DESC_RU = {
    "automation": "Ленты, вставщики, шахты, сборщики",
    "logistics": "Быстрые ленты и вставщики",
    "steel-proc": "Выплавка стали",
    "electricity": "Солнечные панели, лампы",
    "turrets": "Стены и пулемётные турели",
    "advanced": "Продвинутые схемы и батареи",
    "military": "Лазерные турели",
    "railways": "Рельсы",
}

BIOME_RU = {0: "Равнина", 1: "Пепельник", 2: "Болото", 3: "Пустошь",
            4: "Мерзлота", 5: "Голая земля", 6: "Чаща", 7: "Хребет"}

_EN_ITEM = {k: v[0] for k, v in core.ITEMS.items()}


def set(lang_code):
    global _lang
    _lang = lang_code if lang_code in ("ru", "en") else "en"


def get():
    return _lang


def other():
    return "ru" if _lang == "en" else "en"


def t(key, *args):
    d = RU if _lang == "ru" else EN
    s = d.get(key)
    if s is None:
        s = EN.get(key, key)
    if args:
        return s % args
    return s


def item(key):
    if _lang == "ru":
        return ITEM_RU.get(key, _EN_ITEM.get(key, key))
    return _EN_ITEM.get(key, key)


def tech(key):
    if _lang == "ru":
        return TECH_NAME_RU.get(key, key.replace("-", " ").title())
    return key.replace("-", " ").title()


def tech_desc(key):
    if _lang == "ru":
        return TECH_DESC_RU.get(key, "")
    return core.TECH.get(key, {}).get("desc", "")


def biome(key):
    if _lang == "ru":
        return BIOME_RU.get(key, "")
    return core.BIOME_NAME.get(key, "")