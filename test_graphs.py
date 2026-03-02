#!/usr/bin/env python3
"""
Script de diagnóstico para testar visualização de gráficos
Execute este script e siga os passos:

1. Execute um experimento
2. Selecione o experimento na tabela
3. Clique em "Ver Gantt" ou "Ver Evolução"
4. Veja os logs no console para diagnosticar qualquer problema
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow
import tkinter as tk

def main():
    """Função principal"""
    root = tk.Tk()
    
    # Configura título
    root.title("Job Shop Simulator - Diagnóstico de Gráficos")
    
    # Centraliza janela
    root.update_idletasks()
    width = 1400
    height = 800
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    print("=" * 70)
    print("JOB SHOP SIMULATOR - DIAGNÓSTICO DE GRÁFICOS")
    print("=" * 70)
    print("\nPASSOS PARA DIAGNOSTICAR:")
    print("1. Execute um experimento com Simulated Annealing (~10 iterações)")
    print("2. Após terminar, selecione o experimento na tabela")
    print("3. Clique em 'Ver Gantt' e observe os logs:")
    print("   - Deve ver '[DEBUG] show_selected_gantt() called'")
    print("   - Deve ver '[GanttViewer.plot] ...' messages")
    print("4. Clique em 'Ver Evolução' e observe os logs:")
    print("   - Deve ver '[DEBUG] show_selected_evolution() called'")
    print("   - Deve ver '[EvolutionPlot.plot] ...' messages")
    print("\nSe os logs aparecerem mas o gráfico não:")
    print("- Verifique se o canvas está sendo criado")
    print("- Verifique a aba selecionada (Gantt ou Evolução)")
    print("\n" + "=" * 70 + "\n")
    
    # Inicia aplicação
    app = MainWindow(root)
    
    # Loop principal
    root.mainloop()

if __name__ == "__main__":
    main()
