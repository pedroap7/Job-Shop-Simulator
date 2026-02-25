import os
import json
from datetime import datetime
from utils import load_instance, plot_gantt, save_solution, create_reports_dir
from scheduler import JobShopScheduler
from simulated_annealing import SimulatedAnnealing

class JobShopSimulator:
    def __init__(self, instance_file):
        self.instance = load_instance(instance_file)
        self.scheduler = JobShopScheduler(self.instance)
        self.user_decisions = []
        self.best_solution = None
        
    def run_interactive_mode(self):
        """Modo interativo para testar prioridades"""
        print("\n" + "="*50)
        print("SIMULADOR JOB SHOP - MODO INTERATIVO")
        print("="*50)
        print("\nTodas as operações começam com a mesma prioridade.")
        print("Critérios de desempate fixos (aplicados nesta ordem):")
        print("1 - Primeira operação a entrar na fila (FIFO)")
        print("2 - Menor tempo de processamento (SPT)")
        print("3 - Ordem alfabética do job")
        
        while True:
            print("\n" + "-"*50)
            print("OPÇÕES:")
            print("1. Simular com critérios padrão (FIFO -> SPT -> Alfabética)")
            print("2. Definir prioridades manualmente (sobrepõe critérios)")
            print("3. Executar Simulated Annealing")
            print("4. Ver relatório comparativo")
            print("5. Sair")
            
            choice = input("\nEscolha uma opção (1-5): ").strip()
        
            if choice == '1':
                # Agora chama simulate() sem argumentos, ou com argumento padrão
                results = self.scheduler.simulate()  # ou self.scheduler.simulate('fifo')
                self.display_results(results, "PADRÃO")
                self.user_decisions.append(("PADRÃO", results))
                
            elif choice == '2':
                self.manual_priority_mode()
                
            elif choice == '3':
                self.run_simulated_annealing()
                
            elif choice == '4':
                if self.user_decisions:
                    self.display_comparative_report()
                else:
                    print("Nenhuma simulação realizada ainda!")
                    
            elif choice == '5':
                print("\nEncerrando simulador...")
                break
    
    def manual_priority_mode(self):
        """Modo para definir prioridades manualmente"""
        print("\n--- DEFINIÇÃO MANUAL DE PRIORIDADES ---")
        print("Defina a ordem de prioridade para cada operação (menor número = maior prioridade)")
        print("As operações serão executadas na ordem definida, independente do critério de desempate")
        
        priority_order = {}
        
        print("\nLista de todas as operações:")
        operations_list = []
        
        for job_name, job_data in self.instance['jobs'].items():
            for op_num in range(1, len(job_data['operations']) + 1):
                machine = job_data['operations'][op_num-1]['machine']
                time = job_data['operations'][op_num-1]['time']
                operations_list.append((job_name, op_num, machine, time))
                print(f"  {len(operations_list)}. Job {job_name} - Op {op_num} (Máq {machine}, Tempo {time})")
        
        print("\nAtribua prioridades (1 = maior prioridade, 25 = menor prioridade)")
        print("Digite o número da operação e a prioridade desejada")
        print("Exemplo: '1 5' para operação 1 com prioridade 5")
        print("Digite 'fim' para encerrar")
        
        used_priorities = set()
        
        while len(priority_order) < len(operations_list):
            try:
                user_input = input(f"\nAtribuição {len(priority_order)+1}/{len(operations_list)}: ").strip()
                
                if user_input.lower() == 'fim':
                    break
                
                parts = user_input.split()
                if len(parts) != 2:
                    print("Formato inválido! Use: 'número_operacao prioridade'")
                    continue
                
                op_idx = int(parts[0]) - 1
                priority = int(parts[1])
                
                if op_idx < 0 or op_idx >= len(operations_list):
                    print(f"Número de operação inválido! Use 1-{len(operations_list)}")
                    continue
                
                if priority in used_priorities:
                    print(f"Prioridade {priority} já foi usada! Escolha outra.")
                    continue
                
                job_name, op_num, _, _ = operations_list[op_idx]
                priority_order[(job_name, op_num)] = priority
                used_priorities.add(priority)
                
                print(f"  OK: Job {job_name} - Op {op_num} recebeu prioridade {priority}")
                
            except ValueError:
                print("Valores inválidos! Digite números inteiros.")
        
        # Completa operações sem prioridade com valores restantes
        remaining_priorities = set(range(1, len(operations_list) + 1)) - used_priorities
        remaining_ops = [op for op in operations_list if (op[0], op[1]) not in priority_order]
        
        for op, priority in zip(remaining_ops, sorted(remaining_priorities)):
            job_name, op_num, _, _ = op
            priority_order[(job_name, op_num)] = priority
            print(f"  Atribuindo prioridade automática {priority} para Job {job_name} - Op {op_num}")
        
        # Executa simulação com prioridades definidas
        print("\nExecutando simulação com prioridades definidas...")
        results = self.scheduler.simulate_with_user_priority(priority_order)
        self.display_results(results, "MANUAL")
        self.user_decisions.append(("MANUAL", results))
    
    def run_simulated_annealing(self):
        """Executa o algoritmo Simulated Annealing"""
        print("\n--- SIMULATED ANNEALING ---")
        
        sa = SimulatedAnnealing(self.instance)
        
        print("Escolha a solução inicial:")
        print("1. Solução aleatória")
        print("2. Melhor solução encontrada até agora")
        print("3. Solução FIFO")
        print("4. Solução SPT")
        
        choice = input("Opção (1-4): ").strip()
        
        initial_solution = None
        if choice == '2' and self.best_solution:
            initial_solution = self.best_solution
            print("Usando melhor solução como ponto de partida...")
        elif choice == '3':
            # Converte solução FIFO para formato de prioridades
            initial_solution = self.convert_schedule_to_priorities('fifo')
            print("Usando solução FIFO como ponto de partida...")
        elif choice == '4':
            initial_solution = self.convert_schedule_to_priorities('spt')
            print("Usando solução SPT como ponto de partida...")
        else:
            print("Gerando solução inicial aleatória...")
        
        print("\nExecutando Simulated Annealing...")
        results = sa.run(initial_solution)
        
        print(f"\nResultados SA:")
        print(f"Makespan: {results['makespan']:.1f}")
        print(f"Atraso Total: {results['tardiness']:.1f}")
        print(f"Custo: {results['cost']:.2f}")
        print(f"Iterações: {results['iterations']}")
        
        self.best_solution = results['solution']
        
        # Salva solução
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_gantt(results['schedule'], results['makespan'], 
                  results['tardiness'], f"SA_{timestamp}")
        
        save_solution(results, f"SA_solution_{timestamp}")
        self.user_decisions.append(("SA", results))
    
    def convert_schedule_to_priorities(self, rule):
        """Converte uma simulação com regra em ordem de prioridades"""
        results = self.scheduler.simulate(rule)
        priority_order = {}
        
        # Cria prioridades baseado na ordem de execução
        priority = 1
        all_ops = []
        
        # Coleta todas as operações com seus tempos de início
        for job, ops in results['schedule'].items():
            for op in ops:
                all_ops.append({
                    'job': job,
                    'op_num': op['op_num'],
                    'start_time': op['start_time']
                })
        
        # Ordena por tempo de início
        all_ops.sort(key=lambda x: x['start_time'])
        
        # Atribui prioridades
        for op in all_ops:
            priority_order[(op['job'], op['op_num'])] = priority
            priority += 1
        
        return priority_order
    
    def display_results(self, results, rule_name):
        """Exibe resultados da simulação"""
        print(f"\n{'='*60}")
        print(f"RESULTADOS - REGRA: {rule_name}")
        print(f"{'='*60}")
        print(f"Makespan: {results['makespan']:.1f}")
        print(f"Atraso Total: {results['tardiness']:.1f}")
        print(f"\nTempos de conclusão por Job:")
        print("-" * 50)
        
        total_atraso = 0
        for job, time in results['job_completion_times'].items():
            due_date = self.instance['jobs'][job]['due_date']
            atraso = max(0, time - due_date)
            total_atraso += atraso
            status = "✅ OK" if time <= due_date else f"⚠️  Atrasado {atraso:.1f}"
            print(f"  {job}: {time:.1f} (Due: {due_date}) - {status}")
        
        print(f"\nTotal de atraso: {total_atraso:.1f}")
        
        # Gera gráfico de Gantt
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_gantt(results['schedule'], results['makespan'], 
                  results['tardiness'], f"{rule_name}_{timestamp}")
        
        # Salva resultados
        save_solution(results, f"{rule_name}_{timestamp}")
    
    def display_comparative_report(self):
        """Exibe relatório comparativo das simulações"""
        print("\n" + "="*70)
        print("RELATÓRIO COMPARATIVO DAS SIMULAÇÕES")
        print("="*70)
        
        print(f"\n{'Regra':<15} {'Makespan':<15} {'Atraso':<15} {'Jobs OK':<15} {'Eficiência':<15}")
        print("-"*70)
        
        best_makespan = min(self.user_decisions, key=lambda x: x[1]['makespan'])[1]['makespan']
        
        for rule, results in self.user_decisions:
            jobs_ok = sum(1 for job, time in results['job_completion_times'].items() 
                         if time <= self.instance['jobs'][job]['due_date'])
            
            # Calcula eficiência relativa ao melhor makespan
            eficiencia = (best_makespan / results['makespan']) * 100
            
            print(f"{rule:<15} {results['makespan']:<15.1f} "
                  f"{results['tardiness']:<15.1f} {jobs_ok}/5 {eficiencia:<14.1f}%")
        
        # Melhores resultados
        if self.user_decisions:
            best_makespan_result = min(self.user_decisions, key=lambda x: x[1]['makespan'])
            best_tardiness_result = min(self.user_decisions, key=lambda x: x[1]['tardiness'])
            best_jobs_result = max(self.user_decisions, key=lambda x: 
                                 sum(1 for job, time in x[1]['job_completion_times'].items() 
                                   if time <= self.instance['jobs'][job]['due_date']))
            
            print("\n" + "="*70)
            print("MELHORES RESULTADOS:")
            print(f"🏆 Menor Makespan: {best_makespan_result[0]} - {best_makespan_result[1]['makespan']:.1f}")
            print(f"🏆 Menor Atraso: {best_tardiness_result[0]} - {best_tardiness_result[1]['tardiness']:.1f}")
            print(f"🏆 Mais Jobs no Prazo: {best_jobs_result[0]} - ", end="")
            
            jobs_ok = sum(1 for job, time in best_jobs_result[1]['job_completion_times'].items() 
                         if time <= self.instance['jobs'][job]['due_date'])
            print(f"{jobs_ok}/5 jobs OK")

