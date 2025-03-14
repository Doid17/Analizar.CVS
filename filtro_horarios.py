#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from bs4 import BeautifulSoup
from typing import List, Dict

class FiltradorHorarios:
    """Classe para filtrar horários de aulas em uma tabela HTML"""

    def __init__(self):
        # Ajusta o regex para capturar horários com ou sem sala
        self.padrao_horario = re.compile(r'(\d[MTN]\d)(?:\([^)]+\))?')

    def ler_arquivo_html(self, caminho: str) -> str:
        """
        Lê o arquivo HTML do caminho especificado

        Args:
            caminho: Caminho do arquivo HTML

        Returns:
            Conteúdo do arquivo HTML

        Raises:
            FileNotFoundError: Se o arquivo não for encontrado
        """
        try:
            with open(caminho, 'r', encoding='windows-1252') as arquivo:
                return arquivo.read()
        except UnicodeDecodeError:
            # Se falhar com windows-1252, tenta utf-8
            with open(caminho, 'r', encoding='utf-8') as arquivo:
                return arquivo.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
        except Exception as e:
            raise Exception(f"Erro ao ler arquivo: {str(e)}")

    def extrair_dados_tabela(self, html: str) -> List[Dict]:
        """
        Extrai dados da tabela HTML

        Args:
            html: Conteúdo HTML

        Returns:
            Lista de dicionários com os dados das linhas
        """
        soup = BeautifulSoup(html, 'html.parser')
        dados = []
        codigo_atual = ""
        disciplina_atual = ""

        # Procura todas as linhas que contêm dados de disciplinas
        for linha in soup.find_all('tr'):
            # Se é uma linha de título de disciplina (tem classe 't')
            titulo = linha.find('td', class_='t')
            if titulo and titulo.find('b'):
                texto = titulo.find('b').text.strip()
                partes = texto.split(' - ', 1)
                codigo_atual = partes[0]
                disciplina_atual = partes[1] if len(partes) > 1 else ""
                print(f"DEBUG - Nova disciplina encontrada: {codigo_atual} - {disciplina_atual}")
                continue

            # Se é uma linha de dados (primeira célula tem classe 'sl')
            colunas = linha.find_all('td')
            primeira_coluna = linha.find('td', class_='sl')
            if primeira_coluna and len(colunas) >= 9:
                turma = primeira_coluna.text.strip()
                horario = colunas[8].text.strip()  # Horário está na coluna 8
                professor = colunas[9].text.strip() if len(colunas) > 9 else ""

                # Debug: imprime os horários encontrados
                print(f"DEBUG - Turma: {turma}")
                print(f"DEBUG - Horário encontrado: {horario}")
                horarios = [match.group(1) for match in self.padrao_horario.finditer(horario)]
                print(f"DEBUG - Horários extraídos: {horarios}")

                dados.append({
                    'codigo': codigo_atual,
                    'disciplina': disciplina_atual,
                    'turma': turma,
                    'horario': horario,
                    'professor': professor
                })

        print(f"DEBUG - Total de dados extraídos: {len(dados)}")
        return dados

    def filtrar_horarios(self, dados: List[Dict], horario_busca: str) -> List[Dict]:
        """
        Filtra as aulas pelo horário especificado

        Args:
            dados: Lista de dicionários com os dados das aulas
            horario_busca: Horário a ser buscado (ex: '2M1')

        Returns:
            Lista de aulas que contêm o horário buscado
        """
        resultados = []

        for aula in dados:
            # Encontra todos os horários no formato dTa (d=dia, T=turno, a=aula)
            horarios = [match.group(1) for match in self.padrao_horario.finditer(aula['horario'])]
            print(f"DEBUG - Verificando horários {horarios} para {aula['turma']}")

            if horario_busca in horarios:
                resultados.append(aula)

        return resultados

    def exibir_resultados(self, resultados: List[Dict]):
        """
        Exibe os resultados formatados

        Args:
            resultados: Lista de aulas filtradas
        """
        if not resultados:
            print("\nNenhuma aula encontrada com o horário especificado.")
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

def main():
    """Função principal do programa"""
    filtrador = FiltradorHorarios()

    # Interface com o usuário
    print("=== Filtrador de Horários de Aulas ===\n")

    # Busca arquivos HTML no diretório atual
    arquivos_html = [f for f in os.listdir('.') if f.endswith('.html')]

    if not arquivos_html:
        print("Erro: Nenhum arquivo HTML encontrado no diretório atual.")
        return

    # Lista arquivos disponíveis
    print("Arquivos HTML disponíveis:")
    for i, arquivo in enumerate(arquivos_html, 1):
        print(f"{i}. {arquivo}")

    # Solicita escolha do arquivo
    while True:
        try:
            escolha = int(input("\nEscolha o número do arquivo (1-{}): ".format(len(arquivos_html))))
            if 1 <= escolha <= len(arquivos_html):
                arquivo_escolhido = arquivos_html[escolha-1]
                break
            print("Escolha inválida. Tente novamente.")
        except ValueError:
            print("Por favor, digite um número válido.")

    # Solicita o horário para filtrar
    print("\nFormato do horário: dTa (d=dia[2-6], T=turno[M,T,N], a=aula[1-6])")
    print("Exemplo: 2M1 (Segunda-feira, Manhã, primeira aula)")

    horario = input("\nDigite o horário que deseja buscar: ").strip().upper()

    # Valida formato do horário
    if not re.match(r'^[2-6][MTN][1-6]$', horario):
        print("Erro: Formato de horário inválido.")
        return

    try:
        # Processa o arquivo
        conteudo_html = filtrador.ler_arquivo_html(arquivo_escolhido)
        dados = filtrador.extrair_dados_tabela(conteudo_html)
        resultados = filtrador.filtrar_horarios(dados, horario)
        filtrador.exibir_resultados(resultados)

    except Exception as e:
        print(f"\nErro ao processar arquivo: {str(e)}")

if __name__ == "__main__":
    main()