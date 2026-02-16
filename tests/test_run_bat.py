import unittest
import os

class TestRunYvoloBat(unittest.TestCase):
    def setUp(self):
        self.bat_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'run_yvolo_ui.bat'))

    def test_bat_exists(self):
        self.assertTrue(os.path.isfile(self.bat_path), f"{self.bat_path} does not exist")

    def test_bat_contains_pythonw_and_ui_main(self):
        # Try utf-8, fallback to cp1252
        try:
            with open(self.bat_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(self.bat_path, 'r', encoding='cp1252') as f:
                content = f.read()
        content_lower = content.lower()
        self.assertIn('pythonw', content_lower)
        self.assertIn('ui_main.py', content_lower)
        # Optional: check for cd /d %~dp0 or similar
        self.assertRegex(content_lower, r'cd\s*/d\s*%~dp0')

if __name__ == "__main__":
    unittest.main()
