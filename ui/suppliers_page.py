import tkinter as tk
from tkinter import ttk, messagebox
from database import StorageError
from .base_page import BasePage
from .widgets import make_table


class SuppliersPage(BasePage):
    def __init__(self, parent, context, on_changed):
        super().__init__(parent, context, on_changed)
        self.rows = []
        ttk.Label(self, text='Nhà cung cấp', style='Heading.TLabel').pack(anchor='w')
        ttk.Label(self, text='Thêm nhà cung cấp trước khi ghi nhận hàng nhập.').pack(anchor='w', pady=(4, 12))
        form = ttk.Frame(self)
        form.pack(fill='x')
        self.name = tk.StringVar()
        self.phone = tk.StringVar()
        ttk.Label(form, text='Tên nhà cung cấp *').grid(row=0, column=0, sticky='w')
        ttk.Label(form, text='Số điện thoại (có thể trống)').grid(row=0, column=1, sticky='w')
        ttk.Entry(form, textvariable=self.name, width=42).grid(row=1, column=0, sticky='ew', padx=(0, 12))
        ttk.Entry(form, textvariable=self.phone, width=28).grid(row=1, column=1, sticky='ew', padx=(0, 12))
        ttk.Button(form, text='Thêm nhà cung cấp', style='Primary.TButton', command=self.save).grid(row=1, column=2)
        form.columnconfigure(0, weight=2)
        form.columnconfigure(1, weight=1)
        self.notice = ttk.Label(self, text='')
        self.notice.pack(anchor='w', pady=10)
        search = ttk.Frame(self)
        search.pack(fill='x', pady=(0, 10))
        ttk.Label(search, text='Tìm tên / điện thoại:').pack(side='left')
        self.query = tk.StringVar()
        ttk.Entry(search, textvariable=self.query, width=35).pack(side='left', padx=8)
        self.count = ttk.Label(search, text='')
        self.count.pack(side='right')
        self.table = make_table(self, [('id', 'Mã', 70), ('name', 'Nhà cung cấp', 400),
                                      ('phone', 'Điện thoại', 240)])
        self.query.trace_add('write', lambda *_: self.render())

    def refresh(self):
        self.rows = self.context.supplier_service.list_suppliers()
        self.render()

    def render(self):
        query = self.query.get().strip().casefold()
        rows = [row for row in self.rows if query in row['name'].casefold() or query in row['phone'].casefold()]
        self.table.delete(*self.table.get_children())
        for row in rows:
            self.table.insert('', 'end', iid=str(row['id']), values=(row['id'], row['name'], row['phone']))
        self.count.configure(text=f'{len(rows)} / {len(self.rows)} nhà cung cấp')

    def save(self):
        try:
            supplier_id = self.context.supplier_service.create_supplier(self.name.get(), self.phone.get())
        except (ValueError, StorageError) as exc:
            messagebox.showerror('Chưa lưu nhà cung cấp', str(exc), parent=self)
            return
        self.name.set('')
        self.phone.set('')
        self.query.set('')
        self.notice.configure(text=f'Đã thêm nhà cung cấp mã {supplier_id}.', foreground='#24613b')
        self.on_changed()
