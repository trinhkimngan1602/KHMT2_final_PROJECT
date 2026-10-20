import tkinter as tk
from tkinter import ttk, messagebox

from database import StorageError
from .base_page import BasePage


class ProductsPage(BasePage):
    def __init__(self, parent, context, on_changed):
        super().__init__(parent, context, on_changed)
        self.selected_product_id = None
        self.rows = {}

        ttk.Label(self, text='Danh mục sản phẩm', style='Heading.TLabel').pack(anchor='w')
        ttk.Label(self, text='Chọn một dòng để sửa. SKU được giữ cố định để lịch sử kho dễ theo dõi.').pack(
            anchor='w', pady=(4, 12))

        fields = [('sku', 'SKU'), ('name', 'Tên sản phẩm'), ('unit', 'Đơn vị'),
                  ('unit_cost', 'Đơn giá VND'), ('min_stock', 'Tồn tối thiểu')]
        form = ttk.Frame(self)
        form.pack(fill='x')
        self.values = {}
        self.entries = {}
        for column, (key, label) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=0, column=column, sticky='w', padx=(0, 8))
            value = tk.StringVar(value='0' if key in ('unit_cost', 'min_stock') else '')
            self.values[key] = value
            entry = ttk.Entry(form, textvariable=value, width=12 if key != 'name' else 22)
            entry.grid(row=1, column=column, sticky='ew', padx=(0, 8))
            self.entries[key] = entry
            form.columnconfigure(column, weight=2 if key == 'name' else 1)

        actions = ttk.Frame(self)
        actions.pack(fill='x', pady=(10, 0))
        self.save_button = ttk.Button(actions, text='Thêm sản phẩm', style='Primary.TButton', command=self.save_product)
        self.save_button.pack(side='left')
        ttk.Button(actions, text='Nhập mới', command=self.reset_form).pack(side='left', padx=8)
        self.active_button = ttk.Button(actions, text='Ngừng sử dụng', command=self.toggle_active)
        self.active_button.pack(side='left')
        self.active_button.state(['disabled'])

        holder = ttk.Frame(self)
        holder.pack(fill='both', expand=True, pady=(16, 0))
        columns = ('sku', 'name', 'unit', 'unit_cost', 'min_stock', 'active')
        self.table = ttk.Treeview(holder, columns=columns, show='headings', height=15)
        labels = ('SKU', 'Tên sản phẩm', 'Đơn vị', 'Đơn giá VND', 'Tồn tối thiểu', 'Đang dùng')
        for col, label in zip(columns, labels):
            self.table.heading(col, text=label)
            self.table.column(col, width=220 if col == 'name' else 115, anchor='w')
        scroll = ttk.Scrollbar(holder, orient='vertical', command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        self.table.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')
        self.table.bind('<<TreeviewSelect>>', self.load_selection)

    def refresh(self):
        self.table.delete(*self.table.get_children())
        self.rows = {str(row['id']): row for row in self.context.product_service.list_products()}
        for product_id, row in self.rows.items():
            self.table.insert('', 'end', iid=product_id,
                              values=(row['sku'], row['name'], row['unit'],
                                      f"{row['unit_cost']:,.2f}", row['min_stock'],
                                      'Có' if row['active'] else 'Không'))
        selected = str(self.selected_product_id)
        if selected in self.rows:
            self.table.selection_set(selected)
            self.load_selection()

    def load_selection(self, _event=None):
        selection = self.table.selection()
        if not selection:
            return
        row = self.rows[selection[0]]
        self.selected_product_id = row['id']
        for key in self.values:
            self.values[key].set(str(row[key]))
        self.entries['sku'].state(['readonly'])
        self.save_button.configure(text='Lưu chỉnh sửa')
        self.active_button.configure(text='Ngừng sử dụng' if row['active'] else 'Dùng lại')
        self.active_button.state(['!disabled'])

    def reset_form(self):
        self.selected_product_id = None
        self.table.selection_remove(*self.table.selection())
        for key, value in self.values.items():
            value.set('0' if key in ('unit_cost', 'min_stock') else '')
        self.entries['sku'].state(['!readonly'])
        self.save_button.configure(text='Thêm sản phẩm')
        self.active_button.state(['disabled'])

    def save_product(self):
        values = {key: value.get() for key, value in self.values.items()}
        try:
            if self.selected_product_id is None:
                self.context.product_service.create_product(**values)
                notice = 'Sản phẩm đã được thêm.'
            else:
                values.pop('sku')
                self.context.product_service.update_product(self.selected_product_id, **values)
                notice = 'Thông tin sản phẩm đã được cập nhật.'
        except (ValueError, StorageError) as exc:
            messagebox.showerror('Chưa lưu sản phẩm', str(exc), parent=self)
            return
        self.reset_form()
        self.on_changed()
        messagebox.showinfo('Đã lưu', notice, parent=self)

    def toggle_active(self):
        if self.selected_product_id is None:
            return
        row = self.rows[str(self.selected_product_id)]
        active = not bool(row['active'])
        if not active and not messagebox.askyesno(
                'Ngừng sử dụng', f"Ngừng sử dụng {row['sku']}? Sản phẩm cần có tồn bằng 0.", parent=self):
            return
        try:
            self.context.product_service.set_product_active(self.selected_product_id, active)
        except (ValueError, StorageError) as exc:
            messagebox.showerror('Chưa đổi trạng thái', str(exc), parent=self)
            return
        self.on_changed()
