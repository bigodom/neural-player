# ========================
# CONFIGURAÇÕES DO JOGO
# ========================

# Configurações do Algoritmo Genético
POP_SIZE = 30
N_GENERATIONS = 20
MUTATION_RATE = 0.2
SAVE_FILE = "melhores_pesos.json"
N_PROCESSES = 7  # Número de processos para paralelização

# Configurações do Tetris
LARGURA, ALTURA = 10, 20
TAMANHO_BLOCO = 30
VELOCIDADE_IA = 20  # FPS para visualização da IA
VELOCIDADE_HUMANO = 10  # FPS para jogo humano

# Peças do Tetris (representadas por números)
PECAS = [
    [[1, 1, 1, 1]],  # I
    [[2, 0, 0], [2, 2, 2]],  # J
    [[0, 0, 3], [3, 3, 3]],  # L
    [[4, 4], [4, 4]],        # O
    [[0, 5, 5], [5, 5, 0]],  # S
    [[0, 6, 0], [6, 6, 6]],  # T
    [[7, 7, 0], [0, 7, 7]]   # Z
]

# Cores para cada tipo de peça
CORES_PECAS = {
    1: (0, 255, 255),    # I - Cyan
    2: (0, 0, 255),      # J - Azul
    3: (255, 165, 0),    # L - Laranja
    4: (255, 255, 0),    # O - Amarelo
    5: (0, 255, 0),      # S - Verde
    6: (128, 0, 128),    # T - Roxo
    7: (255, 0, 0),      # Z - Vermelho
    0: (50, 50, 50)      # Fundo - Cinza escuro
}

# Configurações de tela
LARGURA_TELA = LARGURA * TAMANHO_BLOCO
ALTURA_TELA = ALTURA * TAMANHO_BLOCO
TAMANHO_FONTE = 20
