#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import csv
import sys
from typing import List, Dict, Set

class FiltradorHorarios:
    """Classe para filtrar horários de aulas em uma tabela CSV"""

    def __init__(self):
        # Ajusta o regex para capturar horários com ou sem sala
        self.padrao_horario = re.compile(r'(\d[MTN]\d)(?:\([^)]+\))?')

    def ler_arquivo_csv(self, caminho: str) -> List[str]:
        """
        Lê o arquivo CSV do caminho especificado
        """
        try:
            with open(caminho, 'r', encoding='utf-8') as arquivo:
                return list(csv.reader(arquivo))
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
        except Exception as e:
            raise Exception(f"Erro ao ler arquivo: {str(e)}")

    def extrair_dados_tabela(self, linhas: list) -> List[Dict]:
        """
        Extrai dados das linhas do CSV
        """
        dados = []
        codigo_atual = ""
        disciplina_atual = ""

        for linha in linhas:
            if not linha:  # Pula linhas vazias
                continue

            # Procura por linhas que começam com código da disciplina
            if linha[0].strip():
                texto = linha[0].strip()
                if " - " in texto and "Turma" not in texto and len(texto) > 5:
                    partes = texto.split(" - ", 1)
                    codigo_atual = partes[0].strip()
                    disciplina_atual = partes[1].strip() if len(partes) > 1 else ""
                    continue

            # Uma linha de dados de turma deve ter pelo menos 8 campos não vazios
            campos_nao_vazios = [c.strip() for c in linha if c.strip()]
            if len(campos_nao_vazios) >= 8:
                # Verifica se é uma linha de dados válida (tem turma e horário)
                turma = campos_nao_vazios[0]
                for campo in campos_nao_vazios:
                    if any(p in campo for p in ['(L', '(I', '(H', '(J']):
                        horario = campo
                        # Procura o professor no próximo campo não vazio após o horário
                        idx_horario = campos_nao_vazios.index(campo)
                        professor = campos_nao_vazios[idx_horario + 1] if idx_horario + 1 < len(campos_nao_vazios) else ""

                        dados.append({
                            'codigo': codigo_atual,
                            'disciplina': disciplina_atual,
                            'turma': turma,
                            'horario': horario,
                            'professor': professor
                        })
                        break

        return dados

    def filtrar_horarios(self, dados: List[Dict], horario_busca: str) -> List[Dict]:
        """
        Filtra as aulas pelo horário especificado
        """
        resultados = []

        for aula in dados:
            # Encontra todos os horários no formato dTa (d=dia, T=turno, a=aula)
            horarios = [match.group(1) for match in self.padrao_horario.finditer(aula['horario'])]

            if horario_busca in horarios:
                resultados.append(aula)

        return resultados

    def filtrar_varios_horarios(self, dados: List[Dict], horarios_busca: Set[str]) -> List[Dict]:
        """
        Filtra as aulas que tem todos seus horários dentro do conjunto informado

        Args:
            dados: Lista de dicionários com os dados das aulas
            horarios_busca: Conjunto de horários permitidos (ex: {'2M1', '2M2', '4M3'})

        Returns:
            Lista de aulas que têm todos seus horários dentro do conjunto informado
        """
        resultados = []

        for aula in dados:
            # Encontra todos os horários da aula
            horarios_aula = set(match.group(1) for match in self.padrao_horario.finditer(aula['horario']))

            # Verifica se todos os horários da aula estão no conjunto de busca
            if horarios_aula.issubset(horarios_busca):
                resultados.append(aula)

        return resultados

    def exibir_resultados(self, resultados: List[Dict]):
        """
        Exibe os resultados formatados
        """
        if not resultados:
            print("\nNenhuma aula encontrada com o(s) horário(s) especificado(s).")
            return

        print("\nAulas encontradas:")
        print("-" * 80)
        for aula in resultados:
            if aula['codigo']:
                print(f"Código: {aula['codigo']}")
                print(f"Disciplina: {aula['disciplina']}")
            print(f"Turma: {aula['turma']}")
            print(f"Horário: {aula['horario']}")
            print(f"Professor: {aula['professor']}")
            print("-" * 80)

def validar_formato_horario(horario: str) -> bool:
    """Valida se o horário está no formato correto"""
    return bool(re.match(r'^[2-6][MTN][1-6]$', horario))

def main():
    """Função principal do programa"""
    filtrador = FiltradorHorarios()
    arquivo_csv = "attached_assets/pdf (2).csv"

    # Interface com o usuário
    print("=== Filtrador de Horários de Aulas ===\n")
    print("1. Buscar por um horário específico")
    print("2. Informar horários disponíveis")

    opcao = input("\nEscolha uma opção (1-2): ").strip()

    if opcao == "1":
        # Busca por horário específico
        print("\nFormato do horário: dTa (d=dia[2-6], T=turno[M,T,N], a=aula[1-6])")
        print("Exemplo: 2M1 (Segunda-feira, Manhã, primeira aula)")
        horario = input("\nDigite o horário que deseja buscar: ").strip().upper()

        if not validar_formato_horario(horario):
            print("Erro: Formato de horário inválido.")
            return

        try:
            conteudo = filtrador.ler_arquivo_csv(arquivo_csv)
            dados = filtrador.extrair_dados_tabela(conteudo)
            resultados = filtrador.filtrar_horarios(dados, horario)
            filtrador.exibir_resultados(resultados)
        except Exception as e:
            print(f"\nErro ao processar arquivo: {str(e)}")

    elif opcao == "2":
        # Busca por múltiplos horários
        print("\nInforme os horários disponíveis separados por espaço")
        print("Formato: dTa (d=dia[2-6], T=turno[M,T,N], a=aula[1-6])")
        print("Exemplo: 2M1 2M2 4M3 6M1")

        horarios_input = input("\nDigite os horários: ").strip().upper().split()

        # Valida todos os horários
        if not all(validar_formato_horario(h) for h in horarios_input):
            print("Erro: Um ou mais horários estão em formato inválido.")
            return

        # Converte lista para conjunto para busca mais eficiente
        horarios_busca = set(horarios_input)

        try:
            conteudo = filtrador.ler_arquivo_csv(arquivo_csv)
            dados = filtrador.extrair_dados_tabela(conteudo)
            resultados = filtrador.filtrar_varios_horarios(dados, horarios_busca)
            filtrador.exibir_resultados(resultados)
        except Exception as e:
            print(f"\nErro ao processar arquivo: {str(e)}")

    else:
        print("Opção inválida!")

if __name__ == "__main__":
    main()