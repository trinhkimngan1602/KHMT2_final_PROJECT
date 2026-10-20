import unittest
from datetime import date, timedelta
from decimal import Decimal
from services.context import build_context


class StockRulesTests(unittest.TestCase):
    def setUp(self):
        self.context=build_context(demo=True)
        self.stock=self.context.stock_service
        self.pid=self.context.product_service.create_product('CHECK','Sản phẩm kiểm tra','Cái','50000',7)

    def test_full_warehouse_flow_and_failed_withdrawal_leaves_no_row(self):
        self.stock.record_movement(self.pid,'IN',10,1)
        self.stock.record_movement(self.pid,'OUT',3)
        self.assertEqual(self.stock.get_stock(self.pid),7)
        self.stock.record_movement(self.pid,'ADJUST_OUT',1,note='Vỡ khi kiểm kê')
        self.assertEqual(self.stock.get_stock(self.pid),6)
        row=next(r for r in self.stock.list_inventory() if r['product_id']==self.pid)
        self.assertEqual(row['stock_value'],Decimal('300000.00'))
        self.assertLess(row['stock'],row['min_stock'])
        with self.assertRaisesRegex(ValueError,'Không đủ hàng'):
            self.stock.record_movement(self.pid,'OUT',7)
        self.assertEqual(len(self.stock.list_movements(product_id=self.pid)),3)
        self.assertEqual(self.stock.get_stock(self.pid),6)

    def test_invalid_inputs_do_not_change_stock(self):
        for value in (0,-1,1.5,'abc',True,'NaN','Infinity',2147483648):
            with self.subTest(value=value),self.assertRaises(ValueError):
                self.stock.record_movement(self.pid,'IN',value,1)
        for kind in ('RETURN','in',None):
            with self.subTest(kind=kind),self.assertRaises(ValueError):
                self.stock.record_movement(self.pid,kind,1,1)
        self.assertEqual(self.stock.get_stock(self.pid),0)

    def test_supplier_and_adjustment_validation(self):
        for kind,sid,note in [('IN',None,''),('IN',9999,''),('OUT',1,''),('ADJUST_IN',None,'   ')]:
            with self.subTest(kind=kind,sid=sid),self.assertRaises(ValueError):
                self.stock.record_movement(self.pid,kind,1,sid,note)
        self.stock.record_movement(self.pid,'ADJUST_IN',2,note='Kiểm kê thừa')
        self.stock.record_movement(self.pid,'OUT',2)
        self.assertEqual(self.stock.get_stock(self.pid),0)

    def test_product_validation_and_unique_sku(self):
        for price in ('NaN','-1','0.001','Infinity'):
            with self.subTest(price=price),self.assertRaises(ValueError):
                self.context.product_service.create_product('BAD','Tên','Cái',price)
        with self.assertRaises(ValueError):
            self.context.product_service.create_product('check','Trùng SKU','Cái',1)
        with self.assertRaises(ValueError):
            self.stock.get_stock(9999)

    def test_edit_deactivate_and_reactivate_product(self):
        products = self.context.product_service
        original_sku = next(p['sku'] for p in products.list_products() if p['id'] == self.pid)
        products.update_product(self.pid, 'Tên đã sửa', 'Hộp', '12500.50', 4)
        row = next(p for p in products.list_products() if p['id'] == self.pid)
        self.assertEqual((row['name'], row['unit'], row['unit_cost'], row['min_stock']),
                         ('Tên đã sửa', 'Hộp', Decimal('12500.50'), 4))
        self.assertEqual(row['sku'], original_sku)
        for value in ('NaN', '-1', '0.001'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                products.update_product(self.pid, 'Tên', 'Cái', value)
        self.stock.record_movement(self.pid, 'IN', 2, 1)
        with self.assertRaisesRegex(ValueError, 'Cần xử lý hết tồn kho'):
            products.set_product_active(self.pid, False)
        self.stock.record_movement(self.pid, 'OUT', 2)
        products.set_product_active(self.pid, False)
        with self.assertRaisesRegex(ValueError, 'ngừng sử dụng'):
            self.stock.record_movement(self.pid, 'IN', 1, 1)
        products.set_product_active(self.pid, True)
        self.stock.record_movement(self.pid, 'IN', 1, 1)
        self.assertEqual(self.stock.get_stock(self.pid), 1)

    def test_date_and_type_filters(self):
        self.stock.record_movement(self.pid,'IN',10,1)
        self.stock.record_movement(self.pid,'OUT',3)
        today=date.today()
        rows=self.stock.list_movements(self.pid,'OUT',today.isoformat(),today.isoformat())
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['quantity'],3)
        self.assertEqual(self.stock.list_movements(self.pid,date_from=today+timedelta(days=1)),[])
        with self.assertRaises(ValueError):
            self.stock.list_movements(date_from='2026-99-99')
        with self.assertRaises(ValueError):
            self.stock.list_movements(date_from='2026-02-02',date_to='2026-01-01')

    def test_new_supplier_can_be_used_for_receipts(self):
        service = self.context.supplier_service
        before = len(service.list_suppliers())
        for name, phone in [(' ', ''), ('X' * 121, ''), ('Tên', '0' * 31), ('Tên', None)]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                service.create_supplier(name, phone)
        self.assertEqual(len(service.list_suppliers()), before)
        supplier_id = service.create_supplier('  Nhà cung cấp mới  ', '  0123456789  ')
        supplier = next(row for row in service.list_suppliers() if row['id'] == supplier_id)
        self.assertEqual(supplier['name'], 'Nhà cung cấp mới')
        self.assertEqual(supplier['phone'], '0123456789')
        self.stock.record_movement(self.pid, 'IN', 10, supplier_id)
        self.assertEqual(self.stock.get_stock(self.pid), 10)


if __name__=='__main__':
    unittest.main()
