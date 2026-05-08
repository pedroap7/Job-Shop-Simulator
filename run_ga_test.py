from metaheuristics.genetic_algorithm import GeneticAlgorithm
from utils import load_instance
from core.problem import JobShopProblem

inst = load_instance('data/instance.json')
prob = JobShopProblem(instance_data=inst)

ga = GeneticAlgorithm(prob)
ga.initialize(population_size=20, mutation_rate=0.05, adaptive_mutation=True, mutation_rate_min=0.01, mutation_rate_max=0.3)

for i in range(5):
    sol, fitness = ga.step()
    print(f"Step {i}: mutation_rate={ga.mutation_rate:.4f}, best_fitness={fitness:.2f}")
