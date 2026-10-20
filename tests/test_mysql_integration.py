"""Real MySQL tests in a freshly created, uniquely named disposable database.
Run explicitly: python -m unittest tests.test_mysql_integration -v
The ordinary test suite skips these unless WAREHOUSE_TEST_MYSQL=1.
"""
import os
import unittest
from uuid import uuid4
from threading import Barrier
from concurrent.futures import ThreadPoolExecutor
import mysql.connector
from database import load_settings
from setup_db import initialize
from expand_sample import expand
from services.context import build_context
from tests import test_stock_service


@unittest.skipUnless(os.environ.get('WAREHOUSE_TEST_MYSQL')=='1','Set WAREHOUSE_TEST_MYSQL=1 to test real MySQL')
class MySQLIntegrationTests(test_stock_service.StockRulesTests):
    @classmethod
    def setUpClass(cls):
        cls.settings=load_settings()
        cls.test_db='warehouse_test_'+uuid4().hex[:16]
        cls.settings['database']=cls.test_db
        initialize(cls.settings)

    @classmethod
    def tearDownClass(cls):
        # Delete ONLY the random database created by this class, never configured user data.
        assert cls.settings['database']==cls.test_db and cls.test_db.startswith('warehouse_test_')
        server=dict(cls.settings)
        server.pop('database')
        connection=mysql.connector.connect(**server)
        try:
            cursor=connection.cursor()
            cursor.execute('DROP DATABASE `'+cls.test_db+'`')
            cursor.close()
        finally:
            connection.close()

    def setUp(self):
        self.context=build_context(settings=self.settings)
        self.stock=self.context.stock_service
        self.pid=self.context.product_service.create_product('T'+uuid4().hex[:20],'Sản phẩm kiểm tra','Cái','50000',7)

    def test_product_validation_and_unique_sku(self):
        sku='D'+uuid4().hex[:20]
        self.context.product_service.create_product(sku,'Tên','Cái',1)
        with self.assertRaises(ValueError):
            self.context.product_service.create_product(sku.lower(),'Trùng','Cái',1)
        with self.assertRaises(ValueError):
            self.stock.get_stock(2147483647)

    def test_two_withdrawals_cannot_make_negative_stock(self):
        self.stock.record_movement(self.pid,'IN',10,1)
        barrier=Barrier(2)
        def withdraw():
            barrier.wait(timeout=10)
            try:
                self.stock.record_movement(self.pid,'OUT',7)
                return 'saved'
            except ValueError:
                return 'rejected'
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes=list(pool.map(lambda _:withdraw(),range(2)))
        self.assertCountEqual(outcomes,['saved','rejected'])
        self.assertEqual(self.stock.get_stock(self.pid),3)

    def test_seed_rerun_does_not_overwrite_existing_data(self):
        before=len(self.context.product_service.list_products())
        message=initialize(self.settings)
        self.assertIn('bỏ qua',message)
        self.assertEqual(len(self.context.product_service.list_products()),before)

    def test_expand_sample_preserves_user_rows_and_can_run_twice(self):
        own_id = self.context.product_service.create_product('USERKEEP'+uuid4().hex[:8], 'Hàng tự nhập', 'Cái', 5)
        self.stock.record_movement(own_id, 'IN', 4, 1)
        connection = mysql.connector.connect(**self.settings)
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM products WHERE sku='SP015'")
            sample_id = cursor.fetchone()[0]
            cursor.execute('DELETE FROM stock_movements WHERE product_id=%s', (sample_id,))
            cursor.execute('DELETE FROM products WHERE id=%s', (sample_id,))
            connection.commit()
            cursor.close()
        finally:
            connection.close()
        self.assertEqual(expand(self.settings), 1)
        self.assertEqual(expand(self.settings), 0)
        self.assertEqual(self.stock.get_stock(own_id), 4)
        restored = next(row for row in self.context.product_service.list_products() if row['sku'] == 'SP015')
        self.assertEqual(self.stock.get_stock(restored['id']), 8)
