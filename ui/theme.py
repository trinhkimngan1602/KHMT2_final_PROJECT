"""Pastel palette shared by the standard Tkinter/ttk interface."""
from tkinter import ttk, font
from .appearance import ButtonSkin

FONT = 'Segoe UI'

COLORS = dict(background='#F7F0EF', surface='#FFFCF8', sidebar='#F4E7EB', ink='#393349',
              muted='#766A7C', purple='#655578', lavender='#EBE3F4', peach='#F8E2D7',
              pink='#F6DFE5', mint='#E6EFE9', border='#DDD2DC', accent='#F37C38',
              success='#35634F', error='#A13649')


def apply_theme(root):
    c = COLORS
    global FONT
    families = font.families(root)
    # Static Windows fonts render Vietnamese consistently in Tk, including đ.
    FONT = 'Segoe UI' if 'Segoe UI' in families else 'Arial'
    for name in ('TkDefaultFont', 'TkTextFont', 'TkMenuFont'):
        font.nametofont(name, root=root).configure(family=FONT, size=11)
    root.configure(background=c['background'])
    root.option_add('*TCombobox*Listbox.font', ('Segoe UI', 10))
    root.option_add('*TCombobox*Listbox.background', c['surface'])
    root.option_add('*TCombobox*Listbox.foreground', c['ink'])
    root.option_add('*TCombobox*Listbox.selectBackground', c['lavender'])
    root.option_add('*TCombobox*Listbox.selectForeground', c['ink'])
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('.', font=('Segoe UI', 10), background=c['surface'], foreground=c['ink'])
    style.configure('TFrame', background=c['surface'])
    style.configure('TLabel', background=c['surface'], foreground=c['ink'])
    style.configure('Heading.TLabel', font=('Segoe UI', 20, 'bold'), foreground=c['ink'])
    style.configure('Muted.TLabel', foreground=c['muted'])
    style.configure('TButton', padding=(14, 9), background='#EEEAE6', foreground='#514A45',
                    borderwidth=0, focusthickness=2, focuscolor=c['purple'], font=('Segoe UI', 10, 'bold'))
    style.map('TButton', background=[('disabled', '#F0ECEF'), ('pressed', '#D5CCC3'), ('active', '#E1DAD2')],
              foreground=[('disabled', '#948A96')])
    style.configure('Primary.TButton', background=c['accent'], foreground='#342016', focuscolor='#81330C')
    style.map('Primary.TButton', background=[('disabled', '#F3D8C7'), ('pressed', '#DE692B'), ('active', '#FF914F')],
              foreground=[('disabled', '#75696A'), ('!disabled', '#342016')])
    style.configure('TEntry', padding=(9, 7), fieldbackground='white', bordercolor=c['border'],
                    lightcolor=c['border'], darkcolor=c['border'])
    style.map('TEntry', bordercolor=[('focus', c['purple'])], fieldbackground=[('readonly', '#F1EBF3')])
    style.configure('TCombobox', padding=(8, 7), fieldbackground='white', background=c['lavender'],
                    bordercolor=c['border'], arrowcolor=c['purple'])
    style.map('TCombobox', fieldbackground=[('readonly', 'white')], selectbackground=[('readonly', 'white')],
              selectforeground=[('readonly', c['ink'])], bordercolor=[('focus', c['purple'])])
    style.configure('TCheckbutton', padding=(4, 5), background=c['surface'])
    style.map('TCheckbutton', background=[('active', c['surface'])], indicatorbackground=[('selected', c['purple'])])
    style.configure('Treeview', background='white', fieldbackground='white', foreground=c['ink'],
                    rowheight=34, borderwidth=0, font=('Segoe UI', 10), bordercolor=c['border'],
                    lightcolor=c['border'], darkcolor=c['border'])
    style.configure('Treeview.Heading', background=c['lavender'], foreground=c['purple'],
                    relief='flat', padding=(10, 10), font=('Segoe UI', 10, 'bold'))
    style.map('Treeview', background=[('selected', '#DDD0EE')], foreground=[('selected', c['ink'])])
    style.map('Treeview.Heading', background=[('active', '#DFD2ED')])
    style.configure('TScrollbar', background='#D7C9DC', troughcolor=c['surface'],
                    arrowcolor=c['purple'], borderwidth=0, arrowsize=12)
    style.map('TScrollbar', background=[('active', '#BBA7C8')])
    # The sidebar supplies navigation; Notebook still manages the page widgets.
    style.configure('Workspace.TNotebook', background=c['surface'], borderwidth=0, tabmargins=0,
                    bordercolor=c['surface'], lightcolor=c['surface'], darkcolor=c['surface'])
    style.layout('Workspace.TNotebook.Tab', [])
    style.configure('Nav.TButton', background=c['sidebar'], foreground=c['muted'],
                    anchor='w', padding=(16, 11), font=('Segoe UI', 10))
    style.map('Nav.TButton', background=[('active', '#EADCE6')], foreground=[('active', c['ink'])])
    style.configure('Selected.Nav.TButton', background=c['purple'], foreground='white', font=('Segoe UI', 10, 'bold'))
    style.map('Selected.Nav.TButton', background=[('active', '#554566')], foreground=[('!disabled', 'white')])
    # Resolve the font on this machine, without downloading any font files.
    for name in ('.', 'TButton', 'Treeview', 'Treeview.Heading', 'Nav.TButton', 'Selected.Nav.TButton'):
        bold = name in ('TButton', 'Treeview.Heading', 'Selected.Nav.TButton')
        style.configure(name, font=(FONT, 11, 'bold' if bold else 'normal'))
    style.configure('Heading.TLabel', font=(FONT, 21, 'bold'))
    style.configure('Treeview', rowheight=38)
    style.configure('TButton', padding=(10, 4))
    style.configure('Nav.TButton', padding=(10, 2))
    root.option_add('*TCombobox*Listbox.font', (FONT, 11))
    root.button_skin = ButtonSkin(root, style)
    root.button_skin.install('TButton', '#EEEAE6', '#E5DDD6', '#D9CEC5', '#F0ECE9')
    root.button_skin.install('Primary.TButton', c['accent'], '#FF914F', '#DE692B', '#F3D8C7')
    root.button_skin.install('Nav.TButton', c['sidebar'], '#EADCE6', '#DACCD8', '#F0ECE9', c['sidebar'])
    root.button_skin.install('Selected.Nav.TButton', c['purple'], '#706082', '#554566', '#DDD2DC', '#DBCDD7')
    # Paint the surrounding corners in the surface color; the images supply fills.
    for name in ('TButton', 'Primary.TButton', 'Nav.TButton', 'Selected.Nav.TButton'):
        style.map(name, background=[])
        style.configure(name, background=c['sidebar'] if 'Nav.' in name else c['surface'])
    style.configure('Home.Primary.TButton', background='#F4EFF7')
    return style
