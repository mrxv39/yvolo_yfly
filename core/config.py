# C:\Users\Usuario\Desktop\proyectos\yvolo\core\config.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

from .paths import app_dir, is_frozen_exe, appdata_dir


DEFAULT_CONFIG: Dict[str, Any] = {
    "app_name": "yvolo",
    "language": "es",
    "labels": {
        "btn_open_chat": "Abrir Chat",
        "btn_close_chat": "Cerrar Chat",
        "btn_process_ideas": "Procesar Ideas",
        "btn_new_project": "Nuevo Proyecto",
    },
}


def _ensure_labels(cfg: Dict[str, Any]) -> Dict[str, Any]:
    if "labels" not in cfg or not isinstance(cfg["labels"], dict):
        cfg["labels"] = dict(DEFAULT_CONFIG["labels"])
    if "btn_new_project" not in cfg["labels"]:
        cfg["labels"]["btn_new_project"] = DEFAULT_CONFIG["labels"]["btn_new_project"]
    return cfg


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("settings.json debe ser un objeto JSON")
    return data


def load_config() -> Dict[str, Any]:
    """
    SOURCE:
        <repo>/config/settings.json
        fallback DEFAULT_CONFIG

    EXE:
        1) <exe_dir>/config/settings.json
        2) <exe_dir>/settings.json
        3) %APPDATA%/yvolo/settings.json
        4) DEFAULT_CONFIG
    """

    if not is_frozen_exe():
        cfg_path = app_dir() / "config" / "settings.json"
        try:
            data = _load_json(cfg_path)
            data.setdefault("app_name", DEFAULT_CONFIG["app_name"])
            data = _ensure_labels(data)
            return data
        except Exception:
            return dict(DEFAULT_CONFIG)

    portable_1 = app_dir() / "config" / "settings.json"
    portable_2 = app_dir() / "settings.json"
    user_cfg = appdata_dir() / "settings.json"

    for path in (portable_1, portable_2, user_cfg):
        try:
            if path.exists():
                data = _load_json(path)
                data.setdefault("app_name", DEFAULT_CONFIG["app_name"])
                data = _ensure_labels(data)
                return data
        except Exception:
            continue

    return dict(DEFAULT_CONFIG)
