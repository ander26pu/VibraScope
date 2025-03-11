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
        ctk.set_appearance_mode("dark")  # Modo oscuro
        self.title("VibraScope")
        self.geometry("1000x600")
        
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

        # Label para mostrar el valor actual
        self.value_label = ctk.CTkLabel(self.frame, text="Valor: 0.0", font=("Arial", 16))
        self.value_label.pack(pady=(0, 10))

        # Canvas con fondo personalizado
        self.canvas = tk.Canvas(self.frame, bg="#1E1E1E")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.data = []
        self.max_data = 200

        self.serial_thread = SerialReader(SERIAL_PORT, BAUD_RATE, self.add_data)
        self.serial_thread.start()

        self.update_graph()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def add_data(self, value):
        self.data.append(value)
        if len(self.data) > self.max_data:
            self.data.pop(0)
        # Actualiza el label con el último valor
        self.value_label.configure(text=f"Valor: {value:.2f}")

    def draw_grid(self, width, height, padding):
        # Líneas horizontales y etiquetas en el eje Y
        num_lines = 6
        for i in range(num_lines + 1):
            y = padding + i * ((height - padding) / num_lines)
            self.canvas.create_line(padding, y, width, y, fill="#333333", dash=(2, 4))
            # Etiqueta del eje Y
            val = self.y_max - i * ((self.y_max - self.y_min) / num_lines)
            self.canvas.create_text(padding - 10, y, text=f"{val:.0f}", fill="white", anchor="e", font=("Arial", 10))
        
        # Líneas verticales y etiquetas en el eje X cada 20 puntos de datos
        if self.max_data > 1:
            x_step = (width - padding) / (self.max_data - 1)
            for i in range(0, self.max_data, 20):
                x = padding + i * x_step
                self.canvas.create_line(x, padding, x, height - padding, fill="#333333", dash=(2, 4))
                # Etiqueta del eje X (puede representar tiempo o índice)
                self.canvas.create_text(x, height - padding + 15, text=str(i), fill="white", anchor="n", font=("Arial", 10))

    def update_graph(self):
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        padding = 50  # Espacio para ejes y etiquetas

        # Definición de rango en el eje Y (puede hacerse dinámico)
        self.y_min = 0
        self.y_max = 300
        range_val = self.y_max - self.y_min
        if range_val == 0:
            range_val = 1

        # Dibuja la cuadrícula y etiquetas de los ejes
        self.draw_grid(width, height, padding)

        # Calcular y dibujar la gráfica
        if len(self.data) > 1:
            x_step = (width - padding) / (self.max_data - 1)
            points = []
            for i, value in enumerate(self.data):
                x = padding + i * x_step
                # Ajuste para que la gráfica se dibuje dentro del área delimitada por padding
                y = height - padding - ((value - self.y_min) / range_val) * (height - 2 * padding)
                points.append((x, y))
            
            # Dibujar línea de la gráfica con suavizado
            for i in range(len(points) - 1):
                self.canvas.create_line(points[i][0], points[i][1],
                                        points[i+1][0], points[i+1][1],
                                        fill="#00FFFF", width=2, smooth=True)
        
        # Título del gráfico
        self.canvas.create_text(width/2, padding/2, text="Gráfica de Vibración", fill="white", font=("Arial", 14, "bold"))
        
        self.after(100, self.update_graph)

    def on_closing(self):
        self.serial_thread.stop()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
