import requests


def consultar(cnpj):
    print(cnpj)
    consulta = requests.get(f'https://www.receitaws.com.br/v1/cnpj/{cnpj}').json()
    print(consulta)
    if consulta['status'] == 'ERROR':
        return {"status": 400, "Erro": 'Cnpj não encontrado'}
    else:
        return {"status": 200, "nome_empresa": consulta['nome']}