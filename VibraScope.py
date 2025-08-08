import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import serial
import threading
import time
from collections import deque
import math
import serial.tools.list_ports

# Configuración inicial del puerto serial
DEFAULT_PORT = "COM6"
BAUD_RATE = 115200
MAX_FPS = 30  # Limitar actualizaciones GUI

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
                        data_str = line.split("D:")[1]
                        try:
                            value = float(data_str)
                            current_time = time.monotonic()
                            if current_time - self.last_update >= 1/MAX_FPS:
                                self.callback(value)
                                self.last_update = current_time
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
        self.title("VibraScope")
        self.geometry("800x600")
        
        # Variables de datos
        self.data_lock = threading.Lock()
        self.time_window = 10
        self.raw_data = deque(maxlen=math.ceil(self.time_window * 100))
        self.filtered_data = deque(maxlen=math.ceil(self.time_window * 100))
        self.velocity_data = deque(maxlen=math.ceil(self.time_window * 100))
        self.acceleration_data = deque(maxlen=math.ceil(self.time_window * 100))
        # Datos para la distancia relativa
        self.relative_offset = 0  
        self.relative_data = deque(maxlen=math.ceil(self.time_window * 100))
        
        self.recording = False
        self.recorded_data = []
        self.displacement_range = (-100, 100)
        
        # Nueva variable para pausar la gráfica
        self.paused = False
        
        # Variables para los cursores
        self.cursor1_x = None
        self.cursor2_x = None
        self.active_cursor = None  # "cursor1" o "cursor2"
        
        # Configuración de la interfaz
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Frame principal para gráficos
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        for i in range(4):
            self.content_frame.grid_rowconfigure(i, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Canvas para gráficos
        self.displacement_canvas = tk.Canvas(self.content_frame, bg="#1E1E1E")
        self.displacement_canvas.grid(row=0, column=0, sticky="nsew", padx=5, pady=2)
        # Se han comentado las gráficas de velocidad y aceleración:
        # self.velocity_canvas = tk.Canvas(self.content_frame, bg="#1E1E1E")
        # self.velocity_canvas.grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
        # self.acceleration_canvas = tk.Canvas(self.content_frame, bg="#1E1E1E")
        # self.acceleration_canvas.grid(row=2, column=0, sticky="nsew", padx=5, pady=2)
        self.animation_canvas = tk.Canvas(self.content_frame, bg="#1E1E1E")
        self.animation_canvas.grid(row=3, column=0, sticky="nsew", padx=5, pady=2)
        
        # Vincular eventos del mouse al canvas para los cursores
        self.displacement_canvas.bind("<ButtonPress-1>", self.on_canvas_click)
        self.displacement_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.displacement_canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        # Panel de control derecho
        self.control_panel = ctk.CTkFrame(self)
        self.control_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Widgets del panel de control
        ctk.CTkLabel(self.control_panel, text="Configuración", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Mostrar la distancia actual (Absoluta)
        self.current_distance_label = ctk.CTkLabel(self.control_panel, text="Distancia Absoluta: --", font=("Arial", 16, "bold"))
        self.current_distance_label.pack(pady=5, padx=10, fill='x')
        
        # Mostrar la distancia relativa
        self.relative_distance_label = ctk.CTkLabel(self.control_panel, text="Distancia Relativa: --", font=("Arial", 16, "bold"))
        self.relative_distance_label.pack(pady=5, padx=10, fill='x')
        
        # Botón para setear a cero la distancia relativa
        self.reset_relative_button = ctk.CTkButton(self.control_panel, text="Set a Cero Relativo", command=self.set_relative_zero,
                                                   fg_color="#FFAA00", text_color="#000000")
        self.reset_relative_button.pack(pady=5, padx=10, fill='x')
        
        # Botón de pausa/continuar para la gráfica
        self.pause_button = ctk.CTkButton(self.control_panel, text="Pausar Gráfica", command=self.toggle_pause,
                                          fg_color="#FFA500", text_color="#000000")
        self.pause_button.pack(pady=5, padx=10, fill='x')
        
        # Mostrar T (periodo) y F (frecuencia)
        self.period_label = ctk.CTkLabel(self.control_panel, text="T: -- s", font=("Arial", 14))
        self.period_label.pack(pady=5, padx=10, fill='x')
        self.frequency_label = ctk.CTkLabel(self.control_panel, text="F: -- Hz", font=("Arial", 14))
        self.frequency_label.pack(pady=5, padx=10, fill='x')
        
        # Configuración del puerto COM
        ctk.CTkLabel(self.control_panel, text="Puerto COM:").pack(pady=(10,0))
        self.com_ports = self.get_available_ports()
        self.com_var = tk.StringVar(value=self.com_ports[0] if self.com_ports else "No disponible")
        self.com_dropdown = ctk.CTkComboBox(self.control_panel, variable=self.com_var, values=self.com_ports)
        self.com_dropdown.pack(pady=5, padx=10, fill='x')
        
        self.connect_button = ctk.CTkButton(self.control_panel, text="Conectar", command=self.toggle_serial,
                                            fg_color="#00FFAA", text_color="#000000")
        self.connect_button.pack(pady=5, padx=10, fill='x')
        
        # Configuración del tiempo a mostrar en el eje x
        ctk.CTkLabel(self.control_panel, text="Tiempo (s):").pack(pady=(10,0))
        self.time_window_entry = ctk.CTkEntry(self.control_panel)
        self.time_window_entry.pack(pady=5, padx=10, fill='x')
        self.time_window_entry.insert(0, str(self.time_window))
        self.time_window_entry.bind("<Return>", self.update_time_window)
        
        # Configuración del rango de desplazamiento
        ctk.CTkLabel(self.control_panel, text="Rango Desplazamiento (min, max):").pack(pady=(10,0))
        self.displacement_range_entry = ctk.CTkEntry(self.control_panel)
        self.displacement_range_entry.pack(pady=5, padx=10, fill='x')
        self.displacement_range_entry.insert(0, f"{self.displacement_range[0]},{self.displacement_range[1]}")
        self.displacement_range_entry.bind("<Return>", self.update_displacement_range)
        
        # Botones de control adicionales
        self.reset_button = ctk.CTkButton(self.control_panel, text="Resetear Gráficas", command=self.reset_data,
                                          fg_color="#00FFAA", text_color="#000000")
        self.reset_button.pack(pady=5, padx=10, fill='x')
        self.record_button = ctk.CTkButton(self.control_panel, text="Iniciar Grabación", command=self.toggle_recording,
                                           fg_color="#00FFAA", text_color="#000000")
        self.record_button.pack(pady=5, padx=10, fill='x')
        self.save_button = ctk.CTkButton(self.control_panel, text="Guardar Datos", command=self.save_data,
                                         fg_color="#00FFAA", text_color="#000000")
        self.save_button.pack(pady=5, padx=10, fill='x')
        
        self.velocity_range = (-400, 400)
        self.acceleration_range = (-2000, 2000)
        
        # Parámetros de la animación
        self.block_x = 0
        self.block_y = 0
        self.block_width = 80
        self.block_height = 60
        
        self.serial_thread = None
        self.update_graphs()    # Actualiza los gráficos cada 100 ms
        self.update_animation() # Actualiza la animación cada 20 ms
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def get_available_ports(self):
        """Obtiene la lista de puertos COM disponibles."""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def update_time_window(self, event=None):
        try:
            new_window = float(self.time_window_entry.get())
            if new_window > 0:
                self.time_window = new_window
        except ValueError:
            pass

    def update_displacement_range(self, event=None):
        try:
            parts = self.displacement_range_entry.get().split(',')
            if len(parts) == 2:
                new_min = float(parts[0])
                new_max = float(parts[1])
                if new_min < new_max:
                    self.displacement_range = (new_min, new_max)
        except ValueError:
            pass

    def prune_old_data(self, current_time):
        cutoff = current_time - self.time_window
        while self.raw_data and self.raw_data[0][0] < cutoff:
            self.raw_data.pop(0)
        while self.filtered_data and self.filtered_data[0][0] < cutoff:
            self.filtered_data.pop(0)
        while self.velocity_data and self.velocity_data[0][0] < cutoff:
            self.velocity_data.pop(0)
        while self.acceleration_data and self.acceleration_data[0][0] < cutoff:
            self.acceleration_data.pop(0)
        with self.data_lock:
            while self.relative_data and self.relative_data[0][0] < cutoff:
                self.relative_data.pop(0)

    def add_data(self, value, error=None):
        if error:
            self.after(0, self.handle_serial_error, error)
            return
        
        current_time = time.time()
        with self.data_lock:
            self.raw_data.append((current_time, value))
            filtered_value = value
            self.filtered_data.append((current_time, filtered_value))
            # Calcular el valor relativo y almacenarlo
            relative_value = value - self.relative_offset
            self.relative_data.append((current_time, relative_value))
            
            # Calcular velocidad
            velocity = 0.0
            if len(self.filtered_data) >= 2:
                t_prev, v_prev = self.filtered_data[-2]
                t_curr, v_curr = self.filtered_data[-1]
                dt = t_curr - t_prev
                velocity = (v_curr - v_prev) / dt if dt > 0 else 0
            self.velocity_data.append((current_time, velocity))
            
            # Calcular aceleración
            acceleration = 0.0
            if len(self.velocity_data) >= 2:
                t_prev, vel_prev = self.velocity_data[-2]
                t_curr, vel_curr = self.velocity_data[-1]
                dt = t_curr - t_prev
                acceleration = (vel_curr - vel_prev) / dt if dt > 0 else 0
            self.acceleration_data.append((current_time, acceleration))
            if self.recording:
                # guarda: (timestamp, desplazamiento, velocidad, aceleración)
                self.recorded_data.append((
                    current_time,
                    filtered_value,
                    velocity,
                    acceleration
                ))
            
        self.after(0, lambda: self.current_distance_label.configure(text=f"Distancia Absoluta: {value:.2f} mm"))
        self.after(0, lambda: self.relative_distance_label.configure(text=f"Distancia Relativa: {relative_value:.2f} mm"))
        
        # Actualizamos la animación usando el valor relativo
        self.update_mass_position(relative_value)

        if self.recording:
            # guarda el timestamp, valor, velocidad y aceleración
            self.recorded_data.append((current_time, filtered_value, velocity, acceleration))

    def handle_serial_error(self, error):
        if self.serial_thread:
            self.serial_thread.stop()
            self.serial_thread = None
            self.connect_button.configure(text="Conectar")
        messagebox.showerror("Error Serial", f"Se perdió la conexión: {str(error)}")

    def set_relative_zero(self):
        """Reinicia el offset para la distancia relativa al último valor absoluto recibido
           y limpia el deque de datos relativos para que la gráfica comience desde 0."""
        with self.data_lock:
            self.relative_offset = self.raw_data[-1][1] if self.raw_data else 0
            self.relative_data.clear()
        self.relative_distance_label.configure(text="Distancia Relativa: 0.00 mm")

    def toggle_pause(self):
        """Activa o desactiva el modo pausa en la actualización de la gráfica."""
        self.paused = not self.paused
        self.pause_button.configure(text="Continuar Gráfica" if self.paused else "Pausar Gráfica")

    def toggle_serial(self):
        if self.serial_thread and self.serial_thread.running:
            self.serial_thread.stop()
            self.serial_thread.join(timeout=1)
            self.serial_thread = None
            self.connect_button.configure(text="Conectar")
        else:
            selected_port = self.com_var.get()
            try:
                self.serial_thread = SerialReader(selected_port, BAUD_RATE, self.add_data)
                self.serial_thread.start()
                self.connect_button.configure(text="Desconectar")
            except Exception as e:
                messagebox.showerror("Error", f"Error al conectar: {str(e)}")
    
    def _filter_time_window(self, data):
        current_time = time.time()
        return [(t, val) for (t, val) in data if t >= current_time - self.time_window]
    
    def draw_graph(self, canvas, data, y_range, title):
        try:
            canvas.delete("graph")
            w = canvas.winfo_width()
            h = canvas.winfo_height()
            if w <= 0 or h <= 0:
                return
            left_pad = 50
            top_pad = 30
            bottom_pad = 30
            current_time = time.time()
            num_lines = 5
            for i in range(num_lines + 1):
                y = top_pad + (h - top_pad - bottom_pad) * (i / num_lines)
                canvas.create_line(left_pad, y, w, y, fill="#333333", dash=(2, 2), tags="graph")
                value = y_range[0] + (y_range[1] - y_range[0]) * (1 - i/num_lines)
                canvas.create_text(left_pad-10, y, text=f"{value:.0f}", fill="white", anchor="e", tags="graph")
            times = [current_time - self.time_window,
                     current_time - self.time_window/2,
                     current_time]
            for t in times:
                x = left_pad + ((t - (current_time - self.time_window)) / self.time_window) * (w - left_pad)
                time_str = time.strftime("%H:%M:%S", time.localtime(t))
                canvas.create_text(x, h - bottom_pad + 15, text=time_str, fill="white", anchor="n", tags="graph")
            filtered_data = [(t, val) for (t, val) in data if t >= current_time - self.time_window]
            if len(filtered_data) > 1:
                points = []
                for (t, val) in filtered_data:
                    x = left_pad + ((t - (current_time - self.time_window)) / self.time_window) * (w - left_pad)
                    y = top_pad + (h - top_pad - bottom_pad) * (1 - (val - y_range[0])/(y_range[1]-y_range[0]))
                    points.append((x, y))
                if len(points) > 1:
                    flat_points = [coord for point in points for coord in point]
                    canvas.create_line(*flat_points, fill="#00FFAA", width=1, smooth=True, tags="graph")
            canvas.create_text(left_pad + 10, top_pad - 20, text=title, fill="white",
                               anchor="w", font=("Arial", 10, "bold"), tags="graph")
        except Exception as e:
            print("Error en draw_graph:", e)
    
    def update_graphs(self):
        # Si no está en pausa, se actualiza la gráfica de desplazamiento
        if not self.paused:
            with self.data_lock:
                relative_copy = list(self.relative_data)
            self.draw_graph(self.displacement_canvas, relative_copy, self.displacement_range, "Desplazamiento Relativo (mm)")
        # Siempre se dibujan los cursores
        self.draw_cursors()
        self.after(100, self.update_graphs)
    
    def update_mass_position(self, value):
        w = self.animation_canvas.winfo_width()
        if w <= 0:
            return
        margin = w * 0.1
        anim_x_min = margin
        anim_x_max = w - margin
        normalized = (value - self.displacement_range[0]) / (self.displacement_range[1] - self.displacement_range[0])
        normalized = max(0, min(1, normalized))
        self.block_x = anim_x_min + normalized * (anim_x_max - anim_x_min - self.block_width)
    
    def update_animation(self):
        try:
            self.animation_canvas.delete("animation")
            w = self.animation_canvas.winfo_width()
            h = self.animation_canvas.winfo_height()
            if w <= 0 or h <= 0:
                self.after(20, self.update_animation)
                return
            if not self.raw_data:
                self.block_x = 50
            spring_color = "#606060"
            spring_left = [(30, h/2), (self.block_x - 10, h/2)]
            spring_right = [(self.block_x + self.block_width + 10, h/2), (w - 30, h/2)]
            self.animation_canvas.create_line(spring_left[0], spring_left[1],
                                               fill=spring_color, width=3, tags="animation")
            self.animation_canvas.create_rectangle(
                self.block_x, h/2 - self.block_height/2,
                self.block_x + self.block_width, h/2 + self.block_height/2,
                fill="#00FFAA", outline="#303030", tags="animation")
            self.animation_canvas.create_line(spring_right[0], spring_right[1],
                                               fill=spring_color, width=3, tags="animation")
        except Exception as e:
            print("Error en update_animation:", e)
        finally:
            self.after(20, self.update_animation)
    
    def draw_cursors(self):
        """Dibuja dos líneas verticales (cursores) en la gráfica de desplazamiento y actualiza T y F."""
        canvas = self.displacement_canvas
        canvas.delete("cursor")
        w = canvas.winfo_width()
        # Definir el margen usado en draw_graph (fijado en 50)
        left_pad = 50
        if w <= left_pad:
            return
        # Si aún no se han definido, inicializarlos en 1/3 y 2/3 del ancho útil
        if self.cursor1_x is None:
            self.cursor1_x = left_pad + (w - left_pad) * 0.33
        if self.cursor2_x is None:
            self.cursor2_x = left_pad + (w - left_pad) * 0.66
        # Dibujar líneas verticales
        canvas.create_line(self.cursor1_x, 0, self.cursor1_x, canvas.winfo_height(), fill="red", width=2, tags="cursor")
        canvas.create_line(self.cursor2_x, 0, self.cursor2_x, canvas.winfo_height(), fill="red", width=2, tags="cursor")
        # Actualizar T y F en el panel: se asume que la diferencia horizontal representa self.time_window segundos
        effective_width = w - left_pad
        delta_pixels = abs(self.cursor2_x - self.cursor1_x)
        T = (delta_pixels / effective_width) * self.time_window  # Periodo en segundos
        F = 1 / T if T > 0 else 0
        self.period_label.configure(text=f"T: {T:.2f} s")
        self.frequency_label.configure(text=f"F: {F:.2f} Hz")
    
    def on_canvas_click(self, event):
        """Detecta si se hace clic cerca de alguno de los cursores."""
        threshold = 10  # píxeles
        if self.cursor1_x is not None and abs(event.x - self.cursor1_x) < threshold:
            self.active_cursor = "cursor1"
        elif self.cursor2_x is not None and abs(event.x - self.cursor2_x) < threshold:
            self.active_cursor = "cursor2"
        else:
            self.active_cursor = None

    def on_canvas_drag(self, event):
        """Permite arrastrar el cursor activo."""
        if self.active_cursor is not None:
            # Obtener los límites del canvas (se usa left_pad = 50)
            left_pad = 50
            w = self.displacement_canvas.winfo_width()
            new_x = max(left_pad, min(event.x, w))
            if self.active_cursor == "cursor1":
                self.cursor1_x = new_x
            elif self.active_cursor == "cursor2":
                self.cursor2_x = new_x
            self.draw_cursors()

    def on_canvas_release(self, event):
        """Al soltar el botón del mouse se finaliza el movimiento."""
        self.active_cursor = None
        self.draw_cursors()

    def reset_data(self):
        with self.data_lock:
            self.raw_data.clear()
            self.filtered_data.clear()
            self.velocity_data.clear()
            self.acceleration_data.clear()
            self.relative_data.clear()
        # También reiniciamos la posición de los cursores (se harán nuevos en draw_cursors)
        self.cursor1_x = None
        self.cursor2_x = None
    
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
            messagebox.showwarning("Advertencia", "No hay datos guardados")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files","*.csv"),("Todos los archivos","*.*")]
        )
        if not file_path:
            return

        import csv
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Tiempo","Desplaz.","Velocidad","Aceleración"])
            for t, v, vel, acc in self.recorded_data:
                writer.writerow([f"{t:.3f}", f"{v:.3f}", f"{vel:.3f}", f"{acc:.3f}"])
        messagebox.showinfo("Éxito","Datos guardados correctamente")


    
    def on_closing(self):
        if self.serial_thread:
            self.serial_thread.stop()
            self.serial_thread.join(timeout=2)
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
