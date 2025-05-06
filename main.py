# main.py
import tkinter as tk
from tkinter import ttk
# Asegúrate que el nombre del archivo es correcto
from interfaz import Interfaz

def main():
    root = tk.Tk()
    # Aplicar un tema ttk (opcional, prueba 'clam', 'alt', 'default', 'vista', etc.)
    # Requiere importar ttk al principio de main.py: from tkinter import ttk
    try:
        style = ttk.Style(root)
        # Preferir temas más modernos si están disponibles en el sistema
        available_themes = style.theme_names()
        if 'vista' in available_themes: style.theme_use('vista') # Windows
        elif 'clam' in available_themes: style.theme_use('clam') # Bueno en Linux/Mac
        else: style.theme_use(style.theme_use()) # Usar el default del sistema
    except tk.TclError:
         print("Temas ttk no disponibles o error al aplicar.")

    app = Interfaz(root)
    root.mainloop()

if __name__ == "__main__":
    main()