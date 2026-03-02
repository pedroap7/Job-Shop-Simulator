import json
from copy import deepcopy

class Solution:
    """
    Representação de uma solução do problema Job Shop
    """
    
    def __init__(self, problem, priorities=None):
        """
        Inicializa uma solução
        
        Args:
            problem: Instância do problema
            priorities: Dicionário de prioridades {(job, op_num): prioridade}
        """
        self.problem = problem
        
        if priorities:
            self.priorities = deepcopy(priorities)
        else:
            # Solução inicial: todas prioridades 25
            self.priorities = {}
            for job_name in problem.jobs:
                for op_num in range(1, len(problem.jobs[job_name]['operations']) + 1):
                    self.priorities[(job_name, op_num)] = 25
    
    def get_priority(self, job_name, op_num):
        """Retorna prioridade de uma operação"""
        return self.priorities.get((job_name, op_num), 25)
    
    def set_priority(self, job_name, op_num, priority):
        """Define prioridade de uma operação"""
        self.priorities[(job_name, op_num)] = max(1, min(50, priority))
    
    def mutate(self, operation=None, delta=None):
        """
        Aplica mutação na solução
        
        Args:
            operation: Operação específica (se None, escolhe aleatória)
            delta: Variação na prioridade (se None, escolhe aleatório)
        """
        import random
        
        if operation is None:
            operations = self.problem.get_all_operations()
            operation = random.choice(operations)
        
        if delta is None:
            delta = random.choice([-1, 1])
        
        current = self.get_priority(*operation)
        new_value = current + delta
        new_value = max(1, min(50, new_value))
        
        self.set_priority(*operation, new_value)
        
        return operation, delta
    
    def copy(self):
        """Cria cópia da solução"""
        return Solution(self.problem, deepcopy(self.priorities))
    
    def to_dict(self):
        """Converte para dicionário serializável"""
        return {f"{k[0]}_{k[1]}": v for k, v in self.priorities.items()}
    
    @classmethod
    def from_dict(cls, problem, data):
        """Cria solução a partir de dicionário"""
        priorities = {}
        for key, value in data.items():
            if '_' in key:
                job, op = key.rsplit('_', 1)
                priorities[(job, int(op))] = value
        return cls(problem, priorities)
    
    def get_stats(self):
        """Retorna estatísticas da solução"""
        values = list(self.priorities.values())
        return {
            'min': min(values),
            'max': max(values),
            'mean': sum(values) / len(values),
            'high_priority': sum(1 for v in values if v <= 10),
            'low_priority': sum(1 for v in values if v >= 40)
        }