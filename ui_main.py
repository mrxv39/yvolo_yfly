import tkinter as tk

class YvoloApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("yvolo")
        self.resizable(False, False)
        window_width = 400
        window_height = 300
        # Center the window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Create a frame to center buttons vertically
        frame = tk.Frame(self)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        button_pad = {'padx': 20, 'pady': 10}

        btn_abrir = tk.Button(frame, text="Abrir Chat", width=20, command=lambda: print("Abrir Chat clicked"))
        btn_abrir.pack(**button_pad)

        btn_cerrar = tk.Button(frame, text="Cerrar Chat", width=20, command=lambda: print("Cerrar Chat clicked"))
        btn_cerrar.pack(**button_pad)

        btn_procesar = tk.Button(frame, text="Procesar Ideas", width=20, command=lambda: print("Procesar Ideas clicked"))
        btn_procesar.pack(**button_pad)

if __name__ == "__main__":
    app = YvoloApp()
    app.mainloop()
