# C:\Users\Usuario\Desktop\proyectos\yvolo\ui_main.py
import argparse
import json
import os
import re
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk


DEFAULT_CONFIG = {
    "app_name": "yvolo",
    "language": "es",
    "labels": {
        "btn_open_chat": "Abrir Chat",
        "btn_close_chat": "Cerrar Chat",
        "btn_process_ideas": "Procesar Ideas",
        "btn_new_project": "Nuevo Proyecto",
    },
}


# =========================
# Runtime paths (source vs exe)
# =========================

def is_frozen_exe() -> bool:
    return bool(getattr(sys, "frozen", False))


def app_dir() -> Path:
    """
    - Source: carpeta del archivo ui_main.py (raíz del repo)
    - EXE: carpeta donde vive yvolo.exe
    """
    if is_frozen_exe():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def appdata_dir() -> Path:
    """
    %APPDATA%\yvolo (Windows).
    Fallback: ~/.yvolo
    """
    base = os.environ.get("APPDATA")
    if base:
        return Path(base) / "yvolo"
    return Path.home() / ".yvolo"


# =========================
# Config
# =========================

def _ensure_labels_key(cfg: dict) -> dict:
    if "labels" not in cfg or not isinstance(cfg["labels"], dict):
        cfg["labels"] = dict(DEFAULT_CONFIG["labels"])
    # asegurar key nueva
    if "btn_new_project" not in cfg["labels"]:
        cfg["labels"]["btn_new_project"] = DEFAULT_CONFIG["labels"]["btn_new_project"]
    return cfg


def load_config() -> dict:
    """
    MODO SOURCE (tests/dev):
      - Solo lee: <repo>\config\settings.json
      - Si falta o es inválido => DEFAULT_CONFIG
      (NO usa APPDATA para evitar no-determinismo en tests)

    MODO EXE (producto):
      Prioridad:
        1) <exe_dir>\config\settings.json   (portable)
        2) <exe_dir>\settings.json          (portable alt)
        3) %APPDATA%\yvolo\settings.json    (usuario)
        4) DEFAULT_CONFIG
    """
    if not is_frozen_exe():
        cfg_path = app_dir() / "config" / "settings.json"
        try:
            with cfg_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("settings.json debe ser un objeto JSON")
            data.setdefault("app_name", DEFAULT_CONFIG["app_name"])
            data = _ensure_labels_key(data)
            return data
        except Exception as e:
            print(f"WARN: No se pudo cargar config/settings.json, usando valores por defecto. ({e})")
            return dict(DEFAULT_CONFIG)

    # EXE mode
    portable_1 = app_dir() / "config" / "settings.json"
    portable_2 = app_dir() / "settings.json"
    user_cfg = appdata_dir() / "settings.json"

    for cfg_path in (portable_1, portable_2, user_cfg):
        try:
            if cfg_path.exists():
                with cfg_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, dict):
                    raise ValueError("settings.json debe ser un objeto JSON")
                data.setdefault("app_name", DEFAULT_CONFIG["app_name"])
                data = _ensure_labels_key(data)
                return data
        except Exception as e:
            print(f"WARN: No se pudo cargar config: {cfg_path} ({e})")

    return dict(DEFAULT_CONFIG)


# =========================
# Project creation (works in exe)
# =========================

def _sanitize_project_name(name: str) -> str:
    name = (name or "").strip()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^A-Za-z0-9_\-\.]", "", name)
    name = name.strip("._-")
    return name


def _projects_base_dir() -> str:
    return os.path.join(os.path.expanduser("~"), "Desktop", "proyectos")


