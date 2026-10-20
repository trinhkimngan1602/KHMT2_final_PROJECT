"""Export the complete inventory as Excel-friendly UTF-8 CSV."""
import csv
import os
from pathlib import Path
import tempfile

FIELDS = ['product_id', 'sku', 'name', 'unit', 'unit_cost', 'min_stock', 'active', 'stock', 'stock_value']


def spreadsheet_text(value):
    text = str(value)
    # Treat user-entered names as literal text if opened in spreadsheet software.
    if text.lstrip().startswith(('=', '+', '-', '@')) or text.startswith(('\t', '\r', '\n')):
        return "'" + text
    return text


def export_inventory(path, rows):
    """Write all rows atomically. Return the number of exported products."""
    target = Path(path)
    temporary = None
    count = 0
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8-sig', newline='',
                                         dir=target.parent, prefix='.warehouse_', suffix='.tmp',
                                         delete=False) as stream:
            temporary = Path(stream.name)
            writer = csv.DictWriter(stream, fieldnames=FIELDS)
            writer.writeheader()
            for row in rows:
                record = {key: row[key] for key in FIELDS}
                for key in ('sku', 'name', 'unit'):
                    record[key] = spreadsheet_text(record[key])
                record['active'] = int(bool(record['active']))
                writer.writerow(record)
                count += 1
        os.replace(temporary, target)
        return count
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
