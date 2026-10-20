import csv
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from repositories.memory_repository import MemoryRepository
from services.csv_export import export_inventory, FIELDS


class CsvTests(unittest.TestCase):
    def test_round_trip_vietnamese_and_spreadsheet_text(self):
        rows = MemoryRepository().list_inventory()[:5]
        rows[0]['name'] = 'Bút, màu xanh\nHộp lớn'
        rows[1]['name'] = '=1+1'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'ton.csv'
            self.assertEqual(export_inventory(path, rows), 5)
            self.assertTrue(path.read_bytes().startswith(b'\xef\xbb\xbf'))
            with path.open(encoding='utf-8-sig', newline='') as stream:
                result = list(csv.DictReader(stream))
            self.assertEqual(result[0]['name'], rows[0]['name'])
            self.assertEqual(result[1]['name'], "'=1+1")
            self.assertEqual(result[0]['stock'], '7')

    def test_empty_export_and_failed_replace_preserve_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'ton.csv'
            export_inventory(path, [])
            with path.open(encoding='utf-8-sig', newline='') as stream:
                self.assertEqual(list(csv.reader(stream)), [FIELDS])
            before = path.read_bytes()
            with patch('services.csv_export.os.replace', side_effect=PermissionError('File đang mở')):
                with self.assertRaises(PermissionError):
                    export_inventory(path, MemoryRepository().list_inventory())
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(list(Path(directory).iterdir()), [path])