def _write_text(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _git_init(project_dir: str) -> None:
    try:
        subprocess.run(["git", "init"], cwd=project_dir, check=False, capture_output=True, text=True)
    except Exception:
        pass


def _maybe_open_vscode(project_dir: str) -> None:
    try:
        subprocess.run(["code", "."], cwd=project_dir, check=False, capture_output=True, text=True)
    except Exception:
        pass


def _scaffold_common(project_dir: str, project_name: str) -> None:
    _write_text(
        os.path.join(project_dir, "README.md"),
        f"# {project_name}\n\nProyecto creado desde yvolo.\n",
    )
    _write_text(
        os.path.join(project_dir, ".gitignore"),
        "\n".join(
            [
                "__pycache__/",
                "*.pyc",
                ".venv/",
                "venv/",
                ".env",
                ".DS_Store",
                ".idea/",
                ".vscode/",
                "dist/",
                "build/",
                "",
            ]
        ),
    )
    _write_text(
        os.path.join(project_dir, "hoja_de_ruta.txt"),
        "\n".join(
            [
                "#ProyectoInfo",
                "--------------------------------------------------",
                f"name_project: {project_name}",
                "repo_git: ",
                "backup: ",
                "--------------------------------------------------",
                "",
                "#Sprints",
                "- Sprint 1 (1:30):",
                "  - [ ] Definir alcance",
                "  - [ ] Estructura base",
                "  - [ ] Primer commit",
                "",
            ]
        ),
    )
    _write_text(
        os.path.join(project_dir, "promp_maestro.txt"),
        "\n".join(
            [
                f"Proyecto: {project_name}",
                "",
                "Objetivo:",
                "- Describe aquí qué quieres construir.",
                "",
                "Reglas:",
                "- Mantenerlo simple.",
                "- Commits pequeños y limpios.",
                "",
            ]
        ),
    )


def _scaffold_empty(project_dir: str, project_name: str) -> None:
    _scaffold_common(project_dir, project_name)
    src_dir = os.path.join(project_dir, "src")
    os.makedirs(src_dir, exist_ok=True)
    _write_text(os.path.join(src_dir, "main.txt"), "Proyecto vacío (placeholder).\n")


def _scaffold_python(project_dir: str, project_name: str) -> None:
    _scaffold_common(project_dir, project_name)
    src_dir = os.path.join(project_dir, "src")
    os.makedirs(src_dir, exist_ok=True)
    _write_text(
        os.path.join(src_dir, "main.py"),
        "\n".join(
            [
                "def main() -> None:",
                f"    print('Hola desde {project_name}')",
                "",
                "if __name__ == '__main__':",
                "    main()",
                "",
            ]
        ),
    )
    _write_text(os.path.join(project_dir, "requirements.txt"), "# añade dependencias aquí\n")


def _scaffold_flask(project_dir: str, project_name: str) -> None:
    _scaffold_common(project_dir, project_name)

    os.makedirs(os.path.join(project_dir, "templates"), exist_ok=True)
    os.makedirs(os.path.join(project_dir, "static"), exist_ok=True)

    _write_text(
        os.path.join(project_dir, "app.py"),
        "\n".join(
            [
                "from flask import Flask, render_template",
                "",
                "app = Flask(__name__)",
                "",
                "@app.get('/')",
                "def home():",
                "    return render_template('index.html')",
                "",
                "if __name__ == '__main__':",
                "    app.run(debug=True)",
                "",
            ]
        ),
    )
    _write_text(
        os.path.join(project_dir, "templates", "index.html"),
        "\n".join(
            [
                "<!doctype html>",
                "<html lang='es'>",
                "<head>",
                "  <meta charset='utf-8'/>",
                f"  <title>{project_name}</title>",
                "</head>",
                "<body>",
                f"  <h1>{project_name}</h1>",
                "  <p>Proyecto Flask creado desde yvolo.</p>",
                "</body>",
                "</html>",
                "",
            ]
        ),
    )
    _write_text(os.path.join(project_dir, "requirements.txt"), "flask\n")


def create_new_project(project_name: str, project_type: str, open_vscode: bool) -> tuple[bool, str]:
    name = _sanitize_project_name(project_name)
    if not name:
        return False, "Nombre de proyecto inválido."

    base = _projects_base_dir()
    project_dir = os.path.join(base, name)

    if os.path.exists(project_dir):
        return False, f"Ya existe: {project_dir}"

    try:
        os.makedirs(project_dir, exist_ok=False)

        if project_type == "Python":
            _scaffold_python(project_dir, name)
        elif project_type == "Flask":
            _scaffold_flask(project_dir, name)
        else:
            _scaffold_empty(project_dir, name)

        _git_init(project_dir)

        if open_vscode:
            _maybe_open_vscode(project_dir)

        return True, f"Proyecto creado: {project_dir}"
    except Exception as e:
        return False, f"Error creando proyecto: {e}"


# =========================
# UI - New Project Dialog
# =========================

class NewProjectDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.title("Nuevo Proyecto")
        self.resizable(False, False)
        self.result = None

        self.transient(parent)
        self.grab_set()

        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Nombre del proyecto:").grid(row=0, column=0, sticky="w", padx=4, pady=6)
        self.name_var = tk.StringVar(value="")
        self.entry_name = ttk.Entry(frm, textvariable=self.name_var, width=34)
        self.entry_name.grid(row=0, column=1, sticky="ew", padx=4, pady=6)

        ttk.Label(frm, text="Tipo:").grid(row=1, column=0, sticky="w", padx=4, pady=6)
        self.type_var = tk.StringVar(value="Vacío")
        self.combo_type = ttk.Combobox(
            frm,
            textvariable=self.type_var,
            values=["Vacío", "Python", "Flask"],
            state="readonly",
            width=31,
        )
        self.combo_type.grid(row=1, column=1, sticky="ew", padx=4, pady=6)

        self.open_vscode_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, text="Abrir VS Code al crear", variable=self.open_vscode_var).grid(
            row=2, column=0, columnspan=2, sticky="w", padx=4, pady=6
        )

        btns = ttk.Frame(frm)
        btns.grid(row=3, column=0, columnspan=2, sticky="e", padx=4, pady=(10, 0))

        ttk.Button(btns, text="Cancelar", command=self._cancel).pack(side="right", padx=(6, 0))
        ttk.Button(btns, text="Crear", command=self._create).pack(side="right")

        frm.columnconfigure(1, weight=1)

        self.bind("<Return>", lambda _e: self._create())
        self.bind("<Escape>", lambda _e: self._cancel())

        self.entry_name.focus_set()

    def _create(self):
        name = self.name_var.get().strip()
        if not _sanitize_project_name(name):
            messagebox.showwarning("Nuevo Proyecto", "Nombre inválido. Usa letras/números/._-")
            return

        self.result = {
            "name": name,
            "type": (self.type_var.get() or "Vacío").strip(),
            "open_vscode": bool(self.open_vscode_var.get()),
        }
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()


