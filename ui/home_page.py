"""Home dashboard. Figures come from services; no SQL in this screen."""
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from services.inventory_report import inventory_report
from .base_page import BasePage
from .theme import COLORS as C
from . import theme
from .appearance import RoundedPanel


class HomePage(BasePage):
    def __init__(self, parent, context, on_changed, navigate):
        super().__init__(parent, context, on_changed)
        self.navigate = navigate
        self.configure(padding=0)
        self.canvas = tk.Canvas(self, background=C['surface'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)
        self.body = tk.Frame(self.canvas, background=C['surface'], padx=24, pady=20)
        self.body_window = self.canvas.create_window(0, 0, window=self.body, anchor='nw')
        self.body.bind('<Configure>', lambda event: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>', lambda event: self.canvas.itemconfigure(self.body_window, width=event.width))
        self._build_hero()
        self._build_metrics()
        self._build_actions()
        self._bind_scroll(self)

    def _bind_scroll(self, widget):
        widget.bind('<MouseWheel>', self._scroll, add='+')
        for child in widget.winfo_children():
            self._bind_scroll(child)

    def _scroll(self, event):
        if self.body.winfo_height() > self.canvas.winfo_height():
            self.canvas.yview_scroll(-1 if event.delta > 0 else 1, 'units')
        return 'break'

    def _build_hero(self):
        # Full-width photo first; figures and all actions follow beneath it.
        self.hero = tk.Canvas(self.body, background=C['purple'], height=290,
                              highlightthickness=0)
        self.hero.pack(fill='x')
        assets = Path(__file__).resolve().parents[1] / 'assets'
        path = assets / 'warehouse_hd.png'
        if not path.exists():
            path = assets / 'warehouse.png'
        try:
            self.warehouse_image = tk.PhotoImage(master=self, file=str(path))
        except tk.TclError:
            self.warehouse_image = None
        self._photo_scale = None
        self._photo_display = None
        self.hero.bind('<Configure>', self._render_photo)

        caption = tk.Frame(self.body, background=C['peach'], padx=20, pady=14)
        caption.pack(fill='x')
        ttk.Button(caption, text='Xem tồn kho',
                   command=lambda: self.navigate('inventory')).pack(side='right')
        tk.Label(caption, text='Quản lý kho', background=C['peach'],
                 foreground=C['ink'], font=(theme.FONT, 20, 'bold')).pack(anchor='w')
        tk.Label(caption, text='Theo dõi hàng hóa, nhập xuất và tồn kho mỗi ngày.',
                 background=C['peach'], foreground=C['muted'],
                 font=(theme.FONT, 11)).pack(anchor='w', pady=(3, 0))

    def _render_photo(self, event):
        width, height = event.width, event.height
        self.hero.delete('all')
        if self.warehouse_image is None:
            self.hero.create_text(width / 2, height / 2, text='QUẢN LÝ KHO',
                                  fill='white', font=(theme.FONT, 24, 'bold'))
            return
        # Downsample only. Never enlarge a small asset into visible square pixels.
        scale = max(1, min(self.warehouse_image.width() // max(1, width),
                           self.warehouse_image.height() // max(1, height)))
        if scale != self._photo_scale:
            self._photo_display = self.warehouse_image.subsample(scale)
            self._photo_scale = scale
        self.hero.create_image(width / 2, height / 2, image=self._photo_display)

    def _build_metrics(self):
        heading = tk.Frame(self.body, background=C['surface'])
        heading.pack(fill='x', pady=(22, 10))
        tk.Label(heading, text='Kho hàng của bạn', font=(theme.FONT, 14, 'bold'),
                 background=C['surface'], foreground=C['ink']).pack(side='left')
        self.data_hint = tk.Label(heading, text='Đang tải số liệu…', background=C['surface'],
                                  foreground=C['muted'], font=(theme.FONT, 11))
        self.data_hint.pack(side='right')
        cards = tk.Frame(self.body, background=C['surface'])
        cards.pack(fill='x')
        self.metrics = {}
        self.metric_panels = []
        definitions = [('products', 'Sản phẩm', 'Trong danh mục', C['lavender']),
                       ('suppliers', 'Nhà cung cấp', 'Đối tác nhập hàng', C['pink']),
                       ('low', 'Dưới mức tối thiểu', 'Sản phẩm cần bổ sung', C['peach']),
                       ('value', 'Giá trị tồn - VND', 'Theo đơn giá hiện tại', C['mint'])]
        for column, (key, title, hint, color) in enumerate(definitions):
            cards.columnconfigure(column, weight=1, uniform='metric')
            panel = RoundedPanel(cards, color, padding=12, width=180)
            panel.grid(row=0, column=column, sticky='nsew', padx=(0, 12 if column < 3 else 0))
            self.metric_panels.append(panel)
            card = panel.content
            tk.Label(card, text=title, background=color, foreground=C['ink'],
                     font=(theme.FONT, 11, 'bold')).pack(anchor='w')
            value = tk.Label(card, text='—', background=color, foreground=C['ink'],
                             font=(theme.FONT, 21 if key != 'value' else 18, 'bold'))
            value.pack(anchor='w', pady=(5, 2))
            tk.Label(card, text=hint, background=color, foreground=C['muted'], font=(theme.FONT, 11)).pack(anchor='w')
            self.metrics[key] = value
        cards.bind('<Configure>', self._arrange_metrics)

    def _arrange_metrics(self, event):
        columns = 4 if event.width >= 1000 else 2
        for column in range(4):
            event.widget.columnconfigure(column, weight=1 if column < columns else 0,
                                         uniform='metric' if column < columns else '')
        for index, panel in enumerate(self.metric_panels):
            panel.grid(row=index // columns, column=index % columns,
                       padx=(0, 12 if index % columns < columns - 1 else 0), pady=(0, 10))

    def _build_actions(self):
        bottom = tk.Frame(self.body, background=C['surface'])
        bottom.pack(fill='x', pady=(20, 0))
        bottom.columnconfigure(0, weight=1, uniform='bottom')
        bottom.columnconfigure(1, weight=1, uniform='bottom')
        actions_panel = RoundedPanel(bottom, '#F4EFF7', width=350)
        actions_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 12))
        actions = actions_panel.content
        tk.Label(actions, text='Bắt đầu công việc', background='#F4EFF7', foreground=C['ink'],
                 font=(theme.FONT, 13, 'bold')).pack(anchor='w')
        tk.Label(actions, text='Ghi nhận hàng đến và hàng rời kho.', background='#F4EFF7',
                 foreground=C['muted'], font=(theme.FONT, 11)).pack(anchor='w', pady=(5, 12))
        buttons = tk.Frame(actions, background='#F4EFF7')
        buttons.pack(anchor='w')
        ttk.Button(buttons, text='Nhập kho', style='Home.Primary.TButton',
                   command=lambda: self.navigate('receipts')).pack(side='left', padx=(0, 8))
        ttk.Button(buttons, text='Xuất kho', style='Home.Primary.TButton', command=lambda: self.navigate('issues')).pack(side='left')
        attention_panel = RoundedPanel(bottom, '#FBF0E8', width=350)
        attention_panel.grid(row=0, column=1, sticky='nsew')
        attention = attention_panel.content
        tk.Label(attention, text='Cần chú ý', background='#FBF0E8', foreground=C['error'],
                 font=(theme.FONT, 13, 'bold')).pack(anchor='w')
        self.attention = tk.Label(attention, text='Đang tải…', background='#FBF0E8', foreground=C['error'],
                                  font=(theme.FONT, 11, 'bold'), justify='left', wraplength=400)
        self.attention.pack(anchor='w', pady=(5, 3))
        self.attention_hint = tk.Label(attention, text='Xem tồn kho để lên kế hoạch nhập thêm.',
                                       background='#FBF0E8', foreground=C['muted'],
                                       font=(theme.FONT, 11), justify='left', wraplength=400)
        self.attention_hint.pack(anchor='w', pady=(0, 9))
        attention.bind('<Configure>', lambda event: [label.configure(wraplength=max(160, event.width))
                        for label in (self.attention, self.attention_hint)], add='+')
        ttk.Button(attention, text='Xem hàng tồn thấp', command=lambda: self.navigate('low_stock')).pack(anchor='w')

    def refresh(self):
        # Do not present previous figures as current if a database read fails.
        for label in self.metrics.values():
            label.configure(text='—')
        self.attention.configure(text='Chưa tải được số liệu. Hãy bấm Làm mới để thử lại.', foreground=C['error'])
        self.attention_hint.configure(text='')
        self.data_hint.configure(text='Chưa có số liệu mới')
        report = inventory_report(self.context.stock_service.list_inventory())
        suppliers = self.context.supplier_service.list_suppliers()
        self.metrics['products'].configure(text=str(report['product_count']))
        self.metrics['suppliers'].configure(text=str(len(suppliers)))
        self.metrics['low'].configure(text=str(report['low_count']))
        self.metrics['value'].configure(text=f"{report['total_value']:,.2f}")
        empty = sum(bool(row['active']) and row['stock'] == 0 for row in report['rows'])
        needs_attention = report['low_count'] > 0 or empty > 0
        self.attention.configure(text=f"{report['low_count']} sản phẩm dưới mức tối thiểu - {empty} sản phẩm hết hàng",
                                 foreground=C['error'] if needs_attention else C['success'])
        self.attention_hint.configure(text='Xem tồn kho để lên kế hoạch nhập thêm.' if needs_attention else
                                      'Các sản phẩm đang dùng đều đủ mức tồn tối thiểu.')
        self.data_hint.configure(text='Dữ liệu mẫu' if self.context.demo else 'Đã cập nhật từ MySQL')
        self.update_idletasks()
        self.canvas.yview_moveto(0)
