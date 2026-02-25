import random
import math
from copy import deepcopy

class SimulatedAnnealing:
    def __init__(self, instance, initial_temp=1000, cooling_rate=0.95, 
                 min_temp=1, max_iterations=1000):
        self.instance = instance
        self.scheduler = None  # Será criado quando necessário
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.min_temp = min_temp
        self.max_iterations = max_iterations
        
        # Lista de todas as operações para referência
        self.all_operations = []
        for job_name, job_data in instance['jobs'].items():
            for op_num in range(1, len(job_data['operations']) + 1):
                self.all_operations.append((job_name, op_num))
        
        self.num_operations = len(self.all_operations)
        
    def create_scheduler(self):
        """Cria uma nova instância do scheduler (para evitar problemas de referência)"""
        from scheduler import JobShopScheduler
        return JobShopScheduler(self.instance)
        
    def generate_initial_solution(self):
        """
        Gera solução inicial com todas as operações com prioridade média (25)
        Prioridade 1 = mais alta, Prioridade 50 = mais baixa
        """
        priority_vector = {}
        for op in self.all_operations:
            priority_vector[op] = 25  # Prioridade média
        return priority_vector
    
    def get_neighbor(self, current_solution):
        """
        Gera solução vizinha escolhendo uma operação aleatória e
        incrementando ou decrementando sua prioridade em 1 unidade
        Respeitando os limites 1-50
        """
        neighbor = deepcopy(current_solution)
        
        # Escolhe uma operação aleatória
        op = random.choice(self.all_operations)
        
        # Escolhe aleatoriamente incrementar ou decrementar
        if random.random() < 0.5:
            # Incrementar (diminuir prioridade - número maior)
            if neighbor[op] < 50:
                neighbor[op] += 1
        else:
            # Decrementar (aumentar prioridade - número menor)
            if neighbor[op] > 1:
                neighbor[op] -= 1
        
        return neighbor
    
    def get_neighbor_multi(self, current_solution, num_changes=2):
        """
        Gera solução vizinha modificando múltiplas operações
        Útil para explorar melhor o espaço de busca
        """
        neighbor = deepcopy(current_solution)
        
        for _ in range(num_changes):
            op = random.choice(self.all_operations)
            
            if random.random() < 0.5:
                if neighbor[op] < 50:
                    neighbor[op] += 1
            else:
                if neighbor[op] > 1:
                    neighbor[op] -= 1
        
        return neighbor
    
    def evaluate_solution(self, solution, weight_makespan=0.5, weight_tardiness=0.5):
        """
        Avalia qualidade da solução simulando com as prioridades definidas
        """
        scheduler = self.create_scheduler()
        results = scheduler.simulate_with_user_priority(solution)
        
        # Normaliza as métricas
        makespan = results['makespan']
        tardiness = results['tardiness']
        
        # Retorna função objetivo ponderada (minimizar)
        # Adiciona um pequeno termo para evitar divisão por zero
        return weight_makespan * makespan + weight_tardiness * (tardiness + 1)
    
    def print_solution_stats(self, solution, label=""):
        """Imprime estatísticas do vetor de prioridades"""
        if label:
            print(f"\n📊 Estatísticas {label}:")
        
        priorities = list(solution.values())
        print(f"  Mín: {min(priorities)}")
        print(f"  Máx: {max(priorities)}")
        print(f"  Média: {sum(priorities)/len(priorities):.2f}")
        
        # Contagem de prioridades extremas
        high_priority = sum(1 for p in priorities if p <= 10)
        low_priority = sum(1 for p in priorities if p >= 40)
        print(f"  Alta prioridade (≤10): {high_priority}")
        print(f"  Baixa prioridade (≥40): {low_priority}")
    
    def run(self, initial_solution=None, verbose=True, weight_makespan=0.5, 
            weight_tardiness=0.5, multi_changes=False):
        """
        Executa o algoritmo Simulated Annealing
        
        Args:
            initial_solution: solução inicial (se None, gera aleatória)
            verbose: se True, mostra progresso
            weight_makespan: peso do makespan na função objetivo
            weight_tardiness: peso do tardiness na função objetivo
            multi_changes: se True, usa vizinhança com múltiplas mudanças
        """
        print("\n" + "="*70)
        print("🔍 INICIANDO SIMULATED ANNEALING")
        print("="*70)
        print(f"Temperatura inicial: {self.initial_temp}")
        print(f"Taxa de resfriamento: {self.cooling_rate}")
        print(f"Temperatura mínima: {self.min_temp}")
        print(f"Iterações máximas: {self.max_iterations}")
        print(f"Operações: {self.num_operations}")
        print(f"Peso Makespan: {weight_makespan}")
        print(f"Peso Tardiness: {weight_tardiness}")
        print("="*70)
        
        if initial_solution is None:
            current_solution = self.generate_initial_solution()
            print("\n🆕 Solução inicial gerada (todas prioridades = 25)")
        else:
            current_solution = deepcopy(initial_solution)
            print("\n📋 Usando solução fornecida como inicial")
        
        # Mostra estatísticas da solução inicial
        self.print_solution_stats(current_solution, "Inicial")
        
        # Avalia solução inicial
        print("\n⏳ Avaliando solução inicial...")
        current_cost = self.evaluate_solution(current_solution, weight_makespan, weight_tardiness)
        best_solution = deepcopy(current_solution)
        best_cost = current_cost
        
        print(f"✅ Custo inicial: {current_cost:.2f}")
        
        temperature = self.initial_temp
        iteration = 0
        iterations_without_improvement = 0
        
        history = []
        best_history = []
        
        while temperature > self.min_temp and iteration < self.max_iterations:
            # Gera solução vizinha
            if multi_changes:
                neighbor = self.get_neighbor_multi(current_solution, num_changes=2)
            else:
                neighbor = self.get_neighbor(current_solution)
            
            # Avalia vizinho
            neighbor_cost = self.evaluate_solution(neighbor, weight_makespan, weight_tardiness)
            
            # Calcula delta
            delta = neighbor_cost - current_cost
            
            # Aceita solução se for melhor ou com probabilidade de Metropolis
            if delta < 0 or random.random() < math.exp(-delta / temperature):
                current_solution = neighbor
                current_cost = neighbor_cost
                
                # Atualiza melhor solução
                if current_cost < best_cost:
                    best_solution = deepcopy(current_solution)
                    best_cost = current_cost
                    iterations_without_improvement = 0
                    if verbose:
                        print(f"  ✨ Nova melhor solução! Custo: {best_cost:.2f}")
                else:
                    iterations_without_improvement += 1
            else:
                iterations_without_improvement += 1
            
            # Resfriamento
            temperature *= self.cooling_rate
            iteration += 1
            
            # Registra histórico
            history.append(current_cost)
            best_history.append(best_cost)
            
            # Adaptive cooling - se não há melhora, acelera resfriamento
            if iterations_without_improvement > 100:
                temperature *= 0.9
                iterations_without_improvement = 0
            
            # Mostra progresso
            if verbose and iteration % 50 == 0:
                print(f"\n📊 Iteração {iteration}:")
                print(f"  Temp: {temperature:.2f}")
                print(f"  Custo atual: {current_cost:.2f}")
                print(f"  Melhor custo: {best_cost:.2f}")
                self.print_solution_stats(current_solution, "Atual")
        
        print("\n" + "="*70)
        print("🏁 SIMULATED ANNEALING CONCLUÍDO!")
        print("="*70)
        print(f"Iterações realizadas: {iteration}")
        print(f"Temperatura final: {temperature:.2f}")
        print(f"Melhor custo encontrado: {best_cost:.2f}")
        
        # Mostra estatísticas da melhor solução
        self.print_solution_stats(best_solution, "Melhor solução")
        
        # Avalia melhor solução para obter resultados detalhados
        print("\n⏳ Avaliando melhor solução...")
        scheduler = self.create_scheduler()
        final_results = scheduler.simulate_with_user_priority(best_solution)
        
        return {
            'solution': best_solution,
            'cost': best_cost,
            'makespan': final_results['makespan'],
            'tardiness': final_results['tardiness'],
            'schedule': final_results['schedule'],
            'job_completion_times': final_results['job_completion_times'],
            'iterations': iteration,
            'history': history,
            'best_history': best_history
        }
    
    def run_adaptive(self, initial_solution=None, verbose=True, time_limit=60):
        """
        Versão adaptativa que ajusta os pesos durante a execução
        """
        print("\n" + "="*70)
        print("🔍 SIMULATED ANNEALING ADAPTATIVO")
        print("="*70)
        
        import time
        start_time = time.time()
        
        if initial_solution is None:
            current_solution = self.generate_initial_solution()
        else:
            current_solution = deepcopy(initial_solution)
        
        # Pesos iniciais
        weight_makespan = 0.5
        weight_tardiness = 0.5
        
        current_cost = self.evaluate_solution(current_solution, weight_makespan, weight_tardiness)
        best_solution = deepcopy(current_solution)
        best_cost = current_cost
        
        temperature = self.initial_temp
        iteration = 0
        
        while time.time() - start_time < time_limit and temperature > self.min_temp:
            # Ajusta pesos dinamicamente baseado no progresso
            if iteration % 100 == 0:
                # Alterna entre focar em makespan e tardiness
                if iteration % 200 == 0:
                    weight_makespan = 0.7
                    weight_tardiness = 0.3
                    print("\n🔄 Focando em makespan...")
                else:
                    weight_makespan = 0.3
                    weight_tardiness = 0.7
                    print("\n🔄 Focando em tardiness...")
            
            neighbor = self.get_neighbor_multi(current_solution, num_changes=2)
            neighbor_cost = self.evaluate_solution(neighbor, weight_makespan, weight_tardiness)
            
            delta = neighbor_cost - current_cost
            
            if delta < 0 or random.random() < math.exp(-delta / temperature):
                current_solution = neighbor
                current_cost = neighbor_cost
                
                if current_cost < best_cost:
                    best_solution = deepcopy(current_solution)
                    best_cost = current_cost
            
            temperature *= self.cooling_rate
            iteration += 1
            
            if verbose and iteration % 50 == 0:
                elapsed = time.time() - start_time
                print(f"\n📊 Iteração {iteration} (tempo: {elapsed:.1f}s):")
                print(f"  Temp: {temperature:.2f}")
                print(f"  Melhor custo: {best_cost:.2f}")
        
        print("\n" + "="*70)
        print("🏁 SA ADAPTATIVO CONCLUÍDO!")
        print("="*70)
        
        scheduler = self.create_scheduler()
        final_results = scheduler.simulate_with_user_priority(best_solution)
        
        return {
            'solution': best_solution,
            'cost': best_cost,
            'makespan': final_results['makespan'],
            'tardiness': final_results['tardiness'],
            'schedule': final_results['schedule'],
            'iterations': iteration
        }