# Job Shop Simulator - Guia de Uso

## Como Usar o Programa

### 1. Iniciar a Aplicação

Execute o programa com:
```bash
python -m main
```

Ou a partir da raiz do projeto:
```bash
python main.py
```

### 2. Executar um Experimento

1. **Selecione uma Metaheurística:**
   - Simulated Annealing (padrão) ou Algoritmo Genético

2. **Configure os Parâmetros:**
   - Temperatura Inicial (SA): 100-10000 (padrão: 1000)
   - Taxa de Resfriamento (SA): 0.8-0.99 (padrão: 0.95)
   - Ou configurar parâmetros do AG se escolhido

3. **Escolha o Modo de Execução:**
   - Iterações: número fixo de iterações
   - Tempo (s): tempo máximo em segundos

4. **Clique em "Executar"** para iniciar o experimento

### 3. Visualizar Resultados

Após o experimento terminar:

1. **Selecione um experimento** na tabela "Resultados"
   - Clique em uma linha da tabela para selecioná-lo
   - Você verá uma mensagem no console indicando que foi selecionado

2. **Visualize o Gráfico de Gantt:**
   - Clique no botão "Ver Gantt" ou menu "Visualização > Gráfico de Gantt"
   - O gráfico mostrará o cronograma das operações por máquina

3. **Visualize a Evolução:**
   - Clique no botão "Ver Evolução" ou menu "Visualização > Evolução"
   - O gráfico mostrará:
     - Evolução completa do custo
     - Melhoria ao longo das iterações
     - Estatísticas de convergência

### 4. Comparar Experimentos

1. Execute múltiplos experimentos com diferentes parâmetros
2. Menu "Experimentos > Comparar Experimentos"
3. Visualize a comparação em gráficos e tabelas

### 5. Salvar e Carregar Experimentos

- **Salvar:** Menu "Arquivo > Salvar Experimento" após selecionar um
- **Carregar:** Menu "Arquivo > Carregar Experimento"
- **Exportar Relatório:** Menu "Arquivo > Exportar Relatório"

## Troubleshooting

### Os gráficos não aparecem?

**Solução:**
1. Certifique-se de que selecionou um experimento na tabela (verá mensagem no console)
2. Verifique a aba correta (Gantt ou Evolução) no notebook
3. Se houver erro, será mostrada uma mensagem de erro descritiva

### Erro: "Nenhum experimento selecionado"

**Solução:** Clique em uma linha na tabela de resultados antes de tentar visualizar os gráficos

### Experimento levando muito tempo?

**Solução:** 
- Reduza o número de iterações ou limite de tempo
- Ou clique em "Parar" para interromper

## Estrutura do Projeto

```
core/
  ├── problem.py       # Definição do problema Job Shop
  ├── scheduler.py     # Simulador de agendamento
  └── solution.py      # Representação de solução

metaheuristics/
  ├── base.py          # Classe base para metaheurísticas
  ├── simulated_annealing.py
  └── genetic_algorithm.py

gui/
  ├── main_window.py   # Interface principal
  ├── experiment_panel.py
  ├── gantt_viewer.py  # Visualizador de Gantt
  ├── evolution_plot.py # Gráfico de evolução
  └── comparison_view.py

data/
  └── instance.json    # Instância do problema

main.py               # Ponto de entrada
utils.py              # Funções utilitárias
```

## Dicas de Uso

1. **Para melhores resultados:** Aumentar iterações ou tempo de execução
2. **Comparar algoritmos:** Use metaheurísticas diferentes com os mesmos parâmetros
3. **Análise:** Exporte relatório em HTML para análise posterior
4. **Instâncias customizadas:** Edite `data/instance.json` para usar outros problemas

## Contato e Suporte

Para reportar problemas ou sugestões, sinta-se a vontade para me contatar.

pedro.amaral@int.gov.br
---
Última atualização: 02/03/2026
