# C:\Users\Usuario\Desktop\proyectos\yvolo\core\git_utils.py
from __future__ import annotations

import os
import subprocess


def git_init_if_needed(project_dir: str) -> None:
    """
    Inicializa repo git si no existe carpeta .git
    """
    git_dir = os.path.join(project_dir, ".git")
    if os.path.isdir(git_dir):
        return

    try:
        subprocess.run(
            ["git", "init"],
            cwd=project_dir,
            check=False,
            capture_output=True,
            text=True,
        )
    except Exception:
        # no romper flujo
        pass


def git_get_origin(project_dir: str) -> str:
    """
    Devuelve URL del remoto origin si existe, si no string vacío.
    """
    try:
        r = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=project_dir,
            capture_output=True,
            text=True,
        )
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return ""


def git_try_create_remote_with_gh(project_dir: str, project_name: str) -> str:
    """
    Intenta:
        gh repo create <project_name> --public --source . --remote origin --push --confirm

    Requiere:
        - gh instalado
        - gh auth status OK

    Devuelve:
        URL del remoto origin si éxito, si no string vacío.
    """

    # comprobar gh auth
    try:
        chk = subprocess.run(
            ["gh", "auth", "status"],
            cwd=project_dir,
            capture_output=True,
            text=True,
        )
        if chk.returncode != 0:
            return ""
    except Exception:
        return ""

    # crear repo
    try:
        cmd = [
            "gh",
            "repo",
            "create",
            project_name,
            "--public",
            "--source",
            ".",
            "--remote",
            "origin",
            "--push",
            "--confirm",
        ]
        r = subprocess.run(
            cmd,
            cwd=project_dir,
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            return ""
    except Exception:
        return ""

    return git_get_origin(project_dir)
