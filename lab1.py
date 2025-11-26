import tkinter as tk
from tkinter import ttk, colorchooser


def rgb_to_cmyk(r, g, b):
    if (r, g, b) == (0, 0, 0):
        return 0, 0, 0, 1

    c = 1 - r / 255
    m = 1 - g / 255
    y = 1 - b / 255

    k = min(c, m, y)

    c = (c - k) / (1 - k) if k != 1 else 0
    m = (m - k) / (1 - k) if k != 1 else 0
    y = (y - k) / (1 - k) if k != 1 else 0

    return c, m, y, k


def cmyk_to_rgb(c, m, y, k):
    r = 255 * (1 - c) * (1 - k)
    g = 255 * (1 - m) * (1 - k)
    b = 255 * (1 - y) * (1 - k)
    return int(round(r)), int(round(g)), int(round(b))



def rgb_to_hls(r, g, b):
    r, g, b = r / 255, g / 255, b / 255
    max_val = max(r, g, b)
    min_val = min(r, g, b)

    l = (max_val + min_val) / 2

    if max_val == min_val:
        return 0, l, 0

    d = max_val - min_val

    s = d / (2 - max_val - min_val) if l > 0.5 else d / (max_val + min_val)

    if max_val == r:
        h = (g - b) / d % 6
    elif max_val == g:
        h = (b - r) / d + 2
    else:
        h = (r - g) / d + 4

    h *= 60

    return h, l, s


def hls_to_rgb(h, l, s):
    h = h % 360
    h = h / 360

    def f(n):
        k = (n + h * 12) % 12
        a = s * min(l, 1 - l)
        return l - a * max(-1, min(min(k - 3, 9 - k), 1))

    r = int(round(f(0) * 255))
    g = int(round(f(8) * 255))
    b = int(round(f(4) * 255))
    return r, g, b



class ColorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Конвертер цветов: CMYK ↔ RGB ↔ HLS')
        self.resizable(False, False)

        
        self.rgb = {c: tk.IntVar(value=128) for c in 'RGB'}
        self.cmyk = {c: tk.DoubleVar(value=0.0) for c in 'CMYK'}
        self.hls = {
            'H': tk.DoubleVar(value=0.0),
            'L': tk.DoubleVar(value=0.5),
            'S': tk.DoubleVar(value=0.5)
        }

        self.updating = False

        
        self.build_ui()
        self.update_from_rgb()

    def build_ui(self):
        root = ttk.Frame(self, padding=12)
        root.pack(fill='both', expand=True)

        
        title = ttk.Label(root, text="Color Converter — вертикальный UI", font=('Segoe UI', 11, 'bold'))
        title.pack(anchor='w', pady=(0,8))

        
        col = ttk.Frame(root)
        col.pack(side='left', fill='both', expand=True)

        
        rgb_f = ttk.LabelFrame(col, text='RGB (0–255)', padding=8)
        rgb_f.pack(fill='x', pady=6)

        self.rgb_entries = {}
        self.rgb_scales = {}
        for i, c in enumerate('RGB'):
            row = ttk.Frame(rgb_f)
            row.pack(fill='x', pady=3)

            lbl = ttk.Label(row, text=c, width=3)
            lbl.pack(side='left')

            scale = ttk.Scale(row, from_=0, to=255, variable=self.rgb[c], orient='horizontal')
            scale.pack(side='left', fill='x', expand=True, padx=6)
            scale.bind('<ButtonPress-1>', lambda e, cc=c: self.on_rgb_drag_start(cc))
            scale.bind('<ButtonRelease-1>', lambda e, cc=c: self.on_rgb_drag_end(cc))
            self.rgb_scales[c] = scale

            entry = ttk.Entry(row, width=6, textvariable=self.rgb[c])
            entry.pack(side='left', padx=6)
            entry.bind('<Return>', lambda e, cc=c: self.on_rgb_entry(cc))
            self.rgb_entries[c] = entry

        
        cmyk_f = ttk.LabelFrame(col, text='CMYK (0–1)', padding=8)
        cmyk_f.pack(fill='x', pady=6)

        self.cmyk_entries = {}
        self.cmyk_scales = {}
        for i, c in enumerate('CMYK'):
            row = ttk.Frame(cmyk_f)
            row.pack(fill='x', pady=3)

            lbl = ttk.Label(row, text=c, width=3)
            lbl.pack(side='left')

            scale = ttk.Scale(row, from_=0.0, to=1.0, variable=self.cmyk[c], orient='horizontal')
            scale.pack(side='left', fill='x', expand=True, padx=6)
            scale.bind('<ButtonPress-1>', lambda e, cc=c: self.on_cmyk_drag_start(cc))
            scale.bind('<ButtonRelease-1>', lambda e, cc=c: self.on_cmyk_drag_end(cc))
            self.cmyk_scales[c] = scale

            entry = ttk.Entry(row, width=6, textvariable=self.cmyk[c])
            entry.pack(side='left', padx=6)
            entry.bind('<Return>', lambda e, cc=c: self.on_cmyk_entry(cc))
            self.cmyk_entries[c] = entry

        
        hls_f = ttk.LabelFrame(col, text='HLS (H 0–360, L/S 0–1)', padding=8)
        hls_f.pack(fill='x', pady=6)

        self.hls_entries = {}
        self.hls_scales = {}

        ranges = {'H': (0, 360), 'L': (0, 1), 'S': (0, 1)}
        for i, c in enumerate(['H', 'L', 'S']):
            row = ttk.Frame(hls_f)
            row.pack(fill='x', pady=3)

            lbl = ttk.Label(row, text=c, width=3)
            lbl.pack(side='left')

            lo, hi = ranges[c]
            scale = ttk.Scale(row, from_=lo, to=hi, variable=self.hls[c], orient='horizontal')
            scale.pack(side='left', fill='x', expand=True, padx=6)
            scale.bind('<ButtonPress-1>', lambda e, cc=c: self.on_hls_drag_start(cc))
            scale.bind('<ButtonRelease-1>', lambda e, cc=c: self.on_hls_drag_end(cc))
            self.hls_scales[c] = scale

            entry = ttk.Entry(row, width=7, textvariable=self.hls[c])
            entry.pack(side='left', padx=6)
            entry.bind('<Return>', lambda e, cc=c: self.on_hls_entry(cc))
            self.hls_entries[c] = entry

        
        bottom = ttk.Frame(root, padding=8)
        bottom.pack(side='right', fill='y', padx=12, pady=6)

    
        self.swatch = tk.Label(bottom, text='', bg='#808080', width=28, height=10, relief='ridge')
        self.swatch.pack(pady=(0,12))

        btn_pick = ttk.Button(bottom, text='Выбрать цвет', command=self.pick_color)
        btn_pick.pack(fill='x', pady=(0,6))

        
        self.warn = ttk.Label(bottom, text='', foreground='orange')
        self.warn.pack()

    def on_rgb_drag_start(self, c):
        
        self.rgb_scales[c].bind('<Motion>', lambda e, cc=c: self.update_from_rgb())

    def on_rgb_drag_end(self, c):
        self.rgb_scales[c].unbind('<Motion>')
        self.update_from_rgb()

    def on_rgb_entry(self, c):
        try:
            v = max(0, min(255, int(self.rgb[c].get())))
            self.rgb[c].set(v)
            self.update_from_rgb()
        except:
            pass


    def on_hls_drag_start(self, c):
        self.hls_scales[c].bind('<Motion>', lambda e, cc=c: self.update_from_hls())

    def on_hls_drag_end(self, c):
        self.hls_scales[c].unbind('<Motion>')
        self.update_from_hls()

    def on_hls_entry(self, c):
        try:
            lo, hi = (0, 360) if c == 'H' else (0, 1)
            v = float(self.hls[c].get())
            v = max(lo, min(hi, v))
            self.hls[c].set(v)
            self.update_from_hls()
        except:
            pass


    def on_cmyk_drag_start(self, c):
        self.cmyk_scales[c].bind('<Motion>', lambda e, cc=c: self.update_from_cmyk())

    def on_cmyk_drag_end(self, c):
        self.cmyk_scales[c].unbind('<Motion>')
        self.update_from_cmyk()

    def on_cmyk_entry(self, c):
        try:
            v = float(self.cmyk[c].get())
            v = max(0, min(1, v))
            self.cmyk[c].set(v)
            self.update_from_cmyk()
        except:
            pass

    
    def update_from_rgb(self):
        if self.updating: return
        self.updating = True

        r, g, b = self.rgb['R'].get(), self.rgb['G'].get(), self.rgb['B'].get()

    
        h, l, s = rgb_to_hls(r, g, b)
        self.hls['H'].set(round(h, 1))
        self.hls['L'].set(round(l, 3))
        self.hls['S'].set(round(s, 3))

        
        c, m, y, k = rgb_to_cmyk(r, g, b)
        self.cmyk['C'].set(round(c, 3))
        self.cmyk['M'].set(round(m, 3))
        self.cmyk['Y'].set(round(y, 3))
        self.cmyk['K'].set(round(k, 3))

        self.set_swatch(r, g, b)
        self.warn.config(text='')
        self.updating = False

    def update_from_hls(self):
        if self.updating: return
        self.updating = True

        h = float(self.hls['H'].get())
        l = float(self.hls['L'].get())
        s = float(self.hls['S'].get())

        
        r, g, b = hls_to_rgb(h, l, s)

        clipped = not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255)
        r, g, b = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))

        self.rgb['R'].set(r)
        self.rgb['G'].set(g)
        self.rgb['B'].set(b)

    
        c, m, y, k = rgb_to_cmyk(r, g, b)
        self.cmyk['C'].set(round(c, 3))
        self.cmyk['M'].set(round(m, 3))
        self.cmyk['Y'].set(round(y, 3))
        self.cmyk['K'].set(round(k, 3))

        self.set_swatch(r, g, b)
        self.warn.config(text='RGB усечён!' if clipped else '')
        self.updating = False

    def update_from_cmyk(self):
        if self.updating: return
        self.updating = True

        c, m, y, k = [self.cmyk[x].get() for x in "CMYK"]

        r, g, b = cmyk_to_rgb(c, m, y, k)

        self.rgb['R'].set(r)
        self.rgb['G'].set(g)
        self.rgb['B'].set(b)

        h, l, s = rgb_to_hls(r, g, b)
        self.hls['H'].set(round(h, 1))
        self.hls['L'].set(round(l, 3))
        self.hls['S'].set(round(s, 3))

        self.set_swatch(r, g, b)
        self.warn.config(text='')
        self.updating = False


    def pick_color(self):
        current_rgb = f'#{self.rgb["R"].get():02x}{self.rgb["G"].get():02x}{self.rgb["B"].get():02x}'
        col = colorchooser.askcolor(color=current_rgb)
        if not col or not col[0]:
            return

        r, g, b = map(int, col[0])

        self.rgb['R'].set(r)
        self.rgb['G'].set(g)
        self.rgb['B'].set(b)

        h, l, s = rgb_to_hls(r, g, b)
        self.hls['H'].set(round(h, 1))
        self.hls['L'].set(round(l, 3))
        self.hls['S'].set(round(s, 3))

        c, m, y, k = rgb_to_cmyk(r, g, b)
        self.cmyk['C'].set(round(c, 3))
        self.cmyk['M'].set(round(m, 3))
        self.cmyk['Y'].set(round(y, 3))
        self.cmyk['K'].set(round(k, 3))

        self.set_swatch(r, g, b)

    def set_swatch(self, r, g, b):
    
        self.swatch.config(bg=f'#{r:02x}{g:02x}{b:02x}')


if __name__ == "__main__":
    app = ColorApp()
    app.mainloop()
