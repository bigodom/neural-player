import pygame
import random
import numpy as np
import json
import os
import time
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
from functools import partial

# ========================
# CONFIGURAÇÕES
# ========================
POP_SIZE = 30
N_GENERATIONS = 20
MUTATION_RATE = 0.2
SAVE_FILE = "melhores_pesos.json"
N_PROCESSES = min(cpu_count(), 8)  # Usa até 8 cores ou todos disponíveis

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
def fitness(individuo, pbar=None):
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

        # Atualiza barra de progresso se fornecida
        if pbar:
            pbar.update(1)

    return jogo.pontos

def fitness_wrapper(individuo):
    """Wrapper para a função fitness que funciona com multiprocessing"""
    # Converte de volta para numpy array se for lista
    if isinstance(individuo, list):
        individuo = np.array(individuo)
    return fitness(individuo, pbar=None)

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

def avaliar_populacao_paralela(populacao, geracao):
    """Avalia toda a população em paralelo com barra de progresso e estatísticas"""
    print(f"\n🔄 Avaliando Geração {geracao} em paralelo ({N_PROCESSES} processos)...")
    
    # Converte para lista de listas para serialização
    populacao_serializavel = [individuo.tolist() for individuo in populacao]
    
    # Processa em paralelo
    with Pool(processes=N_PROCESSES) as pool:
        # Barra de progresso para acompanhar o processamento
        with tqdm(total=POP_SIZE, desc=f"Geração {geracao}", unit="indivíduo", 
                  bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]') as pbar:
            
            # Executa fitness em paralelo
            pontuacoes = []
            for score in pool.imap(fitness_wrapper, populacao_serializavel):
                pontuacoes.append(score)
                pbar.update(1)
                pbar.set_postfix({
                    'Melhor': max(pontuacoes),
                    'Média': f"{np.mean(pontuacoes):.1f}",
                    'Atual': score
                })
    
    # Estatísticas finais
    melhor_score = max(pontuacoes)
    pior_score = min(pontuacoes)
    media_score = np.mean(pontuacoes)
    desvio_score = np.std(pontuacoes)
    
    print(f"📊 Estatísticas da Geração {geracao}:")
    print(f"   🏆 Melhor: {melhor_score}")
    print(f"   📉 Pior: {pior_score}")
    print(f"   📈 Média: {media_score:.2f}")
    print(f"   📊 Desvio: {desvio_score:.2f}")
    print(f"   ⚡ Velocidade: {POP_SIZE/pbar.format_dict['elapsed']:.1f} indivíduos/seg")
    
    return pontuacoes, melhor_score, pior_score, media_score

def avaliar_populacao_sequencial(populacao, geracao):
    """Versão sequencial para comparação ou quando paralelo não é possível"""
    print(f"\n🔄 Avaliando Geração {geracao} (sequencial)...")
    
    pontuacoes = []
    
    # Barra de progresso para a população
    with tqdm(total=POP_SIZE, desc=f"Geração {geracao}", unit="indivíduo", 
              bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]') as pbar:
        
        for i, individuo in enumerate(populacao):
            score = fitness(individuo, pbar=None)
            pontuacoes.append(score)
            
            # Atualiza estatísticas na barra principal
            pbar.set_postfix({
                'Melhor': max(pontuacoes),
                'Média': f"{np.mean(pontuacoes):.1f}",
                'Atual': score
            })
            pbar.update(1)
    
    # Estatísticas finais
    melhor_score = max(pontuacoes)
    pior_score = min(pontuacoes)
    media_score = np.mean(pontuacoes)
    desvio_score = np.std(pontuacoes)
    
    print(f"📊 Estatísticas da Geração {geracao}:")
    print(f"   🏆 Melhor: {melhor_score}")
    print(f"   📉 Pior: {pior_score}")
    print(f"   📈 Média: {media_score:.2f}")
    print(f"   📊 Desvio: {desvio_score:.2f}")
    
    return pontuacoes, melhor_score, pior_score, media_score

def salvar_melhor_geracao(melhor_pesos, melhor_score, geracao):
    # Carrega dados existentes ou cria lista vazia
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
        except:
            data = []
    else:
        data = []
    
    # Adiciona o melhor da geração atual
    novo_registro = {
        "geracao": geracao,
        "pesos": list(melhor_pesos),
        "score": int(melhor_score)
    }
    data.append(novo_registro)
    
    # Salva de volta
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

