# C:\Users\Usuario\Desktop\proyectos\yvolo\core\project_creator.py
from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from .paths import projects_base_dir, yvolo_root_file
from .git_utils import (
    git_init_if_needed,
    git_get_origin,
    git_try_create_remote_with_gh,
)


def sanitize_project_name(name: str) -> str:
    name = (name or "").strip()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^A-Za-z0-9_\-\.]", "", name)
    name = name.strip("._-")
    return name


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _format_tasks(tasks: List[str]) -> str:
    lines: List[str] = []
    for t in tasks:
        t = (t or "").strip()
        if not t:
            continue
        lines.append(f"- Descripción: {t}")
        lines.append("  Critica: No critica")
        lines.append("  Implementada: No implementada")
        lines.append("  Dependencias: Ninguna")
        lines.append("")
    return "\n".join(lines)


def _apply_hoja_template(
    template_text: str,
    project_name: str,
    repo_url: str,
    backup_value: str,
    tasks: List[str],
) -> str:
    text = template_text.replace("\r\n", "\n")

    # Insert tasks after #Tareas
    if "#Tareas" not in text:
        raise ValueError("La plantilla hoja_de_ruta.txt no contiene #Tareas")

    parts = text.split("#Tareas", 1)
    head = parts[0] + "#Tareas\n"
    rest = parts[1].lstrip("\n")

    tasks_block = _format_tasks(tasks)
    if tasks_block:
        text = head + tasks_block + "\n" + rest
    else:
        text = head + rest

    # Replace ProyectoInfo fields
    def replace_line(prefix: str, value: str, s: str) -> str:
        pattern = rf"(?m)^{re.escape(prefix)}\s*.*$"
        if re.search(pattern, s):
            return re.sub(pattern, f"{prefix} {value}".rstrip(), s)
        return s

    text = replace_line("repo_git:", repo_url, text)
    text = replace_line("name_project:", project_name, text)
    text = replace_line("backup:", backup_value, text)

    return text


def create_new_project(
    project_name: str,
    project_type: str,
    open_vscode: bool,
    tasks: List[str],
) -> Tuple[bool, str]:
    name = sanitize_project_name(project_name)
    if not name:
        return False, "Nombre de proyecto inválido."

    base = projects_base_dir()
    project_dir = base / name

    if project_dir.exists():
        return False, f"Ya existe: {project_dir}"

    try:
        project_dir.mkdir(parents=True, exist_ok=False)

        # Copiar promp_maestro exacto
        promp_template = yvolo_root_file("promp_maestro.txt")
        if not promp_template.exists():
            return False, "No existe promp_maestro.txt en raíz de yvolo."

        promp_content = promp_template.read_text(encoding="utf-8")
        _write_text(project_dir / "promp_maestro.txt", promp_content)

        # Generar hoja_de_ruta desde plantilla base
        hoja_template_path = yvolo_root_file("hoja_de_ruta.txt")
        if not hoja_template_path.exists():
            return False, "No existe hoja_de_ruta.txt en raíz de yvolo."

        hoja_template = hoja_template_path.read_text(encoding="utf-8")

        backup_value = f"Desktop\\backups\\backup_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

        # Git
        git_init_if_needed(str(project_dir))

        repo_url = git_get_origin(str(project_dir))
        if not repo_url:
            repo_url = git_try_create_remote_with_gh(str(project_dir), name)

        hoja_final = _apply_hoja_template(
            hoja_template,
            project_name=name,
            repo_url=repo_url,
            backup_value=backup_value,
            tasks=tasks,
        )

        _write_text(project_dir / "hoja_de_ruta.txt", hoja_final)

        # Scaffold mínimo según tipo (sin tocar plantillas)
        if project_type == "Python":
            (project_dir / "src").mkdir(exist_ok=True)
            _write_text(
                project_dir / "src" / "main.py",
                f"def main():\n    print('Hola desde {name}')\n\nif __name__ == '__main__':\n    main()\n",
            )
        elif project_type == "Flask":
            (project_dir / "templates").mkdir(exist_ok=True)
            (project_dir / "static").mkdir(exist_ok=True)
            _write_text(
                project_dir / "app.py",
                "from flask import Flask\napp = Flask(__name__)\n\n@app.get('/')\ndef home():\n    return 'Hola'\n\nif __name__ == '__main__':\n    app.run(debug=True)\n",
            )

        # VSCode
        if open_vscode:
            try:
                import subprocess
                subprocess.run(["code", "."], cwd=str(project_dir), check=False)
            except Exception:
                pass

        return True, f"Proyecto creado: {project_dir}"

    except Exception as e:
        return False, f"Error creando proyecto: {e}"
