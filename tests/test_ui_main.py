import unittest
import tkinter as tk
import os
import shutil
import json
from ui_main import YvoloApp, load_config, DEFAULT_CONFIG

CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config', 'settings.json'))

class TestYvoloApp(unittest.TestCase):
    def setUp(self):
        self._backup_config = None
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'rb') as f:
                self._backup_config = f.read()
        self.config = load_config()
        self.app = YvoloApp(config=self.config)
        self.app.update()

    def tearDown(self):
        self.app.destroy()
        # Restore config if it was backed up
        if self._backup_config is not None:
            with open(CONFIG_PATH, 'wb') as f:
                f.write(self._backup_config)

    def test_title_from_config(self):
        self.assertEqual(self.app.title(), self.config["app_name"])

    def test_not_resizable(self):
        width_resizable = self.app.resizable()[0]
        height_resizable = self.app.resizable()[1]
        self.assertFalse(width_resizable)
        self.assertFalse(height_resizable)

    def test_buttons_match_labels(self):
        # Find all Button widgets in the app
        buttons = []
        def find_buttons(widget):
            if isinstance(widget, tk.Button):
                buttons.append(widget)
            for child in widget.winfo_children():
                find_buttons(child)
        find_buttons(self.app)
        self.assertEqual(len(buttons), 3)
        texts = sorted([b.cget('text') for b in buttons])
        expected = sorted([
            self.config["labels"]["btn_open_chat"],
            self.config["labels"]["btn_close_chat"],
            self.config["labels"]["btn_process_ideas"]
        ])
        self.assertEqual(texts, expected)

    def test_fallback_on_missing_config(self):
        # Temporarily rename config file
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
            # Find all Button widgets
            buttons = []
            def find_buttons(widget):
                if isinstance(widget, tk.Button):
                    buttons.append(widget)
                for child in widget.winfo_children():
                    find_buttons(child)
            find_buttons(app)
            self.assertEqual(len(buttons), 3)
            texts = sorted([b.cget('text') for b in buttons])
            expected = sorted([
                DEFAULT_CONFIG["labels"]["btn_open_chat"],
                DEFAULT_CONFIG["labels"]["btn_close_chat"],
                DEFAULT_CONFIG["labels"]["btn_process_ideas"]
            ])
            self.assertEqual(texts, expected)
            app.destroy()
        finally:
            # Restore config file
            if temp_path and os.path.exists(temp_path):
                os.rename(temp_path, CONFIG_PATH)

if __name__ == "__main__":
    unittest.main()
