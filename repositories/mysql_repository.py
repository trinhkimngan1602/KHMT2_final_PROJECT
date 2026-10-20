from datetime import timedelta
from decimal import Decimal
import mysql.connector

STOCK_SQL = """SELECT COALESCE(SUM(CASE WHEN movement_type IN ('IN','ADJUST_IN')
              THEN quantity ELSE -quantity END), 0) AS stock
              FROM stock_movements WHERE product_id = %s"""


class MySQLRepository:
    def __init__(self, database):
        self.database = database

    def _read(self, sql, params=()):
        with self.database.transaction() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute(sql, params)
                return cursor.fetchall()
            finally:
                cursor.close()

    def list_products(self):
        return self._read('SELECT id, sku, name, unit, unit_cost, min_stock, active FROM products ORDER BY sku')

    def list_suppliers(self):
        return self._read('SELECT id, name, phone FROM suppliers ORDER BY name')

    def insert_supplier(self, name, phone):
        """Persistence helper for B's SupplierService, after input validation."""
        with self.database.transaction() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute('INSERT INTO suppliers (name,phone) VALUES (%s,%s)', (name,phone))
                return cursor.lastrowid
            finally:
                cursor.close()

    def create_product(self, product):
        with self.database.transaction() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute('INSERT INTO products (sku,name,unit,unit_cost,min_stock) VALUES (%s,%s,%s,%s,%s)',
                               (product.sku, product.name, product.unit, product.unit_cost, product.min_stock))
                return cursor.lastrowid
            except mysql.connector.IntegrityError as exc:
                if exc.errno == 1062:
                    raise ValueError('SKU đã tồn tại.') from None
                raise
            finally:
                cursor.close()

    def update_product(self, product_id, name, unit, unit_cost, min_stock):
        with self.database.transaction() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute('''UPDATE products SET name=%s, unit=%s, unit_cost=%s, min_stock=%s
                    WHERE id=%s''', (name, unit, unit_cost, min_stock, product_id))
                if cursor.rowcount == 0:
                    cursor.execute('SELECT id FROM products WHERE id=%s', (product_id,))
                    if cursor.fetchone() is None:
                        raise ValueError('Không tìm thấy sản phẩm.')
            finally:
                cursor.close()

    def set_product_active(self, product_id, active):
        with self.database.transaction() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute('SELECT id, active FROM products WHERE id=%s FOR UPDATE', (product_id,))
                product = cursor.fetchone()
                if product is None:
                    raise ValueError('Không tìm thấy sản phẩm.')
                if not active and product['active']:
                    cursor.execute(STOCK_SQL, (product_id,))
                    stock = int(cursor.fetchone()['stock'])
                    if stock != 0:
                        raise ValueError(f'Cần xử lý hết tồn kho ({stock}) trước khi ngừng sử dụng sản phẩm.')
                cursor.execute('UPDATE products SET active=%s WHERE id=%s', (active, product_id))
            finally:
                cursor.close()

    def get_stock(self, product_id):
        if not self._read('SELECT id FROM products WHERE id=%s', (product_id,)):
            raise ValueError('Không tìm thấy sản phẩm.')
        return int(self._read(STOCK_SQL, (product_id,))[0]['stock'])

    def record_movement(self, movement):
        # Lock one product so two simultaneous withdrawals cannot spend the same stock.
        # READ COMMITTED gives the next withdrawal the committed balance after waiting.
        with self.database.transaction() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute('SELECT id, active FROM products WHERE id=%s FOR UPDATE', (movement.product_id,))
                product = cursor.fetchone()
                if product is None:
                    raise ValueError('Không tìm thấy sản phẩm.')
                if not product['active']:
                    raise ValueError('Sản phẩm đã ngừng sử dụng.')
                if movement.supplier_id is not None:
                    cursor.execute('SELECT id FROM suppliers WHERE id=%s', (movement.supplier_id,))
                    if cursor.fetchone() is None:
                        raise ValueError('Không tìm thấy nhà cung cấp.')
                cursor.execute(STOCK_SQL, (movement.product_id,))
                balance = int(cursor.fetchone()['stock'])
                if balance + movement.signed_quantity < 0:
                    raise ValueError(f'Không đủ hàng. Tồn hiện tại: {balance}.')
                cursor.execute('''INSERT INTO stock_movements
                    (product_id,supplier_id,movement_type,quantity,note) VALUES (%s,%s,%s,%s,%s)''',
                    (movement.product_id, movement.supplier_id, movement.movement_type, movement.quantity, movement.note))
                return cursor.lastrowid
            finally:
                cursor.close()

    def list_inventory(self):
        rows = self._read('''SELECT p.id AS product_id,p.sku,p.name,p.unit,p.unit_cost,p.min_stock,p.active,
            COALESCE(s.stock,0) AS stock FROM products p LEFT JOIN (
                SELECT product_id, SUM(CASE WHEN movement_type IN ('IN','ADJUST_IN')
                THEN quantity ELSE -quantity END) AS stock FROM stock_movements GROUP BY product_id
            ) s ON s.product_id=p.id ORDER BY p.sku''')
        for row in rows:
            row['stock'] = int(row['stock'])
            row['stock_value'] = Decimal(row['unit_cost']) * row['stock']
        return rows

    def list_movements(self, product_id=None, movement_type=None, date_from=None, date_to=None):
        clauses, params = [], []
        for column, value in (('m.product_id', product_id), ('m.movement_type', movement_type)):
            if value is not None:
                clauses.append(column + '=%s')
                params.append(value)
        if date_from is not None:
            clauses.append('m.created_at >= %s')
            params.append(date_from)
        if date_to is not None:
            # Avoid overflow for date.max; ordinary course dates use an exclusive next day.
            if date_to.year == 9999 and date_to.month == 12 and date_to.day == 31:
                clauses.append('DATE(m.created_at) <= %s')
                params.append(date_to)
            else:
                clauses.append('m.created_at < %s')
                params.append(date_to + timedelta(days=1))
        sql = '''SELECT m.id,m.created_at,p.sku,p.name,m.movement_type,m.quantity,m.note,s.name AS supplier_name
            FROM stock_movements m JOIN products p ON p.id=m.product_id
            LEFT JOIN suppliers s ON s.id=m.supplier_id'''
        if clauses:
            sql += ' WHERE ' + ' AND '.join(clauses)
        return self._read(sql + ' ORDER BY m.created_at DESC,m.id DESC', tuple(params))
