import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from database import StorageError
from .theme import COLORS as C, apply_theme
from . import theme
from .products_page import ProductsPage
from .inventory_page import InventoryPage
from .suppliers_page import SuppliersPage
from .receipts_page import ReceiptsPage
from .adjustments_page import AdjustmentsPage
from .issues_page import IssuesPage
from .history_page import HistoryPage
from .home_page import HomePage


class WarehouseApp(tk.Tk):
    PAGE_SPECS = [('products', 'Sản phẩm', ProductsPage), ('inventory', 'Tồn kho', InventoryPage),
                  ('suppliers', 'Nhà cung cấp', SuppliersPage), ('receipts', 'Nhập kho', ReceiptsPage),
                  ('adjustments', 'Điều chỉnh', AdjustmentsPage), ('issues', 'Xuất kho', IssuesPage),
                  ('history', 'Lịch sử', HistoryPage)]

    def __init__(self, context):
        super().__init__()
        self.context = context
        self.title('Quản lý kho')
        width = min(1360, self.winfo_screenwidth() - 60)
        height = min(770, self.winfo_screenheight() - 110)
        self.geometry(f'{width}x{height}+{max(0, (self.winfo_screenwidth() - width) // 2)}+25')
        self.minsize(1120, 660)
        self.style = apply_theme(self)
        sidebar = tk.Frame(self, background=C['sidebar'], width=204)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        workspace = tk.Frame(self, background=C['background'])
        workspace.pack(side='right', fill='both', expand=True)
        self._build_header(workspace)
        footer = tk.Frame(workspace, background=C['background'], padx=22, pady=9)
        footer.pack(side='bottom', fill='x')
        self.status = tk.Label(footer, text='Đang nạp dữ liệu…', background=C['background'],
                               foreground=C['muted'], font=(theme.FONT, 11))
        self.status.pack(side='left')
        tk.Label(footer, text='Quản lý kho - Nhập - Xuất - Tồn', background=C['background'],
                 foreground=C['muted'], font=(theme.FONT, 11)).pack(side='right')
        self.notebook = ttk.Notebook(workspace, style='Workspace.TNotebook')
        self.pages = []
        self.page_by_key = {}
        for key, title, page_class in self.PAGE_SPECS:
            page = page_class(self.notebook, context, self.on_changed)
            self.pages.append(page)
            self.page_by_key[key] = page
            self.notebook.add(page, text=title)
        self.home_page = HomePage(self.notebook, context, self.on_changed, self.show_page)
        self.pages.append(self.home_page)
        self.page_by_key['home'] = self.home_page
        self.notebook.add(self.home_page, text='Trang chủ')
        self.notebook.pack(fill='both', expand=True, padx=18)
        self._build_sidebar(sidebar)
        self.build_menu()
        self.notebook.bind('<<NotebookTabChanged>>', lambda event: self.on_changed())
        self.notebook.select(self.home_page)
        self._initial_refresh = self.after(100, self.on_changed)
        self.protocol('WM_DELETE_WINDOW', self.confirm_exit)

    def _build_header(self, parent):
        header = tk.Frame(parent, background=C['background'], padx=24, pady=17)
        header.pack(fill='x')
        text = tk.Frame(header, background=C['background'])
        text.pack(side='left')
        tk.Label(text, text='QUẢN LÝ KHO', background=C['background'], foreground=C['muted'],
                 font=(theme.FONT, 11, 'bold')).pack(anchor='w')
        self.page_title = tk.Label(text, text='Tổng quan kho hàng', background=C['background'],
                                    foreground=C['ink'], font=(theme.FONT, 18, 'bold'))
        self.page_title.pack(anchor='w', pady=(3, 0))
        ttk.Button(header, text='Làm mới', command=self.on_changed).pack(side='right')
        mode = 'BẢN MẪU - không lưu' if self.context.demo else 'MYSQL - dữ liệu được lưu'
        tk.Label(header, text=mode, background=C['lavender'] if self.context.demo else C['mint'],
                 foreground=C['purple'] if self.context.demo else C['success'],
                 padx=12, pady=8, font=('Arial', 11, 'bold')).pack(side='right', padx=14)

    def _build_sidebar(self, sidebar):
        brand = tk.Frame(sidebar, background=C['sidebar'], padx=18, pady=16)
        brand.pack(fill='x')
        icon = tk.Canvas(brand, width=36, height=36, background=C['purple'], highlightthickness=0)
        icon.pack(anchor='w')
        icon.create_line(7, 16, 18, 8, 29, 16, fill='white', width=2)
        icon.create_rectangle(9, 16, 27, 29, outline='white', width=2)
        icon.create_line(18, 17, 18, 28, fill='white', width=2)
        tk.Label(brand, text='QUẢN LÝ KHO', background=C['sidebar'], foreground=C['ink'],
                 font=(theme.FONT, 12, 'bold')).pack(anchor='w', pady=(10, 0))
        tk.Label(brand, text='Nhập xuất tồn', background=C['sidebar'],
                 foreground=C['muted'], font=(theme.FONT, 11)).pack(anchor='w', pady=(3, 0))
        tk.Label(sidebar, text='ĐIỀU HƯỚNG', background=C['sidebar'], foreground=C['muted'],
                 font=(theme.FONT, 11, 'bold')).pack(anchor='w', padx=22, pady=(8, 10))
        self.nav_buttons = {}
        order = [('home', 'Trang chủ')] + [(key, title) for key, title, _ in self.PAGE_SPECS]
        for key, title in order:
            button = ttk.Button(sidebar, text=title, style='Nav.TButton', command=lambda key=key: self.show_page(key))
            button.pack(fill='x', padx=12, pady=3)
            self.nav_buttons[key] = button
        bottom = tk.Frame(sidebar, background=C['sidebar'], padx=18, pady=18)
        bottom.pack(side='bottom', fill='x')
        ttk.Button(bottom, text='Hướng dẫn nhanh', command=self.show_help).pack(fill='x')
        tk.Label(bottom, text=date.today().strftime('Ngày %d/%m/%Y'), background=C['sidebar'],
                 foreground=C['muted'], font=(theme.FONT, 11)).pack(anchor='w', pady=(12, 0))

    def show_page(self, key):
        if key == 'low_stock':
            page = self.page_by_key['inventory']
            page.clear_filters()
            page.low_only.set(True)
        else:
            page = self.page_by_key[key]
        already_selected = self.notebook.select() == str(page)
        self.notebook.select(page)
        if already_selected:
            self.on_changed()

    def build_menu(self):
        menu = tk.Menu(self, tearoff=False)
        application = tk.Menu(menu, tearoff=False)
        application.add_command(label='Làm mới trang hiện tại', command=self.on_changed)
        application.add_command(label='Xuất toàn bộ tồn kho CSV', command=self.page_by_key['history'].export_csv)
        application.add_separator()
        application.add_command(label='Thoát', command=self.confirm_exit)
        menu.add_cascade(label='Ứng dụng', menu=application)
        navigation = tk.Menu(menu, tearoff=False)
        navigation.add_command(label='Trang chủ', command=lambda: self.show_page('home'))
        for key, title, _ in self.PAGE_SPECS:
            navigation.add_command(label=title, command=lambda key=key: self.show_page(key))
        menu.add_cascade(label='Chức năng', menu=navigation)
        help_menu = tk.Menu(menu, tearoff=False)
        help_menu.add_command(label='Hướng dẫn nhanh', command=self.show_help)
        menu.add_cascade(label='Trợ giúp', menu=help_menu)
        self.configure(menu=menu)

    def show_help(self):
        mode = ('Bản mẫu: thay đổi mất khi đóng ứng dụng.' if self.context.demo else
                'Bản MySQL: giao dịch đã lưu được giữ khi đóng ứng dụng.')
        messagebox.showinfo('Hướng dẫn nhanh',
            'Trang chủ hiển thị số liệu tổng quan. Dùng thanh bên trái để mở từng chức năng.\n\n'
            '1. Thêm sản phẩm và nhà cung cấp.\n'
            '2. Nhập kho để tăng tồn; xuất kho để giảm tồn.\n'
            '3. Khi kiểm kê chênh lệch, điều chỉnh Tăng/Giảm và ghi lý do.\n'
            '4. Xem số lượng, cảnh báo và giá trị ở mục Tồn kho.\n'
            '5. Lọc giao dịch và xuất CSV ở mục Lịch sử.\n\n'
            'Số lượng là số nguyên dương. Không thể xuất hoặc giảm quá tồn.\n'
            'Vàng: tồn dưới mức tối thiểu. Đỏ: hết hàng.\n\n' + mode, parent=self)

    def confirm_exit(self):
        detail = ('Dữ liệu trong bản mẫu sẽ mất khi đóng ứng dụng.' if self.context.demo else
                  'Dữ liệu đã lưu trong MySQL vẫn được giữ lại.')
        if messagebox.askyesno('Xác nhận thoát',
                              'Bạn có chắc muốn thoát ứng dụng không?\n\n'
                              'Thông tin đang nhập nhưng chưa bấm lưu sẽ không được lưu.\n' + detail,
                              parent=self, default=messagebox.NO):
            self.destroy()

    def destroy(self):
        self.after_cancel(self._initial_refresh)
        super().destroy()

    def on_changed(self):
        if not self.notebook.select():
            return
        page = self.pages[self.notebook.index('current')]
        key = next(key for key, value in self.page_by_key.items() if value is page)
        for name, button in self.nav_buttons.items():
            button.configure(style='Selected.Nav.TButton' if name == key else 'Nav.TButton')
        self.page_title.configure(text='Tổng quan kho hàng' if key == 'home' else self.notebook.tab(page, 'text'))
        try:
            page.refresh()
        except (StorageError, ValueError) as exc:
            self.status.configure(text=str(exc), foreground=C['error'])
        else:
            self.status.configure(text='Dữ liệu mẫu đã nạp.' if self.context.demo else 'Sẵn sàng.', foreground=C['success'])
