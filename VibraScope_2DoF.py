# VibraScope.py - Sistema masa-resorte 2DOF con dos sensores VL53L0X
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import serial
import threading
import time
from collections import deque
import math
import serial.tools.list_ports

# Configuración serial
DEFAULT_PORT = "COM4"
BAUD_RATE = 115200
MAX_FPS = 60  # Actualizaciones GUI por segundo

class SerialReader(threading.Thread):
    def __init__(self, port, baudrate, callback):
        super().__init__()
        self.ser = None
        self.port = port
        self.baudrate = baudrate
        self.callback = callback
        self.running = True
        self.last_update = 0
        try:
            self.ser = serial.Serial(port, baudrate, timeout=0.1)
        except Exception as e:
            raise e

    def run(self):
        if not self.ser:
            return
        while self.running:
            try:
                if self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    if line.startswith("D:"):
                        parts = line[2:].split(",")
                        if len(parts) == 2:
                            try:
                                s1 = float(parts[0])
                                s2 = float(parts[1])
                                now = time.monotonic()
                                if now - self.last_update >= 1 / MAX_FPS:
                                    self.callback((s1, s2))
                                    self.last_update = now
                            except ValueError:
                                pass
            except serial.SerialException as e:
                print("Error de comunicación serial:", e)
                self.stop()
                self.callback(None, error=e)
            except Exception as e:
                print("Error leyendo el serial:", e)
        if self.ser and self.ser.is_open:
            time.sleep(0.1)
            self.ser.close()

    def stop(self):
        self.running = False

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.title("VibraScope 2DOF")
        self.geometry("900x600")

        # Parámetros de datos
        self.time_window = 10  # segundos

        # Cursores para cada gráfica
        self.cursor1_x_1 = None         # cursor1 de masa 1
        self.cursor2_x_1 = None         # cursor2 de masa 1
        self.active_cursor_1 = None
        self.cursor1_x_2 = None         # cursor1 de masa 2
        self.cursor2_x_2 = None
        self.active_cursor_2 = None

        maxlen = math.ceil(self.time_window * 100)
        self.sensor1_data = deque(maxlen=maxlen)
        self.sensor2_data = deque(maxlen=maxlen)
        self.relative1_data = deque(maxlen=maxlen)
        self.relative2_data = deque(maxlen=maxlen)

        self.relative_offset1 = 0
        self.relative_offset2 = 0

        self.last_s1 = 0
        self.last_s2 = 0

        self.last_rel1 = 0
        self.last_rel2 = 0

        self.displacement_range = (0, 600)  # Valor inicial por defecto

        self.paused = False
        self.data_lock = threading.Lock()
        self.recording = False
        self.recorded_data = []   # almacenará tuplas (s1, s2, rel1, rel2, timestamp)

        # Layout
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Contenedor de gráficos
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        for i in range(3):
            self.content_frame.grid_rowconfigure(i, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Canvas para desplazamientos relativos
        self.disp1_canvas = tk.Canvas(self.content_frame, bg="#1E1E1E")
        self.disp1_canvas.grid(row=0, column=0, sticky="nsew", padx=5, pady=2)
        self.disp1_canvas.bind("<ButtonPress-1>", lambda e: self.on_canvas_click(e, 1))
        self.disp1_canvas.bind("<B1-Motion>",   lambda e: self.on_canvas_drag(e, 1))
        self.disp1_canvas.bind("<ButtonRelease-1>", lambda e: self.on_canvas_release(e, 1))
        self.disp2_canvas = tk.Canvas(self.content_frame, bg="#1E1E1E")
        self.disp2_canvas.grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
        self.disp2_canvas.bind("<ButtonPress-1>", lambda e: self.on_canvas_click(e, 2))
        self.disp2_canvas.bind("<B1-Motion>",   lambda e: self.on_canvas_drag(e, 2))
        self.disp2_canvas.bind("<ButtonRelease-1>", lambda e: self.on_canvas_release(e, 2))

        # Canvas para animación
        self.animation_canvas = tk.Canvas(self.content_frame, bg="#1E1E1E")
        self.animation_canvas.grid(row=2, column=0, sticky="nsew", padx=5, pady=2)

        # Panel de control
        self.control_panel = ctk.CTkFrame(self)
        self.control_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Labels para sensores y relativos
        self.s1_label = ctk.CTkLabel(self.control_panel, text="S1: -- mm", font=("Arial", 14))
        self.s1_label.pack(pady=5)
        self.rel1_label = ctk.CTkLabel(self.control_panel, text="Rel1: -- mm", font=("Arial", 14))
        self.rel1_label.pack(pady=5)
        self.s2_label = ctk.CTkLabel(self.control_panel, text="S2: -- mm", font=("Arial", 14))
        self.s2_label.pack(pady=5)
        self.rel2_label = ctk.CTkLabel(self.control_panel, text="Rel2: -- mm", font=("Arial", 14))
        self.rel2_label.pack(pady=5)

        self.period1_label = ctk.CTkLabel(self.control_panel, text="T1: -- s", font=("Arial", 12))
        self.period1_label.pack(pady=2, fill='x')
        self.freq1_label   = ctk.CTkLabel(self.control_panel, text="F1: -- Hz", font=("Arial", 12))
        self.freq1_label.pack(pady=2, fill='x')
        self.period2_label = ctk.CTkLabel(self.control_panel, text="T2: -- s", font=("Arial", 12))
        self.period2_label.pack(pady=2, fill='x')
        self.freq2_label   = ctk.CTkLabel(self.control_panel, text="F2: -- Hz", font=("Arial", 12))
        self.freq2_label.pack(pady=2, fill='x')

        # Botones
        self.reset_button = ctk.CTkButton(self.control_panel, text="Set a Cero Relativo",
                                          command=self.set_relative_zero,fg_color="#00FFAA",text_color="#000000")
        self.reset_button.pack(pady=5, fill='x')
        self.pause_button = ctk.CTkButton(self.control_panel, text="Pausar Gráficas",
                                          command=self.toggle_pause,fg_color="#00FFAA",text_color="#000000")
        self.pause_button.pack(pady=5, fill='x')

        self.record_button = ctk.CTkButton(self.control_panel, text="Iniciar Grabación",
                                           command=self.toggle_recording,fg_color="#00FFAA",text_color="#000000")
        self.record_button.pack(pady=5, fill='x')
        self.save_button   = ctk.CTkButton(self.control_panel, text="Guardar Datos",
                                           command=self.save_data,fg_color="#00FFAA",text_color="#000000")
        self.save_button.pack(pady=5, fill='x')

        # Configuración serial
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.com_var = tk.StringVar(value=ports[0] if ports else "")
        self.com_dropdown = ctk.CTkComboBox(self.control_panel, variable=self.com_var, values=ports)
        self.com_dropdown.pack(pady=5, fill='x')
        self.conn_button = ctk.CTkButton(self.control_panel, text="Conectar",
                                         command=self.toggle_serial,fg_color="#00FFAA",text_color="#000000")
        self.conn_button.pack(pady=5, fill='x')

        self.serial_thread = None
        # Inicia loops
        self.after(100, self.update_graphs)
        self.after(20, self.update_animation)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def set_relative_zero(self):
        with self.data_lock:
            if self.sensor1_data:
                self.relative_offset1 = self.sensor1_data[-1][1]
            if self.sensor2_data:
                self.relative_offset2 = self.sensor2_data[-1][1]
            self.relative1_data.clear()
            self.relative2_data.clear()
        # Calcular displacement_range como 3 veces el promedio de los sensores
            if self.sensor1_data and self.sensor2_data:
                s1 = self.sensor1_data[-1][1]
                s2 = self.sensor2_data[-1][1]
                avg = (s1 + s2) / 2
                self.displacement_range = (0, 3 * avg)
        self.rel1_label.configure(text="Rel1: 0.00 mm")
        self.rel2_label.configure(text="Rel2: 0.00 mm")

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_button.configure(text="Continuar Gráficas" if self.paused else "Pausar Gráficas")

    def add_data(self, values, error=None):
        if error or values is None:
            return
        s1, s2 = values
        now = time.time()
        rel1 = s1 - self.relative_offset1
        rel2 = s2 - self.relative_offset2
        with self.data_lock:
            self.sensor1_data.append((now, s1))
            self.sensor2_data.append((now, s2))
            self.relative1_data.append((now, rel1))
            self.relative2_data.append((now, rel2))
        # Guardar para animación
        self.last_s1 = s1
        self.last_s2 = s2
        self.last_rel1 = rel1
        self.last_rel2 = rel2
        # Actualizar labels
        self.s1_label.configure(text=f"S1: {s1:.1f} mm")
        self.rel1_label.configure(text=f"Rel1: {rel1:.1f} mm")
        self.s2_label.configure(text=f"S2: {s2:.1f} mm")
        self.rel2_label.configure(text=f"Rel2: {rel2:.1f} mm")
        if self.recording:
            timestamp = time.time()
            self.recorded_data.append((self.last_s1, self.last_s2,
                                       self.last_rel1, self.last_rel2,
                                       timestamp))
            
    def toggle_recording(self):
        if not self.recording:
            # borra datos de la sesión anterior
            self.recorded_data = []
        self.recording = not self.recording
        self.record_button.configure(
            text="Detener Grabación" if self.recording else "Iniciar Grabación"
        )


    def save_data(self):
        if not self.recorded_data:
            messagebox.showwarning("Atención", "No hay datos para guardar.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV","*.csv")])
        if not path:
            return
        with open(path, "w") as f:
            f.write("S1, S2, Rel1, Rel2, Timestamp\n")
            for s1,s2,r1,r2,ts in self.recorded_data:
                f.write(f"{s1:.2f},{s2:.2f},{r1:.2f},{r2:.2f},{ts:.3f}\n")
        messagebox.showinfo("Éxito", "Datos guardados correctamente.")

    def update_graphs(self):
        if not self.paused:
            with self.data_lock:
                d1 = list(self.relative1_data)
                d2 = list(self.relative2_data)
            self.draw_graph(self.disp1_canvas, d1, (0.8 * self.displacement_range[0], 0.2 * self.displacement_range[1]), "Masa 1 Relativo (mm)")
            self.draw_graph(self.disp2_canvas, d2, (0.5 * self.displacement_range[1], 0.8 * self.displacement_range[0]), "Masa 2 Relativo (mm)")
            
        self.draw_cursors_and_freq(self.disp1_canvas, mass=1)
        self.draw_cursors_and_freq(self.disp2_canvas, mass=2)
        self.after(100, self.update_graphs)

    def displacement_range(self):
        return self.displacement_range


    def draw_graph(self, canvas, data, y_range, title):
        canvas.delete("graph")
        w, h = canvas.winfo_width(), canvas.winfo_height()
        if w <= 0 or h <= 0 or len(data) < 2:
            return

        left, top, bottom = 50, 30, 30
        # Título
        canvas.create_text(left + 10, top - 20,
                        text=title,
                        fill="white",
                        anchor="w",
                        tags="graph")

        # Elegir color según el título
        if title == "Masa 1 Relativo (mm)":
            line_color = "#00FFAA"
        elif title == "Masa 2 Relativo (mm)":
            line_color = "#00AAFF"
        else:
            line_color = "#FFFFFF"  # color por defecto si quieres

        current = time.time()
        # Calcular puntos
        points = []
        for t, val in data:
            x = left + (t - (current - self.time_window)) / self.time_window * (w - left)
            y = top + (h - top - bottom) * (1 - (val - y_range[0]) / (y_range[1] - y_range[0]))
            points.extend((x, y))

        # Dibujar línea con el color seleccionado
        canvas.create_line(*points,
                        fill=line_color,
                        width=3,      # ajusta aquí el grosor si quieres
                        smooth=True,
                        tags="graph")


    def update_animation(self):
        self.animation_canvas.delete("anim")
        w, h = self.animation_canvas.winfo_width(), self.animation_canvas.winfo_height()
        if w <= 0 or h <= 0:
            self.after(20, self.update_animation)
            return
        margin = w * 0.1
        usable = w - 2 * margin
        def norm(v):
            return max(0, min(1, (v - self.displacement_range[0]) / (self.displacement_range[1] - self.displacement_range[0])))
        x1 = margin + norm(self.last_s1) * usable
        x2 = w - margin - norm(self.last_s2) * usable
        # Resortes y bloques
        self.animation_canvas.create_line(30, h/2, x1-40, h/2, fill="#666", width=3, tags="anim")
        self.animation_canvas.create_rectangle(x1-40, h/2-30, x1+40, h/2+30, fill="#00FFAA", tags="anim")
        self.animation_canvas.create_line(x1+40, h/2, x2-40, h/2, fill="#666", width=3, tags="anim")
        self.animation_canvas.create_rectangle(x2-40, h/2-30, x2+40, h/2+30, fill="#00AAFF", tags="anim")
        self.animation_canvas.create_line(x2+40, h/2, w-30, h/2, fill="#666", width=3, tags="anim")
        self.after(20, self.update_animation)

    def on_canvas_click(self, event, mass):
        threshold = 10
        if mass == 1:
            if self.cursor1_x_1 and abs(event.x - self.cursor1_x_1) < threshold:
                self.active_cursor_1 = "c1"
            elif self.cursor2_x_1 and abs(event.x - self.cursor2_x_1) < threshold:
                self.active_cursor_1 = "c2"
        else:
            if self.cursor1_x_2 and abs(event.x - self.cursor1_x_2) < threshold:
                self.active_cursor_2 = "c1"
            elif self.cursor2_x_2 and abs(event.x - self.cursor2_x_2) < threshold:
                self.active_cursor_2 = "c2"

    def on_canvas_drag(self, event, mass):
        left_pad = 50
        w = (self.disp1_canvas if mass==1 else self.disp2_canvas).winfo_width()
        new_x = max(left_pad, min(event.x, w))
        if mass == 1 and self.active_cursor_1:
            setattr(self, f"cursor{1 if self.active_cursor_1=='c1' else 2}_x_1", new_x)
        elif mass == 2 and self.active_cursor_2:
            setattr(self, f"cursor{1 if self.active_cursor_2=='c1' else 2}_x_2", new_x)

    def on_canvas_release(self, event, mass):
        if mass == 1:
            self.active_cursor_1 = None
        else:
            self.active_cursor_2 = None

    def draw_cursors_and_freq(self, canvas, mass):
        canvas.delete("cursor")
        w = canvas.winfo_width()
        left_pad = 50
        # Inicialización
        cx1 = getattr(self, f"cursor1_x_{mass}") or (left_pad + (w-left_pad)*0.33)
        cx2 = getattr(self, f"cursor2_x_{mass}") or (left_pad + (w-left_pad)*0.66)
        setattr(self, f"cursor1_x_{mass}", cx1)
        setattr(self, f"cursor2_x_{mass}", cx2)
        # Dibujar
        canvas.create_line(cx1, 0, cx1, canvas.winfo_height(), fill="red", width=2, tags="cursor")
        canvas.create_line(cx2, 0, cx2, canvas.winfo_height(), fill="red", width=2, tags="cursor")
        # Cálculo T y F
        delta = abs(cx2 - cx1)
        T = (delta / (w-left_pad)) * self.time_window
        F = 1/T if T>0 else 0
        # Actualizar labels (añadir en panel de control dos labels extra)
        if mass == 1:
            self.period1_label.configure(text=f"T1: {T:.2f} s")
            self.freq1_label .configure(text=f"F1: {F:.2f} Hz")
        else:
            self.period2_label.configure(text=f"T2: {T:.2f} s")
            self.freq2_label .configure(text=f"F2: {F:.2f} Hz")

    def toggle_serial(self):
        if self.serial_thread and self.serial_thread.running:
            self.serial_thread.stop()
            self.serial_thread.join(timeout=1)
            self.serial_thread = None
            self.conn_button.configure(text="Conectar")
        else:
            port = self.com_var.get()
            try:
                self.serial_thread = SerialReader(port, BAUD_RATE, self.add_data)
                self.serial_thread.start()
                self.conn_button.configure(text="Desconectar")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo conectar: {e}")

    def on_closing(self):
        if self.serial_thread:
            self.serial_thread.stop()
            self.serial_thread.join(timeout=1)
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
