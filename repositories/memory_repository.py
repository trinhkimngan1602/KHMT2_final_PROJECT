"""Explicit in-memory demo for teammates building screens without MySQL."""
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from threading import RLock
from sample_data import EXTRA_PRODUCTS, EXTRA_SUPPLIERS


class MemoryRepository:
    def __init__(self):
        self.lock = RLock()
        self.products = [
            dict(id=i, sku=f'SP{i:03}', name=name, unit=unit, unit_cost=Decimal(cost), min_stock=minimum, active=True)
            for i, name, unit, cost, minimum in [
                (1, 'Bút bi', 'Hộp', '50000.00', 7), (2, 'Giấy A4', 'Ram', '75000.00', 10),
                (3, 'Băng keo', 'Cuộn', '12000.00', 5), (4, 'Thùng carton', 'Cái', '15000.00', 10),
                (5, 'Bìa hồ sơ', 'Cái', '5000.00', 5)]]
        self.suppliers = [dict(id=1, name='Nhà cung cấp mẫu A', phone=''), dict(id=2, name='Nhà cung cấp mẫu B', phone='')]
        self.movements = []
        from models import StockMovement
        for pid, kind, qty, sid in [(1,'IN',10,1),(1,'OUT',3,None),(2,'IN',30,2),(3,'IN',3,1),(4,'IN',20,2),(4,'OUT',5,None)]:
            self.record_movement(StockMovement(pid, kind, qty, sid, 'Dữ liệu mẫu'))
        for offset, (name, phone) in enumerate(EXTRA_SUPPLIERS, start=3):
            self.suppliers.append(dict(id=offset, name=name, phone=phone))
        for product_id, (sku, name, unit, cost, minimum, movements) in enumerate(EXTRA_PRODUCTS, start=6):
            self.products.append(dict(id=product_id, sku=sku, name=name, unit=unit,
                                      unit_cost=Decimal(cost), min_stock=minimum, active=True))
            for kind, quantity, supplier_index, note in movements:
                supplier_id = supplier_index + 1 if supplier_index is not None else None
                self.record_movement(StockMovement(product_id, kind, quantity, supplier_id, note))

    def _product(self, product_id):
        for product in self.products:
            if product['id'] == product_id:
                return product
        raise ValueError('Không tìm thấy sản phẩm.')

    def list_products(self):
        return [p.copy() for p in sorted(self.products, key=lambda p: p['sku'])]

    def list_suppliers(self):
        return [s.copy() for s in self.suppliers]

    def insert_supplier(self, name, phone):
        with self.lock:
            new_id = max((s['id'] for s in self.suppliers), default=0) + 1
            self.suppliers.append(dict(id=new_id,name=name,phone=phone))
            return new_id

    def create_product(self, product):
        with self.lock:
            if any(p['sku'].casefold() == product.sku.casefold() for p in self.products):
                raise ValueError('SKU đã tồn tại.')
            new_id = max((p['id'] for p in self.products), default=0) + 1
            self.products.append(dict(id=new_id, active=True, **asdict(product)))
            return new_id

    def update_product(self, product_id, name, unit, unit_cost, min_stock):
        with self.lock:
            self._product(product_id).update(name=name, unit=unit, unit_cost=unit_cost, min_stock=min_stock)

    def set_product_active(self, product_id, active):
        with self.lock:
            product = self._product(product_id)
            if not active and product['active']:
                stock = self.get_stock(product_id)
                if stock != 0:
                    raise ValueError(f'Cần xử lý hết tồn kho ({stock}) trước khi ngừng sử dụng sản phẩm.')
            product['active'] = active

    def get_stock(self, product_id):
        self._product(product_id)
        return sum(m['quantity'] if m['movement_type'] in ('IN','ADJUST_IN') else -m['quantity']
                   for m in self.movements if m['product_id'] == product_id)

    def record_movement(self, movement):
        with self.lock:
            if not self._product(movement.product_id)['active']:
                raise ValueError('Sản phẩm đã ngừng sử dụng.')
            if movement.supplier_id is not None and not any(s['id'] == movement.supplier_id for s in self.suppliers):
                raise ValueError('Không tìm thấy nhà cung cấp.')
            balance = self.get_stock(movement.product_id)
            if balance + movement.signed_quantity < 0:
                raise ValueError(f'Không đủ hàng. Tồn hiện tại: {balance}.')
            new_id = len(self.movements) + 1
            self.movements.append(dict(id=new_id, created_at=datetime.now(), **asdict(movement)))
            return new_id

    def list_inventory(self):
        rows = []
        for product in self.list_products():
            row = dict(product)
            row['product_id'] = row.pop('id')
            row['stock'] = self.get_stock(row['product_id'])
            row['stock_value'] = row['stock'] * row['unit_cost']
            rows.append(row)
        return rows

    def list_movements(self, product_id=None, movement_type=None, date_from=None, date_to=None):
        rows = []
        for m in reversed(self.movements):
            if product_id is not None and m['product_id'] != product_id:
                continue
            if movement_type is not None and m['movement_type'] != movement_type:
                continue
            if date_from and m['created_at'].date() < date_from:
                continue
            if date_to and m['created_at'].date() > date_to:
                continue
            product = self._product(m['product_id'])
            supplier = next((s for s in self.suppliers if s['id'] == m['supplier_id']), None)
            rows.append(dict(id=m['id'], created_at=m['created_at'], sku=product['sku'], name=product['name'],
                             movement_type=m['movement_type'], quantity=m['quantity'], note=m['note'],
                             supplier_name=supplier['name'] if supplier else None))
        return rows
