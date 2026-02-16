import unittest
import os
import json

class TestConfigSettings(unittest.TestCase):
    def setUp(self):
        self.config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'settings.json')
        self.config_path = os.path.abspath(self.config_path)

    def test_settings_json_exists(self):
        self.assertTrue(os.path.isfile(self.config_path), f"{self.config_path} does not exist")

    def test_settings_json_content(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertEqual(data.get('app_name'), 'yvolo')
        self.assertEqual(data.get('language'), 'es')
        self.assertIn('version', data)
        self.assertIn('features', data)

if __name__ == "__main__":
    unittest.main()
