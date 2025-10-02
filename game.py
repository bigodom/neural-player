import pygame
import random
import numpy as np
import json
import os

# ========================
# CONFIGURAÇÕES
# ========================
POP_SIZE = 30
N_GENERATIONS = 20
MUTATION_RATE = 0.2
SAVE_FILE = "melhores_pesos.json"

# ========================
# ENGINE SIMPLIFICADA DO TETRIS
# ========================
LARGURA, ALTURA = 10, 20
PECAS = [
    [[1, 1, 1, 1]],  # I
    [[2, 0, 0], [2, 2, 2]],  # J
    [[0, 0, 3], [3, 3, 3]],  # L
    [[4, 4], [4, 4]],        # O
    [[0, 5, 5], [5, 5, 0]],  # S
    [[0, 6, 0], [6, 6, 6]],  # T
    [[7, 7, 0], [0, 7, 7]]   # Z
]

class Tetris:
    def __init__(self):
        self.tabuleiro = [[0 for _ in range(LARGURA)] for _ in range(ALTURA)]
        self.peca_atual = self.nova_peca()
        self.x = LARGURA // 2 - len(self.peca_atual[0]) // 2
        self.y = 0
        self.pontos = 0
        self.game_over = False

    def nova_peca(self):
        return random.choice(PECAS)

    def colide(self, px, py, peca):
        for i, linha in enumerate(peca):
            for j, val in enumerate(linha):
                if val:
                    x, y = px+j, py+i
                    if x < 0 or x >= LARGURA or y >= ALTURA:
                        return True
                    if y >= 0 and self.tabuleiro[y][x]:
                        return True
        return False

    def fixa_peca(self):
        for i, linha in enumerate(self.peca_atual):
            for j, val in enumerate(linha):
                if val:
                    y = self.y + i
                    x = self.x + j
                    if 0 <= y < ALTURA and 0 <= x < LARGURA:
                        self.tabuleiro[y][x] = val
        self.remove_linhas()
        self.peca_atual = self.nova_peca()
        self.x = LARGURA // 2 - len(self.peca_atual[0]) // 2
        self.y = 0
        if self.colide(self.x, self.y, self.peca_atual):
            self.game_over = True

    def remove_linhas(self):
        linhas_removidas = 0
        for i in range(ALTURA-1, -1, -1):
            if all(self.tabuleiro[i]):
                del self.tabuleiro[i]
                self.tabuleiro.insert(0, [0 for _ in range(LARGURA)])
                linhas_removidas += 1
        self.pontos += linhas_removidas ** 2

    def passo(self):
        if not self.colide(self.x, self.y+1, self.peca_atual):
            self.y += 1
        else:
            self.fixa_peca()

    # ---------- Funções para IA ----------
    def clonar_tabuleiro(self):
        return [linha[:] for linha in self.tabuleiro]

    def simula_jogada(self, px, rotacoes):
        peca = self.peca_atual
        for _ in range(rotacoes):
            peca = [list(row) for row in zip(*peca[::-1])]

        # Checa se a peça rotacionada cabe na posição
        largura_peca = len(peca[0])
        if px < 0 or px + largura_peca > LARGURA:
            return -999, 99, 99, 99  # penalidade alta

        # simula queda
        y = 0
        while not self.colide(px, y+1, peca):
            y += 1

        # cria cópia e fixa
        tab = self.clonar_tabuleiro()
        for i, linha in enumerate(peca):
            for j, val in enumerate(linha):
                if val and y+i < ALTURA and px+j < LARGURA:
                    tab[y+i][px+j] = val

        # avalia tabuleiro
        return self.heuristica(tab)

    def heuristica(self, tab):
        linhas = sum(1 for linha in tab if all(linha))
        altura = max((y for y, linha in enumerate(tab) if any(linha)), default=0)
        buracos = sum(
            1 for x in range(LARGURA)
            for y in range(ALTURA)
            if tab[y][x] == 0 and any(tab[k][x] for k in range(y))
        )
        uniformidade = sum(abs(sum(tab[y][x] != 0 for y in range(ALTURA)) -
                               sum(tab[y][x+1] != 0 for y in range(ALTURA)))
                           for x in range(LARGURA-1))
        return linhas, altura, buracos, uniformidade

# ========================
# FUNÇÃO DE FITNESS
# ========================
def fitness(individuo):
    jogo = Tetris()
    total_score = 0

    while not jogo.game_over:
        melhor_score = -99999
        melhor_acao = None
        for rot in range(4):
            for x in range(LARGURA):
                if not jogo.colide(x, 0, jogo.peca_atual):
                    linhas, altura, buracos, uniforme = jogo.simula_jogada(x, rot)
                    w1, w2, w3, w4 = individuo
                    score = w1*linhas - w2*buracos - w3*altura + w4*uniforme
                    if score > melhor_score:
                        melhor_score = score
                        melhor_acao = (x, rot)

        # aplica melhor jogada
        if melhor_acao:
            x, rot = melhor_acao
            for _ in range(rot):
                jogo.peca_atual = [list(row) for row in zip(*jogo.peca_atual[::-1])]
            jogo.x = x

        jogo.passo()
        total_score += 1

        if total_score > 500:  # limite p/ evitar rodadas infinitas
            break

    return jogo.pontos

