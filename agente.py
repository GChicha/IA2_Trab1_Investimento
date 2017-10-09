from collections import namedtuple
from functools import reduce

from file_reader import CotacaoDia

Variavel = namedtuple("Variavel", "primeira segunda terceira quarta quinta sexta")

def bd_to_cot(raw_cotacao):
    '''Converte de tupla do bd para namedtuple'''
    return CotacaoDia(*raw_cotacao)

def get_cotacoes_empresa(empresa, cursor):
    return map(bd_to_cot,
               cursor.execute('''SELECT * FROM cotacoes WHERE cod_neg LIKE ? ORDER BY data''',
                              (empresa,)))

def get_lista_empresas(cursor):
    '''Obtem a lista dos códigos de negociação'''
    return map(lambda x: x[0], cursor.execute('''SELECT cod_neg FROM cotacoes GROUP BY cod_neg'''))

def get_last(empresa, cursor):
    '''Obtem o ultimo da empresa'''
    return bd_to_cot(cursor.execute('''SELECT *
                                         FROM cotacoes
                                         WHERE cod_neg LIKE ?
                                         ORDER BY data ASC
                                         LIMIT 1''',
                                    empresa).fetchone()[0])


def abaixo_media(empresa, cursor):
    '''Retorna se a empresa está abaixo da sua média'''
    cotacoes = list(get_cotacoes_empresa(empresa, cursor))

    soma_todas_medias_diarias = reduce(lambda c1, c2: c1 + c2.preco_med, [0] + cotacoes)

    media_diaria = soma_todas_medias_diarias / len(cotacoes)

    return get_last(empresa, cursor).preco_med < media_diaria

def mais_cresce_que_cai(empresa, cursor):
    '''Retorna se a empresa mais cresce do que cai'''
    cotacoes = list(get_cotacoes_empresa(empresa, cursor))

    qnt_sobe = 0

    for i in range(1, len(cotacoes)):
        qnt_sobe += 1 if cotacoes[i] > cotacoes[i - 1] else 0

    return True if (qnt_sobe / len(cotacoes)) > 0.5 else False

def duracao_susto(cotacoes):
    '''Duração de um susto, se a diferenca entre os dias do maior valor
       e menor valor eh muito grande'''
    menor_valor = min(enumerate(cotacoes), key=lambda x: x[1].preco_min)
    maior_valor = max(enumerate(cotacoes), key=lambda x: x[1].preco_max)

    metade_dias = len(cotacoes)/2

    dif_menor_maior = abs(menor_valor[0] - maior_valor[0])

    return dif_menor_maior < metade_dias

def generate_agente(cursor):
    empresas = get_lista_empresas(cursor)

    for empresa in empresas:
        cotacoes = list(get_cotacoes_empresa(empresa, cursor))
