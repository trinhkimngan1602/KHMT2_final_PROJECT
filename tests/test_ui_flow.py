"""Exercise real Tkinter callbacks with demo data; dialogs are intercepted."""
import csv
from datetime import date
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from services.context import build_context
from ui.app import WarehouseApp
from database import StorageError


class UserJourneyTests(unittest.TestCase):
    def setUp(self):
        self.context = build_context(demo=True)
        self.app = WarehouseApp(self.context)
        self.app.withdraw()
        self.app.update()
        self.info = patch('tkinter.messagebox.showinfo').start()
        self.error = patch('tkinter.messagebox.showerror').start()
        self.addCleanup(patch.stopall)
        self.addCleanup(self.app.destroy)

    def page(self, index):
        self.app.notebook.select(index)
        self.app.update()
        page = self.app.pages[index]
        page.refresh()
        return page

    def select_product(self, page, pid):
        page.product.set(next(label for label, value in page.products.items() if value == pid))

    def test_home_updates_summary_and_opens_low_stock(self):
        home = self.app.home_page
        self.assertEqual(self.app.notebook.select(), str(home))
        self.assertIsNotNone(home.warehouse_image)
        self.assertEqual(home.metrics['products'].cget('text'), '50')
        self.assertEqual(home.metrics['value'].cget('text'), '26,496,000.00')
        pid = self.context.product_service.create_product('HOME', 'Hàng trang chủ', 'Hộp', 50000, 7)
        self.context.stock_service.record_movement(pid, 'IN', 6, 1)
        self.app.show_page('home')
        self.app.update()
        self.assertEqual(home.metrics['products'].cget('text'), '51')
        self.assertEqual(home.metrics['low'].cget('text'), '17')
        self.assertEqual(home.metrics['value'].cget('text'), '26,796,000.00')
        self.app.show_page('low_stock')
        self.app.update()
        inventory = self.app.page_by_key['inventory']
        self.assertEqual(self.app.notebook.select(), str(inventory))
        self.assertTrue(inventory.low_only.get())
        self.assertIn(str(pid), inventory.table.get_children())
        self.assertEqual(len(inventory.table.get_children()), 17)
        self.app.nav_buttons['home'].invoke()
        self.app.update()
        self.assertEqual(self.app.notebook.select(), str(home))

    def test_window_close_cancel_preserves_form_then_confirm_closes(self):
        products = self.page(0)
        products.values['name'].set('Chưa lưu')
        protocol = self.app.protocol('WM_DELETE_WINDOW')
        with patch('tkinter.messagebox.askyesno', return_value=False) as ask, \
             patch.object(self.app, 'destroy') as close:
            self.app.tk.call(protocol)
            close.assert_not_called()
            self.assertEqual(products.values['name'].get(), 'Chưa lưu')
            self.assertEqual(ask.call_args.kwargs['default'], 'no')
            ask.return_value = True
            self.app.tk.call(protocol)
            close.assert_called_once()

    def test_exit_menu_asks_before_closing(self):
        menu = self.app.nametowidget(self.app.cget('menu'))
        application = self.app.nametowidget(menu.entrycget(0, 'menu'))
        with patch('tkinter.messagebox.askyesno', return_value=False) as ask, \
             patch.object(self.app, 'destroy') as close:
            application.invoke(application.index('end'))
            ask.assert_called_once()
            close.assert_not_called()

    def test_home_connection_error_clears_previous_figures(self):
        with patch.object(self.context.stock_service, 'list_inventory', side_effect=StorageError('Mất kết nối')):
            self.app.show_page('home')
        self.assertEqual(self.app.status.cget('text'), 'Mất kết nối')
        self.assertTrue(all(label.cget('text') == '—' for label in self.app.home_page.metrics.values()))
        self.assertEqual(self.app.home_page.data_hint.cget('text'), 'Chưa có số liệu mới')

    def test_export_menu_works_from_home(self):
        menu = self.app.nametowidget(self.app.cget('menu'))
        application = self.app.nametowidget(menu.entrycget(0, 'menu'))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'from_home.csv'
            with patch('ui.history_page.filedialog.asksaveasfilename', return_value=str(path)):
                application.invoke(1)
            with path.open(encoding='utf-8-sig', newline='') as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 50)
        self.assertEqual(self.app.notebook.select(), str(self.app.home_page))

    def test_deactivated_selection_requires_explicit_new_choice(self):
        pid = self.context.product_service.create_product('STOP', 'Hàng tạm', 'Hộp', 1)
        receipts = self.page(3)
        self.select_product(receipts, pid)
        receipts.quantity.set('2')
        before = self.context.stock_service.list_movements()
        self.context.product_service.set_product_active(pid, False)
        receipts.refresh()
        receipts.refresh()
        self.assertEqual(receipts.product.get(), '')
        receipts.save()
        self.error.assert_called_once()
        self.assertEqual(receipts.quantity.get(), '2')
        self.assertEqual(self.context.stock_service.list_movements(), before)

    def test_failed_refresh_does_not_display_previous_stock(self):
        receipts = self.page(3)
        self.select_product(receipts, 1)
        receipts.load_product()
        receipts.quantity.set('2')
        receipts.note.insert('1.0', 'Giữ nội dung để thử lại')
        with patch.object(self.context.stock_service, 'get_stock', side_effect=StorageError('Mất kết nối')):
            with self.assertRaises(StorageError):
                receipts.refresh()
        self.assertEqual(receipts.stock_label.cget('text'), 'Không đọc được tồn hiện tại.')
        self.assertEqual(receipts.quantity.get(), '2')
        self.assertEqual(receipts.note.get('1.0', 'end-1c'), 'Giữ nội dung để thử lại')
        self.assertEqual(receipts.table.get_children(), ())

    def test_complete_ten_feature_journey(self):
        products = self.page(0)
        for key, value in dict(sku='FLOW', name='Hàng kiểm tra', unit='Hộp', unit_cost='50000', min_stock='7').items():
            products.values[key].set(value)
        products.save_product()
        pid = next(row['id'] for row in self.context.product_service.list_products() if row['sku'] == 'FLOW')
        products.table.selection_set(str(pid))
        products.load_selection()
        products.values['name'].set('Hàng kiểm tra đã sửa')
        products.save_product()

        suppliers = self.page(2)
        suppliers.name.set('NCC kiểm tra')
        suppliers.phone.set('0123456789')
        suppliers.save()
        sid = next(row['id'] for row in self.context.supplier_service.list_suppliers() if row['name'] == 'NCC kiểm tra')

        receipts = self.page(3)
        self.select_product(receipts, pid)
        receipts.supplier.set(next(label for label, value in receipts.suppliers.items() if value == sid))
        receipts.quantity.set('10')
        receipts.save()
        self.assertEqual(self.context.stock_service.get_stock(pid), 10)
        self.assertEqual(receipts.quantity.get(), '')

        issues = self.page(5)
        self.select_product(issues, pid)
        issues.quantity.set('3')
        issues.save()
        self.assertEqual(self.context.stock_service.get_stock(pid), 7)

        adjustments = self.page(4)
        self.select_product(adjustments, pid)
        adjustments.direction.set('Giảm')
        adjustments.quantity.set('1')
        adjustments.save()  # Missing reason must keep the form and stock unchanged.
        self.error.assert_called_once()
        self.assertEqual(adjustments.quantity.get(), '1')
        self.assertEqual(self.context.stock_service.get_stock(pid), 7)
        adjustments.note.insert('1.0', 'Hỏng khi kiểm kê')
        adjustments.save()
        self.assertEqual(self.context.stock_service.get_stock(pid), 6)

        inventory = self.page(1)
        inventory.query.set('FLOW')
        inventory.low_only.set(True)
        inventory.render()
        values = inventory.table.item(str(pid))['values']
        self.assertEqual(values[3], 6)
        self.assertEqual(values[5], 1)
        self.assertEqual(values[7], '300,000.00')

        issues = self.page(5)
        self.select_product(issues, pid)
        issues.quantity.set('7')
        issues.save()
        self.assertEqual(self.error.call_count, 2)
        self.assertEqual(self.context.stock_service.get_stock(pid), 6)

        history = self.page(6)
        self.select_product(history, pid)
        history.date_from.set(date.today().isoformat())
        history.date_to.set(date.today().isoformat())
        history.apply_filters()
        self.assertEqual(len(history.table.get_children()), 3)
        history.kind.set('Xuất')
        history.apply_filters()
        self.assertEqual(len(history.table.get_children()), 1)
        history.date_from.set('sai ngày')
        history.apply_filters()
        self.assertEqual(self.error.call_count, 3)
        history.clear_filters()
        with patch('ui.history_page.filedialog.asksaveasfilename', return_value=''), \
             patch('ui.history_page.export_inventory') as write:
            history.export_csv()
            write.assert_not_called()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'ton.csv'
            with patch('ui.history_page.filedialog.asksaveasfilename', return_value=str(path)):
                history.export_csv()
            with path.open(encoding='utf-8-sig', newline='') as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 51)  # CSV exports all products despite inventory filters.
            row = next(row for row in rows if row['sku'] == 'FLOW')
            self.assertEqual(row['stock'], '6')
            self.assertEqual(row['stock_value'], '300000.00')
