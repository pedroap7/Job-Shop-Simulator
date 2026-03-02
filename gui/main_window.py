import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from datetime import datetime

from core.scheduler import JobShopScheduler
from core.problem import JobShopProblem
from gui.gantt_viewer import GanttViewer
from gui.evolution_plot import EvolutionPlot
from gui.experiment_panel import ExperimentPanel
from gui.comparison_view import ComparisonView
from utils import load_instance

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Job Shop Simulator - Interface de Experimentos")
        
        # Carrega instância do problema
        self.instance_file = 'data/instance.json'
        self.ensure_instance_file()
        self.instance = load_instance(self.instance_file)
        self.problem = JobShopProblem(instance_data=self.instance)
        
        # Dados dos experimentos
        self.experiments = []
        self.current_experiment = None
        self.scheduler = JobShopScheduler(self.instance)
        
        # Configura estilo
        self.setup_styles()
        
        # Cria interface
        self.create_menu()
        self.create_main_layout()
        
    def ensure_instance_file(self):
        """Garante que o arquivo de instância existe"""
        if not os.path.exists(self.instance_file):
            os.makedirs('data', exist_ok=True)
            
            default_instance = {
                "jobs": {
                    "Job1": {"due_date": 100, "operations": [
                        {"machine": 1, "time": 8}, {"machine": 3, "time": 12},
                        {"machine": 2, "time": 10}, {"machine": 4, "time": 7},
                        {"machine": 5, "time": 9}
                    ]},
                    "Job2": {"due_date": 120, "operations": [
                        {"machine": 1, "time": 6}, {"machine": 2, "time": 14},
                        {"machine": 4, "time": 9}, {"machine": 5, "time": 11},
                        {"machine": 3, "time": 8}
                    ]},
                    "Job3": {"due_date": 90, "operations": [
                        {"machine": 1, "time": 10}, {"machine": 4, "time": 8},
                        {"machine": 5, "time": 12}, {"machine": 3, "time": 9},
                        {"machine": 2, "time": 7}
                    ]},
                    "Job4": {"due_date": 110, "operations": [
                        {"machine": 1, "time": 7}, {"machine": 5, "time": 13},
                        {"machine": 3, "time": 8}, {"machine": 2, "time": 10},
                        {"machine": 4, "time": 12}
                    ]},
                    "Job5": {"due_date": 130, "operations": [
                        {"machine": 1, "time": 9}, {"machine": 3, "time": 11},
                        {"machine": 4, "time": 10}, {"machine": 5, "time": 8},
                        {"machine": 2, "time": 13}
                    ]}
                },
                "machines": [1, 2, 3, 4, 5]
            }
            
            with open(self.instance_file, 'w', encoding='utf-8') as f:
                json.dump(default_instance, f, indent=2)
    
    def setup_styles(self):
        """Configura estilos da interface"""
        style = ttk.Style()
        style.theme_use('clam')
        
        self.bg_color = '#f0f0f0'
        self.primary_color = '#2c3e50'
        self.secondary_color = '#3498db'
        
        self.root.configure(bg=self.bg_color)
        
    def create_menu(self):
        """Cria menu principal"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Carregar Instância", command=self.load_instance)
        file_menu.add_command(label="Salvar Experimento", command=self.save_experiment)
        file_menu.add_command(label="Carregar Experimento", command=self.load_experiment)
        file_menu.add_separator()
        file_menu.add_command(label="Exportar Relatório", command=self.export_report)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)
        
        # Menu Experimentos
        exp_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Experimentos", menu=exp_menu)
        exp_menu.add_command(label="Novo Experimento", command=self.new_experiment)
        exp_menu.add_command(label="Comparar Experimentos", command=self.compare_experiments)
        exp_menu.add_separator()
        exp_menu.add_command(label="Limpar Todos", command=self.clear_experiments)
        
        # Menu Visualização
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Visualização", menu=view_menu)
        view_menu.add_command(label="Gráfico de Gantt", command=self.show_selected_gantt)
        view_menu.add_command(label="Evolução", command=self.show_selected_evolution)
        
        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Sobre", command=self.show_about)
        help_menu.add_command(label="Documentação", command=self.show_docs)
        
    def create_main_layout(self):
        """Cria layout principal"""
        # Painel esquerdo
        left_panel = ttk.Frame(self.root, width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left_panel.pack_propagate(False)
        
        # Painel direito
        right_panel = ttk.Frame(self.root)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Cria componentes
        self.create_info_panel(left_panel)
        self.exp_panel = ExperimentPanel(left_panel, self)
        self.exp_panel.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.create_results_panel(right_panel)
        
    def create_info_panel(self, parent):
        """Painel de informações do problema"""
        frame = ttk.LabelFrame(parent, text="Informações do Problema", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        num_jobs = len(self.instance['jobs'])
        num_machines = len(self.instance['machines'])
        num_operations = sum(len(job['operations']) for job in self.instance['jobs'].values())
        
        info_text = f"Jobs: {num_jobs}\nMáquinas: {num_machines}\nOperações: {num_operations}"
        label = ttk.Label(frame, text=info_text, justify=tk.LEFT)
        label.pack()
        
        ttk.Button(frame, text="Ver Detalhes", 
                  command=self.show_instance_details).pack(pady=5)
        
    def create_results_panel(self, parent):
        """Painel de resultados"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba de resultados
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="Resultados")
        
        # Aba de Gantt
        self.gantt_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.gantt_frame, text="Gráfico de Gantt")
        
        # Aba de evolução
        self.evolution_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.evolution_frame, text="Evolução")
        
        # Inicializa visualizadores
        self.gantt_viewer = GanttViewer(self.gantt_frame)
        self.evolution_plot = EvolutionPlot(self.evolution_frame)
        
        self.create_results_table()
        
    def create_results_table(self):
        """Cria tabela de resultados"""
        columns = ('Experimento', 'Metaheurística', 'Makespan', 'Atraso', 'Custo', 'Iterações', 'Tempo(s)')
        self.tree = ttk.Treeview(self.results_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(self.results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind('<<TreeviewSelect>>', self.on_experiment_select)
        
        # Botões
        button_frame = ttk.Frame(self.results_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Ver Gantt", 
                  command=self.show_selected_gantt).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Ver Evolução", 
                  command=self.show_selected_evolution).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Salvar", 
                  command=self.save_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remover", 
                  command=self.remove_selected).pack(side=tk.LEFT, padx=5)
        
    def load_instance(self):
        """Carrega nova instância do problema"""
        filename = filedialog.askopenfilename(
            title="Selecionar Instância",
            filetypes=[("JSON files", "*.json")]
        )
        if filename:
            try:
                self.instance = load_instance(filename)
                self.problem = JobShopProblem(instance_data=self.instance)
                self.scheduler = JobShopScheduler(self.instance)
                messagebox.showinfo("Sucesso", "Instância carregada com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar instância: {e}")
    
    def save_experiment(self):
        """Salva experimento atual"""
        if not self.current_experiment:
            messagebox.showwarning("Aviso", "Nenhum experimento selecionado!")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Salvar Experimento",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.current_experiment, f, indent=2, default=str)
                messagebox.showinfo("Sucesso", "Experimento salvo com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar: {e}")
    
    def load_experiment(self):
        """Carrega experimento salvo"""
        filename = filedialog.askopenfilename(
            title="Carregar Experimento",
            filetypes=[("JSON files", "*.json")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    experiment = json.load(f)
                self.experiments.append(experiment)
                self.update_results_table()
                messagebox.showinfo("Sucesso", "Experimento carregado com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar: {e}")
    
    def new_experiment(self):
        """Inicia novo experimento"""
        self.exp_panel.show_new_experiment_dialog()
    
    def compare_experiments(self):
        """Compara múltiplos experimentos"""
        if len(self.experiments) < 2:
            messagebox.showwarning("Aviso", "É necessário pelo menos 2 experimentos para comparação!")
            return
        
        ComparisonView(self.root, self.experiments)
    
    def clear_experiments(self):
        """Limpa todos os experimentos"""
        if messagebox.askyesno("Confirmar", "Limpar todos os experimentos?"):
            self.experiments.clear()
            self.update_results_table()
            self.gantt_viewer.clear()
            self.evolution_plot.clear()
            self.current_experiment = None
    
    def update_results_table(self):
        """Atualiza tabela de resultados"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for exp in self.experiments:
            self.tree.insert('', tk.END, values=(
                exp.get('name', 'Exp'),
                exp.get('metaheuristic', 'N/A'),
                f"{exp.get('makespan', 0):.1f}",
                f"{exp.get('tardiness', 0):.1f}",
                f"{exp.get('best_cost', 0):.2f}",
                exp.get('iterations', 0),
                f"{exp.get('execution_time', 0):.2f}"
            ))
    
    def on_experiment_select(self, event):
        """Callback quando experimento é selecionado"""
        selection = self.tree.selection()
        if selection:
            idx = self.tree.index(selection[0])
            self.current_experiment = self.experiments[idx]
            print(f"Experimento selecionado: {self.current_experiment.get('name', 'N/A')}")
            print(f"  Has schedule: {'schedule' in self.current_experiment}")
            print(f"  Has history: {'history' in self.current_experiment}")
    
    def show_selected_gantt(self):
        """Mostra gráfico de Gantt do experimento selecionado"""
        print("[DEBUG] show_selected_gantt() called")
        if not self.current_experiment:
            print("[DEBUG] No experiment selected")
            messagebox.showwarning("Aviso", "Nenhum experimento selecionado!")
            return
        
        print(f"[DEBUG] Current experiment: {self.current_experiment.get('name')}")
        print(f"[DEBUG] Keys in experiment: {list(self.current_experiment.keys())}")
        
        if 'schedule' not in self.current_experiment:
            print("[DEBUG] No schedule in experiment")
            messagebox.showerror("Erro", "Este experimento não possui dados de schedule.")
            return
        
        try:
            print("[DEBUG] Selecting gantt_frame")
            self.notebook.select(self.gantt_frame)
            print("[DEBUG] Calling gantt_viewer.plot()")
            self.gantt_viewer.plot(
                self.current_experiment['schedule'],
                self.current_experiment.get('makespan', 0),
                self.current_experiment.get('tardiness', 0)
            )
            print("[DEBUG] gantt_viewer.plot() completed")
        except Exception as e:
            print(f"[DEBUG] Exception in show_selected_gantt: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro ao plotar Gantt", f"Erro: {str(e)}")
    
    def show_selected_evolution(self):
        """Mostra gráfico de evolução do experimento selecionado"""
        print("[DEBUG] show_selected_evolution() called")
        if not self.current_experiment:
            print("[DEBUG] No experiment selected")
            messagebox.showwarning("Aviso", "Nenhum experimento selecionado!")
            return
        
        print(f"[DEBUG] Current experiment: {self.current_experiment.get('name')}")
        print(f"[DEBUG] Keys in experiment: {list(self.current_experiment.keys())}")
        
        if 'history' not in self.current_experiment:
            print("[DEBUG] No history in experiment")
            messagebox.showerror("Erro", "Este experimento não possui dados de history.")
            return
        
        try:
            print("[DEBUG] Selecting evolution_frame")
            self.notebook.select(self.evolution_frame)
            print("[DEBUG] Calling evolution_plot.plot()")
            self.evolution_plot.plot(
                self.current_experiment['history'],
                self.current_experiment.get('best_history', []),
                self.current_experiment.get('best_cost', 0)
            )
            print("[DEBUG] evolution_plot.plot() completed")
        except Exception as e:
            print(f"[DEBUG] Exception in show_selected_evolution: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro ao plotar Evolução", f"Erro: {str(e)}")
    
    def save_selected(self):
        """Salva experimento selecionado"""
        if self.current_experiment:
            self.save_experiment()
    
    def remove_selected(self):
        """Remove experimento selecionado"""
        if self.current_experiment:
            idx = self.experiments.index(self.current_experiment)
            self.experiments.pop(idx)
            self.update_results_table()
            self.current_experiment = None
    
    def show_instance_details(self):
        """Mostra detalhes da instância"""
        details = "Detalhes da Instância:\n\n"
        for job_name, job_data in self.instance['jobs'].items():
            details += f"{job_name} (Due: {job_data['due_date']}):\n"
            for i, op in enumerate(job_data['operations'], 1):
                details += f"  Op{i}: Máq {op['machine']} - {op['time']} unidades\n"
        
        messagebox.showinfo("Detalhes da Instância", details)
    
    def export_report(self):
        """Exporta relatório dos experimentos"""
        if not self.experiments:
            messagebox.showwarning("Aviso", "Nenhum experimento para exportar!")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Exportar Relatório",
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("CSV files", "*.csv")]
        )
        
        if filename:
            self.generate_report(filename)
    
    def generate_report(self, filename):
        """Gera relatório em HTML"""
        html_content = f"""
        <html>
        <head>
            <title>Relatório de Experimentos - Job Shop</title>
            <style>
                body {{ font-family: Arial; margin: 20px; }}
                h1 {{ color: #2c3e50; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th {{ background: #3498db; color: white; padding: 10px; }}
                td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
                tr:nth-child(even) {{ background: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Relatório de Experimentos - Job Shop</h1>
            <p>Data: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p>Instância: {os.path.basename(self.instance_file)}</p>
            <table>
                <tr>
                    <th>Experimento</th>
                    <th>Metaheurística</th>
                    <th>Makespan</th>
                    <th>Atraso</th>
                    <th>Custo</th>
                    <th>Iterações</th>
                    <th>Tempo (s)</th>
                </tr>
        """
        
        for exp in self.experiments:
            html_content += f"""
                <tr>
                    <td>{exp.get('name', 'N/A')}</td>
                    <td>{exp.get('metaheuristic', 'N/A')}</td>
                    <td>{exp.get('makespan', 0):.1f}</td>
                    <td>{exp.get('tardiness', 0):.1f}</td>
                    <td>{exp.get('best_cost', 0):.2f}</td>
                    <td>{exp.get('iterations', 0)}</td>
                    <td>{exp.get('execution_time', 0):.2f}</td>
                </tr>
            """
        
        html_content += """
            </table>
        </body>
        </html>
        """
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        messagebox.showinfo("Sucesso", f"Relatório exportado para {filename}")
    
    def show_about(self):
        """Mostra informações sobre o software"""
        about_text = """
        Job Shop Simulator v2.0
        
        Uma plataforma para experimentação com
        metaheurísticas aplicadas ao problema
        de job shop scheduling.
        
        Funcionalidades:
        • Múltiplas metaheurísticas
        • Visualização de Gantt
        • Gráficos de evolução
        • Comparação de experimentos
        • Exportação de relatórios
        
        Desenvolvido em Python com Tkinter
        """
        messagebox.showinfo("Sobre", about_text)
    
    def show_docs(self):
        """Mostra documentação"""
        docs_text = """
        Documentação Rápida:
        
        1. Escolha uma metaheurística no painel
        2. Configure os parâmetros
        3. Execute o experimento
        4. Visualize os resultados
        
        Metaheurísticas disponíveis:
        • Simulated Annealing
        • Algoritmo Genético
        
        Dicas:
        • Use o painel de comparação para avaliar
          diferentes configurações
        • Salve experimentos para análise futura
        """
        messagebox.showinfo("Documentação", docs_text)