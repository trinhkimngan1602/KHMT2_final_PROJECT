"""Common form for receipts, issues, and stock adjustments."""
import tkinter as tk
from tkinter import ttk, messagebox
from database import StorageError
from .base_page import BasePage
from .widgets import MOVEMENT_LABELS, make_table, fill_choices
from .theme import COLORS
from . import theme


class MovementPage(BasePage):
    def __init__(self, parent, context, on_changed, mode):
        super().__init__(parent, context, on_changed)
        self.mode = mode
        self.products = {}
        self.suppliers = {}
        titles = {'IN': 'Nhập hàng vào kho', 'OUT': 'Xuất hàng khỏi kho', 'ADJUST': 'Điều chỉnh tồn kho'}
        hints = {'IN': 'Chọn sản phẩm, nhà cung cấp và số lượng nhập.',
                 'OUT': 'Số lượng xuất phải lớn hơn 0 và không vượt số hàng hiện có.',
                 'ADJUST': 'Nhập phần chênh lệch. Ví dụ: tồn ghi 10, kiểm kê còn 9 → giảm 1. Bắt buộc ghi lý do.'}
        ttk.Label(self, text=titles[mode], style='Heading.TLabel').pack(anchor='w')
        ttk.Label(self, text=hints[mode], wraplength=950).pack(anchor='w', pady=(4, 12))
        form = ttk.Frame(self)
        form.pack(fill='x')
        ttk.Label(form, text='Sản phẩm đang dùng *').grid(row=0, column=0, sticky='w')
        self.product = tk.StringVar()
        self.product_combo = ttk.Combobox(form, textvariable=self.product, state='readonly', width=43)
        self.product_combo.grid(row=1, column=0, sticky='ew', padx=(0, 16))
        self.product_combo.bind('<<ComboboxSelected>>', self.product_changed)
        self.stock_label = ttk.Label(form, text='Tồn hiện tại: —')
        self.stock_label.grid(row=2, column=0, sticky='w', pady=(6, 0))
        self.quantity = tk.StringVar()
        ttk.Label(form, text='Số lượng *').grid(row=0, column=1, sticky='w')
        ttk.Entry(form, textvariable=self.quantity, width=14).grid(row=1, column=1, sticky='ew', padx=(0, 16))
        self.supplier = tk.StringVar()
        self.direction = tk.StringVar(value='Tăng')
        if mode == 'IN':
            ttk.Label(form, text='Nhà cung cấp *').grid(row=0, column=2, sticky='w')
            self.supplier_combo = ttk.Combobox(form, textvariable=self.supplier, state='readonly', width=32)
            self.supplier_combo.grid(row=1, column=2, sticky='ew')
        elif mode == 'ADJUST':
            ttk.Label(form, text='Loại điều chỉnh').grid(row=0, column=2, sticky='w')
            ttk.Combobox(form, textvariable=self.direction, values=['Tăng', 'Giảm'], state='readonly',
                         width=18).grid(row=1, column=2, sticky='ew')
        form.columnconfigure(0, weight=3)
        form.columnconfigure(2, weight=2)
        ttk.Label(self, text='Lý do điều chỉnh *' if mode == 'ADJUST' else 'Ghi chú (có thể trống)').pack(
            anchor='w', pady=(10, 4))
        self.note = tk.Text(self, height=2, wrap='word', font=(theme.FONT, 11),
                            relief='flat', highlightthickness=1, highlightbackground=COLORS['border'],
                            highlightcolor=COLORS['purple'], padx=9, pady=7,
                            background='white', foreground=COLORS['ink'], insertbackground=COLORS['ink'])
        self.note.pack(fill='x')
        actions = ttk.Frame(self)
        actions.pack(fill='x', pady=10)
        self.save_button = ttk.Button(actions, text='Lưu giao dịch', style='Primary.TButton', command=self.save)
        self.save_button.pack(side='left')
        ttk.Button(actions, text='Xóa nội dung nhập', command=self.clear_form).pack(side='left', padx=8)
        self.notice = ttk.Label(actions, text='')
        self.notice.pack(side='left', padx=8)
        ttk.Label(self, text='Tối đa 20 giao dịch gần nhất của sản phẩm đang chọn',
                  font=(theme.FONT, 11, 'bold')).pack(anchor='w', pady=(0, 6))
        self.table = make_table(self, [('id', 'Mã', 65), ('date', 'Thời gian', 160),
                                      ('kind', 'Loại', 150), ('quantity', 'Số lượng', 85),
                                      ('note', 'Ghi chú', 400)], height=6)

    def refresh(self):
        self.stock_label.configure(text='Không đọc được tồn hiện tại.')
        self.table.delete(*self.table.get_children())
        rows = [row for row in self.context.product_service.list_products() if row['active']]
        self.products = fill_choices(self.product_combo, self.product, self.products, rows,
                                     lambda row: f"{row['sku']} — {row['name']}")
        if self.mode == 'IN':
            suppliers = self.context.supplier_service.list_suppliers()
            self.suppliers = fill_choices(self.supplier_combo, self.supplier, self.suppliers, suppliers,
                                          lambda row: f"#{row['id']} — {row['name']}")
        self.load_product()

    def product_changed(self, _event=None):
        self.notice.configure(text='')
        try:
            self.load_product()
        except (ValueError, StorageError) as exc:
            self.stock_label.configure(text='Không đọc được tồn hiện tại.')
            messagebox.showerror('Không tải được sản phẩm', str(exc), parent=self)

    def load_product(self):
        product_id = self.products.get(self.product.get())
        self.table.delete(*self.table.get_children())
        if product_id is None:
            self.stock_label.configure(text='Hãy chọn sản phẩm để xem tồn hiện tại.' if self.products else
                                       'Chưa có sản phẩm đang dùng. Hãy thêm ở tab Sản phẩm.')
            return
        self.stock_label.configure(text='Không đọc được tồn hiện tại.')
        stock = self.context.stock_service.get_stock(product_id)
        rows = self.context.stock_service.list_movements(product_id=product_id)
        self.stock_label.configure(text=f'Tồn hiện tại: {stock}')
        for row in rows[:20]:
            self.table.insert('', 'end', values=(row['id'], row['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
                              MOVEMENT_LABELS[row['movement_type']], row['quantity'], row['note']))

    def clear_form(self):
        self.quantity.set('')
        self.note.delete('1.0', 'end')
        self.notice.configure(text='')

    def save(self):
        self.save_button.state(['disabled'])
        try:
            product_id = self.products.get(self.product.get())
            if product_id is None:
                raise ValueError('Hãy chọn sản phẩm. Nếu danh sách trống, thêm sản phẩm ở tab Sản phẩm.')
            kind = self.mode
            if self.mode == 'ADJUST':
                kind = 'ADJUST_IN' if self.direction.get() == 'Tăng' else 'ADJUST_OUT'
            supplier_id = self.suppliers.get(self.supplier.get()) if self.mode == 'IN' else None
            movement_id = self.context.stock_service.record_movement(
                product_id, kind, self.quantity.get(), supplier_id=supplier_id,
                note=self.note.get('1.0', 'end-1c'))
        except (ValueError, StorageError) as exc:
            messagebox.showerror('Chưa lưu giao dịch', str(exc), parent=self)
            return
        finally:
            self.save_button.state(['!disabled'])
        self.clear_form()
        self.notice.configure(text=f'Đã lưu giao dịch #{movement_id}: {MOVEMENT_LABELS[kind]}.', foreground='#24613b')
        self.on_changed()
