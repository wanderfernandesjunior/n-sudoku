# n-sudoku

Solução do problema n-sudoku.

ENTRADA: O programa lê dois parâmetros:
- n: dimensão do problema
- tabuleiro: n^2 linhas contendo n^2 números cada

SAÍDA: o programa retorna a primeira solução encontrada, por exemplo:

    localhost:~$ ./sudoku.py
    3
    0 0 0 2 6 0 7 0 1
    6 8 0 0 7 0 0 9 0
    1 9 0 0 0 4 5 0 0
    8 2 0 1 0 0 0 4 0
    0 0 4 6 0 2 9 0 0
    0 5 0 0 0 3 0 2 8
    0 0 9 3 0 0 0 7 4
    0 4 0 0 5 0 0 3 6
    7 0 3 0 1 8 0 0 0
    Resposta:
    4 3 5 2 6 9 7 8 1
    6 8 2 5 7 1 4 9 3
    1 9 7 8 3 4 5 6 2
    8 2 6 1 9 5 3 4 7
    3 7 4 6 8 2 9 1 5
    9 5 1 7 4 3 6 2 8
    5 1 9 3 2 6 8 7 4
    2 4 8 9 5 7 1 3 6
    7 6 3 4 1 8 2 5 9

Alternativa:

    localhost:~$ ./sudoku < game_n3.txt

Referências consultadas:

 - Livro AIMA - "Artificial Intelligence - A Modern Approach"
 - Github oficial do livro AIMA (https://github.com/aimacode)
 - Documentação do Python (https://docs.python.org)
