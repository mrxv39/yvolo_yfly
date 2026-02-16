# C:\Users\Usuario\Desktop\proyectos\yvolo\ui\app.py
from __future__ import annotations

import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

from core.config import load_config
from core.paths import yvolo_root_file
from core.project_creator import create_new_project
from ui.new_project_dialog import NewProjectDialog


class YvoloApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.config_data = load_config()
        self.title(self.config_data.get("app_name", "yvolo"))
        self.resizable(False, False)

        self._build_ui()

    # =========================
    # UI
    # =========================

    def _build_ui(self) -> None:
        pad = {"padx": 10, "pady": 5}

        labels = self.config_data.get("labels", {})

        ttk.Button(
            self,
            text=labels.get("btn_open_chat", "Abrir Chat"),
            command=self._open_chat,
        ).grid(row=0, column=0, **pad)

        ttk.Button(
            self,
            text=labels.get("btn_close_chat", "Cerrar Chat"),
            command=self.destroy,
        ).grid(row=1, column=0, **pad)

        ttk.Button(
            self,
            text=labels.get("btn_process_ideas", "Procesar Ideas"),
            command=self._process_ideas_placeholder,
        ).grid(row=2, column=0, **pad)

        ttk.Button(
            self,
            text=labels.get("btn_new_project", "Nuevo Proyecto"),
            command=self._open_new_project_dialog,
        ).grid(row=3, column=0, **pad)

    # =========================
    # Actions
    # =========================

    def _process_ideas_placeholder(self) -> None:
        messagebox.showinfo("Info", "Funcionalidad no implementada aún.")

    def _open_new_project_dialog(self) -> None:
        dialog = NewProjectDialog(self)
        self.wait_window(dialog)

        if dialog.project_name:
            ok, msg = create_new_project(
                project_name=dialog.project_name,
                project_type=dialog.project_type or "Vacío",
                open_vscode=dialog.open_vscode,
                tasks=dialog.tasks,
            )

            if ok:
                messagebox.showinfo("Éxito", msg)
            else:
                messagebox.showerror("Error", msg)

    def _open_chat(self) -> None:
        """
        Mantiene lógica original:
        Copia hoja_de_ruta.txt y promp_maestro.txt al portapapeles como FileDropList.
        """

        hoja = yvolo_root_file("hoja_de_ruta.txt")
        promp = yvolo_root_file("promp_maestro.txt")

        files = []
        if hoja.exists():
            files.append(str(hoja))
        if promp.exists():
            files.append(str(promp))

        if not files:
            messagebox.showwarning("WARN", "No se encontraron archivos para copiar.")
            return

        try:
            ps_command = (
                "Add-Type -AssemblyName System.Windows.Forms;"
                "$files = New-Object System.Collections.Specialized.StringCollection;"
            )

            for f in files:
                ps_command += f'$files.Add("{f}");'

            ps_command += "[System.Windows.Forms.Clipboard]::SetFileDropList($files);"

            subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_command],
                check=False,
                capture_output=True,
                text=True,
            )

            messagebox.showinfo("OK", "Archivos copiados al portapapeles.")

        except Exception:
            messagebox.showerror("Error", "No se pudo copiar al portapapeles.")
