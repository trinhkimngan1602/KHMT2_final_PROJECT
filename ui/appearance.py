"""Rounded surfaces drawn with Tkinter only."""
import math
import tkinter as tk


class ButtonSkin:
    """Image borders keep ttk keyboard, focus and disabled behavior intact."""
    def __init__(self, root, style):
        self.root = root
        self.style = style
        self.images = []

    def _image(self, fill, shadow, pressed=False):
        image = tk.PhotoImage(master=self.root, width=32, height=32)
        # A fixed corner radius survives ttk's nine-part image stretching.
        for color, top, bottom in [(shadow, 3, 31), (fill, 2 if pressed else 0, 29)]:
            radius = 6
            for y in range(top, bottom):
                edge = min(y - top, bottom - 1 - y)
                inset = math.ceil(radius - math.sqrt(max(0, radius ** 2 - (radius - edge - .5) ** 2))) if edge < radius else 0
                image.put(color, to=(1 + inset, y, 31 - inset, y + 1))
        self.images.append(image)
        return image

    def install(self, name, normal, hover, pressed, disabled, shadow='#D8CDC7'):
        images = [self._image(normal, shadow), self._image(hover, shadow),
                  self._image(pressed, shadow, True), self._image(disabled, '#E6DFDA')]
        element = name + '.rounded'
        self.style.element_create(element, 'image', images[0],
                                  ('disabled', images[3]), ('pressed', images[2]),
                                  ('active', images[1]), border=9, sticky='nsew')
        self.style.layout(name, [(element, {'sticky': 'nsew', 'children': [
            ('Button.focus', {'sticky': 'nsew', 'children': [
                ('Button.padding', {'sticky': 'nsew', 'children': [
                    ('Button.label', {'sticky': 'nsew'})]})]})]})])


class RoundedPanel(tk.Canvas):
    """A small rounded card with a subtle two-pixel shadow and normal children."""
    def __init__(self, parent, color, padding=16, **kwargs):
        super().__init__(parent, background=parent.cget('background'),
                         highlightthickness=0, borderwidth=0, height=120, **kwargs)
        self.color = color
        self.padding = padding
        self.content = tk.Frame(self, background=color)
        self.window = self.create_window(padding, padding, anchor='nw', window=self.content)
        self.bind('<Configure>', self._draw)
        self.content.bind('<Configure>', self._resize)

    def _resize(self, event):
        height = self.content.winfo_reqheight() + self.padding * 2 + 3
        if self.winfo_reqheight() != height:
            self.configure(height=height)

    def _round_rect(self, x, y, width, height, color):
        r = 8
        self.create_polygon(x+r, y, width-r, y, width, y, width, y+r,
                            width, height-r, width, height, width-r, height,
                            x+r, height, x, height, x, height-r, x, y+r, x, y,
                            smooth=True, splinesteps=16, fill=color, outline='', tags='surface')

    def _draw(self, event):
        self.delete('surface')
        self._round_rect(1, 3, event.width-1, event.height-1, '#DED5D0')
        self._round_rect(0, 0, event.width-2, event.height-4, self.color)
        self.tag_lower('surface')
        self.itemconfigure(self.window, width=max(1, event.width - self.padding * 2 - 2))
