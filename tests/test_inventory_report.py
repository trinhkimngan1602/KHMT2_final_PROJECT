import unittest
from decimal import Decimal
from repositories.memory_repository import MemoryRepository
from services.inventory_report import inventory_report


class InventoryReportTests(unittest.TestCase):
    def setUp(self):
        # Keep the original five-row fixture for focused report calculations.
        self.rows = MemoryRepository().list_inventory()[:5]

    def test_low_stock_shortage_and_scoped_value(self):
        result = inventory_report(self.rows, low_only=True)
        self.assertEqual([r['sku'] for r in result['rows']], ['SP003', 'SP005'])
        self.assertEqual([r['shortage'] for r in result['rows']], [2, 5])
        self.assertEqual(result['total_value'], Decimal('36000.00'))
        self.assertEqual(result['low_count'], 2)
        self.assertNotIn('shortage', self.rows[0])

    def test_search_sort_and_empty_report(self):
        self.assertEqual(inventory_report(self.rows, query='giẤy')['rows'][0]['sku'], 'SP002')
        self.assertEqual(inventory_report(self.rows, sort_by='value')['rows'][0]['sku'], 'SP002')
        self.assertEqual(inventory_report(self.rows, sort_by='stock')['rows'][0]['sku'], 'SP005')
        report = inventory_report(self.rows, query='NO MATCH')
        self.assertEqual(report['product_count'], 0)
        self.assertEqual(report['total_value'], Decimal('0.00'))

    def test_inactive_stock_stays_in_value_but_not_low_alerts(self):
        # Historical/imported inactive items must not disappear from overall valuation.
        self.rows[2]['active'] = False
        self.assertEqual(inventory_report(self.rows)['total_value'], Decimal('2861000.00'))
        self.assertEqual(inventory_report(self.rows, low_only=True)['product_count'], 1)
        self.assertEqual(inventory_report(self.rows, active_only=True)['product_count'], 4)


if __name__ == '__main__':
    unittest.main()
