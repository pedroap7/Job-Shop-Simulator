import random
import math
from copy import deepcopy
from .base import Metaheuristic
from core.scheduler import JobShopScheduler
from core.solution import Solution

class SimulatedAnnealing(Metaheuristic):
    """
    Implementação do Simulated Annealing para Job Shop
    """
    
    def __init__(self, problem_instance):
        super().__init__("Simulated Annealing", problem_instance)
        
        self.initial_temp = 1000
        self.cooling_rate = 0.95
        self.min_temp = 1
        self.weight_makespan = 0.5
        self.weight_tardiness = 0.5
        self.multi_changes = False
        
        from core.problem import JobShopProblem
        if isinstance(problem_instance, JobShopProblem):
            self.problem_obj = problem_instance
        else:
            from core.problem import JobShopProblem
            self.problem_obj = JobShopProblem(instance_data=problem_instance)
        
        self.all_operations = self.problem_obj.get_all_operations()
        self.num_operations = len(self.all_operations)
        self.current_solution = None
        self.current_cost = None
        self.temperature = None
        
    def get_params_info(self):
        return {
            'initial_temp': {
                'type': 'float',
                'default': 1000,
                'min': 100,
                'max': 10000,
                'description': 'Temperatura inicial'
            },
            'cooling_rate': {
                'type': 'float',
                'default': 0.95,
                'min': 0.8,
                'max': 0.99,
                'description': 'Taxa de resfriamento'
            },
            'min_temp': {
                'type': 'float',
                'default': 1,
                'min': 0.1,
                'max': 100,
                'description': 'Temperatura mínima'
            },
            'weight_makespan': {
                'type': 'float',
                'default': 0.5,
                'min': 0,
                'max': 1,
                'description': 'Peso do makespan'
            },
            'multi_changes': {
                'type': 'bool',
                'default': False,
                'description': 'Múltiplas mudanças'
            }
        }
    
    def initialize(self, **kwargs):
        self.initial_temp = kwargs.get('initial_temp', 1000)
        self.cooling_rate = kwargs.get('cooling_rate', 0.95)
        self.min_temp = kwargs.get('min_temp', 1)
        self.weight_makespan = kwargs.get('weight_makespan', 0.5)
        self.weight_tardiness = 1.0 - self.weight_makespan
        self.multi_changes = kwargs.get('multi_changes', False)
        
        self.params = {
            'initial_temp': self.initial_temp,
            'cooling_rate': self.cooling_rate,
            'min_temp': self.min_temp,
            'weight_makespan': self.weight_makespan,
            'weight_tardiness': self.weight_tardiness,
            'multi_changes': self.multi_changes
        }
        
        if kwargs.get('initial_solution'):
            if isinstance(kwargs['initial_solution'], Solution):
                self.current_solution = kwargs['initial_solution'].copy()
            else:
                self.current_solution = Solution(self.problem_obj, deepcopy(kwargs['initial_solution']))
        else:
            self.current_solution = Solution(self.problem_obj)
        
        self.current_cost = self._evaluate(self.current_solution)
        self.best_solution = self.current_solution.copy()
        self.best_cost = self.current_cost
        self.temperature = self.initial_temp
    
    def _get_neighbor(self, solution):
        neighbor = solution.copy()
        op = random.choice(self.all_operations)
        
        if random.random() < 0.5:
            current = neighbor.get_priority(*op)
            if current < 50:
                neighbor.set_priority(*op, current + 1)
        else:
            current = neighbor.get_priority(*op)
            if current > 1:
                neighbor.set_priority(*op, current - 1)
        
        return neighbor
    
    def _get_neighbor_multi(self, solution, num_changes=2):
        neighbor = solution.copy()
        
        for _ in range(num_changes):
            op = random.choice(self.all_operations)
            if random.random() < 0.5:
                current = neighbor.get_priority(*op)
                if current < 50:
                    neighbor.set_priority(*op, current + 1)
            else:
                current = neighbor.get_priority(*op)
                if current > 1:
                    neighbor.set_priority(*op, current - 1)
        
        return neighbor
    
    def _evaluate(self, solution):
        scheduler = JobShopScheduler(self.problem_obj.data)
        results = scheduler.simulate_with_user_priority(solution.priorities)
        
        makespan = results['makespan']
        tardiness = results['tardiness']
        
        return self.weight_makespan * makespan + self.weight_tardiness * (tardiness + 1)
    
    def evaluate_solution(self, solution):
        scheduler = JobShopScheduler(self.problem_obj.data)
        return scheduler.simulate_with_user_priority(solution.priorities)
    
    def step(self):
        if self.multi_changes:
            neighbor = self._get_neighbor_multi(self.current_solution)
        else:
            neighbor = self._get_neighbor(self.current_solution)
        
        neighbor_cost = self._evaluate(neighbor)
        delta = neighbor_cost - self.current_cost
        
        if delta < 0 or random.random() < math.exp(-delta / self.temperature):
            self.current_solution = neighbor
            self.current_cost = neighbor_cost
        
        self.temperature *= self.cooling_rate
        
        return self.current_solution, self.current_cost