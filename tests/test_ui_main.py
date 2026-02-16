# tests/test_ui_main.py

import os
import unittest
import tkinter as tk
from unittest.mock import patch

from ui_main import YvoloApp, load_config, DEFAULT_CONFIG


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "settings.json")


class TestYvoloApp(unittest.TestCase):

    def setUp(self):
        # Guardar config original si existe
        self._backup_config = None
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "rb") as f:
                self._backup_config = f.read()

        self.config = load_config()
        self.app = YvoloApp(config=self.config)
        self.app.update()

    def tearDown(self):
        try:
            self.app.destroy()
        except Exception:
            pass

        # Restaurar config original si existía
        if self._backup_config is not None:
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, "wb") as f:
                f.write(self._backup_config)

    def _find_buttons(self, root_widget):
        buttons = []

        def walk(w):
            if isinstance(w, tk.Button):
                buttons.append(w)
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
        self.assertEqual(len(buttons), 3)

        texts = sorted([b.cget("text") for b in buttons])
        expected = sorted([
            self.config["labels"]["btn_open_chat"],
            self.config["labels"]["btn_close_chat"],
            self.config["labels"]["btn_process_ideas"],
        ])

        self.assertEqual(texts, expected)

    def test_fallback_on_missing_config(self):
        if os.path.exists(CONFIG_PATH):
            temp_path = CONFIG_PATH + ".bak"
            os.rename(CONFIG_PATH, temp_path)
        else:
            temp_path = None

        try:
            config = load_config()
            app = YvoloApp(config=config)
            app.update()

            self.assertEqual(app.title(), DEFAULT_CONFIG["app_name"])

            buttons = self._find_buttons(app)
            self.assertEqual(len(buttons), 3)

            texts = sorted([b.cget("text") for b in buttons])
            expected = sorted([
                DEFAULT_CONFIG["labels"]["btn_open_chat"],
                DEFAULT_CONFIG["labels"]["btn_close_chat"],
                DEFAULT_CONFIG["labels"]["btn_process_ideas"],
            ])

            self.assertEqual(texts, expected)
            app.destroy()
        finally:
            if temp_path and os.path.exists(temp_path):
                os.rename(temp_path, CONFIG_PATH)

    @patch("ui_main.subprocess.run")
    def test_open_chat_copies_files_calls_powershell(self, mock_run):
        existing_file = os.path.abspath(__file__)
        self.app.get_backup_path = lambda: existing_file

        hoja_path = os.path.join(BASE_DIR, "hoja_de_ruta.txt")
        promp_path = os.path.join(BASE_DIR, "promp_maestro.txt")

        for p in [hoja_path, promp_path]:
            if not os.path.exists(p):
                with open(p, "w", encoding="utf-8") as f:
                    f.write("test")

        self.app.open_chat()

        self.assertTrue(mock_run.called)
        args, _kwargs = mock_run.call_args
        cmd = args[0]

        self.assertIn("SetFileDropList", cmd[-1])
        self.assertIn(existing_file, cmd[-1])
        self.assertIn(os.path.abspath(hoja_path), cmd[-1])
        self.assertIn(os.path.abspath(promp_path), cmd[-1])

    @patch("ui_main.subprocess.run")
    def test_open_chat_skips_missing_files(self, mock_run):
        self.app.get_backup_path = lambda: r"C:\no\such\file.zip"

        hoja_path = os.path.join(BASE_DIR, "hoja_de_ruta.txt")

        if not os.path.exists(hoja_path):
            with open(hoja_path, "w", encoding="utf-8") as f:
                f.write("test")

        self.app.open_chat()

        self.assertTrue(mock_run.called)
        args, _kwargs = mock_run.call_args
        cmd = args[0]

        self.assertIn("SetFileDropList", cmd[-1])
        self.assertIn(os.path.abspath(hoja_path), cmd[-1])
        self.assertNotIn(r"C:\no\such\file.zip", cmd[-1])

    @patch("ui_main.subprocess.run")
    def test_open_chat_button_invoke_triggers_copy(self, mock_run):
        target_text = self.config["labels"]["btn_open_chat"]
        buttons = self._find_buttons(self.app)

        open_button = None
        for b in buttons:
            if b.cget("text") == target_text:
                open_button = b
                break

        self.assertIsNotNone(open_button, "No se encontró el botón Abrir Chat")

        open_button.invoke()

        self.assertTrue(mock_run.called)
        args, _kwargs = mock_run.call_args
        cmd = args[0]

        self.assertIn("SetFileDropList", cmd[-1])


if __name__ == "__main__":
    unittest.main()