# =========================
# UI - Main App
# =========================

class YvoloApp(tk.Tk):
    def __init__(self, config=None):
        super().__init__()
        if config is None:
            config = load_config()
        self.config_data = config

        self.title(config.get("app_name", DEFAULT_CONFIG["app_name"]))
        self.resizable(False, False)

        window_width = 400
        window_height = 300

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        frame = tk.Frame(self)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        labels = config.get("labels", DEFAULT_CONFIG["labels"])
        if not isinstance(labels, dict):
            labels = dict(DEFAULT_CONFIG["labels"])

        # asegurar label nuevo
        if "btn_new_project" not in labels:
            labels["btn_new_project"] = DEFAULT_CONFIG["labels"]["btn_new_project"]

        self.btn_open_chat = tk.Button(
            frame,
            text=labels.get("btn_open_chat", DEFAULT_CONFIG["labels"]["btn_open_chat"]),
            width=20,
            command=self.open_chat,
        )
        self.btn_close_chat = tk.Button(
            frame,
            text=labels.get("btn_close_chat", DEFAULT_CONFIG["labels"]["btn_close_chat"]),
            width=20,
            command=lambda: self.set_status("Cerrar Chat (placeholder)."),
        )
        self.btn_process_ideas = tk.Button(
            frame,
            text=labels.get("btn_process_ideas", DEFAULT_CONFIG["labels"]["btn_process_ideas"]),
            width=20,
            command=lambda: self.set_status("Procesar Ideas (placeholder)."),
        )

        self.btn_new_project = tk.Button(
            frame,
            text=labels.get("btn_new_project", DEFAULT_CONFIG["labels"]["btn_new_project"]),
            width=20,
            command=self.open_new_project_dialog,
        )

        self.btn_open_chat.grid(row=0, column=0, padx=10, pady=10)
        self.btn_close_chat.grid(row=0, column=1, padx=10, pady=10)
        self.btn_process_ideas.grid(row=1, column=0, padx=10, pady=10)
        self.btn_new_project.grid(row=1, column=1, padx=10, pady=10)

        self.status_var = tk.StringVar(value="Listo.")
        self.status_label = tk.Label(self, textvariable=self.status_var, anchor="w", fg="gray")
        self.status_label.pack(side="bottom", fill="x", padx=5, pady=2)

    def set_status(self, txt: str) -> None:
        try:
            self.status_var.set(txt)
        except Exception:
            pass

    # --------- Open Chat: FileDropList ---------

    def _yvolo_data_file(self, filename: str) -> Path:
        """
        Source: archivos en el repo (misma carpeta que ui_main.py)
        EXE: archivos en %APPDATA%\yvolo\<filename>
        """
        if not is_frozen_exe():
            return app_dir() / filename

        d = appdata_dir()
        d.mkdir(parents=True, exist_ok=True)
        return d / filename

    def get_backup_path(self) -> str:
        hoja_path = self._yvolo_data_file("hoja_de_ruta.txt")
        try:
            if hoja_path.exists():
                with hoja_path.open("r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip().lower().startswith("backup:"):
                            return line.split("backup:", 1)[1].strip()
        except Exception as e:
            print(f"WARN: No se pudo leer hoja_de_ruta.txt para backup: {e}")
        return ""

    def copy_files_to_clipboard(self, paths: list[str]) -> None:
        existing = [os.path.abspath(p) for p in paths if p and os.path.isfile(p)]
        if not existing:
            print("WARN: No files to copy")
            self.set_status("WARN: No hay archivos para copiar.")
            return

        try:
            script_lines = [
                "Add-Type -AssemblyName System.Windows.Forms;",
                "$sc = New-Object System.Collections.Specialized.StringCollection;",
            ]
            for p in existing:
                # se usa comilla simple en PS: duplicar ' para escapar
                p_escaped = p.replace("'", "''")
                script_lines.append(f"$null = $sc.Add('{p_escaped}');")
            script_lines.append("[System.Windows.Forms.Clipboard]::SetFileDropList($sc);")

            script = " ".join(script_lines)
            cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script]
            subprocess.run(cmd, check=False, capture_output=True, text=True)
            print("Archivos copiados al portapapeles")
            self.set_status("Archivos copiados (FileDropList).")
        except Exception as e:
            print(f"WARN: No se pudo copiar archivos al portapapeles: {e}")
            self.set_status("WARN: fallo copiando archivos.")

    def open_chat(self):
        # asegurar archivos mínimos en EXE (solo si faltan)
        if is_frozen_exe():
            hoja = self._yvolo_data_file("hoja_de_ruta.txt")
            if not hoja.exists():
                _write_text(
                    str(hoja),
                    "\n".join(
                        [
                            "#ProyectoInfo",
                            "--------------------------------------------------",
                            "repo_git: ",
                            "name_project: yvolo",
                            "backup: ",
                            "--------------------------------------------------",
                            "",
                        ]
                    ),
                )
            promp = self._yvolo_data_file("promp_maestro.txt")
            if not promp.exists():
                _write_text(str(promp), "yvolo\n\nPrompt maestro (placeholder).\n")

        backup_path = self.get_backup_path()
        hoja_path = str(self._yvolo_data_file("hoja_de_ruta.txt"))
        promp_path = str(self._yvolo_data_file("promp_maestro.txt"))

        files = [backup_path, hoja_path, promp_path]
        self.copy_files_to_clipboard(files)

    # --------- New Project ---------

    def open_new_project_dialog(self):
        dlg = NewProjectDialog(self)
        self.wait_window(dlg)

        if not dlg.result:
            self.set_status("Nuevo Proyecto: cancelado.")
            return

        ok, msg = create_new_project(
            project_name=dlg.result["name"],
            project_type=dlg.result["type"],
            open_vscode=dlg.result["open_vscode"],
        )

        if ok:
            self.set_status(msg)
            messagebox.showinfo("yvolo", msg)
        else:
            self.set_status(f"WARN: {msg}")
            messagebox.showwarning("yvolo", msg)


# =========================
# CLI (works in exe)
# =========================

def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(add_help=True)
    p.add_argument("--create", dest="create", default="", help="Crea un proyecto (sin abrir UI)")
    p.add_argument("--type", dest="ptype", default="Vacío", choices=["Vacío", "Python", "Flask"], help="Tipo de proyecto")
    p.add_argument("--open-vscode", dest="open_vscode", default="0", choices=["0", "1"], help="Abrir VS Code (1/0)")
    return p.parse_args(argv)


def main() -> int:
    args = parse_args(sys.argv[1:])

    # CLI headless
    if args.create:
        ok, msg = create_new_project(
            project_name=args.create,
            project_type=args.ptype,
            open_vscode=(args.open_vscode == "1"),
        )
        print(msg)
        return 0 if ok else 1

    # UI
    cfg = load_config()
    app = YvoloApp(config=cfg)
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
