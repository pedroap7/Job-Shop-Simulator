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
        # cache for evaluated permutations: key -> fitness
        self.eval_cache = {}
        
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
            ,
            'random_injection': {
                'type': 'int',
                'default': 0,
                'min': 0,
                'max': 100,
                'description': 'Número de indivíduos aleatórios a inserir por geração'
            }
            ,
            'memetic': {
                'type': 'bool',
                'default': False,
                'description': 'Ativa busca local (memetic) sobre filhos'
            },
            'memetic_tries': {
                'type': 'int',
                'default': 10,
                'min': 1,
                'max': 200,
                'description': 'Número de tentativas na busca local por filho'
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
        # random injection per generation
        self.random_injection = kwargs.get('random_injection', 0)
        # memetic parameters
        self.memetic = kwargs.get('memetic', False)
        self.memetic_tries = kwargs.get('memetic_tries', 10)
        
        self.params = {
            'population_size': self.population_size,
            'mutation_rate': self.mutation_rate,
            'crossover_rate': self.crossover_rate,
            'elite_size': self.elite_size,
            'tournament_size': self.tournament_size,
            'weight_makespan': self.weight_makespan,
            'weight_tardiness': self.weight_tardiness
            , 'random_injection': self.random_injection
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
            # Gera permutação única de 1..n (representação por posição)
            perm = list(range(1, self.num_operations + 1))
            random.shuffle(perm)
            solution = Solution(self.problem_obj)
            for idx, op in enumerate(self.all_operations):
                solution.set_priority(*op, perm[idx])
            population.append(solution)
        return population
    
    def _evaluate(self, individual):
        # use cache keyed by ordered priorities tuple
        key = tuple(individual.get_priority(*op) for op in self.all_operations)
        if key in self.eval_cache:
            return self.eval_cache[key]

        scheduler = JobShopScheduler(self.problem_obj.data)
        results = scheduler.simulate_with_user_priority(deepcopy(individual.priorities))

        makespan = results['makespan']
        tardiness = results['tardiness']

        val = self.weight_makespan * makespan + self.weight_tardiness * (tardiness + 1)
        self.eval_cache[key] = val
        return val

    def _local_search(self, individual, tries=10):
        """Simple swap-based hill-climbing: try random swaps and keep improvement."""
        best = individual
        best_cost = self._evaluate(best)
        n = self.num_operations
        for _ in range(tries):
            i, j = random.randrange(n), random.randrange(n)
            if i == j:
                continue
            a_op = self.all_operations[i]
            b_op = self.all_operations[j]
            new = best.copy()
            pa = new.get_priority(*a_op)
            pb = new.get_priority(*b_op)
            new.set_priority(*a_op, pb)
            new.set_priority(*b_op, pa)
            cost = self._evaluate(new)
            if cost < best_cost:
                best, best_cost = new, cost
        return best
    
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
        # Converte pais para permutações (listas de prioridades)
        p1 = [parent1.get_priority(*op) for op in self.all_operations]
        p2 = [parent2.get_priority(*op) for op in self.all_operations]

        # Aplicar PMX (Partially Mapped Crossover) para preservar permutação
        def pmx(a, b):
            n = len(a)
            c = [-1] * n
            i, j = sorted(random.sample(range(n), 2))
            # copia segmento
            for k in range(i, j + 1):
                c[k] = a[k]

            # mapeia os valores do outro pai
            for k in range(i, j + 1):
                if b[k] not in c:
                    val = b[k]
                    pos = k
                    while True:
                        mapped = a[pos]
                        try:
                            pos = b.index(mapped)
                        except ValueError:
                            break
                        if c[pos] == -1:
                            break
                    c[pos] = val

            # preenche restantes com valores de b
            bi = 0
            for idx in range(n):
                if c[idx] == -1:
                    while b[bi] in c:
                        bi += 1
                    c[idx] = b[bi]
            return c

        child_perm1 = pmx(p1, p2)
        child_perm2 = pmx(p2, p1)

        # converte permutações em Solution
        child1 = Solution(self.problem_obj)
        child2 = Solution(self.problem_obj)
        for idx, op in enumerate(self.all_operations):
            child1.set_priority(*op, child_perm1[idx])
            child2.set_priority(*op, child_perm2[idx])

        return child1, child2
    
    def _mutate(self, individual):
        # Mutação por trocas (swap) mantendo permutação 1..n
        mutated = deepcopy(individual)
        n = self.num_operations
        # Para cada posição, com probabilidade mutation_rate troque com outra posição
        for i, op in enumerate(self.all_operations):
            if random.random() < self.mutation_rate:
                j = random.randrange(n)
                # troca prioridades entre posições i e j
                pri_i = mutated.get_priority(*op)
                op_j = self.all_operations[j]
                pri_j = mutated.get_priority(*op_j)
                mutated.set_priority(*op, pri_j)
                mutated.set_priority(*op_j, pri_i)

        return mutated

    def _compute_diversity(self):
        """
        Computa uma medida simples de diversidade da população baseada
        na proporção média de valores únicos de prioridade por operação.
        Retorna valor no intervalo [0,1], onde 0 = nenhuma diversidade, 1 = alta diversidade.
        """
        if not self.population:
            return 0.0

        total_ratio = 0.0
        for op in self.all_operations:
            values = [ind.get_priority(*op) for ind in self.population]
            unique = len(set(values))
            ratio = unique / 50.0
            total_ratio += ratio

        return total_ratio / max(1, len(self.all_operations))
    
    def _generate_random_individuals(self, k):
        inds = []
        fits = []
        for _ in range(k):
            perm = list(range(1, self.num_operations + 1))
            random.shuffle(perm)
            sol = Solution(self.problem_obj)
            for idx, op in enumerate(self.all_operations):
                sol.set_priority(*op, perm[idx])
            f = self._evaluate(sol)
            inds.append(sol)
            fits.append(f)
        return inds, fits
    
    def step(self):
        new_population = []
        new_fitness = []

        # (No adaptive mutation) — optionally inject random individuals below
        
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

            # optional memetic local search
            if getattr(self, 'memetic', False):
                child1 = self._local_search(child1, tries=self.memetic_tries)
                child2 = self._local_search(child2, tries=self.memetic_tries)

            fitness1 = self._evaluate(child1)
            fitness2 = self._evaluate(child2)
            
            new_population.extend([child1, child2])
            new_fitness.extend([fitness1, fitness2])
        
        # Inject random individuals if configured
        if getattr(self, 'random_injection', 0) and self.random_injection > 0:
            inds, fits = self._generate_random_individuals(self.random_injection)
            new_population.extend(inds)
            new_fitness.extend(fits)

        # select best individuals to maintain population size
        idxs_sorted = sorted(range(len(new_fitness)), key=lambda i: new_fitness[i])
        selected = idxs_sorted[:self.population_size]
        self.population = [new_population[i] for i in selected]
        self.fitness = [new_fitness[i] for i in selected]

        best_idx = min(range(len(self.fitness)), key=lambda i: self.fitness[i])
        return self.population[best_idx], self.fitness[best_idx]