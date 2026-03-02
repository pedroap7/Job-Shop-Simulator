# Job Shop Simulator 🛠️

> Simulador de eventos discretos para o clássico problema de *Job Shop*.

> Este projeto oferece uma plataforma para modelar, simular e otimizar sequenciamento de operações em máquinas distintas, considerando restrições típicas do problema **Job Shop Scheduling**. Além da simulação, o sistema incorpora metaheurísticas para buscar soluções de alta qualidade.

---

## 🌟 Principais Características

- **Simulação de eventos discretos**: cenário controlado onde cada evento (início/fim de operações) altera o estado do sistema.
- **Estrutura modular**: código organizado em pacotes `core`, `metaheuristics`, `gui` e outros.
- **Metaheurísticas implementadas**:
  - Algoritmo Genético
  - Simulated Annealing
  - Possibilidade de extensão para outras técnicas
- **Visualização**: interfaces gráficas para análise de resultados, gráficos de evolução, cronogramas (Gantt) e comparações.
- **Flexibilidade de instâncias**: os dados de instâncias podem ser definidos em JSON (`data/instance.json`), permitindo testes variados.

---

## 📁 Estrutura do Repositório

```
main.py
USAGE.md
utils.py
core/             # Lógica principal de modelagem e solução
metaheuristics/   # Implementações de algoritmos de otimização
gui/              # Componentes de interface gráfica
data/             # Arquivos de instância e configurações
reports/          # (vazio) espaço para relatórios gerados
```

---

## 🚀 Como usar

1. **Preparar a instância**
   - Edite `data/instance.json` conforme o formato esperado.
2. **Executar o simulador**
   ```bash
   python main.py
   ```
3. **Selecionar metaheurística**
   - As opções encontradas em `metaheuristics/`.
   - Ajuste parâmetros diretamente nos módulos ou via interface gráfica.
4. **Visualizar resultados**
   - Use a interface gráfica para ver gráficos de evolução, cronogramas e comparar soluções.

---

### 🖥️ Linguagens
<img align="center" alt="Python" src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
