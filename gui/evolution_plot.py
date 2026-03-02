import tkinter as tk
from tkinter import ttk, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class EvolutionPlot(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.figure = None
        self.canvas = None
        self.create_widgets()
        self.pack(fill=tk.BOTH, expand=True)  # Make the frame itself visible
        
    def create_widgets(self):
        """Cria widgets do visualizador"""
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, pady=5)
        
        ttk.Button(toolbar, text="Salvar", command=self.save_figure).pack(side=tk.LEFT, padx=5)
        
        self.plot_frame = ttk.Frame(self)
        self.plot_frame.pack(fill=tk.BOTH, expand=True)
        
    def plot(self, history, best_history, best_cost):
        """Plota gráfico de evolução"""
        print(f"[EvolutionPlot.plot] Called with {len(history)} iterations, best_cost={best_cost}")
        try:
            print("[EvolutionPlot.plot] Clearing plot_frame")
            for widget in self.plot_frame.winfo_children():
                widget.destroy()
            
            if not history or len(history) == 0:
                raise ValueError("History não pode estar vazio")
            
            print("[EvolutionPlot.plot] Creating figure")
            self.figure, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            
            iterations = range(1, len(history) + 1)
            
            # Gráfico 1
            ax1.plot(iterations, history, 'b-', alpha=0.5, linewidth=1, label='Atual')
            if best_history and len(best_history) > 0:
                ax1.plot(iterations, best_history, 'r-', linewidth=2, label='Melhor')
            ax1.set_xlabel('Iteração')
            ax1.set_ylabel('Custo')
            ax1.set_title('Evolução do Algoritmo')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            if best_history and len(best_history) > 0:
                best_iter = np.argmin(best_history) + 1
                ax1.plot(best_iter, best_cost, 'g*', markersize=15, 
                        label=f'Melhor: {best_cost:.2f}')
                ax1.legend()
            
            # Gráfico 2
            cutoff = int(len(history) * 0.8)
            if cutoff < len(history):
                ax2.plot(iterations[cutoff:], history[cutoff:], 'b-', alpha=0.5, linewidth=1)
                if best_history and len(best_history) > 0:
                    ax2.plot(iterations[cutoff:], best_history[cutoff:], 'r-', linewidth=2)
                ax2.set_xlabel('Iteração')
                ax2.set_ylabel('Custo')
                ax2.set_title('Convergência (últimas 20%)')
                ax2.grid(True, alpha=0.3)
            
            stats_text = f"Melhor: {best_cost:.2f}\n"
            stats_text += f"Inicial: {history[0]:.2f}\n"
            if best_cost < history[0]:
                stats_text += f"Melhoria: {(history[0]-best_cost)/history[0]*100:.1f}%"
            
            ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes,
                    fontsize=10, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            self.figure.tight_layout()
            
            print(f"[EvolutionPlot.plot] Creating FigureCanvasTkAgg")
            self.canvas = FigureCanvasTkAgg(self.figure, self.plot_frame)
            print(f"[EvolutionPlot.plot] Drawing canvas")
            self.canvas.draw()
            print(f"[EvolutionPlot.plot] Packing canvas widget")
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            print(f"[EvolutionPlot.plot] Done!")
        except Exception as e:
            import traceback
            print(f"Erro ao plotar Evolução: {e}")
            print(traceback.format_exc())
            raise
        
    def save_figure(self):
        """Salva figura"""
        if self.figure:
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf")]
            )
            if filename:
                self.figure.savefig(filename, dpi=300, bbox_inches='tight')
    
    def clear(self):
        """Limpa gráfico"""
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        self.figure = None
        self.canvas = None