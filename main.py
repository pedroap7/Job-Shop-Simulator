#!/usr/bin/env python3
"""
Job Shop Simulator - Ponto de entrada principal
"""

import sys
import os

# Adiciona o diretório atual ao path do Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow
import tkinter as tk

def main():
    """Função principal"""
    root = tk.Tk()
    
    # Configura título
    root.title("Job Shop Simulator - Metaheuristics Platform")
    
    # Configura ícone se existir
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    # Centraliza janela
    root.update_idletasks()
    width = 1400
    height = 800
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Inicia aplicação
    app = MainWindow(root)
    
    # Loop principal
    root.mainloop()

if __name__ == "__main__":
    main()