"""Small reusable Tkinter helpers; database work stays in services."""
from tkinter import ttk

MOVEMENT_LABELS = {'IN': 'Nhập', 'OUT': 'Xuất', 'ADJUST_IN': 'Điều chỉnh tăng',
                   'ADJUST_OUT': 'Điều chỉnh giảm'}


def make_table(parent, columns, height=10):
    holder = ttk.Frame(parent)
    holder.pack(fill='both', expand=True)
    table = ttk.Treeview(holder, columns=[col[0] for col in columns], show='headings', height=height)
    for key, title, width in columns:
        table.heading(key, text=title)
        table.column(key, width=width, minwidth=width, anchor='w')
    vertical = ttk.Scrollbar(holder, orient='vertical', command=table.yview)
    horizontal = ttk.Scrollbar(holder, orient='horizontal', command=table.xview)
    table.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
    table.grid(row=0, column=0, sticky='nsew')
    vertical.grid(row=0, column=1, sticky='ns')
    horizontal.grid(row=1, column=0, sticky='ew')
    holder.rowconfigure(0, weight=1)
    holder.columnconfigure(0, weight=1)
    return table


def fill_choices(combo, variable, old_mapping, rows, label, include_all=False):
    """Keep selected database ID even when a name changes."""
    old_id = old_mapping.get(variable.get())
    mapping = {'Tất cả sản phẩm': None} if include_all else {}
    mapping.update((label(row), row['id']) for row in rows)
    combo.configure(values=list(mapping))
    chosen = next((text for text, row_id in mapping.items() if row_id == old_id), '')
    # A vanished selection must not silently target a different product/supplier.
    # Only history has an explicit default meaning: all products.
    if not chosen and include_all:
        chosen = next(iter(mapping))
    variable.set(chosen)
    return mapping
