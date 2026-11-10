
import requests

API_URL = "http://10.135.232.25:5000"


# FUNÇÃO PARA BUSCAR INFORMAÇÕES
def consultar_api(endpoint):
    resposta = requests.get(
        f"{API_URL}/{endpoint}",
        timeout=10
    )

    resposta.raise_for_status()
    return resposta.json()


# FUNÇÃO PARA CADASTRAR INFORMAÇÕES
def enviar_api(endpoint, dados):
    resposta = requests.post(
        f"{API_URL}/{endpoint}",
        json=dados,
        timeout=10
    )

    try:
        resultado = resposta.json()
    except ValueError:
        resultado = {}

    return resultado, resposta.status_code


# LOGIN
def login_usuario(email, senha):
    dados = {
        "email": email,
        "senha": senha
    }

    return enviar_api("login", dados)


# BUSCAS
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


def get_alertas():
    return consultar_api("todos_alertas")



def post_galpao(nome, descricao, status):
    dados = {
        "nome": nome,
        "descricao": descricao,
        "status": status
    }

    return enviar_api("api/cadastrar_galpoes", dados)


# EDITAR GALPAO
def put_galpao(id_galpao, status):

    dados = {
        "status": status
    }

    resposta = requests.put(
        f"{API_URL}/api/editar_galpao/{id_galpao}",
        json=dados,
        timeout=10
    )

    try:
        resultado = resposta.json()
    except ValueError:
        resultado = {}

    return resultado, resposta.status_code



def post_bloco(nome, id_galpao):
    dados = {
        "nome": nome,
        "id_galpao": id_galpao
    }

    return enviar_api("api/cadastrar_blocos", dados)


def post_setor(nome, id_insumo, id_bloco, capacidade):
    dados = {
        "nome": nome,
        "id_insumo": id_insumo,
        "id_bloco": id_bloco,
        "capacidade": capacidade
    }

    return enviar_api("api/cadastrar_setores", dados)


def post_insumo(nome, tipo, umidade_max, umidade_min,
                temperatura_max, temperatura_min,
                quantidade, unidade_medida):

    dados = {
        "nome": nome,
        "tipo": tipo,
        "umidade_max": umidade_max,
        "umidade_min": umidade_min,
        "temperatura_max": temperatura_max,
        "temperatura_min": temperatura_min,
        "quantidade": quantidade,
        "unidade_medida": unidade_medida
    }

    return enviar_api("api/cadastrar_insumos", dados)


def post_sensor(id_setor):
    dados = {
        "id_setor": id_setor
    }

    return enviar_api("api/cadastrar_sensores", dados)


def post_leitura(id_sensor, temperatura, umidade):
    dados = {
        "id_sensor": id_sensor,
        "temperatura": temperatura,
        "umidade": umidade
    }

    return enviar_api("api/cadastrar_leituras", dados)
