# -*- coding: utf-8 -*-
"""Samitorio v0.4 - persistent settings (language, sound, volumes)."""
import json
import os

_DIR = os.path.dirname(os.path.abspath(__file__))
_PATH = os.path.join(_DIR, "saves", "settings.json")

DEFAULTS = {
    "lang": "en",
    "sound": True,
    "music": True,
    "sfx_vol": 0.7,
    "music_vol": 0.45,
    "show_fps": True,
}

_data = dict(DEFAULTS)


def load():
    global _data
    try:
        with open(_PATH, "r", encoding="utf-8") as f:
            saved = json.load(f)
        _data = dict(DEFAULTS)
        _data.update({k: v for k, v in saved.items() if k in DEFAULTS})
    except (OSError, ValueError):
        _data = dict(DEFAULTS)
    return _data


def save():
    try:
        os.makedirs(os.path.dirname(_PATH), exist_ok=True)
        with open(_PATH, "w", encoding="utf-8") as f:
            json.dump(_data, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def get(key):
    return _data.get(key)


def set(key, value):
    if key in DEFAULTS and isinstance(value, type(DEFAULTS[key])):
        _data[key] = value
    save()
    return _data[key]