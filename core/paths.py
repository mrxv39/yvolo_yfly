# C:\Users\Usuario\Desktop\proyectos\yvolo\core\paths.py
from __future__ import annotations

import os
import sys
from pathlib import Path


def is_frozen_exe() -> bool:
    """
    True si corre como .exe empaquetado (PyInstaller).
    """
    return bool(getattr(sys, "frozen", False))


def app_dir() -> Path:
    """
    - Source: carpeta donde vive ui_main.py (raíz del repo)
    - EXE: carpeta donde vive yvolo.exe
    """
    if is_frozen_exe():
        return Path(sys.executable).resolve().parent
    # En source, este módulo está en core/, así que subimos un nivel
    return Path(__file__).resolve().parent.parent


def appdata_dir() -> Path:
    """
    %APPDATA%\\yvolo en Windows.
    Fallback: ~/.yvolo
    """
    base = os.environ.get("APPDATA")
    if base:
        return Path(base) / "yvolo"
    return Path.home() / ".yvolo"


def yvolo_root_file(filename: str) -> Path:
    """
    Archivo en la raíz del proyecto yvolo (source).
    En EXE se asume modo portable: junto al exe.
    """
    return app_dir() / filename


def projects_base_dir() -> Path:
    """
    Carpeta estándar para proyectos: Desktop\\proyectos
    """
    return Path.home() / "Desktop" / "proyectos"
