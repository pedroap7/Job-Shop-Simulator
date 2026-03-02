import tkinter as tk
from tkinter import ttk, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as mpatches

class GanttViewer(ttk.Frame):
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
        
    def plot(self, schedule, makespan, tardiness):
        """Plota gráfico de Gantt"""
        print(f"[GanttViewer.plot] Called with makespan={makespan}, tardiness={tardiness}")
        try:
            print("[GanttViewer.plot] Clearing plot_frame")
            for widget in self.plot_frame.winfo_children():
                widget.destroy()
            
            if not schedule:
                raise ValueError("Schedule não pode estar vazio")
            
            self.figure = plt.Figure(figsize=(12, 6))
            ax = self.figure.add_subplot(111)
            
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
            
            job_list = list(schedule.keys())
            for job_idx, job_name in enumerate(job_list):
                job_ops = schedule[job_name]
                for op in job_ops:
                    start = op['start_time']
                    end = op['end_time']
                    machine = op['machine']
                    
                    ax.barh(y=f'Máquina {machine}', 
                           width=end-start, 
                           left=start, 
                           height=0.5,
                           color=colors[job_idx % len(colors)],
                           edgecolor='black',
                           alpha=0.8)
                    
                    ax.text(start + (end-start)/2, f'Máquina {machine}', 
                           f'J{job_idx+1}.O{op["op_num"]}',
                           ha='center', va='center', fontsize=8, fontweight='bold')
            
            ax.set_xlabel('Tempo', fontsize=12)
            ax.set_ylabel('Máquinas', fontsize=12)
            ax.set_title(f'Diagrama de Gantt - Makespan: {makespan:.1f}, Atraso: {tardiness:.1f}', 
                        fontsize=14, fontweight='bold')
            
            handles = [mpatches.Patch(color=colors[i], label=f'Job {i+1}') for i in range(len(job_list))]
            ax.legend(handles=handles, loc='upper right')
            
            ax.grid(True, alpha=0.3)
            ax.set_xlim(0, makespan * 1.05 if makespan > 0 else 1)
            
            self.figure.tight_layout()
            
            print(f"[GanttViewer.plot] Creating FigureCanvasTkAgg")
            self.canvas = FigureCanvasTkAgg(self.figure, self.plot_frame)
            print(f"[GanttViewer.plot] Drawing canvas")
            self.canvas.draw()
            print(f"[GanttViewer.plot] Packing canvas widget")
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            print(f"[GanttViewer.plot] Done!")
        except Exception as e:
            import traceback
            print(f"Erro ao plotar Gantt: {e}")
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