def carregar_pesos():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            # Suporte retrocompatível: se for lista de listas, converte
            if data and isinstance(data[0], list) and not isinstance(data[0], dict):
                return [np.array(m) for m in data]
            # Caso novo: lista de dicts com geração
            if data and isinstance(data[0], dict):
                # Retorna apenas os pesos do melhor de cada geração
                return [np.array(item["pesos"]) for item in data]
    return None

def carregar_historico_completo():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            if data and isinstance(data[0], dict):
                return data
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
    historico = carregar_historico_completo()
    if not historico:
        print("Nenhum peso salvo encontrado!")
        return None

    print("\nGerações salvas disponíveis:")
    for item in historico:
        if isinstance(item, dict) and "geracao" in item:
            print(f"Geração {item['geracao']}: Score {item['score']} - Pesos: {item['pesos']}")
        else:
            # Suporte retrocompatível
            print(f"[{historico.index(item)}] {item}")

    if historico and isinstance(historico[0], dict) and "geracao" in historico[0]:
        geracao = int(input("Digite o número da geração para ver o replay: "))
        for item in historico:
            if item["geracao"] == geracao:
                return item["pesos"]
        print("Geração não encontrada!")
        return None
    else:
        # Suporte retrocompatível
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

        print(f"\n🚀 Iniciando treinamento por {N_GENERATIONS} gerações...")
        print(f"📋 População: {POP_SIZE} indivíduos")
        print(f"🧬 Taxa de mutação: {MUTATION_RATE}")
        print(f"⚡ Processos paralelos: {N_PROCESSES} cores")
        print(f"💻 CPUs detectadas: {cpu_count()}")
        
        # Pergunta se quer usar paralelo ou sequencial
        try:
            usar_paralelo = input("\nUsar processamento paralelo? (s/N): ").strip().lower()
            usar_paralelo = usar_paralelo in ['s', 'sim', 'y', 'yes']
        except:
            usar_paralelo = True  # Default para paralelo
        
        if usar_paralelo and N_PROCESSES > 1:
            print(f"✅ Usando processamento paralelo com {N_PROCESSES} processos")
            avaliar_func = avaliar_populacao_paralela
        else:
            print("🐌 Usando processamento sequencial")
            avaliar_func = avaliar_populacao_sequencial
        
        # Barra de progresso para as gerações
        with tqdm(total=N_GENERATIONS, desc="Evolução", unit="geração", 
                  bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]') as ger_pbar:
            
            for ger in range(N_GENERATIONS):
                # Avalia a população com estatísticas detalhadas
                pontuacoes, melhor_score, pior_score, media_score = avaliar_func(populacao, ger)
                
                melhor_idx = np.argmax(pontuacoes)
                melhor_individuo = populacao[melhor_idx]
                
                melhores_idx = np.argsort(pontuacoes)[-POP_SIZE//2:]
                melhores = [populacao[i] for i in melhores_idx]

                print(f"💾 Salvando melhor da Geração {ger} (Score: {melhor_score})")
                salvar_melhor_geracao(melhor_individuo, melhor_score, ger)

                # Atualiza barra de progresso das gerações
                ger_pbar.set_postfix({
                    'Melhor': melhor_score,
                    'Média': f"{media_score:.1f}",
                    'Pior': pior_score
                })
                ger_pbar.update(1)

                # Cria nova geração
                print(f"🧬 Criando próxima geração...")
                nova_pop = []
                while len(nova_pop) < POP_SIZE:
                    pai, mae = random.sample(melhores, 2)
                    filho = crossover(pai, mae)
                    filho = mutacao(filho)
                    nova_pop.append(filho)
                populacao = nova_pop

        melhor = melhores[-1]
        
        # Resumo final do treinamento
        print(f"\n🎉 Treinamento concluído!")
        print(f"🏆 Melhor score final: {melhor_score}")
        print(f"🧬 Gerações treinadas: {N_GENERATIONS}")
        print(f"📊 Total de indivíduos avaliados: {N_GENERATIONS * POP_SIZE}")
        print(f"🎮 Iniciando replay do melhor indivíduo...")
        
        replay_visual(melhor)

    elif modo == "r":
        peso = escolher_peso()
        if peso:
            replay_visual(peso)

