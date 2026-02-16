import unittest
import tkinter as tk
import os
from unittest.mock import patch

from ui_main import YvoloApp, load_config, DEFAULT_CONFIG

CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "settings.json"))


class TestYvoloApp(unittest.TestCase):
    def setUp(self):
        # Backup settings.json (so tests can temporarily rename it)
        self._backup_config = None
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "rb") as f:
                self._backup_config = f.read()

        self.config = load_config()
        self.app = YvoloApp(config=self.config)
        self.app.update()

    def tearDown(self):
        # Close any extra windows safely, then destroy root
        try:
            self.app.destroy()
        except Exception:
            pass

        # Restore settings.json if needed
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
        expected = sorted(
            [
                self.config["labels"]["btn_open_chat"],
                self.config["labels"]["btn_close_chat"],
                self.config["labels"]["btn_process_ideas"],
            ]
        )
        self.assertEqual(texts, expected)

    def test_fallback_on_missing_config(self):
        # Temporarily rename config file to force fallback
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
            expected = sorted(
                [
                    DEFAULT_CONFIG["labels"]["btn_open_chat"],
                    DEFAULT_CONFIG["labels"]["btn_close_chat"],
                    DEFAULT_CONFIG["labels"]["btn_process_ideas"],
                ]
            )
            self.assertEqual(texts, expected)
            app.destroy()
        finally:
            if temp_path and os.path.exists(temp_path):
                os.rename(temp_path, CONFIG_PATH)

    @patch("ui_main.subprocess.run")
    def test_open_chat_copies_files_calls_powershell(self, mock_run):
        # Force backup path to be an existing file
        existing_file = os.path.abspath(__file__)
        self.app.get_backup_path = lambda: existing_file

        hoja_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "hoja_de_ruta.txt"))
        promp_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "promp_maestro.txt"))

        # Ensure hoja and promp exist for this test
        for p in [hoja_path, promp_path]:
            if not os.path.exists(p):
                with open(p, "w", encoding="utf-8") as f:
                    f.write("test")

        self.app.open_chat()

        self.assertTrue(mock_run.called)
        args, _kwargs = mock_run.call_args
        cmd = args[0]  # list like ["powershell","-Command","Set-Clipboard -Path ..."]
        self.assertIn("powershell", cmd[0].lower())
        self.assertIn("Set-Clipboard", cmd[-1])
        self.assertIn(existing_file, cmd[-1])
        self.assertIn(hoja_path, cmd[-1])
        self.assertIn(promp_path, cmd[-1])

    @patch("ui_main.subprocess.run")
    def test_open_chat_skips_missing_files(self, mock_run):
        # Backup path missing, promp missing; hoja exists -> should still call powershell with hoja only
        self.app.get_backup_path = lambda: r"C:\no\such\file.zip"

        hoja_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "hoja_de_ruta.txt"))
        if not os.path.exists(hoja_path):
            with open(hoja_path, "w", encoding="utf-8") as f:
                f.write("test")

        promp_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "promp_maestro.txt"))
        if os.path.exists(promp_path):
            os.remove(promp_path)

        self.app.open_chat()

        self.assertTrue(mock_run.called)
        args, _kwargs = mock_run.call_args
        cmd = args[0]
        self.assertIn("Set-Clipboard", cmd[-1])
        self.assertIn(hoja_path, cmd[-1])
        self.assertNotIn(r"C:\no\such\file.zip", cmd[-1])


if __name__ == "__main__":
    unittest.main()
