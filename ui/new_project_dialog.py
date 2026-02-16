# C:\Users\Usuario\Desktop\proyectos\yvolo\ui\new_project_dialog.py
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional


class NewProjectDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.title("Nuevo Proyecto")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.project_name: Optional[str] = None
        self.project_type: Optional[str] = None
        self.open_vscode: bool = False
        self.tasks: List[str] = []

        self._build_ui()

    def _build_ui(self) -> None:
        pad = {"padx": 10, "pady": 5}

        ttk.Label(self, text="Nombre del proyecto:").grid(row=0, column=0, sticky="w", **pad)
        self.entry_name = ttk.Entry(self, width=40)
        self.entry_name.grid(row=1, column=0, **pad)

        ttk.Label(self, text="Tipo de proyecto:").grid(row=2, column=0, sticky="w", **pad)
        self.combo_type = ttk.Combobox(
            self,
            values=["Vacío", "Python", "Flask"],
            state="readonly",
            width=37,
        )
        self.combo_type.current(0)
        self.combo_type.grid(row=3, column=0, **pad)

        self.var_vscode = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            self,
            text="Abrir en VSCode",
            variable=self.var_vscode,
        ).grid(row=4, column=0, sticky="w", **pad)

        ttk.Label(self, text="¿Qué queremos hacer? (una tarea por línea)").grid(
            row=5, column=0, sticky="w", **pad
        )

        self.text_tasks = tk.Text(self, width=40, height=6)
        self.text_tasks.grid(row=6, column=0, **pad)

        frame_buttons = ttk.Frame(self)
        frame_buttons.grid(row=7, column=0, pady=10)

        ttk.Button(frame_buttons, text="Cancelar", command=self._cancel).pack(
            side="left", padx=5
        )
        ttk.Button(frame_buttons, text="Crear", command=self._confirm).pack(
            side="left", padx=5
        )

    def _cancel(self) -> None:
        self.destroy()

    def _confirm(self) -> None:
        name = self.entry_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Debes indicar un nombre de proyecto.")
            return

        self.project_name = name
        self.project_type = self.combo_type.get()
        self.open_vscode = self.var_vscode.get()

        raw_tasks = self.text_tasks.get("1.0", "end").strip()
        if raw_tasks:
            self.tasks = [line.strip() for line in raw_tasks.splitlines() if line.strip()]
        else:
            self.tasks = []

        self.destroy()
