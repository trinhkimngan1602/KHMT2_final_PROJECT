"""Configuration mistakes should produce useful errors without exposing passwords."""
from pathlib import Path
import tempfile
import unittest

from database import StorageError, load_settings


class SettingsTests(unittest.TestCase):
    def test_invalid_file_reports_configuration_error(self):
        samples = [
            'password=private-example\n',
            '[mysql]\nuser=root\nuser=duplicate\npassword=private-example\n',
            '[mysql]\nuser=root\nport=invalid\n',
            '[mysql]\nuser=root\nport=0\n',
            '[mysql]\nuser=root\nport=65536\n',
            '[mysql]\nuser=\n',
        ]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'config.ini'
            for content in samples:
                with self.subTest(content=content):
                    path.write_text(content, encoding='utf-8')
                    with self.assertRaises(StorageError) as caught:
                        load_settings(path)
                    self.assertNotIn('private-example', str(caught.exception))

    def test_bom_and_password_characters_are_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'config.ini'
            path.write_text('[mysql]\nuser=root\npassword=p%#;example\n', encoding='utf-8-sig')
            settings = load_settings(path)
            self.assertEqual(settings['password'], 'p%#;example')
            self.assertEqual(settings['port'], 3306)

    def test_missing_file_reports_next_step(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(StorageError, 'config.example.ini'):
                load_settings(Path(folder) / 'missing.ini')
