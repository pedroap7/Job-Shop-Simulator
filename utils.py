import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime
import os

def load_instance(filepath):
    """Carrega a instância do problema do arquivo JSON"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_solution(solution, filename):
    """Salva uma solução em arquivo JSON"""
    with open(f'reports/{filename}.json', 'w', encoding='utf-8') as f:
        json.dump(solution, f, indent=2)

def plot_gantt(schedule, makespan, tardiness, filename=None):
    """Plota gráfico de Gantt da solução"""
    fig, ax = plt.subplots(figsize=(15, 8))
    
    # Cores para diferentes jobs
    colors = ["#F01111", "#2D20BD", '#45B7D1', "#ADD010", "#ECB80D"]
    
    # Para cada job
    for job_idx, job_ops in schedule.items():
        job_num = int(job_idx.replace('Job', '')) - 1
        for op in job_ops:
            start = op['start_time']
            end = op['end_time']
            machine = op['machine']
            
            ax.barh(y=f'Máquina {machine}', 
                   width=end-start, 
                   left=start, 
                   height=0.5,
                   color=colors[job_num % len(colors)],
                   edgecolor='black',
                   label=f'Job {job_num+1}' if op['op_num'] == 1 else "")
            
            # Adicionar texto da operação
            ax.text(start + (end-start)/2, f'Máquina {machine}', 
                   f'J{job_num+1}.O{op["op_num"]}',
                   ha='center', va='center', fontsize=8)
    
    ax.set_xlabel('Tempo')
    ax.set_ylabel('Máquinas')
    ax.set_title(f'Diagrama de Gantt - Makespan: {makespan:.1f}, Atraso Total: {tardiness:.1f}')
    
    # Legenda
    handles = [mpatches.Patch(color=colors[i], label=f'Job {i+1}') for i in range(5)]
    ax.legend(handles=handles, loc='upper right')
    
    ax.grid(True, alpha=0.3)
    
    if filename:
        plt.savefig(f'reports/{filename}.png', dpi=100, bbox_inches='tight')
    plt.show()

def create_reports_dir():
    """Cria diretório de relatórios se não existir"""
    if not os.path.exists('reports'):
        os.makedirs('reports')