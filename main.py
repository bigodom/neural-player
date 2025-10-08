#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tetris IA - Sistema de treinamento de IA para Tetris usando Algoritmo Genético
Autor: Assistente IA
Data: 2024

Este programa permite:
1. Treinar uma IA para jogar Tetris usando algoritmo genético
2. Assistir a IA jogar com os melhores pesos treinados
3. Jogar Tetris manualmente
"""

import sys
import os
from genetic_algorithm import treinar_ia, carregar_historico_completo
from visual import VisualizadorTetris


def mostrar_menu_console():
    """Mostra o menu principal no console"""
    print("\n" + "="*50)
    print("TETRIS IA - Sistema de Treinamento")
    print("="*50)
    print("1. Treinar IA (Algoritmo Genético)")
    print("2. Ver IA jogar (Replay)")
    print("3. Jogar você mesmo")
    print("4. Ver estatísticas de treinamento")
    print("5. Sair")
    print("="*50)


def treinar_ia_console():
    """Treina a IA via console"""
    print("\nIniciando treinamento da IA...")
    print("Este processo pode demorar vários minutos!")
    
    try:
        melhor_pesos = treinar_ia()
        print(f"\nTreinamento concluído!")
        print(f"Melhores pesos encontrados: {melhor_pesos}")
        
        # Pergunta se quer ver o replay
        resposta = input("\nDeseja ver a IA jogar com os melhores pesos? (s/N): ").strip().lower()
        if resposta in ['s', 'sim', 'y', 'yes']:
            visualizador = VisualizadorTetris()
            try:
                visualizador.replay_ia(melhor_pesos)
            finally:
                visualizador.fechar()
                
    except KeyboardInterrupt:
        print("\nTreinamento interrompido pelo usuário!")
    except Exception as e:
        print(f"\nErro durante o treinamento: {e}")


def ver_ia_jogar():
    """Permite assistir a IA jogar"""
    print("\nCarregando IA treinada...")
    
    historico = carregar_historico_completo()
    if not historico:
        print("Nenhuma IA treinada encontrada!")
        print("Treine uma IA primeiro usando a opção 1.")
        return
    
    visualizador = VisualizadorTetris()
    try:
        pesos = visualizador.escolher_peso_para_replay()
        if pesos:
            print(f"\nIniciando replay da IA...")
            print("Pressione ESC para voltar ao menu durante o jogo.")
            visualizador.replay_ia(pesos)
        else:
            print("Nenhum peso válido selecionado!")
    finally:
        visualizador.fechar()


def jogar_humano():
    """Permite jogar Tetris manualmente"""
    print("\nIniciando jogo humano...")
    print("Controles:")
    print("   Setas esquerda/direita : Mover peça")
    print("   Seta para cima : Rotacionar peça")
    print("   Seta para baixo : Acelerar queda")
    print("   ESPAÇO : Drop rápido")
    print("   P ou PAUSE : Pausar/Despausar")
    print("   ESC : Sair do jogo")
    print("\nPreparando interface gráfica...")
    
    visualizador = VisualizadorTetris()
    try:
        visualizador.jogar_humano()
    finally:
        visualizador.fechar()


def mostrar_estatisticas():
    """Mostra estatísticas do treinamento"""
    print("\nCarregando estatísticas...")
    
    historico = carregar_historico_completo()
    if not historico:
        print("Nenhuma estatística encontrada!")
        print("Treine uma IA primeiro usando a opção 1.")
        return
    
    print(f"\nESTATÍSTICAS DE TREINAMENTO")
    print("="*50)
    print(f"Total de gerações: {len(historico)}")
    
    if historico:
        melhor_score = max(item['score'] for item in historico)
        pior_score = min(item['score'] for item in historico)
        media_score = sum(item['score'] for item in historico) / len(historico)
        
        print(f"Melhor score: {melhor_score}")
        print(f"Pior score: {pior_score}")
        print(f"Score médio: {media_score:.2f}")
        
        print(f"\nHISTÓRICO DAS GERAÇÕES:")
        print("-" * 50)
        for item in historico[-10:]:  # Mostra últimas 10 gerações
            print(f"Geração {item['geracao']:3d}: Score {item['score']:4d} | "
                  f"Pesos: [{item['pesos'][0]:6.2f}, {item['pesos'][1]:6.2f}, "
                  f"{item['pesos'][2]:6.2f}, {item['pesos'][3]:6.2f}]")
        
        if len(historico) > 10:
            print(f"... e mais {len(historico) - 10} gerações anteriores")


def main():
    """Função principal do programa"""
    print("Bem-vindo ao Tetris IA!")
    print("Este programa treina uma IA para jogar Tetris usando Algoritmo Genético")
    
    while True:
        try:
            mostrar_menu_console()
            opcao = input("\nEscolha uma opção (1-5): ").strip()
            
            if opcao == "1":
                treinar_ia_console()
            elif opcao == "2":
                ver_ia_jogar()
            elif opcao == "3":
                jogar_humano()
            elif opcao == "4":
                mostrar_estatisticas()
            elif opcao == "5":
                print("\nObrigado por usar o Tetris IA!")
                print("Até a próxima!")
                break
            else:
                print("\nOpção inválida! Escolha um número de 1 a 5.")
                
        except KeyboardInterrupt:
            print("\n\nPrograma interrompido pelo usuário!")
            print("Até a próxima!")
            break
        except Exception as e:
            print(f"\nErro inesperado: {e}")
            print("Tente novamente ou reinicie o programa.")
        
        input("\nPressione ENTER para continuar...")


if __name__ == "__main__":
    main()
