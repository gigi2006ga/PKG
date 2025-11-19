import tkinter as tk
from tkinter import ttk
from tkinter import colorchooser
from tkinter import messagebox
import math

def clamp(v, a, b):
    return max(a, min(b, v))

def rgb_to_cmyk(r, g, b):
    if (r, g, b) == (0, 0, 0):
        return 0.0, 0.0, 0.0, 100.0
    r_p = r / 255.0
    g_p = g / 255.0
    b_p = b / 255.0
    k = 1 - max(r_p, g_p, b_p)
    c = (1 - r_p - k) / (1 - k) if (1 - k) != 0 else 0
    m = (1 - g_p - k) / (1 - k) if (1 - k) != 0 else 0
    y = (1 - b_p - k) / (1 - k) if (1 - k) != 0 else 0
    return round(c * 100, 2), round(m * 100, 2), round(y * 100, 2), round(k * 100, 2)

def cmyk_to_rgb(c, m, y, k):
    c_p = clamp(c / 100.0, 0.0, 1.0)
    m_p = clamp(m / 100.0, 0.0, 1.0)
    y_p = clamp(y / 100.0, 0.0, 1.0)
    k_p = clamp(k / 100.0, 0.0, 1.0)
    r = 255 * (1 - c_p) * (1 - k_p)
    g = 255 * (1 - m_p) * (1 - k_p)
    b = 255 * (1 - y_p) * (1 - k_p)
    return int(round(r)), int(round(g)), int(round(b))

def rgb_to_hls(r, g, b):
    r_p = r / 255.0
    g_p = g / 255.0
    b_p = b / 255.0
    
    max_val = max(r_p, g_p, b_p)
    min_val = min(r_p, g_p, b_p)
    
    l = (max_val + min_val) / 2.0
    
    if max_val == min_val:

        return 0.0, round(l * 100, 2), 0.0
    
    
    if l <= 0.5:
        s = (max_val - min_val) / (max_val + min_val)
    else:
        s = (max_val - min_val) / (2.0 - max_val - min_val)
    
    
    d = max_val - min_val
    if max_val == r_p:
        h = (g_p - b_p) / d
        if g_p < b_p:
            h += 6.0
    elif max_val == g_p:
        h = (b_p - r_p) / d + 2.0
    else:  
        h = (r_p - g_p) / d + 4.0
    
    h = h * 60.0  
    
    return round(h, 2), round(l * 100, 2), round(s * 100, 2)

def hls_to_rgb(h, l, s):
    
    h_normalized = h % 360  
    l_p = clamp(l / 100.0, 0.0, 1.0)
    s_p = clamp(s / 100.0, 0.0, 1.0)
    
    if s_p == 0:
        
        gray = int(round(l_p * 255))
        return gray, gray, gray
    
    
    if l_p < 0.5:
        temp2 = l_p * (1.0 + s_p)
    else:
        temp2 = l_p + s_p - (l_p * s_p)
    
    temp1 = 2.0 * l_p - temp2
    

    h_p = h_normalized / 360.0
    
    
    rgb = []
    for i in range(3):
        t = h_p + 1.0/3.0 * -(i - 1)  
        if t < 0:
            t += 1
        if t > 1:
            t -= 1
        
        if 6.0 * t < 1.0:
            color = temp1 + (temp2 - temp1) * 6.0 * t
        elif 2.0 * t < 1.0:
            color = temp2
        elif 3.0 * t < 2.0:
            color = temp1 + (temp2 - temp1) * (2.0/3.0 - t) * 6.0
        else:
            color = temp1
        
        rgb.append(int(round(color * 255)))
    
    return rgb[0], rgb[1], rgb[2]

def rgb_to_hex(r, g, b):
    return '#{:02X}{:02X}{:02X}'.format(clamp(int(round(r)), 0, 255), clamp(int(round(g)), 0, 255), clamp(int(round(b)), 0, 255))

class ColorConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Color Converter — RGB <-> CMYK <-> HLS')
        self.resizable(False, False)
        self.style = ttk.Style(self)
        self.updating = False  
        self.last_changed_model = None
        self._was_near_max = False
        
    
        self.rgb = (0, 0, 255)
        self.warn_var = tk.StringVar(value='')
        
        self.rgb_vars = []
        self.cmyk_vars = []
        self.hls_vars = []
        
        self._build_ui()
        self._update_all_from_rgb()

    def _build_ui(self):
        pad = 8
        main = ttk.Frame(self, padding=pad)
        main.grid(row=0, column=0)
        models_frame = ttk.Frame(main)
        models_frame.grid(row=0, column=0, sticky='n')
        self._build_rgb_frame(models_frame).grid(row=0, column=0, pady=pad, sticky='w')
        self._build_cmyk_frame(models_frame).grid(row=1, column=0, pady=pad, sticky='w')
        self._build_hls_frame(models_frame).grid(row=2, column=0, pady=pad, sticky='w')
        right = ttk.Frame(main)
        right.grid(row=0, column=1, padx=10, sticky='n')
        preview_label = ttk.Label(right, text='Preview')
        preview_label.grid(row=0, column=0, pady=(0,6))
        self.preview = tk.Canvas(right, width=160, height=120, bd=1, relief='sunken')
        self.preview.grid(row=1, column=0)
        self.hex_var = tk.StringVar(value=rgb_to_hex(*self.rgb))
        hex_entry = ttk.Entry(right, textvariable=self.hex_var, width=12)
        hex_entry.grid(row=2, column=0, pady=(6,0))
        hex_entry.bind('<Return>', self._on_hex_entry)
        ttk.Button(right, text='Copy HEX', command=self._copy_hex).grid(row=3, column=0, pady=(6,0))
        ttk.Button(right, text='Choose color...', command=self._choose_color).grid(row=4, column=0, pady=(6,0))
        self.warn_label = ttk.Label(main, textvariable=self.warn_var, foreground='dark orange')
        self.warn_label.grid(row=1, column=0, columnspan=2, sticky='w', padx=pad)

    def _build_rgb_frame(self, parent):
        frame = ttk.LabelFrame(parent, text='RGB (0-255)')
        labels = ('R', 'G', 'B')
        for i, lab in enumerate(labels):
            v = tk.IntVar(value=self.rgb[i])
            self.rgb_vars.append(v)
            row = ttk.Frame(frame)
            row.grid(row=i, column=0, sticky='w', pady=2, padx=6)
            ttk.Label(row, text=lab).grid(row=0, column=0)
            s = ttk.Scale(row, from_=0, to=255, orient='horizontal',
                      variable=v, command=lambda val, idx=i: self._on_rgb_slider(idx, val))
            s.grid(row=0, column=1, padx=6)
            e = ttk.Entry(row, width=5, textvariable=v)
            e.grid(row=0, column=2)
            e.bind('<Return>', lambda ev, idx=i: self._on_rgb_entry(idx))
        return frame

    def _build_cmyk_frame(self, parent):
        frame = ttk.LabelFrame(parent, text='CMYK (0-100%)')
        labels = ('C', 'M', 'Y', 'K')
        for i, lab in enumerate(labels):
            v = tk.DoubleVar(value=0.0)
            self.cmyk_vars.append(v)
            row = ttk.Frame(frame)
            row.grid(row=i, column=0, sticky='w', pady=2, padx=6)
            ttk.Label(row, text=lab).grid(row=0, column=0)
            s = ttk.Scale(row, from_=0, to=100, orient='horizontal', variable=v, 
                          command=lambda val, idx=i: self._on_cmyk_slider(idx, val))
            s.grid(row=0, column=1, padx=6)
            e = ttk.Entry(row, width=6, textvariable=v)
            e.grid(row=0, column=2)
            e.bind('<Return>', lambda ev, idx=i: self._on_cmyk_entry(idx))
        return frame

    def _build_hls_frame(self, parent):
        frame = ttk.LabelFrame(parent, text='HLS (H:0-360; L,S:0-100)')
        labels = ('H', 'L', 'S')
        ranges = [(0, 360), (0, 100), (0, 100)]
        for i, lab in enumerate(labels):
            v = tk.DoubleVar(value=0.0)
            self.hls_vars.append(v)
            row = ttk.Frame(frame)
            row.grid(row=i, column=0, sticky='w', pady=2, padx=6)
            ttk.Label(row, text=lab).grid(row=0, column=0)
            low, high = ranges[i]
            s = ttk.Scale(row, from_=low, to=high, orient='horizontal', variable=v, 
                          command=lambda val, idx=i: self._on_hls_slider(idx, val))
            s.grid(row=0, column=1, padx=6)
            e = ttk.Entry(row, width=6, textvariable=v)
            e.grid(row=0, column=2)
            e.bind('<Return>', lambda ev, idx=i: self._on_hls_entry(idx))
            
            
            if i == 0:
                self.h_slider = s
        return frame
    
    def _on_hex_entry(self, event=None):
        if self.updating: 
            return
        try:
            self.updating = True
            hex_code = self.hex_var.get().strip()
            if hex_code.startswith('#'):
                hex_code = hex_code[1:]
            if len(hex_code) != 6:
                self.warn_var.set('HEX должен быть в формате RRGGBB')
                return
            r = int(hex_code[0:2], 16)
            g = int(hex_code[2:4], 16)
            b = int(hex_code[4:6], 16)
            self.last_changed_model = 'hex'
            self._set_rgb_and_update((r, g, b))
        except ValueError:
            self.warn_var.set('Некорректный HEX')
        finally:
            self.updating = False

    def _on_rgb_slider(self, idx, val):
        if self.updating: return
        try:
            self.updating = True
            v = int(float(val))
            self.rgb_vars[idx].set(v)
            self.rgb = (self.rgb_vars[0].get(), self.rgb_vars[1].get(), self.rgb_vars[2].get())
            self.last_changed_model = 'rgb'
            self._update_from_rgb()
        finally:
            self.updating = False

    def _on_rgb_entry(self, idx):
        if self.updating: return
        try:
            self.updating = True
            v = clamp(int(self.rgb_vars[idx].get()), 0, 255)
            self.rgb_vars[idx].set(v)
            self.rgb = (self.rgb_vars[0].get(), self.rgb_vars[1].get(), self.rgb_vars[2].get())
            self.last_changed_model = 'rgb'
            self._update_from_rgb()
        finally:
            self.updating = False

    def _on_cmyk_slider(self, idx, val):
        if self.updating: return
        try:
            self.updating = True
            v = round(float(val), 2)
            self.cmyk_vars[idx].set(v)
            
            c = self.cmyk_vars[0].get()
            m = self.cmyk_vars[1].get()
            y = self.cmyk_vars[2].get()
            k = self.cmyk_vars[3].get()
            
            
            if idx in [0, 1, 2]:
                max_cmy = max(c, m, y)
                new_k = 100 - max_cmy
                self.cmyk_vars[3].set(max(0, new_k))
                k = new_k
            
            self.last_changed_model = 'cmyk'
            r, g, b = cmyk_to_rgb(c, m, y, k)
            self._set_rgb_and_update((r, g, b))
        finally:
            self.updating = False

    def _on_cmyk_entry(self, idx):
        if self.updating: return
        try:
            self.updating = True
            v = clamp(float(self.cmyk_vars[idx].get()), 0.0, 100.0)
            self.cmyk_vars[idx].set(round(v, 2))
            
            c = self.cmyk_vars[0].get()
            m = self.cmyk_vars[1].get()
            y = self.cmyk_vars[2].get()
            k = self.cmyk_vars[3].get()
            
    
            if idx in [0, 1, 2]:  
                max_cmy = max(c, m, y)
                new_k = 100 - max_cmy
                self.cmyk_vars[3].set(max(0, new_k))
                k = new_k
            
            self.last_changed_model = 'cmyk'
            r, g, b = cmyk_to_rgb(c, m, y, k)
            self._set_rgb_and_update((r, g, b))
        finally:
            self.updating = False

    def _on_hls_slider(self, idx, val):
        if self.updating: return
        try:
            self.updating = True
            v = round(float(val), 2)
            
            
            if idx == 0 and v == 0 and self._was_near_max:
                v = 360.0  
                self._was_near_max = False
            
        
            if idx == 0 and v >= 359:
                self._was_near_max = True
            elif idx == 0:
                self._was_near_max = False
                
            self.hls_vars[idx].set(v)
            
            h = self.hls_vars[0].get()
            l_val = self.hls_vars[1].get()
            s = self.hls_vars[2].get()
            
            self.last_changed_model = 'hls'
            r, g, b = hls_to_rgb(h, l_val, s)
            self._set_rgb_and_update((r, g, b))
            
            
            if idx == 0 and v == 360:
                self.h_slider.set(360)
                
        finally:
            self.updating = False

    def _on_hls_entry(self, idx):
        if self.updating: return
        try:
            self.updating = True
            ranges = [(0, 360), (0, 100), (0, 100)]
            low, high = ranges[idx]
            v = clamp(float(self.hls_vars[idx].get()), low, high)
            self.hls_vars[idx].set(round(v, 2))
            
            h = self.hls_vars[0].get()
            l_val = self.hls_vars[1].get()
            s = self.hls_vars[2].get()
            
            self.last_changed_model = 'hls'
            r, g, b = hls_to_rgb(h, l_val, s)
            self._set_rgb_and_update((r, g, b))
            
            
            if idx == 0 and v == 360:
                self.h_slider.set(360)
        finally:
            self.updating = False

    def _set_rgb_and_update(self, rgb_tuple):
        r, g, b = rgb_tuple
        r_c = clamp(int(round(r)), 0, 255)
        g_c = clamp(int(round(g)), 0, 255)
        b_c = clamp(int(round(b)), 0, 255)
        self.rgb = (r_c, g_c, b_c)
        if (r, g, b) != (r_c, g_c, b_c):
            self.warn_var.set('Warning: some components were clipped to valid range (0..255).')
        else:
            self.warn_var.set('')

        
        self._update_all_from_rgb()

    def _update_from_rgb(self):
        """Обновляем только те модели, которые НЕ были изменены пользователем"""
        if self.last_changed_model != 'rgb':
            for i, v in enumerate(self.rgb_vars):
                v.set(self.rgb[i])
        
        if self.last_changed_model != 'cmyk':
            c, m, y, k = rgb_to_cmyk(*self.rgb)
            self.cmyk_vars[0].set(c)
            self.cmyk_vars[1].set(m)
            self.cmyk_vars[2].set(y)
            self.cmyk_vars[3].set(k)
        
        if self.last_changed_model != 'hls':
            h, l_val, s = rgb_to_hls(*self.rgb)
            self.hls_vars[0].set(h)
            self.hls_vars[1].set(l_val)
            self.hls_vars[2].set(s)
        
        self._update_preview()
        self.hex_var.set(rgb_to_hex(*self.rgb))

    def _update_all_from_rgb(self):
        """Обновляем ВСЕ модели - используется когда меняем RGB напрямую"""
        for i, v in enumerate(self.rgb_vars):
            v.set(self.rgb[i])
        
        c, m, y, k = rgb_to_cmyk(*self.rgb)
        self.cmyk_vars[0].set(c)
        self.cmyk_vars[1].set(m)
        self.cmyk_vars[2].set(y)
        self.cmyk_vars[3].set(k)
        
        h, l_val, s = rgb_to_hls(*self.rgb)
        self.hls_vars[0].set(h)
        self.hls_vars[1].set(l_val)
        self.hls_vars[2].set(s)
        
        self._update_preview()
        self.hex_var.set(rgb_to_hex(*self.rgb))

    def _update_preview(self):
        self.preview.delete('all')
        self.preview.create_rectangle(0, 0, 160, 120, fill=rgb_to_hex(*self.rgb), outline='')

    def _copy_hex(self):
        try:
            self.clipboard_clear()
            self.clipboard_append(self.hex_var.get())
            self.warn_var.set('HEX copied to clipboard')
            self.after(1500, lambda: self.warn_var.set(''))
        except Exception as e:
            messagebox.showerror('Error', f'Could not copy to clipboard: {e}')

    def _choose_color(self):
        result = colorchooser.askcolor(color=self.hex_var.get(), parent=self)
        if result:
            rgb_tuple, hex_code = result  
            if rgb_tuple:  
                r, g, b = map(int, rgb_tuple)
                self.last_changed_model = 'picker'
                self._set_rgb_and_update((r, g, b))

if __name__ == '__main__':
    app = ColorConverterApp()
    app.mainloop()
