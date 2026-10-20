"""Initialize new project tables. No existing rows are removed or overwritten."""
from pathlib import Path
import argparse
import re
import sys
import mysql.connector
from database import ROOT, load_settings, StorageError


def statements(filename):
    # These bundled scripts have no stored procedures or semicolons inside strings.
    text = (ROOT / filename).read_text(encoding='utf-8')
    text = '\n'.join(line for line in text.splitlines() if not line.strip().startswith('--'))
    return [part.strip() for part in text.split(';') if part.strip()]


def initialize(settings, with_seed=True):
    name = settings['database']
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,63}', name):
        raise ValueError('Tên database chỉ gồm chữ, số và gạch dưới, bắt đầu bằng chữ.')
    server = dict(settings)
    server.pop('database')
    connection = mysql.connector.connect(**server)
    try:
        cursor = connection.cursor()
        for statement in statements('schema.sql'):
            cursor.execute(statement.replace('warehouse_mgmt', name))
        connection.commit()
        if with_seed:
            cursor.execute('SELECT (SELECT COUNT(*) FROM products) + (SELECT COUNT(*) FROM suppliers) + (SELECT COUNT(*) FROM stock_movements)')
            if cursor.fetchone()[0] != 0:
                return 'Schema sẵn sàng; bỏ qua seed vì database đã có dữ liệu.'
            for statement in statements('seed.sql'):
                cursor.execute(statement.replace('warehouse_mgmt', name))
            connection.commit()
        return 'Đã tạo schema và dữ liệu mẫu.' if with_seed else 'Đã tạo schema rỗng.'
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == '__main__':
    if sys.stdout is not None:
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path)
    parser.add_argument('--no-seed', action='store_true')
    args = parser.parse_args()
    try:
        print(initialize(load_settings(args.config), not args.no_seed))
    except (mysql.connector.Error, StorageError, ValueError) as exc:
        code = getattr(exc, 'errno', None)
        print(f'Chưa khởi tạo được database. Mã MySQL: {code}. Kiểm tra config.local.ini và quyền tạo database.')
        raise SystemExit(1)
