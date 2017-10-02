import argparse
from collections import namedtuple
import datetime
import json

def _json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def _convert_to_date(date_string):
    return datetime.datetime.strptime(date_string, "%Y%m%d")

CotacaoDia = namedtuple('CotacaoDia',
                        [
                            'data',
                            'cod_bdi',
                            'cod_neg',
                            'tipo_mer',
                            'nome_res',
                            'esp_papel',
                            'prazo',
                            'moeda',
                            'preco_abertura',
                            'preco_max',
                            'preco_min',
                            'preco_med',
                            'preco_ultimo',
                            'preco_melhor_compra',
                            'preco_melhor_venda',
                            'total_negociado',
                            'quantidade_total',
                            'volume_total',
                            'preco_exercicio',
                            'indicador_correcao',
                            'data_venc',
                            'fator_cotacao',
                            'preco_pontos',
                            'cod_isin',
                            'dis_papel'
                            ])

def parse_line(linha):
    data = _convert_to_date(linha[2:10])
    cod_bdi = linha[10:12].strip()
    cod_neg = linha[12:24].strip()
    tipo_mer = int(linha[24:27])
    nome_res = linha[27:39].strip()
    esp_papel = linha[39:49].strip()
    prazo = int(linha[49:52]) if linha[49:52].strip() else float('inf')
    moeda = linha[52:56].strip()
    preco_abertura = float(linha[56:69])
    preco_max = float(linha[69:82])
    preco_min = float(linha[82:95])
    preco_med = float(linha[95:108])
    preco_ultimo = float(linha[108:121])
    preco_melhor_compra = float(linha[121:134])
    preco_melhor_venda = float(linha[134:147])
    total_negociado = float(linha[147:152])
    quantidade_total = float(linha[152:170])
    volume_total = float(linha[170:188])
    preco_exercicio = float(linha[188:201])
    indicador_correcao = linha[201:202]
    data_venc = _convert_to_date(linha[202:210])
    fator_cotacao = int(linha[210:217])
    preco_pontos = float(linha[217:230])
    cod_isin = linha[230:242].strip()
    dis_papel = int(linha[243:245])

    return CotacaoDia(data,
                      cod_bdi,
                      cod_neg,
                      tipo_mer,
                      nome_res,
                      esp_papel,
                      prazo,
                      moeda,
                      preco_abertura,
                      preco_max,
                      preco_min,
                      preco_med,
                      preco_ultimo,
                      preco_melhor_compra,
                      preco_melhor_venda,
                      total_negociado,
                      quantidade_total,
                      volume_total,
                      preco_exercicio,
                      indicador_correcao,
                      data_venc,
                      fator_cotacao,
                      preco_pontos,
                      cod_isin,
                      dis_papel)

def parse_header(linha):
    ''' Retorna o ano do arquivo

    Parameters
    ----------
    linha : str
        string da linha de entrada

    Returns
    data :datetime
        data da produção do arquivo
    '''

    data = _convert_to_date(linha[23:31])

    return data

def parse_file(arquivo_entrada):
    for line in arquivo_entrada:
        if line[0:2] == "01":
            yield parse_line(line)

def main():
    parser = argparse.ArgumentParser(description="Extrai informações do arquivo bovespa")
    parser.add_argument('entrada', metavar='FILE', nargs='+', type=argparse.FileType('r'),
                        help="Arquivos de entrada")

    parsed = parser.parse_args()

    for arquivo in parsed.entrada:
        print(json.dumps(parse_file(arquivo), indent=4, sort_keys=True, default=_json_serial))

if __name__ == '__main__':
    main()
