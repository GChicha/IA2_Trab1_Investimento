from file_reader import CotacaoDia

def get_cotacoes_2anos_empresa(empresa, cursor):
    return cursor.execute('''SELECT * FROM cotacoes WHERE cod_neg LIKE ? ORDER BY data''',
                          (empresa,))

def preco_baixo(cotacoes):
    '''Com base no extremos define se está em baixa'''
    menor_valor = min(cotacoes, key=lambda x: x.preco_min)
    maior_valor = max(cotacoes, key=lambda x: x.preco_max)

    return menor_valor.preco_min / maior_valor.preco_max

def duracao_susto(cotacoes):
    '''Duração de um susto, em dias'''
    menor_valor = min(enumerate(cotacoes), key=lambda x: x[1].preco_min)
    maior_valor = max(enumerate(cotacoes), key=lambda x: x[1].preco_max)

    return abs(menor_valor[0] - maior_valor[0])/len(cotacoes)

def media_prejuizo(cotacoes):
    '''Calcula a media dos prejuizo'''
    prejuizo_acumulado = 0
    dias_prejuizo = 0

    for i in range(1, len(cotacoes)):
        if cotacoes[i].preco_med - cotacoes[i - 1].preco_med < 0:
            prejuizo_acumulado += cotacoes[i].preco_med / cotacoes[i - 1].preco_med
            dias_prejuizo += 1

    return prejuizo_acumulado / dias_prejuizo

def dias_crescimento_ponderado(cotacoes):
    '''Dias com crecimento, ponderado considerando que crescimento mais recentes são melhores'''
    ponderador = 1
    dias_crescimento = 0

    acumulador_ponderador = 0

    for i in range(1, len(cotacoes)):
        if cotacoes[i].preco_med - cotacoes[i - 1].preco_med > 0:
            dias_crescimento += ponderador

            acumulador_ponderador += ponderador

            dias_crescimento /= acumulador_ponderador
        ponderador *= 2

    return dias_crescimento

def agente(empresas, cursor):
    for empresa in empresas:
        cotacoes = list(map(lambda cotacao: CotacaoDia(*cotacao), get_cotacoes_2anos_empresa(empresa, cursor)))

        print(str(empresa) + ": " + str(dias_crescimento_ponderado(cotacoes) * preco_baixo(cotacoes) * media_prejuizo(cotacoes) * duracao_susto(cotacoes)))
