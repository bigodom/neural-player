#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste completo para verificar:
- Remoção de múltiplas linhas (1, 2, 3, 4 linhas)
- Sistema de pontuação do Tetris original
- Funcionamento geral do jogo
"""

from tetris import Tetris
from config import LARGURA, ALTURA

def teste_uma_linha():
    """Testa remoção de 1 linha"""
    print("\n=== TESTE: 1 LINHA ===")
    jogo = Tetris()
    
    # Preenche apenas a linha 19 (última linha)
    for x in range(LARGURA):
        jogo.tabuleiro[19][x] = 1
    
    pontos_antes = jogo.pontos
    linhas_antes = jogo.linhas_removidas
    
    print(f"Antes: Pontos={pontos_antes}, Linhas={linhas_antes}")
    
    jogo.remove_linhas()
    
    print(f"Depois: Pontos={jogo.pontos}, Linhas={jogo.linhas_removidas}")
    print(f"Pontos ganhos: {jogo.pontos - pontos_antes}")
    print(f"Linhas removidas: {jogo.linhas_removidas - linhas_antes}")
    
    esperado = 40 * jogo.nivel
    ganho_real = jogo.pontos - pontos_antes
    
    if ganho_real == esperado:
        print(f"SUCESSO: 1 linha = {esperado} pontos")
    else:
        print(f"ERRO: Esperado {esperado}, recebido {ganho_real}")
    
    return ganho_real == esperado

def teste_duas_linhas():
    """Testa remoção de 2 linhas"""
    print("\n=== TESTE: 2 LINHAS ===")
    jogo = Tetris()
    
    # Preenche linhas 18 e 19
    for linha_idx in [18, 19]:
        for x in range(LARGURA):
            jogo.tabuleiro[linha_idx][x] = 1
    
    pontos_antes = jogo.pontos
    linhas_antes = jogo.linhas_removidas
    
    print(f"Antes: Pontos={pontos_antes}, Linhas={linhas_antes}")
    
    jogo.remove_linhas()
    
    print(f"Depois: Pontos={jogo.pontos}, Linhas={jogo.linhas_removidas}")
    print(f"Pontos ganhos: {jogo.pontos - pontos_antes}")
    print(f"Linhas removidas: {jogo.linhas_removidas - linhas_antes}")
    
    esperado = 100 * jogo.nivel
    ganho_real = jogo.pontos - pontos_antes
    
    if ganho_real == esperado:
        print(f"SUCESSO: 2 linhas = {esperado} pontos")
    else:
        print(f"ERRO: Esperado {esperado}, recebido {ganho_real}")
    
    return ganho_real == esperado

def teste_tres_linhas():
    """Testa remoção de 3 linhas"""
    print("\n=== TESTE: 3 LINHAS ===")
    jogo = Tetris()
    
    # Preenche linhas 17, 18 e 19
    for linha_idx in [17, 18, 19]:
        for x in range(LARGURA):
            jogo.tabuleiro[linha_idx][x] = 1
    
    pontos_antes = jogo.pontos
    linhas_antes = jogo.linhas_removidas
    
    print(f"Antes: Pontos={pontos_antes}, Linhas={linhas_antes}")
    
    jogo.remove_linhas()
    
    print(f"Depois: Pontos={jogo.pontos}, Linhas={jogo.linhas_removidas}")
    print(f"Pontos ganhos: {jogo.pontos - pontos_antes}")
    print(f"Linhas removidas: {jogo.linhas_removidas - linhas_antes}")
    
    esperado = 300 * jogo.nivel
    ganho_real = jogo.pontos - pontos_antes
    
    if ganho_real == esperado:
        print(f"SUCESSO: 3 linhas = {esperado} pontos")
    else:
        print(f"ERRO: Esperado {esperado}, recebido {ganho_real}")
    
    return ganho_real == esperado

def teste_tetris_completo():
    """Testa remoção de 4 linhas (Tetris completo)"""
    print("\n=== TESTE: TETRIS (4 LINHAS) ===")
    jogo = Tetris()
    
    # Preenche linhas 16, 17, 18 e 19
    for linha_idx in [16, 17, 18, 19]:
        for x in range(LARGURA):
            jogo.tabuleiro[linha_idx][x] = 1
    
    pontos_antes = jogo.pontos
    linhas_antes = jogo.linhas_removidas
    
    print(f"Antes: Pontos={pontos_antes}, Linhas={linhas_antes}")
    print(f"Linhas completas detectadas: {sum(1 for linha in jogo.tabuleiro if all(linha))}")
    
    jogo.remove_linhas()
    
    print(f"Depois: Pontos={jogo.pontos}, Linhas={jogo.linhas_removidas}")
    print(f"Pontos ganhos: {jogo.pontos - pontos_antes}")
    print(f"Linhas removidas: {jogo.linhas_removidas - linhas_antes}")
    print(f"Linhas completas restantes: {sum(1 for linha in jogo.tabuleiro if all(linha))}")
    
    esperado = 1200 * jogo.nivel
    ganho_real = jogo.pontos - pontos_antes
    
    if ganho_real == esperado:
        print(f"SUCESSO: Tetris (4 linhas) = {esperado} pontos")
    else:
        print(f"ERRO: Esperado {esperado}, recebido {ganho_real}")
    
    return ganho_real == esperado

def teste_cenario_complexo():
    """Testa cenário com linhas não consecutivas"""
    print("\n=== TESTE: LINHAS NÃO CONSECUTIVAS ===")
    jogo = Tetris()
    
    # Preenche linhas 15, 17 e 19 (pula 16 e 18)
    for linha_idx in [15, 17, 19]:
        for x in range(LARGURA):
            jogo.tabuleiro[linha_idx][x] = 1
    
    pontos_antes = jogo.pontos
    linhas_antes = jogo.linhas_removidas
    
    print(f"Antes: Pontos={pontos_antes}, Linhas={linhas_antes}")
    print(f"Linhas completas detectadas: {sum(1 for linha in jogo.tabuleiro if all(linha))}")
    
    jogo.remove_linhas()
    
    print(f"Depois: Pontos={jogo.pontos}, Linhas={jogo.linhas_removidas}")
    print(f"Pontos ganhos: {jogo.pontos - pontos_antes}")
    print(f"Linhas removidas: {jogo.linhas_removidas - linhas_antes}")
    print(f"Linhas completas restantes: {sum(1 for linha in jogo.tabuleiro if all(linha))}")
    
    # Deveria remover 3 linhas
    esperado = 300 * jogo.nivel
    ganho_real = jogo.pontos - pontos_antes
    
    if ganho_real == esperado:
        print(f"SUCESSO: 3 linhas não consecutivas = {esperado} pontos")
    else:
        print(f"ERRO: Esperado {esperado}, recebido {ganho_real}")
    
    return ganho_real == esperado

def teste_nivel_diferente():
    """Testa pontuação com nível diferente"""
    print("\n=== TESTE: NÍVEL DIFERENTE ===")
    jogo = Tetris()
    jogo.nivel = 3  # Define nível 3
    
    # Preenche 2 linhas
    for linha_idx in [18, 19]:
        for x in range(LARGURA):
            jogo.tabuleiro[linha_idx][x] = 1
    
    pontos_antes = jogo.pontos
    
    jogo.remove_linhas()
    
    esperado = 100 * 3  # 2 linhas * nível 3
    ganho_real = jogo.pontos - pontos_antes
    
    print(f"Nível: {jogo.nivel}")
    print(f"2 linhas com nível {jogo.nivel}: {ganho_real} pontos")
    print(f"Esperado: {esperado}")
    
    if ganho_real == esperado:
        print("SUCESSO: Pontuação com nível diferente funcionando!")
    else:
        print(f"ERRO: Esperado {esperado}, recebido {ganho_real}")
    
    return ganho_real == esperado

def verificar_estrutura_tabuleiro():
    """Verifica se o tabuleiro mantém a estrutura correta"""
    print("\n=== TESTE: ESTRUTURA DO TABULEIRO ===")
    jogo = Tetris()
    
    # Preenche algumas linhas
    for linha_idx in [17, 18, 19]:
        for x in range(LARGURA):
            jogo.tabuleiro[linha_idx][x] = 1
    
    print(f"Dimensões originais: {len(jogo.tabuleiro)} x {len(jogo.tabuleiro[0])}")
    
    jogo.remove_linhas()
    
    print(f"Dimensões após remoção: {len(jogo.tabuleiro)} x {len(jogo.tabuleiro[0])}")
    
    # Verifica se as dimensões estão corretas
    if len(jogo.tabuleiro) == ALTURA and len(jogo.tabuleiro[0]) == LARGURA:
        print("SUCESSO: Estrutura do tabuleiro mantida!")
        return True
    else:
        print("ERRO: Estrutura do tabuleiro corrompida!")
        return False

def main():
    """Executa todos os testes"""
    print("="*60)
    print("TESTE COMPLETO - REMOCAO DE LINHAS E PONTUACAO")
    print("="*60)
    
    testes = [
        teste_uma_linha,
        teste_duas_linhas,
        teste_tres_linhas,
        teste_tetris_completo,
        teste_cenario_complexo,
        teste_nivel_diferente,
        verificar_estrutura_tabuleiro
    ]
    
    resultados = []
    
    for teste in testes:
        try:
            resultado = teste()
            resultados.append(resultado)
        except Exception as e:
            print(f"ERRO no teste {teste.__name__}: {e}")
            resultados.append(False)
    
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    
    nomes_testes = [
        "1 linha",
        "2 linhas", 
        "3 linhas",
        "Tetris (4 linhas)",
        "Linhas não consecutivas",
        "Nível diferente",
        "Estrutura do tabuleiro"
    ]
    
    for i, (nome, resultado) in enumerate(zip(nomes_testes, resultados)):
        status = "PASSOU" if resultado else "FALHOU"
        print(f"{i+1}. {nome}: {status}")
    
    total_passou = sum(resultados)
    total_testes = len(resultados)
    
    print(f"\nResultado: {total_passou}/{total_testes} testes passaram")
    
    if total_passou == total_testes:
        print("TODOS OS TESTES PASSARAM!")
    else:
        print("ALGUNS TESTES FALHARAM!")

if __name__ == "__main__":
    main()
