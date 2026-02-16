import unittest
import tkinter as tk
from ui_main import YvoloApp

class TestYvoloApp(unittest.TestCase):
    def setUp(self):
        self.app = YvoloApp()
        self.app.update()  # Ensure widgets are created

    def tearDown(self):
        self.app.destroy()

    def test_title(self):
        self.assertEqual(self.app.title(), "yvolo")

    def test_not_resizable(self):
        width_resizable = self.app.resizable()[0]
        height_resizable = self.app.resizable()[1]
        self.assertFalse(width_resizable)
        self.assertFalse(height_resizable)

    def test_buttons_exist(self):
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
        self.assertEqual(texts, ["Abrir Chat", "Cerrar Chat", "Procesar Ideas"])

if __name__ == "__main__":
    unittest.main()
