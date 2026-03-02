import json

class JobShopProblem:
    """
    Representação do problema Job Shop
    """
    
    def __init__(self, instance_file=None, instance_data=None):
        """
        Inicializa o problema
        
        Args:
            instance_file: Caminho para arquivo JSON com a instância
            instance_data: Dicionário com os dados da instância
        """
        if instance_file:
            with open(instance_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        elif instance_data:
            self.data = instance_data
        else:
            # Instância padrão
            self.data = self._create_default_instance()
        
        self.jobs = self.data['jobs']
        self.machines = self.data['machines']
        self.num_jobs = len(self.jobs)
        self.num_machines = len(self.machines)
        self.num_operations = sum(len(job['operations']) for job in self.jobs.values())
        
    def _create_default_instance(self):
        """Cria instância padrão"""
        return {
            "jobs": {
                "Job1": {"due_date": 100, "operations": [
                    {"machine": 1, "time": 8}, {"machine": 3, "time": 12},
                    {"machine": 2, "time": 10}, {"machine": 4, "time": 7},
                    {"machine": 5, "time": 9}
                ]},
                "Job2": {"due_date": 120, "operations": [
                    {"machine": 1, "time": 6}, {"machine": 2, "time": 14},
                    {"machine": 4, "time": 9}, {"machine": 5, "time": 11},
                    {"machine": 3, "time": 8}
                ]},
                "Job3": {"due_date": 90, "operations": [
                    {"machine": 1, "time": 10}, {"machine": 4, "time": 8},
                    {"machine": 5, "time": 12}, {"machine": 3, "time": 9},
                    {"machine": 2, "time": 7}
                ]},
                "Job4": {"due_date": 110, "operations": [
                    {"machine": 1, "time": 7}, {"machine": 5, "time": 13},
                    {"machine": 3, "time": 8}, {"machine": 2, "time": 10},
                    {"machine": 4, "time": 12}
                ]},
                "Job5": {"due_date": 130, "operations": [
                    {"machine": 1, "time": 9}, {"machine": 3, "time": 11},
                    {"machine": 4, "time": 10}, {"machine": 5, "time": 8},
                    {"machine": 2, "time": 13}
                ]}
            },
            "machines": [1, 2, 3, 4, 5]
        }
    
    def get_all_operations(self):
        """Retorna lista de todas as operações (job, op_num)"""
        operations = []
        for job_name in self.jobs:
            for op_num in range(1, len(self.jobs[job_name]['operations']) + 1):
                operations.append((job_name, op_num))
        return operations
    
    def get_operation_info(self, job_name, op_num):
        """Retorna informações de uma operação específica"""
        return self.jobs[job_name]['operations'][op_num - 1]
    
    def get_due_date(self, job_name):
        """Retorna data de entrega de um job"""
        return self.jobs[job_name]['due_date']
    
    def get_machine_for_operation(self, job_name, op_num):
        """Retorna a máquina de uma operação"""
        return self.jobs[job_name]['operations'][op_num - 1]['machine']
    
    def get_processing_time(self, job_name, op_num):
        """Retorna o tempo de processamento de uma operação"""
        return self.jobs[job_name]['operations'][op_num - 1]['time']
    
    def to_dict(self):
        """Retorna representação em dicionário"""
        return self.data