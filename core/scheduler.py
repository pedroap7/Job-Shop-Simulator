import heapq
from copy import deepcopy

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
        self.job_status = {job: {
            'current_op': 1,
            'completed': False,
            'completion_time': 0,
            'operations': [],
            'last_completion': 0
        } for job in self.jobs}
        self.schedule = {job: [] for job in self.jobs}
        self.event_queue = []
        self.operation_queue = {m: [] for m in self.machines}
        self.processed_ops = set()
        self.event_counter = 0
        
    def initialize_first_operations(self):
        """Inicializa as primeiras operações de cada job"""
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
    
    def get_next_operation_for_machine(self, machine):
        """
        Retorna a próxima operação para uma máquina específica
        Aplica critérios de desempate: FIFO -> SPT -> Alfabética
        """
        ready_ops = [op for op in self.operation_queue[machine] 
                    if op['ready_time'] <= self.current_time]
        
        if not ready_ops:
            return None
        
        # FIFO
        ready_ops.sort(key=lambda x: (x['arrival_time'], x['job']))
        min_arrival = ready_ops[0]['arrival_time']
        arrival_tied = [op for op in ready_ops if op['arrival_time'] == min_arrival]
        
        if len(arrival_tied) == 1:
            return arrival_tied[0]
        
        # SPT
        arrival_tied.sort(key=lambda x: (x['time'], x['job']))
        min_time = arrival_tied[0]['time']
        time_tied = [op for op in arrival_tied if op['time'] == min_time]
        
        if len(time_tied) == 1:
            return time_tied[0]
        
        # Alfabética
        time_tied.sort(key=lambda x: x['job'])
        return time_tied[0]
    
    def add_operation_to_queue(self, job_name, op_num, ready_time):
        """Adiciona uma operação à fila da sua máquina"""
        job_data = self.jobs[job_name]
        op_data = job_data['operations'][op_num - 1]
        
        operation = {
            'job': job_name,
            'op_num': op_num,
            'machine': op_data['machine'],
            'time': op_data['time'],
            'ready_time': ready_time,
            'arrival_time': ready_time
        }
        
        machine = op_data['machine']
        self.operation_queue[machine].append(operation)
        
        self.schedule_event(ready_time, 'check_machine', machine=machine)
    
    def schedule_event(self, event_time, event_type, **kwargs):
        """Agenda um evento na fila de eventos"""
        event = {
            'time': event_time,
            'counter': self.event_counter,
            'type': event_type,
            **kwargs
        }
        self.event_counter += 1
        heapq.heappush(self.event_queue, (event_time, self.event_counter, event))
    
    def process_operation(self, operation):
        """Processa uma operação em uma máquina"""
        job = operation['job']
        op_num = operation['op_num']
        machine = operation['machine']
        proc_time = operation['time']
        
        start_time = max(self.current_time, self.machine_available_time[machine])
        end_time = start_time + proc_time
        
        self.machine_available_time[machine] = end_time
        
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
        
        self.job_status[job]['operations'].append(op_record)
        self.job_status[job]['last_completion'] = end_time
        
        if op_num == self.job_status[job]['current_op']:
            self.job_status[job]['current_op'] += 1
        
        self.schedule_event(end_time, 'operation_complete', 
                           machine=machine, job=job, op_num=op_num)
        
        return end_time
    
    def on_operation_complete(self, job, op_num, machine, completion_time):
        """Callback quando uma operação é concluída"""
        if op_num == len(self.jobs[job]['operations']):
            self.job_status[job]['completed'] = True
            self.job_status[job]['completion_time'] = completion_time
        else:
            next_op_num = op_num + 1
            self.add_operation_to_queue(job, next_op_num, completion_time)
    
    def check_machine(self, machine):
        """Verifica se há operações para processar em uma máquina"""
        while True:
            next_op = self.get_next_operation_for_machine(machine)
            
            if not next_op:
                break
                
            if self.current_time >= self.machine_available_time[machine]:
                self.operation_queue[machine].remove(next_op)
                self.process_operation(next_op)
            else:
                next_free = self.machine_available_time[machine]
                self.schedule_event(next_free, 'check_machine', machine=machine)
                break
    
    def simulate(self):
        """
        Executa simulação com eventos discretos
        Critérios fixos: FIFO -> SPT -> Alfabética
        """
        self.reset()
        
        # Inicializa primeiras operações
        self.initialize_first_operations()
        
        # Agenda verificação inicial
        for machine in self.machines:
            if self.operation_queue[machine]:
                self.schedule_event(0, 'check_machine', machine=machine)
        
        while self.event_queue:
            event_time, counter, event = heapq.heappop(self.event_queue)
            self.current_time = event_time
            
            if event['type'] == 'check_machine':
                machine = event['machine']
                self.check_machine(machine)
                
            elif event['type'] == 'operation_complete':
                job = event['job']
                op_num = event['op_num']
                machine = event['machine']
                self.on_operation_complete(job, op_num, machine, event_time)
                self.check_machine(machine)
            
            # Verifica se todos completaram
            all_completed = all(j['completed'] for j in self.job_status.values())
            if all_completed:
                break
        
        return self.get_results()
    
    def simulate_with_user_priority(self, priority_dict):
        """
        Executa simulação com prioridades definidas pelo usuário
        """
        self.reset()
        
        # Inicializa primeiras operações
        self.initialize_first_operations()
        
        # Agenda verificação inicial
        for machine in self.machines:
            if self.operation_queue[machine]:
                self.schedule_event(0, 'check_machine', machine=machine)
        
        while self.event_queue:
            event_time, counter, event = heapq.heappop(self.event_queue)
            self.current_time = event_time
            
            if event['type'] == 'check_machine':
                machine = event['machine']
                
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
                self.check_machine(machine)
            
            all_completed = all(j['completed'] for j in self.job_status.values())
            if all_completed:
                break
        
        return self.get_results()
    
    def get_results(self):
        """Calcula métricas da simulação"""
        completion_times = []
        tardiness = 0
        
        for job_name, job_data in self.jobs.items():
            comp_time = self.job_status[job_name]['completion_time']
            due_date = job_data['due_date']
            completion_times.append(comp_time)
            
            if comp_time > due_date:
                tardiness += comp_time - due_date
        
        makespan = max(completion_times)
        
        # Organiza schedule
        for job in self.schedule:
            self.schedule[job].sort(key=lambda x: x['start_time'])
        
        return {
            'makespan': makespan,
            'tardiness': tardiness,
            'schedule': self.schedule,
            'job_completion_times': {job: self.job_status[job]['completion_time'] 
                                    for job in self.jobs}
        }