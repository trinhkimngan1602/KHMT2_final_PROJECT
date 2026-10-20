from tkinter import ttk


class BasePage(ttk.Frame):
    """Every team page keeps this constructor and refresh method."""
    def __init__(self, parent, context, on_changed):
        super().__init__(parent, padding=16)
        self.context = context
        self.on_changed = on_changed
        self.bind('<Configure>', self.wrap_descriptions)

    def wrap_descriptions(self, event):
        for widget in self.winfo_children():
            if isinstance(widget, ttk.Label):
                widget.configure(wraplength=max(300, event.width - 36))

    def refresh(self):
        pass


class PlaceholderPage(BasePage):
    def __init__(self, parent, context, on_changed, owner, description):
        super().__init__(parent, context, on_changed)
        ttk.Label(self, text=f'Phần bàn giao cho {owner}', style='Heading.TLabel').pack(anchor='w')
        ttk.Label(self, text=description, wraplength=760, justify='left').pack(anchor='w', pady=16)
        ttk.Label(self, text='Màn hình khung ngày 1. Chưa có thao tác ghi dữ liệu ở đây.\n'
                  'Hướng dẫn lớp màn hình, dữ liệu và tên hàm nằm trong CONTRACT.md.',
                  wraplength=760, justify='left').pack(anchor='w')
