import pygame
import time
from config import (
    LARGURA, ALTURA, TAMANHO_BLOCO, CORES_PECAS, 
    LARGURA_TELA, ALTURA_TELA, TAMANHO_FONTE, VELOCIDADE_IA
)
from tetris import Tetris


class VisualizadorTetris:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
        pygame.display.set_caption("Tetris - IA vs Humano")
        self.clock = pygame.time.Clock()
        self.fonte = pygame.font.SysFont("Arial", TAMANHO_FONTE)
        self.fonte_grande = pygame.font.SysFont("Arial", TAMANHO_FONTE * 2)

    def desenhar_tabuleiro(self, jogo):
        """Desenha o tabuleiro do jogo"""
        self.tela.fill((0, 0, 0))  # Fundo preto
        
        # Desenha peças fixadas no tabuleiro
        for y in range(ALTURA):
            for x in range(LARGURA):
                if jogo.tabuleiro[y][x]:
                    cor = CORES_PECAS.get(jogo.tabuleiro[y][x], (255, 255, 255))
                    pygame.draw.rect(self.tela, cor, 
                                   (x * TAMANHO_BLOCO, y * TAMANHO_BLOCO, 
                                    TAMANHO_BLOCO, TAMANHO_BLOCO))
                    pygame.draw.rect(self.tela, (255, 255, 255), 
                                   (x * TAMANHO_BLOCO, y * TAMANHO_BLOCO, 
                                    TAMANHO_BLOCO, TAMANHO_BLOCO), 1)

        # Desenha a peça atual
        for i, linha in enumerate(jogo.peca_atual):
            for j, val in enumerate(linha):
                if val:
                    cor = CORES_PECAS.get(val, (255, 255, 255))
                    pygame.draw.rect(self.tela, cor, 
                                   ((jogo.x + j) * TAMANHO_BLOCO, 
                                    (jogo.y + i) * TAMANHO_BLOCO, 
                                    TAMANHO_BLOCO, TAMANHO_BLOCO))
                    pygame.draw.rect(self.tela, (255, 255, 255), 
                                   ((jogo.x + j) * TAMANHO_BLOCO, 
                                    (jogo.y + i) * TAMANHO_BLOCO, 
                                    TAMANHO_BLOCO, TAMANHO_BLOCO), 1)

    def desenhar_info(self, jogo, modo="IA"):
        """Desenha informações do jogo na tela"""
        info_textos = [
            f"Modo: {modo}",
            f"Pontos: {jogo.pontos}",
            f"Linhas: {jogo.linhas_removidas}",
            f"Nível: {jogo.nivel}"
        ]
        
        if modo == "Humano":
            controles = [
                "Controles:",
                "← → Mover",
                "↑ Rotacionar", 
                "↓ Acelerar",
                "ESPAÇO Drop"
            ]
            info_textos.extend(controles)
        
        for i, texto in enumerate(info_textos):
            superficie = self.fonte.render(texto, True, (255, 255, 255))
            self.tela.blit(superficie, (10, 10 + i * 25))

    def mostrar_pause(self, jogo, modo="Humano"):
        """Mostra tela de pause"""
        # Cria uma superfície semi-transparente
        overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.tela.blit(overlay, (0, 0))
        
        # Texto principal
        texto_principal = self.fonte_grande.render("PAUSE", True, (255, 255, 0))
        rect_principal = texto_principal.get_rect(center=(LARGURA_TELA//2, ALTURA_TELA//2 - 60))
        self.tela.blit(texto_principal, rect_principal)
        
        # Estatísticas atuais
        stats = [
            f"Modo: {modo}",
            f"Pontuação: {jogo.pontos}",
            f"Linhas Removidas: {jogo.linhas_removidas}",
            f"Nível: {jogo.nivel}"
        ]
        
        for i, stat in enumerate(stats):
            texto = self.fonte.render(stat, True, (255, 255, 255))
            rect = texto.get_rect(center=(LARGURA_TELA//2, ALTURA_TELA//2 + i * 25))
            self.tela.blit(texto, rect)
        
        # Instruções
        instrucoes = [
            "Pressione P para continuar",
            "Pressione ESC para sair"
        ]
        
        for i, instrucao in enumerate(instrucoes):
            texto = self.fonte.render(instrucao, True, (200, 200, 200))
            rect = texto.get_rect(center=(LARGURA_TELA//2, ALTURA_TELA//2 + 120 + i * 25))
            self.tela.blit(texto, rect)
        
        pygame.display.update()

    def mostrar_game_over(self, jogo):
        """Mostra tela de game over"""
        self.tela.fill((0, 0, 0))
        
        # Texto principal
        texto_principal = self.fonte_grande.render("GAME OVER", True, (255, 0, 0))
        rect_principal = texto_principal.get_rect(center=(LARGURA_TELA//2, ALTURA_TELA//2 - 50))
        self.tela.blit(texto_principal, rect_principal)
        
        # Estatísticas finais
        stats = [
            f"Pontuação Final: {jogo.pontos}",
            f"Linhas Removidas: {jogo.linhas_removidas}",
            f"Nível Alcançado: {jogo.nivel}"
        ]
        
        for i, stat in enumerate(stats):
            texto = self.fonte.render(stat, True, (255, 255, 255))
            rect = texto.get_rect(center=(LARGURA_TELA//2, ALTURA_TELA//2 + i * 30))
            self.tela.blit(texto, rect)
        
        # Instruções
        instrucao = self.fonte.render("Pressione ESC para voltar ao menu", True, (200, 200, 200))
        rect_instrucao = instrucao.get_rect(center=(LARGURA_TELA//2, ALTURA_TELA//2 + 150))
        self.tela.blit(instrucao, rect_instrucao)
        
        pygame.display.update()

    def mostrar_menu_principal(self):
        """Mostra o menu principal do jogo"""
        self.tela.fill((0, 0, 50))
        
        # Título
        titulo = self.fonte_grande.render("TETRIS IA", True, (255, 255, 255))
        rect_titulo = titulo.get_rect(center=(LARGURA_TELA//2, 100))
        self.tela.blit(titulo, rect_titulo)
        
        # Opções do menu
        opcoes = [
            "1 - Treinar IA",
            "2 - Ver IA jogar",
            "3 - Jogar você mesmo",
            "4 - Sair"
        ]
        
        for i, opcao in enumerate(opcoes):
            cor = (255, 255, 255) if i < len(opcoes) - 1 else (255, 100, 100)
            texto = self.fonte.render(opcao, True, cor)
            rect = texto.get_rect(center=(LARGURA_TELA//2, 200 + i * 50))
            self.tela.blit(texto, rect)
        
        pygame.display.update()

    def replay_ia(self, pesos):
        """Mostra a IA jogando com os pesos fornecidos"""
        jogo = Tetris()
        rodando = True
        pausado = False
        
        while rodando and not jogo.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    rodando = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        rodando = False
                    elif event.key == pygame.K_p or event.key == pygame.K_PAUSE:
                        # Alterna pause
                        pausado = not pausado

            if pausado:
                # Mostra tela de pause
                self.desenhar_tabuleiro(jogo)
                self.mostrar_pause(jogo, "IA")
            else:
                # IA escolhe jogada (só se não estiver pausado)
                melhor_score = -99999
                melhor_acao = None
                
                for rot in range(4):
                    for x in range(LARGURA):
                        if not jogo.colide(x, 0, jogo.peca_atual):
                            linhas, altura, buracos, uniforme = jogo.simula_jogada(x, rot)
                            w1, w2, w3, w4 = pesos
                            score = w1 * linhas - w2 * buracos - w3 * altura + w4 * uniforme
                            if score > melhor_score:
                                melhor_score = score
                                melhor_acao = (x, rot)

                if melhor_acao:
                    x, rot = melhor_acao
                    for _ in range(rot):
                        jogo.peca_atual = [list(row) for row in zip(*jogo.peca_atual[::-1])]
                    jogo.x = x

                jogo.passo()

                # Desenha o jogo normal
                self.desenhar_tabuleiro(jogo)
                self.desenhar_info(jogo, "IA")
                pygame.display.update()
                self.clock.tick(VELOCIDADE_IA)

        # Mostra game over
        if jogo.game_over:
            self.mostrar_game_over(jogo)
            esperando = True
            while esperando:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        esperando = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            esperando = False

    def jogar_humano(self):
        """Permite ao jogador jogar manualmente"""
        jogo = Tetris()
        rodando = True
        pausado = False
        tempo_queda = time.time()
        intervalo_queda = 1.0  # segundos entre quedas automáticas
        
        while rodando and not jogo.game_over:
            agora = time.time()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    rodando = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        rodando = False
                    elif event.key == pygame.K_p or event.key == pygame.K_PAUSE:
                        # Alterna pause
                        pausado = not pausado
                        if pausado:
                            # Salva o tempo quando pausou
                            tempo_pause = agora
                    elif not pausado:  # Só processa controles se não estiver pausado
                        if event.key == pygame.K_LEFT:
                            jogo.mover_esquerda()
                        elif event.key == pygame.K_RIGHT:
                            jogo.mover_direita()
                        elif event.key == pygame.K_UP:
                            jogo.rotacionar()
                        elif event.key == pygame.K_DOWN:
                            jogo.passo()
                        elif event.key == pygame.K_SPACE:
                            jogo.drop_rapido()

            if pausado:
                # Mostra tela de pause
                self.desenhar_tabuleiro(jogo)
                self.mostrar_pause(jogo, "Humano")
            else:
                # Queda automática (só se não estiver pausado)
                if agora - tempo_queda >= intervalo_queda:
                    jogo.passo()
                    tempo_queda = agora
                    # Aumenta velocidade conforme o nível
                    intervalo_queda = max(0.1, 1.0 - (jogo.nivel - 1) * 0.1)

                # Desenha o jogo normal
                self.desenhar_tabuleiro(jogo)
                self.desenhar_info(jogo, "Humano")
                
                # Adiciona indicação de pause na info
                if pausado:
                    pause_texto = self.fonte.render("PAUSADO", True, (255, 255, 0))
                    self.tela.blit(pause_texto, (10, ALTURA_TELA - 30))
                
                pygame.display.update()
                self.clock.tick(60)  # 60 FPS para jogo humano

        # Mostra game over
        if jogo.game_over:
            self.mostrar_game_over(jogo)
            esperando = True
            while esperando:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        esperando = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            esperando = False

    def escolher_peso_para_replay(self):
        """Interface para escolher qual IA assistir"""
        from genetic_algorithm import carregar_historico_completo
        
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
            try:
                geracao = int(input("Digite o número da geração para ver o replay: "))
                for item in historico:
                    if item["geracao"] == geracao:
                        return item["pesos"]
                print("Geração não encontrada!")
                return None
            except ValueError:
                print("Entrada inválida!")
                return None
        else:
            # Suporte retrocompatível
            try:
                idx = int(input("Digite o número do indivíduo para ver o replay: "))
                return historico[idx] if 0 <= idx < len(historico) else None
            except ValueError:
                print("Entrada inválida!")
                return None

    def fechar(self):
        """Fecha a visualização"""
        pygame.quit()
