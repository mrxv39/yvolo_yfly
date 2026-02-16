# C:\Users\Usuario\Desktop\proyectos\yvolo\core\paths.py
from __future__ import annotations

import os
import sys
from pathlib import Path


def is_frozen_exe() -> bool:
    return bool(getattr(sys, "frozen", False))


def app_dir() -> Path:
    """
    SOURCE:
        carpeta raíz del repo

    EXE (PyInstaller onefile):
        sys._MEIPASS contiene los archivos embebidos
    """
    if is_frozen_exe():
        # PyInstaller onefile extrae aquí los data files
        if hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS)
        return Path(sys.executable).resolve().parent

    # En source, este módulo está en core/, así que subimos un nivel
    return Path(__file__).resolve().parent.parent


def appdata_dir() -> Path:
    base = os.environ.get("APPDATA")
    if base:
        return Path(base) / "yvolo"
    return Path.home() / ".yvolo"


def yvolo_root_file(filename: str) -> Path:
    return app_dir() / filename


def projects_base_dir() -> Path:
    return Path.home() / "Desktop" / "proyectos"
