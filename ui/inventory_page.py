import tkinter as tk
from tkinter import ttk

from services.inventory_report import inventory_report
from .base_page import BasePage


class InventoryPage(BasePage):
    SORT_OPTIONS = {'Mã sản phẩm': 'sku', 'Tồn ít nhất trước': 'stock', 'Giá trị cao nhất trước': 'value'}

    def __init__(self, parent, context, on_changed):
        super().__init__(parent, context, on_changed)
        self.rows = []
        ttk.Label(self, text='Tồn kho và giá trị hàng hóa', style='Heading.TLabel').pack(anchor='w')
        self.summary = ttk.Label(self, text='')
        self.summary.pack(anchor='w', pady=(8, 12))

        filters = ttk.Frame(self)
        filters.pack(fill='x', pady=(0, 8))
        ttk.Label(filters, text='Tìm mã / tên:').pack(side='left')
        self.query = tk.StringVar()
        ttk.Entry(filters, textvariable=self.query, width=23).pack(side='left', padx=(6, 12))
        self.low_only = tk.BooleanVar(value=False)
        self.active_only = tk.BooleanVar(value=False)
        ttk.Checkbutton(filters, text='Chỉ hàng tồn thấp', variable=self.low_only,
                        command=self.render).pack(side='left')
        ttk.Checkbutton(filters, text='Chỉ sản phẩm đang dùng', variable=self.active_only,
                        command=self.render).pack(side='left', padx=8)
        ttk.Button(filters, text='Xóa bộ lọc', command=self.clear_filters).pack(side='right')

        sorting = ttk.Frame(self)
        sorting.pack(fill='x', pady=(0, 10))
        ttk.Label(sorting, text='Sắp xếp:').pack(side='left')
        self.sort_by = tk.StringVar(value='Mã sản phẩm')
        chooser = ttk.Combobox(sorting, textvariable=self.sort_by, values=list(self.SORT_OPTIONS),
                               state='readonly', width=24)
        chooser.pack(side='left', padx=6)
        chooser.bind('<<ComboboxSelected>>', lambda event: self.render())
        self.result_label = ttk.Label(sorting, text='')
        self.result_label.pack(side='right')

        ttk.Label(self, text='Cần bổ sung = số lượng còn thiếu để đạt mức tối thiểu. Cảnh báo chỉ áp dụng cho sản phẩm đang dùng.').pack(
            side='bottom', anchor='w', pady=(4, 0))
        ttk.Label(self, text='Giá trị tồn = tồn × đơn giá hiện tại; tổng tiền tính theo các dòng đang hiển thị.').pack(
            side='bottom', anchor='w', pady=(8, 0))
        ttk.Label(self, text='Màu vàng: còn hàng nhưng dưới mức tối thiểu. Màu đỏ: hết hàng (tồn = 0).',
                  wraplength=950).pack(side='bottom', anchor='w', pady=(8, 0))
        ttk.Label(self, text='Tối thiểu là mức muốn duy trì để nhắc nhập thêm; vẫn được xuất xuống dưới mức này nếu đủ hàng.',
                  wraplength=950).pack(side='bottom', anchor='w', pady=(4, 0))
        holder = ttk.Frame(self)
        holder.pack(fill='both', expand=True)
        columns = ('sku', 'name', 'unit', 'stock', 'minimum', 'shortage', 'cost', 'value', 'status')
        self.table = ttk.Treeview(holder, columns=columns, show='headings', height=12)
        labels = ('SKU', 'Sản phẩm', 'Đơn vị', 'Tồn', 'Tối thiểu', 'Cần bổ sung',
                  'Đơn giá VND', 'Giá trị tồn VND', 'Trạng thái')
        widths = (80, 185, 60, 55, 65, 90, 110, 125, 120)
        for col, label, width in zip(columns, labels, widths):
            self.table.heading(col, text=label)
            self.table.column(col, width=width, minwidth=width,
                              anchor='e' if col in ('stock', 'minimum', 'shortage', 'cost', 'value') else 'w')
        self.table.tag_configure('low', background='#fff0d4')
        self.table.tag_configure('empty', background='#ffe0dd')
        self.table.tag_configure('inactive', foreground='#666666')
        vertical = ttk.Scrollbar(holder, orient='vertical', command=self.table.yview)
        horizontal = ttk.Scrollbar(holder, orient='horizontal', command=self.table.xview)
        self.table.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.table.grid(row=0, column=0, sticky='nsew')
        vertical.grid(row=0, column=1, sticky='ns')
        horizontal.grid(row=1, column=0, sticky='ew')
        holder.rowconfigure(0, weight=1)
        holder.columnconfigure(0, weight=1)
        self.query.trace_add('write', lambda *_: self.render())

    def refresh(self):
        self.rows = self.context.stock_service.list_inventory()
        self.render()

    def clear_filters(self):
        self.low_only.set(False)
        self.active_only.set(False)
        self.sort_by.set('Mã sản phẩm')
        self.query.set('')

    def render(self):
        report = inventory_report(self.rows, self.query.get(), self.low_only.get(),
                                  self.active_only.get(), self.SORT_OPTIONS[self.sort_by.get()])
        self.table.delete(*self.table.get_children())
        for row in report['rows']:
            if not row['active']:
                status, tag = 'Ngừng dùng', 'inactive'
            elif row['stock'] == 0:
                status, tag = 'Hết hàng', 'empty'
            elif row['low_stock']:
                status, tag = 'Tồn thấp', 'low'
            else:
                status, tag = 'Đủ mức tối thiểu', ''
            self.table.insert('', 'end', iid=str(row['product_id']), values=(
                row['sku'], row['name'], row['unit'], row['stock'], row['min_stock'], row['shortage'],
                f"{row['unit_cost']:,.2f}", f"{row['stock_value']:,.2f}", status), tags=(tag,) if tag else ())
        self.summary.configure(text=f"Đang xem: {report['product_count']} sản phẩm  |  "
                               f"{report['low_count']} dưới mức tối thiểu  |  "
                               f"Tổng giá trị: {report['total_value']:,.2f} VND")
        self.result_label.configure(text=f"{report['product_count']} / {len(self.rows)} sản phẩm"
                                    if report['rows'] else 'Không có sản phẩm phù hợp bộ lọc.')
