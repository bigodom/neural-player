import random
import numpy as np
from config import LARGURA, ALTURA, PECAS


class Tetris:
    def __init__(self):
        self.tabuleiro = [[0 for _ in range(LARGURA)] for _ in range(ALTURA)]
        self.peca_atual = self.nova_peca()
        self.x = LARGURA // 2 - len(self.peca_atual[0]) // 2
        self.y = 0
        self.pontos = 0
        self.game_over = False
        self.linhas_removidas = 0
        self.nivel = 1

    def nova_peca(self):
        """Gera uma nova peça aleatória"""
        return random.choice(PECAS)

    def colide(self, px, py, peca):
        """Verifica se a peça colide com o tabuleiro ou bordas"""
        for i, linha in enumerate(peca):
            for j, val in enumerate(linha):
                if val:
                    x, y = px + j, py + i
                    if x < 0 or x >= LARGURA or y >= ALTURA:
                        return True
                    if y >= 0 and self.tabuleiro[y][x]:
                        return True
        return False

    def fixa_peca(self):
        """Fixa a peça atual no tabuleiro"""
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
        """Remove linhas completas e atualiza pontuação"""
        linhas_removidas = 0
        
        # Primeiro, identifica quais linhas estão completas
        linhas_completas = []
        for i in range(ALTURA):
            if all(self.tabuleiro[i]):
                linhas_completas.append(i)
        
        # Remove as linhas completas (de baixo para cima para não afetar os índices)
        for i in reversed(linhas_completas):
            del self.tabuleiro[i]
            self.tabuleiro.insert(0, [0 for _ in range(LARGURA)])
            linhas_removidas += 1
        
        if linhas_removidas > 0:
            self.linhas_removidas += linhas_removidas
            # Sistema de pontuação do Tetris original
            # 1 linha = 40 * nível, 2 linhas = 100 * nível, 3 linhas = 300 * nível, 4 linhas (Tetris) = 1200 * nível
            pontos_linha = [0, 40, 100, 300, 1200]  # 0, 1, 2, 3, 4 linhas
            self.pontos += pontos_linha[min(linhas_removidas, 4)] * self.nivel
            self.nivel = (self.linhas_removidas // 10) + 1

    def passo(self):
        """Move a peça uma posição para baixo"""
        if not self.colide(self.x, self.y + 1, self.peca_atual):
            self.y += 1
        else:
            self.fixa_peca()

    def mover_esquerda(self):
        """Move a peça para a esquerda"""
        if not self.colide(self.x - 1, self.y, self.peca_atual):
            self.x -= 1

    def mover_direita(self):
        """Move a peça para a direita"""
        if not self.colide(self.x + 1, self.y, self.peca_atual):
            self.x += 1

    def rotacionar(self):
        """Rotaciona a peça no sentido horário"""
        peca_rotacionada = [list(row) for row in zip(*self.peca_atual[::-1])]
        if not self.colide(self.x, self.y, peca_rotacionada):
            self.peca_atual = peca_rotacionada

    def drop_rapido(self):
        """Deixa a peça cair rapidamente"""
        while not self.colide(self.x, self.y + 1, self.peca_atual):
            self.y += 1
        self.fixa_peca()

    # ---------- Funções para IA ----------
    def clonar_tabuleiro(self):
        """Cria uma cópia do tabuleiro atual"""
        return [linha[:] for linha in self.tabuleiro]

    def simula_jogada(self, px, rotacoes):
        """Simula uma jogada e retorna métricas de avaliação"""
        peca = self.peca_atual
        for _ in range(rotacoes):
            peca = [list(row) for row in zip(*peca[::-1])]

        # Checa se a peça rotacionada cabe na posição
        largura_peca = len(peca[0])
        if px < 0 or px + largura_peca > LARGURA:
            return -999, 99, 99, 99  # penalidade alta

        # Simula queda
        y = 0
        while not self.colide(px, y + 1, peca):
            y += 1

        # Cria cópia e fixa
        tab = self.clonar_tabuleiro()
        for i, linha in enumerate(peca):
            for j, val in enumerate(linha):
                if val and y + i < ALTURA and px + j < LARGURA:
                    tab[y + i][px + j] = val

        # Avalia tabuleiro
        return self.heuristica(tab)

    def heuristica(self, tab):
        """Calcula métricas heurísticas para avaliação do tabuleiro"""
        # Linhas completas
        linhas = sum(1 for linha in tab if all(linha))
        
        # Altura máxima
        altura = max((y for y, linha in enumerate(tab) if any(linha)), default=0)
        
        # Número de buracos
        buracos = sum(
            1 for x in range(LARGURA)
            for y in range(ALTURA)
            if tab[y][x] == 0 and any(tab[k][x] for k in range(y))
        )
        
        # Uniformidade (variação de altura entre colunas)
        uniformidade = sum(abs(sum(tab[y][x] != 0 for y in range(ALTURA)) -
                               sum(tab[y][x + 1] != 0 for y in range(ALTURA)))
                           for x in range(LARGURA - 1))
        
        return linhas, altura, buracos, uniformidade

    def reset(self):
        """Reinicia o jogo"""
        self.__init__()
