"""Add the extra fictional sample rows to an existing project database.

Existing products, suppliers and movements are never changed. The transaction
is atomic, and repeating the command skips sample SKUs already present.
"""
import sys
import mysql.connector
from database import load_settings, StorageError
from sample_data import EXTRA_PRODUCTS, EXTRA_SUPPLIERS

SUPPLIERS = (('Nhà cung cấp mẫu A', ''), ('Nhà cung cấp mẫu B', '')) + EXTRA_SUPPLIERS


def expand(settings):
    connection = mysql.connector.connect(**settings)
    try:
        connection.start_transaction(isolation_level='READ COMMITTED')
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute('SELECT sku FROM products')
            existing = {row['sku'].casefold() for row in cursor.fetchall()}
            missing = [product for product in EXTRA_PRODUCTS if product[0].casefold() not in existing]
            if not missing:
                connection.rollback()
                return 0
            supplier_ids = {}
            for index, (name, phone) in enumerate(SUPPLIERS):
                cursor.execute('SELECT id FROM suppliers WHERE name=%s ORDER BY id LIMIT 1', (name,))
                row = cursor.fetchone()
                if row:
                    supplier_ids[index] = row['id']
                else:
                    cursor.execute('INSERT INTO suppliers (name,phone) VALUES (%s,%s)', (name, phone))
                    supplier_ids[index] = cursor.lastrowid
            for sku, name, unit, cost, minimum, movements in missing:
                cursor.execute('INSERT INTO products (sku,name,unit,unit_cost,min_stock) '
                               'VALUES (%s,%s,%s,%s,%s)', (sku, name, unit, cost, minimum))
                product_id = cursor.lastrowid
                for kind, quantity, supplier_index, note in movements:
                    supplier_id = supplier_ids[supplier_index] if supplier_index is not None else None
                    cursor.execute('INSERT INTO stock_movements '
                                   '(product_id,supplier_id,movement_type,quantity,note) '
                                   'VALUES (%s,%s,%s,%s,%s)',
                                   (product_id, supplier_id, kind, quantity, note))
            connection.commit()
            return len(missing)
        finally:
            cursor.close()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == '__main__':
    if sys.stdout is not None:
        sys.stdout.reconfigure(encoding='utf-8')
    try:
        count = expand(load_settings())
        print(f'Đã thêm {count} sản phẩm mẫu. Dữ liệu cũ được giữ nguyên.' if count else
              'Bộ dữ liệu mẫu mở rộng đã có sẵn; không thêm dòng trùng.')
    except (mysql.connector.Error, StorageError) as exc:
        print(f'Chưa thêm được dữ liệu mẫu. Mã MySQL: {getattr(exc, "errno", None)}. '
              'Kiểm tra database đã được tạo và MySQL đang chạy.')
        raise SystemExit(1)
