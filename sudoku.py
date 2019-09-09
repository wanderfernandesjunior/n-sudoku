#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" sudoku.py
Problema de CSP (constraint satisfaction problems) 
Referências consultadas:
 - Livro AIMA - "Artificial Intelligence - A Modern Approach"
 - Github oficial do livro AIMA (https://github.com/aimacode)
 - Documentação do Python (https://docs.python.org)"""

import itertools, re, random
from functools import reduce

def ler_entrada():
    """
    Lê dois parâmetros em linha de comando:
    - n: dimensao n do quebra-cabecas 
    - condição inicial do tabuleiro"""
    condicaoinicial = []
    while True:
        try:
            condicaoinicial=[]
            n = int(input())
            for _ in range(n*n):
                linha = input()
                condicaoinicial.append(linha)
            condicaoinicial = ' '.join(condicaoinicial)
            return n, condicaoinicial
        except Exception as erro:
                print(f"Erro: {erro}")

class CSP():
    """Classe generica para solucao de problema de satisfacao de restricoes. """

    def __init__(self, variaveis, dominios, vizinhos, restricoes):
        """Inicializadora da classe. Se variaveis estiver vazia, retorna as chaves dos dominios."""
        self.variaveis = variaveis or list(dominios.keys())
        self.dominios = dominios
        self.vizinhos = vizinhos
        self.restricoes = restricoes
        self.inicio = ()
        self.dominios_atuais = None
        self.numero_atribuicoes = 0

    def atribuir(self, var, val, tarefa):
        """Adiciona {var: val} a tarefa."""
        tarefa[var] = val
        self.numero_atribuicoes += 1

    def desatribuir(self, var, tarefa):
        """Remove {var: val} da tarefa."""
        if var in tarefa:
            del tarefa[var]

    def numero_conflitos(self, var, val, tarefa):
        """Returna o numero de conflitos var=val com outras variaveis."""
        def em_conflito(var2):
            return (var2 in tarefa and
                    not self.restricoes(var, val, var2, tarefa[var2]))
        return contar(em_conflito(v) for v in self.vizinhos[var])

    def imprime_resposta(self, tarefa):
        """Imprime representacao do CSP."""
        print('CSP:', tarefa)

    def acoes(self, estado):
        """Returna lista de acoes aplicaveis: que nao estejam em conflito."""
        if len(estado) == len(self.variaveis):
            return []
        else:
            tarefa = dict(estado)
            var = primeira([v for v in self.variaveis if v not in tarefa])
            return [(var, val) for val in self.dominios[var]
                    if self.numero_conflitos(var, val, tarefa) == 0]

    def resultado(self, estado, acao):
        """Executa uma acao e returna o novo estado."""
        (var, val) = acao
        return estado + ((var, val),)

    def testa_objetivo(self, estado):
        """O objetivo e atribuir todas as variaveis, com todas as restricoes satisfeitas."""
        tarefa = dict(estado)
        return (len(tarefa) == len(self.variaveis)
                and all(self.numero_conflitos(variaveis, tarefa[variaveis], tarefa) == 0
                        for variaveis in self.variaveis))

    # Os metodos abaixo são para propagacao de restricoes

    def suportar_poda(self):
        """Certifica que podemos remover valores de dominios."""
        if self.dominios_atuais is None:
            self.dominios_atuais = {v: list(self.dominios[v]) for v in self.variaveis}

    def presumir(self, var, value):
        """Acumula inferencias de presumir var=value."""
        self.suportar_poda()
        remocoes = [(var, a) for a in self.dominios_atuais[var] if a != value]
        self.dominios_atuais[var] = [value]
        return remocoes

    def podar(self, var, value, remocoes):
        """Remove var=value."""
        self.dominios_atuais[var].remove(value)
        if remocoes is not None:
            remocoes.append((var, value))

    def escolhas(self, var):
        """Retorna todos os valores para var que não estão atualmente descartados."""
        return (self.dominios_atuais or self.dominios)[var]

    def inferir_tarefa(self):
        """Returna as tarefas implicadas pelas inferencias realizadas."""
        self.suportar_poda()
        return {v: self.dominios_atuais[v][0]
                for v in self.variaveis if 1 == len(self.dominios_atuais[v])}

    def restabelecer(self, remocoes):
        """Desfaz uma suposição e todas as inferencias feitas."""
        for B, b in remocoes:
            self.dominios_atuais[B].append(b)


class Sudoku(CSP):
    """ O problema tradicional de Sudoku consiste em um quebra-cabeças sobre uma matriz 9 × 9,
    dividida em 9 sub-matrizes 3 × 3. O problema generalizado de Sudoku e formado por
    uma matriz n^2 × n^2 , dividida em n^2 sub-matrizes de tamanho n × n, para algum inteiro
    n ≥ 2. """
    
    def __init__(self, n , grid):
        """Inicializadora da classe. O número 0 significa que a posição do quebra cabeças está em branco."""
        _RN = list(range(n))
        _CELL = itertools.count().__next__
        _BGRID = [[[[_CELL() for x in _RN] for y in _RN] for bx in _RN] for by in _RN]
        _BOXES = self.flatten([list(map(self.flatten, brow)) for brow in _BGRID])
        _LINHAS = self.flatten([list(map(self.flatten, zip(*brow))) for brow in _BGRID])
        _COLUNAS = list(zip(*_LINHAS))
        _VIZINHOS = {v: set() for v in self.flatten(_LINHAS)}
        for unit in map(set, _BOXES + _LINHAS + _COLUNAS):
            for v in unit:
                _VIZINHOS[v].update(unit - {v})
        
        self.n = n
        self.RN = _RN
        self.cell = _CELL
        self.bgrid = _BGRID
        self.boxes = _BOXES
        self.linhas = _LINHAS
        self.colunas = _COLUNAS
        self.vizinhos = _VIZINHOS

        numeros_entrada = iter(re.findall(r'\d+', grid))
        numeros_possiveis = [i+1 for i in range(n*n)]
        dominios = {var: [num] if num in numeros_possiveis else numeros_possiveis
                   for var, num in zip(self.flatten(self.linhas), numeros_entrada)}

        CSP.__init__(self, None, dominios, self.vizinhos, self.restricao_valores_diferentes)


    def restricao_valores_diferentes(self, A, a, B, b):
        """Restricao para a qual duas variaveis vizinhas devem ter valores distintos."""
        return a != b

    def flatten(self, seqs):
            return sum(seqs, [])

    def imprime_resposta(self, tarefa):
        def show_box(box): return [' '.join(map(show_cell, row)) for row in box]

        def show_cell(cell): return str(tarefa.get(cell, '.'))

        def abut(lines1, lines2): return list(
            map(' '.join, list(zip(lines1, lines2))))
        
        print("Resposta:")
        print('\n'.join('\n'.join(reduce(abut, map(show_box, brow))) for brow in self.bgrid))


def contar(seq):
    """Conta o numero de itens na sequencia que sao interpretados como verdadeiro."""
    return sum(map(bool, seq))

def primeira(iterable, default=None):
    """Returna o primeira elemento da iterable ou default."""
    return next(iter(iterable), default)

# ______________________________________________________________________________
# Propagacao de restricao com AC-3
def AC3(csp, fila=None, remocoes=None):
    if fila is None:
        fila = [(Xi, Xk) for Xi in csp.variaveis for Xk in csp.vizinhos[Xi]]
    csp.suportar_poda()
    while fila:
        (Xi, Xj) = fila.pop()
        if revisar(csp, Xi, Xj, remocoes):
            if not csp.dominios_atuais[Xi]:
                return False
            for Xk in csp.vizinhos[Xi]:
                if Xk != Xj:
                    fila.append((Xk, Xi))
    return True


def revisar(csp, Xi, Xj, remocoes):
    """Returna verdadeiro se um valor foi removido."""
    revisado = False
    for x in csp.dominios_atuais[Xi][:]:
        # If Xi=x em_conflitos with Xj=y for every possible y, eliminate Xi=x
        if all(not csp.restricoes(Xi, x, Xj, y) for y in csp.dominios_atuais[Xj]):
            csp.podar(Xi, x, remocoes)
            revisado = True
    return revisado

# ______________________________________________________________________________
# CSP - Busca por Backtracking

# Selecao de variaveis (primeira_variavel_nao_atribuida, mrv )

def primeira_variavel_nao_atribuida(tarefa, csp):
    """Seleciona a primeira variavel nao atribuida."""
    return primeira([var for var in csp.variaveis if var not in tarefa])

def selecao_heuristica_mrv(tarefa, csp):
    """Heuristica MRV (Minimum-remaining-values)."""

    def shuffled(iterable):
        """Randomly shuffle a copy of iterable."""
        items = list(iterable)
        random.shuffle(items)
        return items

    def argmin_random_tie(seq, key=lambda x: x):
        """Return a minimum element of seq; break ties at random."""
        return min(shuffled(seq), key=key)

    def num_legal_values(csp, var, tarefa):
        if csp.dominios_atuais:
            return len(csp.dominios_atuais[var])
        else:
            return contar(csp.numero_conflitos(var, val, tarefa) == 0
                        for val in csp.dominios[var])

    return argmin_random_tie(
        [v for v in csp.variaveis if v not in tarefa],
        key=lambda var: num_legal_values(csp, var, tarefa))


# Ordenacao de valores (sem ordenacao ou valores com minima restricao)

def sem_ordenacao_valores_dominio(var, tarefa, csp):
    """Retorna os valores possiveis sem ordenacao."""
    return csp.escolhas(var)

def ordenacao_heuristica_lcv(var, tarefa, csp):
    """Heuristica LCV (Least-constraining-values) - para escolher os valores com restrição mínima."""
    return sorted(csp.escolhas(var),
                  key=lambda val: csp.numero_conflitos(var, val, tarefa))


# Inferências (sem inferencia, forward_checking ou mac)

def sem_inferencia(csp, var, value, tarefa, remocoes):
    return True

def forward_checking(csp, var, value, tarefa, remocoes):
    """Poda valores vizinhos inconsistentes com var = value."""
    csp.suportar_poda()
    for B in csp.vizinhos[var]:
        if B not in tarefa:
            for b in csp.dominios_atuais[B][:]:
                if not csp.restricoes(var, value, B, b):
                    csp.podar(B, b, remocoes)
            if not csp.dominios_atuais[B]:
                return False
    return True


def mac(csp, var, value, tarefa, remocoes):
    """Manter a consistência de arco."""
    return AC3(csp, [(X, var) for X in csp.vizinhos[var]], remocoes)


# Busca Backtracking

def busca_backtracking(csp,
                        selecao_variavel_nao_atribuida=primeira_variavel_nao_atribuida,
                        ordenacao_valores_dominio=sem_ordenacao_valores_dominio,
                        inferencia=sem_inferencia):

    def backtrack(tarefa):
        if len(tarefa) == len(csp.variaveis):
            return tarefa
        var = selecao_variavel_nao_atribuida(tarefa, csp)
        for value in ordenacao_valores_dominio(var, tarefa, csp):
            if 0 == csp.numero_conflitos(var, value, tarefa):
                csp.atribuir(var, value, tarefa)
                remocoes = csp.presumir(var, value)
                if inferencia(csp, var, value, tarefa, remocoes):
                    resultado = backtrack(tarefa)
                    if resultado is not None:
                        return resultado
                csp.restabelecer(remocoes)
        csp.desatribuir(var, tarefa)
        return None

    resultado = backtrack({})
    assert resultado is None or csp.testa_objetivo(resultado)
    return resultado

def main():
    """ Programa Principal. """
    n, condicaoinicial = ler_entrada()
    problema = Sudoku(n, condicaoinicial)
    solucao = busca_backtracking(problema, 
                                selecao_variavel_nao_atribuida=selecao_heuristica_mrv, 
                                ordenacao_valores_dominio=ordenacao_heuristica_lcv, 
                                inferencia=forward_checking)
    problema.imprime_resposta(solucao)

if __name__ == '__main__':
    main()