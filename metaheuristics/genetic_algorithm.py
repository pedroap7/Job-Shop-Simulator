import random
from copy import deepcopy
from .base import Metaheuristic
from core.scheduler import JobShopScheduler
from core.solution import Solution

class GeneticAlgorithm(Metaheuristic):
    """
    Implementação de Algoritmo Genético para Job Shop
    """
    
    def __init__(self, problem_instance):
        super().__init__("Algoritmo Genético", problem_instance)
        
        self.population_size = 50
        self.mutation_rate = 0.1
        self.crossover_rate = 0.8
        self.elite_size = 5
        self.tournament_size = 3
        self.weight_makespan = 0.5
        self.weight_tardiness = 0.5
        
        from core.problem import JobShopProblem
        if isinstance(problem_instance, JobShopProblem):
            self.problem_obj = problem_instance
        else:
            from core.problem import JobShopProblem
            self.problem_obj = JobShopProblem(instance_data=problem_instance)
        
        self.all_operations = self.problem_obj.get_all_operations()
        self.num_operations = len(self.all_operations)
        self.population = []
        self.fitness = []
        
    def get_params_info(self):
        return {
            'population_size': {
                'type': 'int',
                'default': 50,
                'min': 10,
                'max': 200,
                'description': 'Tamanho da população'
            },
            'mutation_rate': {
                'type': 'float',
                'default': 0.1,
                'min': 0.01,
                'max': 0.5,
                'description': 'Taxa de mutação'
            },
            'crossover_rate': {
                'type': 'float',
                'default': 0.8,
                'min': 0.5,
                'max': 1.0,
                'description': 'Taxa de crossover'
            },
            'elite_size': {
                'type': 'int',
                'default': 5,
                'min': 1,
                'max': 20,
                'description': 'Número de indivíduos elite'
            },
            'weight_makespan': {
                'type': 'float',
                'default': 0.5,
                'min': 0,
                'max': 1,
                'description': 'Peso do makespan'
            }
        }
    
    def initialize(self, **kwargs):
        self.population_size = kwargs.get('population_size', 50)
        self.mutation_rate = kwargs.get('mutation_rate', 0.1)
        self.crossover_rate = kwargs.get('crossover_rate', 0.8)
        self.elite_size = kwargs.get('elite_size', 5)
        self.tournament_size = kwargs.get('tournament_size', 3)
        self.weight_makespan = kwargs.get('weight_makespan', 0.5)
        self.weight_tardiness = 1.0 - self.weight_makespan
        
        self.params = {
            'population_size': self.population_size,
            'mutation_rate': self.mutation_rate,
            'crossover_rate': self.crossover_rate,
            'elite_size': self.elite_size,
            'tournament_size': self.tournament_size,
            'weight_makespan': self.weight_makespan,
            'weight_tardiness': self.weight_tardiness
        }
        
        if kwargs.get('initial_population'):
            self.population = deepcopy(kwargs['initial_population'])
        else:
            self.population = self._generate_initial_population()
        
        self.fitness = [self._evaluate(ind) for ind in self.population]
        
        best_idx = min(range(len(self.fitness)), key=lambda i: self.fitness[i])
        self.best_solution = self.population[best_idx].copy()
        self.best_cost = self.fitness[best_idx]
    
    def _generate_initial_population(self):
        population = []
        for _ in range(self.population_size):
            solution = Solution(self.problem_obj)
            # Gera prioridades aleatórias
            for op in self.all_operations:
                priority = random.randint(1, 50)
                solution.set_priority(*op, priority)
            population.append(solution)
        return population
    
    def _evaluate(self, individual):
        scheduler = JobShopScheduler(self.problem_obj.data)
        results = scheduler.simulate_with_user_priority(deepcopy(individual.priorities))
        
        makespan = results['makespan']
        tardiness = results['tardiness']
        
        return self.weight_makespan * makespan + self.weight_tardiness * (tardiness + 1)
    
    def evaluate_solution(self, solution):
        scheduler = JobShopScheduler(self.problem_obj.data)
        return scheduler.simulate_with_user_priority(solution.priorities)
    
    def _tournament_selection(self):
        indices = random.sample(range(len(self.population)), self.tournament_size)
        best_idx = min(indices, key=lambda i: self.fitness[i])
        return deepcopy(self.population[best_idx])
    
    def _crossover(self, parent1, parent2):
        if random.random() > self.crossover_rate:
            return parent1.copy(), parent2.copy()
        
        child1 = Solution(self.problem_obj)
        child2 = Solution(self.problem_obj)
        
        for op in self.all_operations:
            if random.random() < 0.5:
                child1.set_priority(*op, parent1.get_priority(*op))
                child2.set_priority(*op, parent2.get_priority(*op))
            else:
                child1.set_priority(*op, parent2.get_priority(*op))
                child2.set_priority(*op, parent1.get_priority(*op))
        
        return child1, child2
    
    def _mutate(self, individual):
        mutated = deepcopy(individual)
        
        for op in self.all_operations:
            if random.random() < self.mutation_rate:
                current = mutated.get_priority(*op)
                delta = random.randint(-40, 40)
                new_value = current + delta
                new_value = max(1, min(50, new_value))
                mutated.set_priority(*op, new_value)
                
        return mutated
    
    def step(self):
        new_population = []
        new_fitness = []
        
        # Elitismo
        elite_indices = sorted(range(len(self.fitness)), key=lambda i: self.fitness[i])[:self.elite_size]
        for idx in elite_indices:
            new_population.append(self.population[idx].copy())
            new_fitness.append(self.fitness[idx])
        
        # Gera resto da população
        while len(new_population) < self.population_size:
            parent1 = self._tournament_selection()
            parent2 = self._tournament_selection()
            
            child1, child2 = self._crossover(parent1, parent2)
            
            child1 = self._mutate(child1)
            child2 = self._mutate(child2)
            
            fitness1 = self._evaluate(child1)
            fitness2 = self._evaluate(child2)
            
            new_population.extend([child1, child2])
            new_fitness.extend([fitness1, fitness2])
        
        self.population = new_population[:self.population_size]
        self.fitness = new_fitness[:self.population_size]
        
        best_idx = min(range(len(self.fitness)), key=lambda i: self.fitness[i])
        
        return self.population[best_idx], self.fitness[best_idx]