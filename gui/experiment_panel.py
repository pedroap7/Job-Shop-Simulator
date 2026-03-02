import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime

from metaheuristics.simulated_annealing import SimulatedAnnealing
from metaheuristics.genetic_algorithm import GeneticAlgorithm

class ExperimentPanel(ttk.Frame):
    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.parent = parent
        self.main_window = main_window
        self.running = False
        self.current_thread = None
        
        self.create_widgets()
        
    def create_widgets(self):
        """Cria widgets do painel"""
        # Frame de seleção
        heur_frame = ttk.LabelFrame(self, text="Metaheurística", padding=10)
        heur_frame.pack(fill=tk.X, pady=5)
        
        self.heuristic_var = tk.StringVar(value="sa")
        ttk.Radiobutton(heur_frame, text="Simulated Annealing", 
                       variable=self.heuristic_var, value="sa",
                       command=self.update_params).pack(anchor=tk.W)
        ttk.Radiobutton(heur_frame, text="Algoritmo Genético", 
                       variable=self.heuristic_var, value="ga",
                       command=self.update_params).pack(anchor=tk.W)
        
        # Frame de parâmetros
        self.params_frame = ttk.LabelFrame(self, text="Parâmetros", padding=10)
        self.params_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.create_sa_params()
        
        # Frame de controle
        control_frame = ttk.LabelFrame(self, text="Controle", padding=10)
        control_frame.pack(fill=tk.X, pady=5)
        
        # Nome
        ttk.Label(control_frame, text="Nome:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.exp_name = ttk.Entry(control_frame)
        self.exp_name.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=5)
        control_frame.columnconfigure(1, weight=1)
        
        # Modo
        ttk.Label(control_frame, text="Modo:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.mode_var = tk.StringVar(value="iterations")
        ttk.Radiobutton(control_frame, text="Iterações", 
                       variable=self.mode_var, value="iterations").grid(row=1, column=1, sticky=tk.W)
        ttk.Radiobutton(control_frame, text="Tempo (s)", 
                       variable=self.mode_var, value="time").grid(row=1, column=2, sticky=tk.W)
        
        # Limite
        ttk.Label(control_frame, text="Limite:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.limit_var = tk.StringVar(value="1000")
        ttk.Entry(control_frame, textvariable=self.limit_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Botões
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        self.run_button = ttk.Button(button_frame, text="Executar", 
                                     command=self.run_experiment)
        self.run_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Parar", 
                                      command=self.stop_experiment, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Progresso
        self.progress = ttk.Progressbar(control_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=3, sticky=tk.EW, pady=5)
        
        # Status
        self.status_label = ttk.Label(control_frame, text="Pronto")
        self.status_label.grid(row=5, column=0, columnspan=3, pady=5)
        
    def create_sa_params(self):
        """Cria parâmetros do SA"""
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        
        params = [
            ("Temperatura Inicial:", "initial_temp", "1000"),
            ("Taxa Resfriamento:", "cooling_rate", "0.95"),
            ("Temp. Mínima:", "min_temp", "1"),
            ("Peso Makespan:", "weight_makespan", "0.5"),
        ]
        
        self.sa_vars = {}
        
        for i, (label, key, default) in enumerate(params):
            ttk.Label(self.params_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            var = tk.StringVar(value=default)
            self.sa_vars[key] = var
            ttk.Entry(self.params_frame, textvariable=var, width=10).grid(row=i, column=1, sticky=tk.W, pady=5, padx=5)
        
        self.multi_changes_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.params_frame, text="Múltiplas mudanças", 
                       variable=self.multi_changes_var).grid(row=len(params), column=0, columnspan=2, sticky=tk.W, pady=5)
        
    def create_ga_params(self):
        """Cria parâmetros do AG"""
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        
        params = [
            ("Tamanho População:", "pop_size", "50"),
            ("Taxa Mutação:", "mutation_rate", "0.1"),
            ("Taxa Crossover:", "crossover_rate", "0.8"),
            ("Tamanho Elite:", "elite_size", "5"),
            ("Peso Makespan:", "weight_makespan", "0.5"),
        ]
        
        self.ga_vars = {}
        
        for i, (label, key, default) in enumerate(params):
            ttk.Label(self.params_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            var = tk.StringVar(value=default)
            self.ga_vars[key] = var
            ttk.Entry(self.params_frame, textvariable=var, width=10).grid(row=i, column=1, sticky=tk.W, pady=5, padx=5)
        
    def update_params(self):
        """Atualiza parâmetros conforme metaheurística"""
        if self.heuristic_var.get() == "sa":
            self.create_sa_params()
        else:
            self.create_ga_params()
    
    def get_heuristic_instance(self):
        """Retorna instância da metaheurística"""
        heur = self.heuristic_var.get()
        
        if heur == "sa":
            sa = SimulatedAnnealing(self.main_window.problem)
            params = {
                'initial_temp': float(self.sa_vars['initial_temp'].get()),
                'cooling_rate': float(self.sa_vars['cooling_rate'].get()),
                'min_temp': float(self.sa_vars['min_temp'].get()),
                'weight_makespan': float(self.sa_vars['weight_makespan'].get()),
                'multi_changes': self.multi_changes_var.get()
            }
            return sa, params
        else:
            ga = GeneticAlgorithm(self.main_window.problem)
            params = {
                'population_size': int(self.ga_vars['pop_size'].get()),
                'mutation_rate': float(self.ga_vars['mutation_rate'].get()),
                'crossover_rate': float(self.ga_vars['crossover_rate'].get()),
                'elite_size': int(self.ga_vars['elite_size'].get()),
                'weight_makespan': float(self.ga_vars['weight_makespan'].get())
            }
            return ga, params
    
    def run_experiment(self):
        """Executa experimento"""
        if self.running:
            return
        
        exp_name = self.exp_name.get().strip()
        if not exp_name:
            exp_name = f"Exp_{datetime.now().strftime('%H%M%S')}"
            self.exp_name.insert(0, exp_name)
        
        heuristic, params = self.get_heuristic_instance()
        
        try:
            limit = float(self.limit_var.get())
        except ValueError:
            messagebox.showerror("Erro", "Limite inválido!")
            return
        
        mode = self.mode_var.get()
        
        self.running = True
        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress.start()
        
        self.current_thread = threading.Thread(
            target=self._run_experiment_thread,
            args=(heuristic, params, mode, limit, exp_name)
        )
        self.current_thread.daemon = True
        self.current_thread.start()
    
    def _run_experiment_thread(self, heuristic, params, mode, limit, exp_name):
        """Thread de execução"""
        def callback(iteration, cost, best_cost, solution):
            self.main_window.root.after(0, self.update_status, 
                                       iteration, cost, best_cost)
            return self.running
        
        try:
            if mode == "iterations":
                results = heuristic.run(
                    max_iterations=int(limit),
                    callback=callback,
                    **params
                )
            else:
                results = heuristic.run_with_time_limit(
                    time_limit_seconds=limit,
                    callback=callback,
                    **params
                )
            
            results['name'] = exp_name
            results['metaheuristic'] = heuristic.name
            
            self.main_window.root.after(0, self._on_experiment_complete, results)
            
        except Exception as e:
            self.main_window.root.after(0, self._on_experiment_error, str(e))
    
    def update_status(self, iteration, cost, best_cost):
        """Atualiza status na interface"""
        self.status_label.config(
            text=f"Iteração {iteration} | Custo: {cost:.2f} | Melhor: {best_cost:.2f}"
        )
    
    def _on_experiment_complete(self, results):
        """Callback quando experimento termina"""
        self.running = False
        self.progress.stop()
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Concluído!")
        
        self.main_window.experiments.append(results)
        self.main_window.update_results_table()
        
        messagebox.showinfo("Sucesso", "Experimento concluído com sucesso!")
    
    def _on_experiment_error(self, error_msg):
        """Callback quando ocorre erro"""
        self.running = False
        self.progress.stop()
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Erro!")
        
        messagebox.showerror("Erro", f"Erro durante execução: {error_msg}")
    
    def stop_experiment(self):
        """Para experimento em execução"""
        self.running = False
        self.status_label.config(text="Parando...")
    
    def show_new_experiment_dialog(self):
        """Mostra diálogo para novo experimento"""
        self.exp_name.delete(0, tk.END)
        self.exp_name.insert(0, f"Exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}")