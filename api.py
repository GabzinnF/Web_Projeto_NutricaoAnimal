
import requests

API_URL = "http://10.135.232.33:5000"


def consultar_api(endpoint):
    resposta = requests.get(f"{API_URL}/{endpoint}", timeout=10)
    resposta.raise_for_status()
    return resposta.json()


def login_usuario(email, senha):
    dados = {"email": email, "senha": senha}

    resposta = requests.post(f"{API_URL}/login", json=dados, timeout=10)

    return resposta.json(), resposta.status_code


def get_galpoes():
    return consultar_api("todos_galpoes")


def get_bloco():
    return consultar_api("todos_blocos")


def get_setor():
    return consultar_api("todos_setores")


def get_insumo():
    return consultar_api("todos_insumos")


def get_sensor():
    return consultar_api("todos_sensores")


def get_leitura():
    return consultar_api("todas_leituras")


def get_usuario():
    return consultar_api("todos_usuarios/")
