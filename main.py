#! /bin/env python3
import sqlite3
import argparse

from file_reader import parse_file, CotacaoDia

def insert_on_bd(cotacao_diaria, cursor):
    # FIXME Replace para evitar a fadiga
    cursor.execute("INSERT OR IGNORE INTO Cotacoes VALUES\
                   (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
                   , cotacao_diaria)

def main():
    parser = argparse.ArgumentParser(description="Extrai informações do arquivo bovespa")
    parser.add_argument('--entrada', metavar='FILE', nargs='*', type=argparse.FileType('r'),
                        help="Arquivos de entrada")
    parser.add_argument('--bdname', metavar='BD', nargs='?', default=":memory:",
                        help="Nome do arquivo do banco de dados se nenhum nome for passado o\
                              banco não será persistido")
    parser.add_argument('--empresa', metavar='EMPRESA', nargs='+',
                        help="Codigo de negociação da empresa a ser avaliada, pode ser inserida\
                              mais de uma empresa",
                        required=True)
    parser.add_argument('--debug', action='store_true', help="Imprime operações com banco de dados")

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
                        dis_papel INT,
                        PRIMARY KEY (data, cod_bdi, cod_neg))''')

    for arquivo in parsed.entrada:
        # Só insere no banco se a empresa é objeto de avaliação
        for cotacao in filter(lambda cot: cot.cod_neg in parsed.empresa, parse_file(arquivo)):
            insert_on_bd(cotacao, cursor_bd)

    banco_dados.commit()

    # TODO Aqui vem a parte que importa

if __name__ == '__main__':
    main()