import os
import json
from datetime import datetime
from utils import load_instance, plot_gantt, save_solution, create_reports_dir
from scheduler import JobShopScheduler
from simulated_annealing import SimulatedAnnealing

class JobShopSimulator:
    def __init__(self, instance_file):
        self.instance = load_instance(instance_file)
        self.scheduler = JobShopScheduler(self.instance)
        self.user_decisions = []
        self.best_solution = None
        
    def run_interactive_mode(self):
        """Modo interativo para testar prioridades"""
        print("\n" + "="*60)
        print("🏭 SIMULADOR JOB SHOP - MODO INTERATIVO")
        print("="*60)
        print("\n📋 Configuração do problema:")
        print(f"  • {len(self.instance['jobs'])} jobs")
        print(f"  • {len(self.instance['machines'])} máquinas")
        print(f"  • {sum(len(job['operations']) for job in self.instance['jobs'].values())} operações")
        print("\n⚖️ Critérios de desempate fixos (aplicados nesta ordem):")
        print("  1️⃣ Primeira operação a entrar na fila (FIFO)")
        print("  2️⃣ Menor tempo de processamento (SPT)")
        print("  3️⃣ Ordem alfabética do job")
        
        while True:
            print("\n" + "─"*60)
            print("📌 MENU PRINCIPAL")
            print("─"*60)
            print("1️⃣  Simular com critérios padrão")
            print("2️⃣  Definir prioridades manualmente")
            print("3️⃣  Executar Simulated Annealing")
            print("4️⃣  Ver relatório comparativo")
            print("5️⃣  Salvar última simulação")
            print("6️⃣  Sair")
            
            choice = input("\n👉 Escolha uma opção (1-6): ").strip()
            
            if choice == '1':
                self.run_standard_simulation()
                
            elif choice == '2':
                self.manual_priority_mode()
                
            elif choice == '3':
                self.run_simulated_annealing()
                
            elif choice == '4':
                if self.user_decisions:
                    self.display_comparative_report()
                else:
                    print("❌ Nenhuma simulação realizada ainda!")
                    
            elif choice == '5':
                if self.user_decisions:
                    self.save_last_simulation()
                else:
                    print("❌ Nenhuma simulação para salvar!")
                    
            elif choice == '6':
                print("\n👋 Encerrando simulador...")
                break
    
    def run_standard_simulation(self):
        """Executa simulação com critérios padrão"""
        print("\n" + "─"*60)
        print("📊 SIMULAÇÃO COM CRITÉRIOS PADRÃO")
        print("─"*60)
        
        results = self.scheduler.simulate()
        self.display_results(results, "PADRÃO")
        self.user_decisions.append(("PADRÃO", results))
        
        # Pergunta se quer salvar
        save = input("\n💾 Salvar esta simulação? (s/N): ").strip().lower()
        if save == 's':
            self.save_simulation(results, "PADRAO")
    
    def manual_priority_mode(self):
        """Modo para definir prioridades manualmente"""
        print("\n" + "─"*60)
        print("✏️  DEFINIÇÃO MANUAL DE PRIORIDADES")
        print("─"*60)
        print("\n📝 Instruções:")
        print("• Cada operação começa com prioridade 25 (valor médio)")
        print("• Prioridade 1 = MAIS ALTA, Prioridade 50 = MAIS BAIXA")
        print("• Valores menores = maior prioridade na fila")
        print("• Digite 'fim' para encerrar a qualquer momento")
        
        priority_order = {}
        
        print("\n📋 Lista de todas as operações:")
        operations_list = []
        
        for job_name, job_data in self.instance['jobs'].items():
            for op_num in range(1, len(job_data['operations']) + 1):
                machine = job_data['operations'][op_num-1]['machine']
                time = job_data['operations'][op_num-1]['time']
                operations_list.append((job_name, op_num, machine, time))
                print(f"  {len(operations_list):2d}. Job {job_name} - Op {op_num} "
                      f"(Máq {machine}, Tempo {time:2d}) [prioridade atual: 25]")
        
        print("\n🎯 Atribua prioridades (1-50) para cada operação:")
        print("   Pressione Enter para manter prioridade 25")
        
        for i, (job_name, op_num, machine, time) in enumerate(operations_list, 1):
            while True:
                user_input = input(f"  Prioridade para Job {job_name} Op {op_num} (1-50) [25]: ").strip()
                
                if user_input.lower() == 'fim':
                    break
                
                if user_input == "":
                    priority = 25
                    break
                
                try:
                    priority = int(user_input)
                    if 1 <= priority <= 50:
                        break
                    else:
                        print("     ❌ Prioridade deve estar entre 1 e 50!")
                except ValueError:
                    print("     ❌ Digite um número válido!")
            
            if user_input.lower() == 'fim':
                break
                
            priority_order[(job_name, op_num)] = priority
            print(f"     ✅ Prioridade {priority} definida")
        
        # Completa operações não definidas com prioridade 25
        for job_name, op_num, _, _ in operations_list:
            if (job_name, op_num) not in priority_order:
                priority_order[(job_name, op_num)] = 25
        
        # Executa simulação com prioridades definidas
        print("\n⏳ Executando simulação com prioridades definidas...")
        results = self.scheduler.simulate_with_user_priority(priority_order)
        self.display_results(results, "MANUAL")
        self.user_decisions.append(("MANUAL", results))
        
        # Pergunta se quer salvar
        save = input("\n💾 Salvar esta simulação? (s/N): ").strip().lower()
        if save == 's':
            # Salva também as prioridades definidas
            results['priorities'] = {f"{k[0]}_{k[1]}": v for k, v in priority_order.items()}
            self.save_simulation(results, "MANUAL")
    
    def run_simulated_annealing(self):
        """Executa o algoritmo Simulated Annealing"""
        print("\n" + "="*70)
        print("🔍 SIMULATED ANNEALING - OTIMIZAÇÃO DE PRIORIDADES")
        print("="*70)
        print("\n📊 O SA trabalhará com um vetor de prioridades onde:")
        print("  • Cada operação tem prioridade de 1 (MAIS ALTA) a 50 (MAIS BAIXA)")
        print("  • Solução inicial: todas operações com prioridade 25")
        print("  • Vizinhança: incrementa ou decrementa prioridade de uma operação")
        
        # Pergunta se quer usar solução inicial personalizada
        print("\n🎯 Opções de solução inicial:")
        print("  1. Usar solução inicial (todas prioridades = 25)")
        print("  2. Usar melhor solução encontrada (se houver)")
        print("  3. Carregar solução de arquivo")
        
        choice = input("\n👉 Escolha (1-3): ").strip()
        
        initial_solution = None
        if choice == '2' and hasattr(self, 'best_solution') and self.best_solution:
            initial_solution = self.best_solution
            print("✅ Usando melhor solução encontrada anteriormente")
        elif choice == '3':
            self.load_solution_from_file()
        
        # Pergunta parâmetros do SA
        print("\n⚙️ Configuração do SA:")
        print("   (Pressione Enter para usar valores padrão)")
        
        temp_input = input("  Temperatura inicial (padrão 1000): ").strip()
        temp = float(temp_input) if temp_input else 1000
        
        cooling_input = input("  Taxa de resfriamento (padrão 0.95): ").strip()
        cooling = float(cooling_input) if cooling_input else 0.95
        
        max_iter_input = input("  Máximo de iterações (padrão 1000): ").strip()
        max_iter = int(max_iter_input) if max_iter_input else 1000
        
        # Pergunta pesos
        print("\n⚖️ Pesos na função objetivo (soma deve ser 1.0):")
        w_makespan_input = input("  Peso para makespan (padrão 0.5): ").strip()
        w_makespan = float(w_makespan_input) if w_makespan_input else 0.5
        w_tardiness = 1.0 - w_makespan
        print(f"  Peso para tardiness: {w_tardiness:.2f}")
        
        # Pergunta tipo de vizinhança
        print("\n🔄 Tipo de vizinhança:")
        print("  1. Simples (muda 1 operação por vez)")
        print("  2. Múltipla (muda 2 operações por vez)")
        viz_type = input("  Escolha (1-2) [1]: ").strip() or "1"
        multi_changes = (viz_type == '2')
        
        # Pergunta modo adaptativo
        print("\n🔄 Modo de execução:")
        print("  1. Padrão (número fixo de iterações)")
        print("  2. Adaptativo (baseado em tempo)")
        mode = input("  Escolha (1-2) [1]: ").strip() or "1"
        
        # Cria instância do SA
        sa = SimulatedAnnealing(
            self.instance, 
            initial_temp=temp, 
            cooling_rate=cooling, 
            max_iterations=max_iter
        )
        
        # Executa
        if mode == '2':
            time_limit_input = input("  Limite de tempo (segundos) [60]: ").strip()
            time_limit = float(time_limit_input) if time_limit_input else 60
            results = sa.run_adaptive(
                initial_solution=initial_solution,
                time_limit=time_limit,
                verbose=True
            )
        else:
            results = sa.run(
                initial_solution=initial_solution,
                weight_makespan=w_makespan,
                weight_tardiness=w_tardiness,
                multi_changes=multi_changes,
                verbose=True
            )
        
        # Mostra resultados
        print("\n" + "="*70)
        print("📊 RESULTADOS DO SIMULATED ANNEALING")
        print("="*70)
        print(f"  Makespan: {results['makespan']:.1f}")
        print(f"  Atraso Total: {results['tardiness']:.1f}")
        print(f"  Custo: {results['cost']:.2f}")
        print(f"  Iterações: {results['iterations']}")
        
        # Mostra tempos de conclusão
        print("\n📅 Tempos de conclusão por Job:")
        for job, time in results['job_completion_times'].items():
            due_date = self.instance['jobs'][job]['due_date']
            status = "✅" if time <= due_date else "🔴"
            atraso = max(0, time - due_date)
            print(f"  {job}: {time:.1f} (due: {due_date}) {status} Atraso: {atraso:.1f}")
        
        # Pergunta se quer salvar
        save = input("\n💾 Salvar esta solução? (s/N): ").strip().lower()
        if save == 's':
            self.save_sa_solution(results, temp, cooling, max_iter, w_makespan, w_tardiness)
        
        # Atualiza melhor solução
        self.best_solution = results['solution']
        self.user_decisions.append(("SA", results))
    
    def load_solution_from_file(self):
        """Carrega solução de um arquivo"""
        import os
        
        # Lista arquivos de solução disponíveis
        if not os.path.exists('reports'):
            print("❌ Diretório 'reports' não encontrado!")
            return None
            
        solution_files = [f for f in os.listdir('reports') 
                         if f.endswith('_solution.json') or f.endswith('_SA.json')]
        
        if not solution_files:
            print("❌ Nenhum arquivo de solução encontrado!")
            return None
        
        print("\n📁 Arquivos disponíveis:")
        for i, f in enumerate(solution_files, 1):
            # Tenta mostrar informações do arquivo
            try:
                with open(f'reports/{f}', 'r') as file:
                    data = json.load(file)
                    if 'makespan' in data:
                        print(f"  {i:2d}. {f} (makespan: {data['makespan']:.1f})")
                    else:
                        print(f"  {i:2d}. {f}")
            except:
                print(f"  {i:2d}. {f}")
        
        file_choice = input("\n👉 Escolha o número do arquivo: ").strip()
        try:
            idx = int(file_choice) - 1
            if 0 <= idx < len(solution_files):
                with open(f'reports/{solution_files[idx]}', 'r') as f:
                    data = json.load(f)
                    
                # Converte de volta para formato de prioridades
                if 'solution' in data:
                    initial_solution = {}
                    for k, v in data['solution'].items():
                        if '_' in k:
                            job, op = k.rsplit('_', 1)
                            initial_solution[(job, int(op))] = v
                    print("✅ Solução carregada com sucesso!")
                    return initial_solution
                else:
                    print("❌ Arquivo não contém uma solução válida!")
            else:
                print("❌ Número inválido!")
        except Exception as e:
            print(f"❌ Erro ao carregar arquivo: {e}")
        
        return None
    
    def save_sa_solution(self, results, temp, cooling, max_iter, w_makespan, w_tardiness):
        """Salva solução do SA em arquivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Converte chaves tuplas para string para JSON
        solution_to_save = {f"{k[0]}_{k[1]}": v for k, v in results['solution'].items()}
        
        save_data = {
            'solution': solution_to_save,
            'makespan': results['makespan'],
            'tardiness': results['tardiness'],
            'cost': results['cost'],
            'iterations': results['iterations'],
            'job_completion_times': results['job_completion_times'],
            'params': {
                'temp': temp,
                'cooling': cooling,
                'max_iter': max_iter,
                'w_makespan': w_makespan,
                'w_tardiness': w_tardiness
            },
            'timestamp': timestamp
        }
        
        filename = f"SA_solution_{timestamp}"
        with open(f'reports/{filename}.json', 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2)
        print(f"✅ Solução salva em reports/{filename}.json")
        
        # Gera gráfico
        plot_gantt(
            results['schedule'], 
            results['makespan'], 
            results['tardiness'], 
            filename
        )
    
    def save_simulation(self, results, rule_name):
        """Salva resultados da simulação"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{rule_name}_{timestamp}"
        
        # Prepara dados para salvar
        save_data = {
            'rule': rule_name,
            'makespan': results['makespan'],
            'tardiness': results['tardiness'],
            'job_completion_times': results['job_completion_times'],
            'timestamp': timestamp
        }
        
        # Se houver prioridades manuais, salva também
        if 'priorities' in results:
            save_data['priorities'] = results['priorities']
        
        # Salva em JSON
        with open(f'reports/{filename}.json', 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2)
        print(f"✅ Simulação salva em reports/{filename}.json")
        
        # Gera gráfico
        plot_gantt(
            results['schedule'], 
            results['makespan'], 
            results['tardiness'], 
            filename
        )
    
    def save_last_simulation(self):
        """Salva a última simulação realizada"""
        if not self.user_decisions:
            print("❌ Nenhuma simulação para salvar!")
            return
        
        last_rule, last_results = self.user_decisions[-1]
        self.save_simulation(last_results, last_rule)
    
    def display_results(self, results, rule_name):
        """Exibe resultados da simulação"""
        print(f"\n{'='*70}")
        print(f"📊 RESULTADOS - REGRA: {rule_name}")
        print(f"{'='*70}")
        print(f"  Makespan: {results['makespan']:.1f}")
        print(f"  Atraso Total: {results['tardiness']:.1f}")
        
        print(f"\n📅 Tempos de conclusão por Job:")
        print("-" * 50)
        
        total_atraso = 0
        jobs_no_prazo = 0
        
        for job, time in results['job_completion_times'].items():
            due_date = self.instance['jobs'][job]['due_date']
            atraso = max(0, time - due_date)
            total_atraso += atraso
            if time <= due_date:
                jobs_no_prazo += 1
                status = "✅ NO PRAZO"
            else:
                status = f"🔴 ATRASADO {atraso:.1f}"
            
            print(f"  {job}: {time:6.1f}  |  Due: {due_date:6.1f}  |  {status}")
        
        print("-" * 50)
        print(f"  Total de jobs no prazo: {jobs_no_prazo}/5")
        print(f"  Atraso acumulado: {total_atraso:.1f}")
        
        # Gera gráfico de Gantt automaticamente
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_gantt(
            results['schedule'], 
            results['makespan'], 
            results['tardiness'], 
            f"{rule_name}_{timestamp}"
        )
    
    def display_comparative_report(self):
        """Exibe relatório comparativo das simulações"""
        print("\n" + "="*80)
        print("📊 RELATÓRIO COMPARATIVO DAS SIMULAÇÕES")
        print("="*80)
        
        print(f"\n{'Regra':<15} {'Makespan':<15} {'Atraso':<15} {'Jobs OK':<10} {'Eficiência':<12}")
        print("-"*80)
        
        if not self.user_decisions:
            print("Nenhuma simulação realizada ainda!")
            return
        
        best_makespan = min(d[1]['makespan'] for d in self.user_decisions)
        best_tardiness = min(d[1]['tardiness'] for d in self.user_decisions)
        
        for rule, results in self.user_decisions:
            jobs_ok = sum(1 for job, time in results['job_completion_times'].items() 
                         if time <= self.instance['jobs'][job]['due_date'])
            
            # Calcula eficiência relativa ao melhor makespan
            eficiencia = (best_makespan / results['makespan']) * 100
            
            # Destaca melhores resultados
            makespan_str = f"{results['makespan']:.1f}"
            tardiness_str = f"{results['tardiness']:.1f}"
            
            if results['makespan'] == best_makespan:
                makespan_str += " 🏆"
            if results['tardiness'] == best_tardiness:
                tardiness_str += " 🏆"
            
            print(f"{rule:<15} {makespan_str:<15} {tardiness_str:<15} {jobs_ok}/5 {eficiencia:<11.1f}%")
        
        # Análise detalhada
        print("\n" + "="*80)
        print("📈 ANÁLISE DETALHADA")
        print("="*80)
        
        # Melhor para makespan
        best_makespan_result = min(self.user_decisions, key=lambda x: x[1]['makespan'])
        print(f"\n🏆 Menor Makespan: {best_makespan_result[0]}")
        print(f"   Makespan: {best_makespan_result[1]['makespan']:.1f}")
        print(f"   Atraso: {best_makespan_result[1]['tardiness']:.1f}")
        
        # Melhor para tardiness
        best_tardiness_result = min(self.user_decisions, key=lambda x: x[1]['tardiness'])
        print(f"\n🏆 Menor Atraso: {best_tardiness_result[0]}")
        print(f"   Makespan: {best_tardiness_result[1]['makespan']:.1f}")
        print(f"   Atraso: {best_tardiness_result[1]['tardiness']:.1f}")
        
        # Mais jobs no prazo
        best_jobs_result = max(self.user_decisions, 
                              key=lambda x: sum(1 for job, time in x[1]['job_completion_times'].items() 
                                              if time <= self.instance['jobs'][job]['due_date']))
        jobs_ok = sum(1 for job, time in best_jobs_result[1]['job_completion_times'].items() 
                     if time <= self.instance['jobs'][job]['due_date'])
        print(f"\n🏆 Mais Jobs no Prazo: {best_jobs_result[0]}")
        print(f"   Jobs OK: {jobs_ok}/5")
        print(f"   Makespan: {best_jobs_result[1]['makespan']:.1f}")
        print(f"   Atraso: {best_jobs_result[1]['tardiness']:.1f}")
        
        # Recomendação
        print("\n" + "="*80)
        print("💡 RECOMENDAÇÃO")
        print("="*80)
        
        # Calcula score composto (normalizado)
        best_composite = None
        best_composite_score = float('inf')
        
        for rule, results in self.user_decisions:
            norm_makespan = results['makespan'] / best_makespan
            norm_tardiness = (results['tardiness'] + 1) / (best_tardiness + 1)
            composite = norm_makespan * 0.4 + norm_tardiness * 0.6  # Peso maior para atraso
            
            if composite < best_composite_score:
                best_composite_score = composite
                best_composite = rule
        
        print(f"Baseado na análise, a melhor estratégia é: {best_composite}")
        print("Esta recomendação considera um equilíbrio entre makespan e atraso,")
        print("com peso ligeiramente maior para minimizar atrasos.")


