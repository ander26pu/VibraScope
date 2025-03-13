import customtkinter as ctk
import tkinter as tk
import serial
import threading

# Configuración del puerto serial
SERIAL_PORT = "COM6"
BAUD_RATE = 115200

class SerialReader(threading.Thread):
    def __init__(self, port, baudrate, callback):
        super().__init__()
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
        except Exception as e:
            print("Error al abrir el puerto serial:", e)
            self.ser = None
        self.callback = callback
        self.running = True

    def run(self):
        if not self.ser:
            return
        while self.running:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if line.startswith("D:"):
                    data_str = line.split("D:")[1]
                    try:
                        value = float(data_str)
                        self.callback(value)
                    except ValueError:
                        pass
            except Exception as e:
                print("Error leyendo el serial:", e)
        if self.ser:
            self.ser.close()

    def stop(self):
        self.running = False

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.title("VibraScope")
        self.geometry("1000x600")
        
        # Frame principal
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Label superior con el valor actual
        self.value_label = ctk.CTkLabel(self.frame, text="Valor: 0.0", font=("Arial", 16))
        self.value_label.pack(pady=(0, 10))
        
        # Frame de contenido para dividir la gráfica y la animación
        self.content_frame = ctk.CTkFrame(self.frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Usamos grid para disponer dos áreas: gráfica (fila 0) y animación (fila 1)
        self.content_frame.grid_rowconfigure(0, weight=3)
        self.content_frame.grid_rowconfigure(1, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Canvas para la gráfica (responsive)
        self.graph_canvas = tk.Canvas(self.content_frame, bg="#1E1E1E")
        self.graph_canvas.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Canvas para la animación (responsive)
        self.animation_canvas = tk.Canvas(self.content_frame, bg="#1E1E1E")
        self.animation_canvas.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        self.data = []
        self.max_data = 200
        
        self.serial_thread = SerialReader(SERIAL_PORT, BAUD_RATE, self.add_data)
        self.serial_thread.start()
        
        # Parámetros para la gráfica
        self.y_min = 0
        self.y_max = 300
        
        # Parámetros para la animación (se actualizarán de forma responsive)
        self.block_x = 0  # posición horizontal de la masa (actualizada en update_mass_position)
        self.block_y = 0  # se calcula como la mitad de la altura del canvas de animación
        self.block_width = 100
        self.block_height = 120
        
        self.update_interface()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def add_data(self, value):
        self.data.append(value)
        if len(self.data) > self.max_data:
            self.data.pop(0)
        self.value_label.configure(text=f"Valor: {value:.2f}")
        self.update_mass_position(value)
    
    def update_interface(self):
        self.update_graph()
        self.update_animation()
        self.after(100, self.update_interface)
    
    def update_graph(self):
        self.graph_canvas.delete("graph")
        width = self.graph_canvas.winfo_width()
        height = self.graph_canvas.winfo_height()
        
        top_padding = 50         # Margen superior para la gráfica
        bottom_padding = 50      # Margen inferior para la gráfica (donde se verá el eje x)
        left_padding = 50        # Margen izquierdo para el eje y y etiquetas
        
        # Dibujar cuadrícula en la gráfica
        num_lines = 6
        for i in range(num_lines + 1):
            y = top_padding + i * ((height - top_padding - bottom_padding) / num_lines)
            self.graph_canvas.create_line(left_padding, y, width, y, fill="#333333", dash=(2, 4), tags="graph")
            val = self.y_max - i * ((self.y_max - self.y_min) / num_lines)
            self.graph_canvas.create_text(left_padding - 10, y, text=f"{val:.0f}", fill="white",
                                        anchor="e", font=("Arial", 10), tags="graph")
        
        # Dibujar la gráfica de datos
        if len(self.data) > 1:
            x_step = (width - left_padding) / (self.max_data - 1)
            points = []
            for i, value in enumerate(self.data):
                x = left_padding + i * x_step
                # Se dibuja en el área entre top_padding y (height - bottom_padding)
                y = (height - bottom_padding) - ((value - self.y_min) / (self.y_max - self.y_min)) * (height - top_padding - bottom_padding)
                points.append((x, y))
            for i in range(len(points) - 1):
                self.graph_canvas.create_line(points[i][0], points[i][1],
                                            points[i+1][0], points[i+1][1],
                                            fill="#00FFFF", width=2, smooth=True, tags="graph")

    
    def update_mass_position(self, value):
        # Se obtienen las dimensiones actuales del canvas de animación para calcular márgenes y límites
        w = self.animation_canvas.winfo_width()
        h = self.animation_canvas.winfo_height()
        margin = w * 0.1  # 10% del ancho como margen
        anim_x_min = margin
        anim_x_max = w - margin
        self.block_y = h / 2
        
        # Normalizamos el valor recibido entre 0 y 1
        normalized = (value - self.y_min) / (self.y_max - self.y_min)
        normalized = max(0, min(1, normalized))
        self.block_x = anim_x_min + normalized * (anim_x_max - anim_x_min)
    
    def update_animation(self):
        self.animation_canvas.delete("animation")
        w = self.animation_canvas.winfo_width()
        h = self.animation_canvas.winfo_height()
        margin = w * 0.1
        anim_x_min = margin
        anim_x_max = w - margin
        self.block_y = h / 2
        
        num_coils = 20
        # Espaciado de resortes basado en el ancho actual
        left_spring_spacing = (self.block_x - anim_x_min) / num_coils if self.block_x > anim_x_min else 0
        right_spring_spacing = (anim_x_max - self.block_x) / num_coils if self.block_x < anim_x_max else 0
        
        # Resorte izquierdo
        left_points = [(anim_x_min, self.block_y)]
        for i in range(1, num_coils):
            x = anim_x_min + i * left_spring_spacing
            y = self.block_y + ((-1)**i * 10)
            left_points.append((x, y))
        left_points.append((self.block_x - self.block_width/2, self.block_y))
        for i in range(len(left_points)-1):
            self.animation_canvas.create_line(left_points[i], left_points[i+1],
                                               fill="white", width=2, tags="animation")
        
        # Resorte derecho
        right_points = [(self.block_x + self.block_width/2, self.block_y)]
        for i in range(1, num_coils):
            x = self.block_x + self.block_width/2 + i * right_spring_spacing
            y = self.block_y + ((-1)**i * 10)
            right_points.append((x, y))
        #right_points.append((anim_x_max, self.block_y))
        for i in range(len(right_points)-1):
            self.animation_canvas.create_line(right_points[i], right_points[i+1],
                                               fill="white", width=2, tags="animation")
        
        # Dibujar la masa (bloque)
        self.animation_canvas.create_rectangle(
            self.block_x - self.block_width/2, self.block_y - self.block_height/2,
            self.block_x + self.block_width/2, self.block_y + self.block_height/2,
            fill="cyan", outline="white", tags="animation"
        )
    
    def on_closing(self):
        self.serial_thread.stop()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
