# 🎮 Tetris IA - Sistema de Treinamento com Algoritmo Genético

Este projeto implementa um sistema completo para treinar uma IA que joga Tetris usando Algoritmo Genético, além de permitir que você jogue manualmente.

## 📁 Estrutura do Projeto

```
├── main.py                 # Arquivo principal com menu de opções
├── config.py              # Configurações do jogo e algoritmo
├── tetris.py              # Classe principal do jogo Tetris
├── genetic_algorithm.py   # Algoritmo genético para treinar IA
├── visual.py              # Interface gráfica com Pygame
├── melhores_pesos.json    # Arquivo com pesos treinados (gerado automaticamente)
└── README.md              # Este arquivo
```

## 🚀 Como Executar

1. **Instale as dependências:**
   ```bash
   pip install pygame numpy tqdm
   ```

2. **Execute o programa principal:**
   ```bash
   python main.py
   ```

## 🎯 Funcionalidades

### 1. 🧠 Treinar IA
- Treina uma IA usando Algoritmo Genético
- Suporte a processamento paralelo para acelerar o treinamento
- Salva automaticamente os melhores pesos de cada geração
- Estatísticas detalhadas durante o treinamento

### 2. 👀 Ver IA Jogar
- Assiste a IA jogar com os pesos treinados
- Escolhe qual geração assistir
- Visualização em tempo real com Pygame

### 3. 🎮 Jogar Você Mesmo
- Interface gráfica completa para jogar Tetris
- Controles intuitivos:
  - **← →** : Mover peça
  - **↑** : Rotacionar peça
  - **↓** : Acelerar queda
  - **ESPAÇO** : Drop rápido
  - **P ou PAUSE** : Pausar/Despausar
  - **ESC** : Sair do jogo
- Sistema de níveis e pontuação
- **Funcionalidade de pause** com tela sobreposta

### 4. 📊 Ver Estatísticas
- Histórico completo de treinamento
- Melhores e piores scores por geração
- Análise de evolução dos pesos

## ⚙️ Configurações

Edite o arquivo `config.py` para personalizar:

- **POP_SIZE**: Tamanho da população (padrão: 30)
- **N_GENERATIONS**: Número de gerações (padrão: 20)
- **MUTATION_RATE**: Taxa de mutação (padrão: 0.2)
- **N_PROCESSES**: Número de processos paralelos
- **LARGURA/ALTURA**: Dimensões do tabuleiro (padrão: 10x20)

## 🧬 Como Funciona a IA

A IA usa 4 pesos para tomar decisões:

1. **w1**: Recompensa por linhas completas
2. **w2**: Penalidade por buracos
3. **w3**: Penalidade por altura
4. **w4**: Recompensa por uniformidade

Para cada peça, a IA:
1. Testa todas as posições e rotações possíveis
2. Simula o resultado de cada jogada
3. Calcula um score usando os pesos
4. Escolhe a jogada com maior score

## 🎨 Interface Visual

- **Cores distintas** para cada tipo de peça
- **Informações em tempo real** (pontos, linhas, nível)
- **Controles visuais** para jogo humano
- **Tela de game over** com estatísticas finais

## 📈 Melhorando a IA

Para melhorar a performance da IA:

1. **Aumente o número de gerações** no `config.py`
2. **Ajuste a taxa de mutação** (0.1-0.3 funciona bem)
3. **Use mais processos paralelos** se tiver CPU potente
4. **Treine por mais tempo** - IA melhora com mais gerações

## 🔧 Solução de Problemas

### Erro de dependências
```bash
pip install --upgrade pygame numpy tqdm
```

### Performance lenta
- Reduza `POP_SIZE` para testes rápidos
- Use menos processos paralelos
- Diminua `N_GENERATIONS`

### IA não melhora
- Aumente `MUTATION_RATE`
- Treine por mais gerações
- Verifique se os pesos iniciais estão bons

## 🎯 Próximos Passos

- [ ] Implementar Deep Learning (Redes Neurais)
- [ ] Adicionar mais heurísticas
- [ ] Sistema de ranking online
- [ ] Modo multiplayer IA vs Humano
- [ ] Interface web

## 📝 Licença

Este projeto é open source. Use e modifique livremente!

---

**Divirta-se jogando e treinando IA! 🎮🤖**
