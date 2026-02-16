# C:\Users\Usuario\Desktop\proyectos\yvolo\tests\test_ui_main.py
import os
import unittest
import tkinter as tk
from unittest.mock import patch

from ui.app import YvoloApp
from core.config import load_config, DEFAULT_CONFIG


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "settings.json")


class TestYvoloApp(unittest.TestCase):
    def setUp(self):
        self._backup_config = None
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "rb") as f:
                self._backup_config = f.read()

        self.config = load_config()
        self.app = YvoloApp()
        self.app.update()

    def tearDown(self):
        try:
            self.app.destroy()
        except Exception:
            pass

        if self._backup_config is not None:
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, "wb") as f:
                f.write(self._backup_config)

    def _find_buttons(self, root_widget):
        buttons = []

        def walk(w):
            # ttk.Button no es tk.Button, así que recogemos ambos
            if isinstance(w, (tk.Button, tk.Widget)) and w.winfo_class() in ("TButton", "Button"):
                try:
                    # Confirmar que tiene texto (evita widgets raros)
                    _ = w.cget("text")
                    buttons.append(w)
                except Exception:
                    pass
            for child in w.winfo_children():
                walk(child)

        walk(root_widget)
        return buttons

    def test_title_from_config(self):
        self.assertEqual(self.app.title(), self.config["app_name"])

    def test_not_resizable(self):
        width_resizable, height_resizable = self.app.resizable()
        self.assertFalse(width_resizable)
        self.assertFalse(height_resizable)

    def test_buttons_match_labels(self):
        buttons = self._find_buttons(self.app)
        # 4 botones
        self.assertEqual(len(buttons), 4)

        texts = sorted([b.cget("text") for b in buttons])
        expected = sorted(
            [
                self.config["labels"]["btn_open_chat"],
                self.config["labels"]["btn_close_chat"],
                self.config["labels"]["btn_process_ideas"],
                self.config["labels"].get("btn_new_project", "Nuevo Proyecto"),
            ]
        )
        self.assertEqual(texts, expected)

    def test_fallback_on_missing_config(self):
        temp_path = None
        app = None
        try:
            if os.path.exists(CONFIG_PATH):
                temp_path = CONFIG_PATH + ".bak"
                os.rename(CONFIG_PATH, temp_path)

            config = load_config()
            app = YvoloApp()
            app.update()

            self.assertEqual(app.title(), DEFAULT_CONFIG["app_name"])

            buttons = self._find_buttons(app)
            self.assertEqual(len(buttons), 4)

            texts = sorted([b.cget("text") for b in buttons])
            expected = sorted(
                [
                    DEFAULT_CONFIG["labels"]["btn_open_chat"],
                    DEFAULT_CONFIG["labels"]["btn_close_chat"],
                    DEFAULT_CONFIG["labels"]["btn_process_ideas"],
                    DEFAULT_CONFIG["labels"].get("btn_new_project", "Nuevo Proyecto"),
                ]
            )
            self.assertEqual(texts, expected)
        finally:
            if app is not None:
                try:
                    app.destroy()
                except Exception:
                    pass
            if temp_path and os.path.exists(temp_path):
                os.rename(temp_path, CONFIG_PATH)

    def test_nuevo_proyecto_button_exists_and_is_safe_to_invoke(self):
        buttons = self._find_buttons(self.app)
        label = self.config["labels"].get("btn_new_project", "Nuevo Proyecto")

        btn = None
        for b in buttons:
            if b.cget("text") == label:
                btn = b
                break
        self.assertIsNotNone(btn, "No se encontró el botón Nuevo Proyecto")

        # No abrir diálogo real ni tocar disco
        with patch.object(self.app, "_open_new_project_dialog", return_value=None) as mocked:
            btn.configure(command=self.app._open_new_project_dialog)
            btn.invoke()
            self.assertTrue(mocked.called)

    @patch("ui.app.subprocess.run")
    def test_open_chat_copies_files_calls_powershell(self, mock_run):
        # Crear archivos mínimos en root si faltan (test aislado)
        hoja_path = os.path.join(BASE_DIR, "hoja_de_ruta.txt")
        promp_path = os.path.join(BASE_DIR, "promp_maestro.txt")

        for p in [hoja_path, promp_path]:
            if not os.path.exists(p):
                with open(p, "w", encoding="utf-8") as f:
                    f.write("test")

        with patch("ui.app.messagebox.showinfo"), patch("ui.app.messagebox.showwarning"), patch("ui.app.messagebox.showerror"):
            self.app._open_chat()

        self.assertTrue(mock_run.called)
        args, _kwargs = mock_run.call_args
        cmd = args[0]
        self.assertIn("SetFileDropList", cmd[-1])
        self.assertIn(os.path.abspath(hoja_path), cmd[-1])
        self.assertIn(os.path.abspath(promp_path), cmd[-1])

    @patch("ui.app.subprocess.run")
    def test_open_chat_button_invoke_triggers_copy(self, mock_run):
        target_text = self.config["labels"]["btn_open_chat"]
        buttons = self._find_buttons(self.app)

        open_button = None
        for b in buttons:
            if b.cget("text") == target_text:
                open_button = b
                break

        self.assertIsNotNone(open_button, "No se encontró el botón Abrir Chat")

        with patch("ui.app.messagebox.showinfo"), patch("ui.app.messagebox.showwarning"), patch("ui.app.messagebox.showerror"):
            open_button.invoke()

        self.assertTrue(mock_run.called)
        args, _kwargs = mock_run.call_args
        cmd = args[0]
        self.assertIn("SetFileDropList", cmd[-1])


if __name__ == "__main__":
    unittest.main()
