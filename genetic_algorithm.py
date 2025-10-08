import random
import numpy as np
import json
import os
from multiprocessing import Pool, cpu_count
from functools import partial
from tqdm import tqdm

from config import POP_SIZE, N_GENERATIONS, MUTATION_RATE, SAVE_FILE, N_PROCESSES, LARGURA
from tetris import Tetris


def fitness(individuo, pbar=None):
    """Calcula o fitness de um indivíduo jogando Tetris"""
    jogo = Tetris()
    total_score = 0

    while not jogo.game_over:
        melhor_score = -99999
        melhor_acao = None
        
        # Testa todas as possíveis jogadas
        for rot in range(4):
            for x in range(LARGURA):
                if not jogo.colide(x, 0, jogo.peca_atual):
                    linhas, altura, buracos, uniforme = jogo.simula_jogada(x, rot)
                    w1, w2, w3, w4 = individuo
                    score = w1 * linhas - w2 * buracos - w3 * altura + w4 * uniforme
                    if score > melhor_score:
                        melhor_score = score
                        melhor_acao = (x, rot)

        # Aplica a melhor jogada
        if melhor_acao:
            x, rot = melhor_acao
            for _ in range(rot):
                jogo.peca_atual = [list(row) for row in zip(*jogo.peca_atual[::-1])]
            jogo.x = x

        jogo.passo()
        total_score += 1

        # Limite para evitar rodadas infinitas
        if total_score > 500:
            break

        # Atualiza barra de progresso se fornecida
        if pbar:
            pbar.update(1)

    return jogo.pontos


def fitness_wrapper(individuo):
    """Wrapper para a função fitness que funciona com multiprocessing"""
    if isinstance(individuo, list):
        individuo = np.array(individuo)
    return fitness(individuo, pbar=None)


def crossover(pai, mae):
    """Realiza crossover entre dois indivíduos"""
    ponto = random.randint(1, len(pai) - 1)
    return np.concatenate([pai[:ponto], mae[ponto:]])


def mutacao(individuo):
    """Aplica mutação em um indivíduo"""
    novo = individuo.copy()
    if random.random() < MUTATION_RATE:
        i = random.randint(0, len(novo) - 1)
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
    """Salva o melhor indivíduo de uma geração"""
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
    """Carrega pesos salvos de gerações anteriores"""
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
    """Carrega histórico completo de gerações"""
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            if data and isinstance(data[0], dict):
                return data
    return None


def treinar_ia():
    """Função principal para treinar a IA"""
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
    
    return melhor
