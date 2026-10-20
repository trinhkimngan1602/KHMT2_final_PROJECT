import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date
from database import StorageError
from services.csv_export import export_inventory
from .base_page import BasePage
from .widgets import MOVEMENT_LABELS, make_table, fill_choices


class HistoryPage(BasePage):
    def __init__(self, parent, context, on_changed):
        super().__init__(parent, context, on_changed)
        self.products = {}
        self.kinds = {'Tất cả loại': None, **{label: key for key, label in MOVEMENT_LABELS.items()}}
        ttk.Label(self, text='Lịch sử biến động kho', style='Heading.TLabel').pack(anchor='w')
        ttk.Label(self, text='Ngày theo dạng YYYY-MM-DD; để trống nếu không giới hạn ngày.').pack(
            anchor='w', pady=(4, 12))
        filters = ttk.Frame(self)
        filters.pack(fill='x')
        self.product = tk.StringVar()
        self.kind = tk.StringVar(value='Tất cả loại')
        self.date_from = tk.StringVar()
        self.date_to = tk.StringVar()
        for column, label in enumerate(['Sản phẩm', 'Loại giao dịch', 'Từ ngày', 'Đến ngày']):
            ttk.Label(filters, text=label).grid(row=0, column=column, sticky='w')
        self.product_combo = ttk.Combobox(filters, textvariable=self.product, state='readonly', width=35)
        self.product_combo.grid(row=1, column=0, sticky='ew', padx=(0, 12))
        ttk.Combobox(filters, textvariable=self.kind, values=list(self.kinds), state='readonly',
                     width=22).grid(row=1, column=1, sticky='ew', padx=(0, 12))
        ttk.Entry(filters, textvariable=self.date_from, width=14).grid(row=1, column=2, sticky='ew', padx=(0, 12))
        ttk.Entry(filters, textvariable=self.date_to, width=14).grid(row=1, column=3, sticky='ew')
        filters.columnconfigure(0, weight=2)
        filters.columnconfigure(1, weight=1)
        actions = ttk.Frame(self)
        actions.pack(fill='x', pady=10)
        ttk.Button(actions, text='Áp dụng bộ lọc', style='Primary.TButton', command=self.apply_filters).pack(side='left')
        ttk.Button(actions, text='Xóa bộ lọc', command=self.clear_filters).pack(side='left', padx=8)
        self.result_label = ttk.Label(actions, text='')
        self.result_label.pack(side='left', padx=8)

        export = ttk.Frame(self)
        export.pack(side='bottom', fill='x', pady=(12, 0))
        ttk.Button(export, text='Xuất toàn bộ tồn kho CSV', command=self.export_csv).pack(side='left')
        ttk.Label(export, text='CSV gồm toàn bộ sản phẩm, không dùng bộ lọc lịch sử ở trên.').pack(side='left', padx=12)
        self.table = make_table(self, [('id', 'Mã', 60), ('date', 'Thời gian', 160), ('sku', 'SKU', 80),
                                      ('name', 'Sản phẩm', 175), ('kind', 'Loại', 135),
                                      ('quantity', 'Số lượng', 80), ('supplier', 'Nhà cung cấp', 175),
                                      ('note', 'Ghi chú', 240)])

    def refresh(self):
        self.products = fill_choices(self.product_combo, self.product, self.products,
                                     self.context.product_service.list_products(),
                                     lambda row: f"{row['sku']} — {row['name']}", include_all=True)
        self.load_history()

    def load_history(self):
        rows = self.context.stock_service.list_movements(
            product_id=self.products.get(self.product.get()), movement_type=self.kinds[self.kind.get()],
            date_from=self.date_from.get().strip(), date_to=self.date_to.get().strip())
        self.table.delete(*self.table.get_children())
        for row in rows:
            self.table.insert('', 'end', iid=str(row['id']), values=(
                row['id'], row['created_at'].strftime('%Y-%m-%d %H:%M:%S'), row['sku'], row['name'],
                MOVEMENT_LABELS[row['movement_type']], row['quantity'], row['supplier_name'] or '', row['note']))
        self.result_label.configure(text=f'{len(rows)} giao dịch' if rows else 'Không có giao dịch phù hợp.')

    def apply_filters(self):
        try:
            self.load_history()
        except (ValueError, StorageError) as exc:
            messagebox.showerror('Chưa áp dụng bộ lọc', str(exc), parent=self)

    def clear_filters(self):
        self.product.set('Tất cả sản phẩm')
        self.kind.set('Tất cả loại')
        self.date_from.set('')
        self.date_to.set('')
        self.apply_filters()

    def export_csv(self):
        path = filedialog.asksaveasfilename(parent=self, title='Lưu bảng tồn kho',
            defaultextension='.csv', filetypes=[('CSV', '*.csv')], initialfile=f'ton_kho_{date.today()}.csv')
        if not path:
            return
        try:
            rows = self.context.stock_service.list_inventory()
            count = export_inventory(path, rows)
        except (OSError, ValueError, StorageError) as exc:
            messagebox.showerror('Chưa xuất được CSV', str(exc), parent=self)
            return
        messagebox.showinfo('Đã xuất CSV', f'Đã lưu {count} sản phẩm tại:\n{path}', parent=self)