def main():
    """Função principal"""
    # Cria diretório de relatórios
    create_reports_dir()
    
    # Verifica se arquivo de instância existe
    instance_file = 'data/instance.json'
    if not os.path.exists(instance_file):
        print("📁 Arquivo de instância não encontrado!")
        print("🔄 Criando arquivo data/instance.json com dados padrão...")
        os.makedirs('data', exist_ok=True)
        
        # Cria instância padrão com due dates
        default_instance = {
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
        
        with open(instance_file, 'w', encoding='utf-8') as f:
            json.dump(default_instance, f, indent=2)
        print("✅ Arquivo criado com sucesso!")
    
    # Mostra banner de boas-vindas
    print("\n" + "★"*60)
    print("🌟 BEM-VINDO AO SIMULADOR JOB SHOP 🌟")
    print("★"*60)
    print("\nEste simulador permite otimizar o sequenciamento")
    print("de 5 jobs em 5 máquinas, cada um com 5 operações.")
    print("\nObjetivos:")
    print("  • Minimizar o makespan (tempo total de produção)")
    print("  • Minimizar atrasos em relação às datas de entrega")
    print("\nEstratégias disponíveis:")
    print("  • Simulação com regras de prioridade fixas")
    print("  • Definição manual de prioridades")
    print("  • Otimização via Simulated Annealing")
    
    # Inicia simulador
    simulator = JobShopSimulator(instance_file)
    simulator.run_interactive_mode()
    
    print("\n" + "★"*60)
    print("👋 OBRIGADO POR USAR O SIMULADOR!")
    print("★"*60)


if __name__ == "__main__":
    main()