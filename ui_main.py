port tkinter as tk
import json
import os

DEFAULT_CONFIG = {
    "app_name": "yvolo",
    "labels": {
        "btn_open_chat": "Abrir Chat",
        "btn_close_chat": "Cerrar Chat",
        "btn_process_ideas": "Procesar Ideas"
    }
}

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config", "settings.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Ensure required keys
        app_name = data.get("app_name", DEFAULT_CONFIG["app_name"])
        labels = data.get("labels", DEFAULT_CONFIG["labels"])
        if not isinstance(labels, dict):
            raise ValueError
        return {"app_name": app_name, "labels": labels}
    except Exception as e:
        print(f"WARN: No se pudo cargar config/settings.json, usando valores por defecto. ({e})")
        return DEFAULT_CONFIG


import subprocess

class YvoloApp(tk.Tk):
    def __init__(self, config=None):
        super().__init__()
        if config is None:
            config = load_config()
        self.config_data = config
        self.title(config["app_name"])
        self.resizable(False, False)
        window_width = 400
        window_height = 300
        # Center the window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Create a frame to center buttons vertically
        frame = tk.Frame(self)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        button_pad = {'padx': 20, 'pady': 10}
        labels = config["labels"]

        btn_abrir = tk.Button(frame, text=labels.get("btn_open_chat", DEFAULT_CONFIG["labels"]["btn_open_chat"]), width=20, command=self.open_chat)
        btn_abrir.pack(**button_pad)

        btn_cerrar = tk.Button(frame, text=labels.get("btn_close_chat", DEFAULT_CONFIG["labels"]["btn_close_chat"]), width=20, command=lambda: print("Cerrar Chat clicked"))
        btn_cerrar.pack(**button_pad)

        btn_procesar = tk.Button(frame, text=labels.get("btn_process_ideas", DEFAULT_CONFIG["labels"]["btn_process_ideas"]), width=20, command=lambda: print("Procesar Ideas clicked"))
        btn_procesar.pack(**button_pad)

    def get_backup_path(self) -> str:
        hoja_path = os.path.join(os.path.dirname(__file__), "hoja_de_ruta.txt")
        try:
            with open(hoja_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("backup:"):
                        return line.split("backup:", 1)[1].strip()
        except Exception as e:
            print(f"WARN: No se pudo leer hoja_de_ruta.txt para backup: {e}")
        return ""

    def copy_files_to_clipboard(self, paths: list[str]) -> None:
        existing = [os.path.abspath(p) for p in paths if os.path.isfile(p)]
        if not existing:
            print("WARN: No files to copy")
            return
        # PowerShell script for SetFileDropList
        try:
            script_lines = [
                "Add-Type -AssemblyName System.Windows.Forms;",
                "$sc = New-Object System.Collections.Specialized.StringCollection;"
            ]
            for p in existing:
                script_lines.append(f"$sc.Add('{p}');")
            script_lines.append("[System.Windows.Forms.Clipboard]::SetFileDropList($sc);")
            script = ' '.join(script_lines)
            cmd = ["powershell", "-Command", script]
            subprocess.run(cmd, check=True)
            print("Archivos copiados al portapapeles")
        except Exception as e:
            print(f"WARN: No se pudo copiar archivos al portapapeles: {e}")

    def open_chat(self):
        # Build list: backup, hoja_de_ruta.txt, promp_maestro.txt
        backup_path = self.get_backup_path()
        hoja_path = os.path.join(os.path.dirname(__file__), "hoja_de_ruta.txt")
        promp_path = os.path.join(os.path.dirname(__file__), "promp_maestro.txt")
        files = [backup_path, hoja_path, promp_path]
        self.copy_files_to_clipboard(files)

if __name__ == "__main__":
    app = YvoloApp()
    app.mainloop()
