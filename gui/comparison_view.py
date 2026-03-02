import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ComparisonView(tk.Toplevel):
    def __init__(self, parent, experiments):
        super().__init__(parent)
        self.parent = parent
        self.experiments = experiments
        
        self.title("Comparação de Experimentos")
        self.geometry("1000x600")
        
        self.create_widgets()
        
    def create_widgets(self):
        """Cria widgets da janela"""
        # Notebook para diferentes visualizações
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Aba de tabela
        table_frame = ttk.Frame(notebook)
        notebook.add(table_frame, text="Tabela Comparativa")
        self.create_table(table_frame)
        
        # Aba de gráfico
        chart_frame = ttk.Frame(notebook)
        notebook.add(chart_frame, text="Gráfico Comparativo")
        self.create_chart(chart_frame)
        
    def create_table(self, parent):
        """Cria tabela comparativa"""
        # Frame para a tabela
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview
        columns = ('Experimento', 'Metaheurística', 'Makespan', 'Atraso', 'Custo', 'Iterações')
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Preenche dados
        for exp in self.experiments:
            tree.insert('', tk.END, values=(
                exp.get('name', 'N/A'),
                exp.get('metaheuristic', 'N/A'),
                f"{exp.get('makespan', 0):.1f}",
                f"{exp.get('tardiness', 0):.1f}",
                f"{exp.get('best_cost', 0):.2f}",
                exp.get('iterations', 0)
            ))
    
    def create_chart(self, parent):
        """Cria gráfico comparativo"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Cria figura
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Prepara dados
        names = [exp.get('name', f'Exp{i}') for i, exp in enumerate(self.experiments)]
        makespans = [exp.get('makespan', 0) for exp in self.experiments]
        tardiness = [exp.get('tardiness', 0) for exp in self.experiments]
        
        # Gráfico de makespan
        x = range(len(names))
        ax1.bar(x, makespans, color='#3498db', alpha=0.8)
        ax1.set_xlabel('Experimento')
        ax1.set_ylabel('Makespan')
        ax1.set_title('Comparação de Makespan')
        ax1.set_xticks(x)
        ax1.set_xticklabels(names, rotation=45, ha='right')
        
        # Gráfico de tardiness
        ax2.bar(x, tardiness, color='#e74c3c', alpha=0.8)
        ax2.set_xlabel('Experimento')
        ax2.set_ylabel('Atraso Total')
        ax2.set_title('Comparação de Atraso')
        ax2.set_xticks(x)
        ax2.set_xticklabels(names, rotation=45, ha='right')
        
        fig.tight_layout()
        
        # Adiciona ao frame
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)