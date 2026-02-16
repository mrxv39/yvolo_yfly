
# C:\Users\Usuario\Desktop\proyectos\yvolo\ui_main.py
from __future__ import annotations

import argparse
import sys

from core.project_creator import create_new_project
from ui.app import YvoloApp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="yvolo")
    parser.add_argument("--create", type=str, help="Nombre del proyecto")
    parser.add_argument("--type", type=str, default="Vacío", help="Tipo: Vacío, Python, Flask")
    parser.add_argument("--open-vscode", type=int, default=1, help="1 = abrir VSCode, 0 = no")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Modo CLI
    if args.create:
        tasks = []  # CLI no pide tareas por ahora
        ok, msg = create_new_project(
            project_name=args.create,
            project_type=args.type,
            open_vscode=bool(args.open_vscode),
            tasks=tasks,
        )

        if ok:
            print(msg)
            sys.exit(0)
        else:
            print(msg)
            sys.exit(1)

    # Modo UI
    app = YvoloApp()
    app.mainloop()


if __name__ == "__main__":
    main()
