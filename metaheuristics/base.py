from abc import ABC, abstractmethod
from datetime import datetime
import json
import os

class Metaheuristic(ABC):
    """
    Classe base abstrata para todas as metaheurísticas
    """
    
    def __init__(self, name, problem_instance):
        """
        Inicializa a metaheurística
        
        Args:
            name: Nome da metaheurística
            problem_instance: Instância do problema job shop
        """
        self.name = name
        self.problem = problem_instance
        self.history = []
        self.best_history = []
        self.execution_time = 0
        self.iteration = 0
        self.best_solution = None
        self.best_cost = float('inf')
        self.params = {}
        
    @abstractmethod
    def initialize(self, **kwargs):
        """Inicializa a metaheurística"""
        pass
    
    @abstractmethod
    def step(self):
        """Executa um passo da metaheurística"""
        pass
    
    @abstractmethod
    def get_params_info(self):
        """Retorna informações sobre os parâmetros"""
        pass
    
    def run(self, max_iterations=1000, callback=None, **kwargs):
        """
        Executa a metaheurística por um número máximo de iterações
        """
        self.initialize(**kwargs)
        
        for iteration in range(max_iterations):
            self.iteration = iteration
            solution, cost = self.step()
            
            self.history.append(cost)
            
            if cost < self.best_cost:
                self.best_cost = cost
                self.best_solution = solution.copy() if hasattr(solution, 'copy') else solution
                
            self.best_history.append(self.best_cost)
            
            if callback:
                should_continue = callback(iteration, cost, self.best_cost, solution)
                if not should_continue:
                    break
        
        final_results = self.evaluate_solution(self.best_solution)
        
        return {
            'name': self.name,
            'best_solution': self.best_solution,
            'best_cost': self.best_cost,
            'makespan': final_results['makespan'],
            'tardiness': final_results['tardiness'],
            'schedule': final_results['schedule'],
            'job_completion_times': final_results['job_completion_times'],
            'history': self.history,
            'best_history': self.best_history,
            'iterations': self.iteration + 1,
            'params': self.params,
            'execution_time': self.execution_time
        }
    
    def run_with_time_limit(self, time_limit_seconds=60, callback=None, **kwargs):
        """
        Executa a metaheurística com limite de tempo
        """
        import time
        
        self.initialize(**kwargs)
        start_time = time.time()
        
        iteration = 0
        while time.time() - start_time < time_limit_seconds:
            self.iteration = iteration
            solution, cost = self.step()
            
            self.history.append(cost)
            
            if cost < self.best_cost:
                self.best_cost = cost
                self.best_solution = solution.copy() if hasattr(solution, 'copy') else solution
                
            self.best_history.append(self.best_cost)
            
            if callback:
                should_continue = callback(iteration, cost, self.best_cost, solution)
                if not should_continue:
                    break
            
            iteration += 1
        
        self.execution_time = time.time() - start_time
        
        final_results = self.evaluate_solution(self.best_solution)
        
        return {
            'name': self.name,
            'best_solution': self.best_solution,
            'best_cost': self.best_cost,
            'makespan': final_results['makespan'],
            'tardiness': final_results['tardiness'],
            'schedule': final_results['schedule'],
            'job_completion_times': final_results['job_completion_times'],
            'history': self.history,
            'best_history': self.best_history,
            'iterations': iteration,
            'params': self.params,
            'execution_time': self.execution_time
        }
    
    @abstractmethod
    def evaluate_solution(self, solution):
        """Avalia uma solução"""
        pass
    
    def save_solution(self, results, filename=None):
        """Salva os resultados em arquivo"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.name}_{timestamp}"
        
        solution_serializable = {}
        if results['best_solution']:
            for k, v in results['best_solution'].items():
                if isinstance(k, tuple):
                    solution_serializable[f"{k[0]}_{k[1]}"] = v
                else:
                    solution_serializable[str(k)] = v
        
        save_data = {
            'metaheuristic': self.name,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'best_cost': results['best_cost'],
            'makespan': results['makespan'],
            'tardiness': results['tardiness'],
            'iterations': results['iterations'],
            'execution_time': results.get('execution_time', 0),
            'params': self.params,
            'solution': solution_serializable,
            'job_completion_times': results['job_completion_times']
        }
        
        os.makedirs('reports', exist_ok=True)
        with open(f'reports/{filename}.json', 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2)
        
        return filename