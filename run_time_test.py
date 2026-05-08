from metaheuristics.simulated_annealing import SimulatedAnnealing
from utils import load_instance

inst = load_instance('data/instance.json')
from core.problem import JobShopProblem
prob = JobShopProblem(instance_data=inst)

sa = SimulatedAnnealing(prob)
res = sa.run(max_iterations=10000)
print('execution_time:', res.get('execution_time'))
print('sa.execution_time:', sa.execution_time)
print('iterations:', res.get('iterations'))
