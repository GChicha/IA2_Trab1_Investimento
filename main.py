#! /bin/env python
import sqlite3
import argparse

from file_reader import parse_file

def insert_on_bd(cotacao_diaria, cursor):
    cursor.execute("INSERT INTO Cotacoes VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
                   , cotacao_diaria)

def main():
    parser = argparse.ArgumentParser(description="Extrai informações do arquivo bovespa")
    parser.add_argument('--entrada', metavar='FILE', nargs='+', type=argparse.FileType('r'),
                        help="Arquivos de entrada", required=True)
    parser.add_argument('--bdname', metavar='BD', nargs='?', default=":memory:",
                        help="Nome do arquivo do banco de dados se nenhum nome for passado o\
                              banco não será persistido")
    parser.add_argument('--empresa', metavar='EMPRESA', nargs='+',
                        help="Empresa a ser avaliada, pode ser inserida mais de uma empresa",
                        required=True)
    parser.add_argument('--debug', action='store_true')

    parsed = parser.parse_args()

    banco_dados = sqlite3.connect(parsed.bdname)

    if parsed.debug:
        banco_dados.set_trace_callback(print)

    cursor_bd = banco_dados.cursor()

    cursor_bd.execute('''CREATE TABLE IF NOT EXISTS Cotacoes
                        (data DATE, cod_bdi TEXT,
                        cod_neg TEXT, tipo_mer INT,
                        nome_res TEXT, esp_papel TEXT,
                        prazo FLOAT, moeda TEXT,
                        preco_abertura FLOAT, preco_max FLOAT,
                        preco_min FLOAT, preco_med FLOAT,
                        preco_ultimo FLOAT, preco_melhor_compra FLOAT,
                        preco_melhor_venda FLOAT, total_negociado FLOAT,
                        quantidade_total FLOAT, volume_total FLOAT,
                        preco_exercicio FLOAT, indicador_correcao TEXT,
                        data_venc DATE, fator_cotacao INT,
                        preco_pontos FLOAT, cod_isin TEXT,
                        dis_papel INT)''')

    for arquivo in parsed.entrada:
        for cotacao in parse_file(arquivo):
            insert_on_bd(cotacao, cursor_bd)

    banco_dados.commit()

if __name__ == '__main__':
    main()
