import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime
import os
import numpy as np

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
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    
    # Para cada job
    for job_idx, (job_name, job_ops) in enumerate(schedule.items()):
        for op in job_ops:
            start = op['start_time']
            end = op['end_time']
            machine = op['machine']
            
            ax.barh(y=f'Máquina {machine}', 
                   width=end-start, 
                   left=start, 
                   height=0.5,
                   color=colors[job_idx % len(colors)],
                   edgecolor='black',
                   label=f'Job {job_idx+1}' if op['op_num'] == 1 else "")
            
            # Adicionar texto da operação
            ax.text(start + (end-start)/2, f'Máquina {machine}', 
                   f'J{job_idx+1}.O{op["op_num"]}',
                   ha='center', va='center', fontsize=8, fontweight='bold')
    
    ax.set_xlabel('Tempo', fontsize=12, fontweight='bold')
    ax.set_ylabel('Máquinas', fontsize=12, fontweight='bold')
    ax.set_title(f'Diagrama de Gantt - Makespan: {makespan:.1f}, Atraso Total: {tardiness:.1f}', 
                fontsize=14, fontweight='bold')
    
    # Legenda
    handles = [mpatches.Patch(color=colors[i], label=f'Job {i+1}') for i in range(5)]
    ax.legend(handles=handles, loc='upper right', fontsize=10)
    
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, makespan * 1.05)  # Margem de 5%
    
    plt.tight_layout()
    
    if filename:
        plt.savefig(f'reports/{filename}.png', dpi=100, bbox_inches='tight')
    plt.show()

def plot_sa_evolution(history, best_history, filename=None):
    """
    Plota a evolução do Simulated Annealing
    history: lista com os custos das soluções atuais ao longo das iterações
    best_history: lista com os melhores custos encontrados até cada iteração
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    iterations = range(1, len(history) + 1)
    
    # Gráfico 1: Evolução completa
    ax1.plot(iterations, history, 'b-', alpha=0.5, linewidth=1, label='Solução Atual')
    ax1.plot(iterations, best_history, 'r-', linewidth=2, label='Melhor Solução')
    ax1.set_xlabel('Iteração', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Custo', fontsize=12, fontweight='bold')
    ax1.set_title('Evolução do Simulated Annealing', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Destacar a melhor solução
    best_iteration = np.argmin(best_history) + 1
    best_value = min(best_history)
    ax1.plot(best_iteration, best_value, 'g*', markersize=15, 
            label=f'Melhor: {best_value:.2f}')
    ax1.legend(fontsize=10)
    
    # Gráfico 2: Convergência (últimas 20% das iterações)
    cutoff = int(len(history) * 0.8)
    if cutoff < len(history):
        ax2.plot(iterations[cutoff:], history[cutoff:], 'b-', alpha=0.5, linewidth=1, label='Solução Atual')
        ax2.plot(iterations[cutoff:], best_history[cutoff:], 'r-', linewidth=2, label='Melhor Solução')
        ax2.set_xlabel('Iteração', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Custo', fontsize=12, fontweight='bold')
        ax2.set_title('Convergência (últimas 20% das iterações)', fontsize=14, fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Estatísticas
    stats_text = f"Estatísticas:\n"
    stats_text += f"• Custo inicial: {history[0]:.2f}\n"
    stats_text += f"• Melhor custo: {best_value:.2f}\n"
    stats_text += f"• Melhoria: {(history[0] - best_value)/history[0]*100:.1f}%\n"
    stats_text += f"• Iteração da melhor: {best_iteration}\n"
    stats_text += f"• Iterações totais: {len(history)}"
    
    ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, 
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    if filename:
        plt.savefig(f'reports/{filename}_evolution.png', dpi=100, bbox_inches='tight')
    
    plt.show()
    
    return fig

def plot_comparative_evolution(sa_results_list, labels=None, filename=None):
    """
    Plota comparação de múltiplas execuções do SA
    sa_results_list: lista de dicionários com 'best_history' de cada execução
    labels: lista de nomes para cada execução
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#C77DFF']
    
    for i, results in enumerate(sa_results_list):
        best_history = results['best_history']
        iterations = range(1, len(best_history) + 1)
        
        label = labels[i] if labels and i < len(labels) else f"Execução {i+1}"
        ax.plot(iterations, best_history, color=colors[i % len(colors)], 
               linewidth=2, label=label)
    
    ax.set_xlabel('Iteração', fontsize=12, fontweight='bold')
    ax.set_ylabel('Melhor Custo', fontsize=12, fontweight='bold')
    ax.set_title('Comparação de Múltiplas Execuções do SA', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if filename:
        plt.savefig(f'reports/{filename}_comparison.png', dpi=100, bbox_inches='tight')
    
    plt.show()
    
    return fig

def create_reports_dir():
    """Cria diretório de relatórios se não existir"""
    if not os.path.exists('reports'):
        os.makedirs('reports')
        print("📁 Diretório 'reports' criado com sucesso!")