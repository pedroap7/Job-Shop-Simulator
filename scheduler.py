import heapq
from copy import deepcopy
from datetime import datetime
import itertools

class JobShopScheduler:
    def __init__(self, instance):
        self.instance = instance
        self.jobs = instance['jobs']
        self.machines = instance['machines']
        self.reset()
    
    def reset(self):
        """Reseta o estado do scheduler"""
        self.current_time = 0
        self.machine_available_time = {m: 0 for m in self.machines}
        self.machine_queue = {m: [] for m in self.machines}
        self.job_status = {job: {
            'current_op': 1,
            'completed': False,
            'completion_time': 0,
            'operations': [],
            'last_completion': 0,
            'next_op_ready_time': 0
        } for job in self.jobs}
        self.schedule = {job: [] for job in self.jobs}
        self.event_queue = []  # Fila de eventos (ordem cronológica)
        self.operation_queue = {m: [] for m in self.machines}  # Fila de operações por máquina
        self.processed_ops = set()  # Conjunto de operações já processadas
        self.event_counter = 0  # Contador para desempate de eventos
        
    def initialize_first_operations(self):
        """Inicializa as primeiras operações de cada job"""
        print("\n--- INICIALIZANDO PRIMEIRAS OPERAÇÕES ---")
        for job_name, job_data in self.jobs.items():
            first_op = job_data['operations'][0]
            operation = {
                'job': job_name,
                'op_num': 1,
                'machine': first_op['machine'],
                'time': first_op['time'],
                'ready_time': 0,
                'arrival_time': 0
            }
            self.operation_queue[first_op['machine']].append(operation)
            print(f"  Job {job_name} - Op 1 adicionada à fila da Máquina {first_op['machine']} (tempo 0)")
    
    def get_next_operation_for_machine(self, machine):
        """
        Retorna a próxima operação para uma máquina específica
        Aplica critérios de desempate:
        1 - FIFO (menor arrival_time)
        2 - SPT (menor tempo de processamento)
        3 - Ordem alfabética
        """
        # Filtra operações prontas para esta máquina
        ready_ops = [op for op in self.operation_queue[machine] 
                    if op['ready_time'] <= self.current_time]
        
        if not ready_ops:
            return None
        
        # Critério 1: FIFO (menor arrival_time)
        ready_ops.sort(key=lambda x: (x['arrival_time'], x['job']))
        
        # Pega o menor arrival_time
        min_arrival = ready_ops[0]['arrival_time']
        arrival_tied = [op for op in ready_ops if op['arrival_time'] == min_arrival]
        
        if len(arrival_tied) == 1:
            return arrival_tied[0]
        
        # Critério 2: SPT (menor tempo de processamento)
        arrival_tied.sort(key=lambda x: (x['time'], x['job']))
        min_time = arrival_tied[0]['time']
        time_tied = [op for op in arrival_tied if op['time'] == min_time]
        
        if len(time_tied) == 1:
            return time_tied[0]
        
        # Critério 3: Ordem alfabética
        time_tied.sort(key=lambda x: x['job'])
        return time_tied[0]
    
    def add_operation_to_queue(self, job_name, op_num, ready_time):
        """
        Adiciona uma operação específica à fila da sua máquina
        """
        job_data = self.jobs[job_name]
        op_data = job_data['operations'][op_num - 1]
        
        operation = {
            'job': job_name,
            'op_num': op_num,
            'machine': op_data['machine'],
            'time': op_data['time'],
            'ready_time': ready_time,
            'arrival_time': ready_time  # Arrival time = ready time (quando fica disponível)
        }
        
        machine = op_data['machine']
        self.operation_queue[machine].append(operation)
        
        print(f"  📥 Job {job_name} - Operação {op_num} entrou na fila da Máquina {machine} "
              f"às {ready_time:.1f} (disponível imediatamente)")
        
        # Agenda verificação da máquina para o momento em que a operação fica pronta
        self.schedule_event(ready_time, 'check_machine', machine=machine)
    
    def schedule_event(self, event_time, event_type, **kwargs):
        """
        Agenda um evento na fila de eventos
        Usa um contador para garantir ordenação única quando há empate de tempo
        """
        event = {
            'time': event_time,
            'counter': self.event_counter,
            'type': event_type,
            **kwargs
        }
        self.event_counter += 1
        # heapq usa o primeiro elemento da tupla para ordenação
        heapq.heappush(self.event_queue, (event_time, self.event_counter, event))
    
    def process_operation(self, operation):
        """Processa uma operação em uma máquina"""
        job = operation['job']
        op_num = operation['op_num']
        machine = operation['machine']
        proc_time = operation['time']
        
        # A operação só pode começar quando a máquina estiver livre
        start_time = max(self.current_time, self.machine_available_time[machine])
        end_time = start_time + proc_time
        
        # Atualiza disponibilidade da máquina
        self.machine_available_time[machine] = end_time
        
        # Registra operação no schedule
        op_record = {
            'job': job,
            'op_num': op_num,
            'machine': machine,
            'start_time': start_time,
            'end_time': end_time,
            'proc_time': proc_time
        }
        
        self.schedule[job].append(op_record)
        self.processed_ops.add((job, op_num))
        
        print(f"  ▶️ Job {job} - Op {op_num} INICIOU na Máq {machine}: {start_time:.1f}")
        
        # Atualiza status do job
        self.job_status[job]['operations'].append(op_record)
        self.job_status[job]['last_completion'] = end_time
        
        # Atualiza current_op do job
        if op_num == self.job_status[job]['current_op']:
            self.job_status[job]['current_op'] += 1
        
        # Agenda evento de fim de processamento
        self.schedule_event(end_time, 'operation_complete', 
                           machine=machine, job=job, op_num=op_num)
        
        return end_time
    
    def on_operation_complete(self, job, op_num, machine, completion_time):
        """Callback quando uma operação é concluída"""
        print(f"  ✅ Job {job} - Operação {op_num} CONCLUÍDA na Máq {machine} às {completion_time:.1f}")
        
        # Verifica se é a última operação
        if op_num == len(self.jobs[job]['operations']):
            self.job_status[job]['completed'] = True
            self.job_status[job]['completion_time'] = completion_time
            print(f"  🏁 Job {job} COMPLETADO em {completion_time:.1f}")
        else:
            # Adiciona próxima operação do job à fila (disponível imediatamente)
            next_op_num = op_num + 1
            self.add_operation_to_queue(job, next_op_num, completion_time)
    
    def check_machine(self, machine):
        """Verifica se há operações para processar em uma máquina no momento atual"""
        # Enquanto houver operações prontas e a máquina estiver livre, processa
        while True:
            next_op = self.get_next_operation_for_machine(machine)
            
            if not next_op:
                break
                
            # Verifica se a máquina está livre
            if self.current_time >= self.machine_available_time[machine]:
                # Remove da fila e processa
                self.operation_queue[machine].remove(next_op)
                self.process_operation(next_op)
            else:
                # Máquina ocupada, agenda para quando ficar livre
                next_free = self.machine_available_time[machine]
                self.schedule_event(next_free, 'check_machine', machine=machine)
                break
    
    def simulate(self, tie_breaker='fifo'):
        """
        Executa simulação com eventos discretos
        O parâmetro tie_breaker é mantido para compatibilidade, mas não é mais usado
        pois os critérios são fixos: FIFO -> SPT -> Alfabética
        """
        self.reset()
        print("\n" + "="*70)
        print("🎯 INICIANDO SIMULAÇÃO JOB SHOP")
        print("="*70)
        print("Critérios de desempate (nesta ordem):")
        print("1. FIFO - Primeira operação a chegar na fila")
        print("2. SPT - Menor tempo de processamento")
        print("3. Ordem Alfabética do job")
        print("="*70)
        
        # Inicializa primeiras operações
        self.initialize_first_operations()
        
        # Agenda verificação inicial de todas as máquinas
        for machine in self.machines:
            if self.operation_queue[machine]:
                self.schedule_event(0, 'check_machine', machine=machine)
        
        step = 1
        
        while self.event_queue:
            # Pega próximo evento (o de menor tempo)
            event_time, counter, event = heapq.heappop(self.event_queue)
            self.current_time = event_time
            
            print(f"\n⏰ Passo {step} [Tempo {self.current_time:.1f}]")
            
            if event['type'] == 'check_machine':
                machine = event['machine']
                print(f"  🔍 Verificando Máquina {machine}...")
                self.check_machine(machine)
                
            elif event['type'] == 'operation_complete':
                job = event['job']
                op_num = event['op_num']
                machine = event['machine']
                self.on_operation_complete(job, op_num, machine, event_time)
                
                # Após completar uma operação, verifica se a máquina pode processar outra
                self.check_machine(machine)
            
            step += 1
            
            # Verifica se todos completaram
            all_completed = all(j['completed'] for j in self.job_status.values())
            if all_completed:
                break
        
        print("\n" + "="*70)
        print("🎉 SIMULAÇÃO CONCLUÍDA! 🎉")
        print("="*70)
        
        return self.get_results()
    
    def simulate_with_user_priority(self, priority_dict):
        """
        Executa simulação com prioridades definidas pelo usuário
        """
        self.reset()
        print("\n" + "="*70)
        print("🎯 SIMULAÇÃO COM PRIORIDADES DO USUÁRIO")
        print("="*70)
        
        # Inicializa primeiras operações
        self.initialize_first_operations()
        
        # Agenda verificação inicial
        for machine in self.machines:
            if self.operation_queue[machine]:
                self.schedule_event(0, 'check_machine', machine=machine)
        
        step = 1
        
        while self.event_queue:
            event_time, counter, event = heapq.heappop(self.event_queue)
            self.current_time = event_time
            
            print(f"\n⏰ Passo {step} [Tempo {self.current_time:.1f}]")
            
            if event['type'] == 'check_machine':
                machine = event['machine']
                print(f"  🔍 Verificando Máquina {machine}...")
                
                # Filtra operações prontas
                ready_ops = [op for op in self.operation_queue[machine] 
                            if op['ready_time'] <= self.current_time]
                
                if ready_ops and self.current_time >= self.machine_available_time[machine]:
                    # Ordena por prioridade do usuário
                    ready_ops.sort(key=lambda x: priority_dict.get(
                        (x['job'], x['op_num']), float('inf')))
                    
                    next_op = ready_ops[0]
                    self.operation_queue[machine].remove(next_op)
                    self.process_operation(next_op)
                    
            elif event['type'] == 'operation_complete':
                job = event['job']
                op_num = event['op_num']
                machine = event['machine']
                self.on_operation_complete(job, op_num, machine, event_time)
                
                # Verifica se a máquina pode processar outra
                self.check_machine(machine)
            
            step += 1
            
            all_completed = all(j['completed'] for j in self.job_status.values())
            if all_completed:
                break
        
        return self.get_results()
    
    def get_results(self):
        """Calcula métricas da simulação"""
        completion_times = []
        tardiness = 0
        
        print("\n📊 RESULTADOS FINAIS:")
        print("-" * 40)
        
        for job_name, job_data in self.jobs.items():
            comp_time = self.job_status[job_name]['completion_time']
            due_date = job_data['due_date']
            completion_times.append(comp_time)
            
            if comp_time > due_date:
                atraso = comp_time - due_date
                tardiness += atraso
                print(f"  {job_name}: {comp_time:.1f} (due: {due_date}) 🔴 Atraso: {atraso:.1f}")
            else:
                print(f"  {job_name}: {comp_time:.1f} (due: {due_date}) ✅ No prazo")
        
        makespan = max(completion_times)
        
        print("-" * 40)
        print(f"  Makespan: {makespan:.1f}")
        print(f"  Atraso Total: {tardiness:.1f}")
        
        return {
            'makespan': makespan,
            'tardiness': tardiness,
            'schedule': self.schedule,
            'job_completion_times': {job: self.job_status[job]['completion_time'] 
                                    for job in self.jobs}
        }