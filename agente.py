from collections import namedtuple, defaultdict
from functools import reduce, partial

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
    return map(lambda x: (x[0], x[1]),
               cursor.execute('''SELECT cod_neg, COUNT(*) FROM cotacoes GROUP BY cod_neg'''))

def get_last(cotacoes):
    '''Obtem o ultimo da empresa'''
    return list(cotacoes)[-1]

def abaixo_media(cotacoes):
    '''Retorna se a empresa está abaixo da sua média'''
    soma_todas_medias_diarias = reduce(lambda c1, c2: c1 + c2.preco_med, [0] + cotacoes)

    media_diaria = soma_todas_medias_diarias / len(cotacoes)

    return get_last(cotacoes).preco_med < media_diaria

def mais_cresce_que_cai(cotacoes):
    '''Retorna se a empresa mais cresce do que cai'''
    cotacoes = list(cotacoes)
    qnt_sobe = 0

    for i in range(1, len(cotacoes)):
        qnt_sobe += 1 if cotacoes[i] > cotacoes[i - 1] else 0

    return True if (qnt_sobe / len(cotacoes)) > 0.5 else False

def duracao_susto(cotacoes):
    '''Duração de um susto, se a diferenca entre os dias do maior valor
       e menor valor eh muito grande'''
    cotacoes = list(cotacoes)
    menor_valor = min(enumerate(cotacoes), key=lambda x: x[1].preco_min)
    maior_valor = max(enumerate(cotacoes), key=lambda x: x[1].preco_max)

    metade_dias = len(cotacoes)/2

    dif_menor_maior = abs(menor_valor[0] - maior_valor[0])

    return dif_menor_maior < metade_dias

def inferencia(empresa, cursor, cpt):
    cotacoes = list(get_cotacoes_empresa(empresa, cursor))

    dur_susto = duracao_susto(cotacoes)
    mais_s_d = mais_cresce_que_cai(cotacoes)
    a_media = abaixo_media(cotacoes)

    return cpt[0][(dur_susto, mais_s_d, a_media)][1]

def cresceu(cotacoes):
    cotacoes = list(cotacoes)

    return cotacoes[0] > cotacoes[-1]

def generate_agente(cursor):
    empresas = list(get_lista_empresas(cursor))

    zero_zero = partial(list, [0, 0, 0])

    cpt_a = defaultdict(zero_zero)
    cpt_b = defaultdict(zero_zero)
    cpt_c = defaultdict(zero_zero)

    cpt_x = defaultdict(zero_zero)

    for empresa in empresas:
        if empresa[1] > 200:
            cotacoes = list(get_cotacoes_empresa(empresa[0], cursor))

            dur_susto = duracao_susto(cotacoes)
            mais_s_d = mais_cresce_que_cai(cotacoes)
            a_media = abaixo_media(cotacoes)

            cpt_a[dur_susto][0] += 1
            cpt_a[dur_susto][1] += dur_susto + 0.001

            cpt_b[mais_s_d][0] += 1
            cpt_b[mais_s_d][1] += mais_s_d + 0.001

            cpt_c[a_media][0] += 1
            cpt_c[a_media][1] += a_media + 0.001

            cpt_x[(dur_susto, mais_s_d, a_media)][0] += 1
            cpt_x[(dur_susto, mais_s_d, a_media)][1] += cresceu(cotacoes) + 0.001

    for key in cpt_x.keys():
        cpt_x[key][2] = cpt_x[key][1] / cpt_x[key][0]

    for key in cpt_a.keys():
        cpt_a[key][2] = cpt_a[key][1] / cpt_a[key][0]

    for key in cpt_b.keys():
        cpt_b[key][2] = cpt_b[key][1] / cpt_b[key][0]

    for key in cpt_c.keys():
        cpt_c[key][2] = cpt_c[key][1] / cpt_c[key][0]

    return [cpt_x, cpt_a, cpt_b, cpt_c]