# ========================
# GENETIC ALGORITHM
# ========================
def crossover(pai, mae):
    ponto = random.randint(1, len(pai)-1)
    return np.concatenate([pai[:ponto], mae[ponto:]])

def mutacao(individuo):
    novo = individuo.copy()
    if random.random() < MUTATION_RATE:
        i = random.randint(0, len(novo)-1)
        novo[i] += random.uniform(-1, 1)
    return novo

def salvar_pesos(melhores, pontuacoes):
    # Salva uma lista de dicts com pesos e score
    data = [
        {"pesos": list(m), "score": int(p)}
        for m, p in zip(melhores, pontuacoes)
    ]
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

def carregar_pesos():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            # Suporte retrocompatível: se for lista de listas, converte
            if data and isinstance(data[0], list):
                return [np.array(m) for m in data]
            # Caso novo: lista de dicts
            return [np.array(item["pesos"]) for item in data]
    return None

def carregar_pesos_com_score():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            if data and isinstance(data[0], dict):
                return [(np.array(item["pesos"]), item["score"]) for item in data]
    return None

def replay_visual(pesos):
    jogo = Tetris()
    pygame.init()
    tela = pygame.display.set_mode((LARGURA*30, ALTURA*30))
    clock = pygame.time.Clock()
    fonte = pygame.font.SysFont("Arial", 20)

    while not jogo.game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                jogo.game_over = True

        # --- IA escolhe jogada ---
        melhor_score = -99999
        melhor_acao = None
        for rot in range(4):
            for x in range(LARGURA):
                if not jogo.colide(x, 0, jogo.peca_atual):
                    linhas, altura, buracos, uniforme = jogo.simula_jogada(x, rot)
                    w1, w2, w3, w4 = pesos
                    score = w1*linhas - w2*buracos - w3*altura + w4*uniforme
                    if score > melhor_score:
                        melhor_score = score
                        melhor_acao = (x, rot)

        if melhor_acao:
            x, rot = melhor_acao
            for _ in range(rot):
                jogo.peca_atual = [list(row) for row in zip(*jogo.peca_atual[::-1])]
            jogo.x = x

        jogo.passo()

        # --- desenhar no pygame ---
        tela.fill((0, 0, 0))
        for y in range(ALTURA):
            for x in range(LARGURA):
                if jogo.tabuleiro[y][x]:
                    pygame.draw.rect(tela, (200,200,200), (x*30, y*30, 30, 30))
        for i, linha in enumerate(jogo.peca_atual):
            for j, val in enumerate(linha):
                if val:
                    pygame.draw.rect(tela, (100,200,100), ((jogo.x+j)*30, (jogo.y+i)*30, 30, 30))

        texto = fonte.render(f"Pontos: {jogo.pontos}", True, (255,255,255))
        tela.blit(texto, (10,10))
        pygame.display.update()
        clock.tick(10)  # velocidade da animação

    pygame.quit()

def escolher_peso():
    try:
        with open("melhores_pesos.json", "r") as f:
            historico = json.load(f)
    except FileNotFoundError:
        print("Nenhum peso salvo encontrado!")
        return None

    print("\nPesos salvos disponíveis:")
    for i, individuo in enumerate(historico):
        print(f"[{i}] {individuo}")

    idx = int(input("Digite o número do indivíduo para ver o replay: "))
    return historico[idx] if 0 <= idx < len(historico) else None
# ========================
# TREINO
# ========================
if __name__ == "__main__":
    modo = input("Digite 't' para treinar ou 'r' para replay: ").strip().lower()

    if modo == "t":
        populacao = carregar_pesos()
        if not populacao:
            populacao = [np.random.uniform(-5, 5, 4) for _ in range(POP_SIZE)]

        for ger in range(N_GENERATIONS):
            pontuacoes = [fitness(ind) for ind in populacao]
            melhores_idx = np.argsort(pontuacoes)[-POP_SIZE//2:]
            melhores = [populacao[i] for i in melhores_idx]
            melhores_scores = [pontuacoes[i] for i in melhores_idx]

            print(f"Geração {ger} | Melhor: {max(pontuacoes)}")
            salvar_pesos(melhores, melhores_scores)

            nova_pop = []
            while len(nova_pop) < POP_SIZE:
                pai, mae = random.sample(melhores, 2)
                filho = crossover(pai, mae)
                filho = mutacao(filho)
                nova_pop.append(filho)
            populacao = nova_pop

        melhor = melhores[-1]
        replay_visual(melhor)

    elif modo == "r":
        peso = escolher_peso()
        if peso:
            replay_visual(peso)

