
import requests

API_URL = "http://10.135.232.33:5000"


def consultar_api(endpoint):
    resposta = requests.get(f"{API_URL}/{endpoint}", timeout=10)
    resposta.raise_for_status()
    return resposta.json()


def enviar_api(endpoint, dados, metodo="POST"):
    resposta = requests.request(
        metodo, f"{API_URL}/{endpoint}", json=dados, timeout=10
    )

    try:
        resultado = resposta.json()
    except ValueError:
        resultado = {}

    return resultado, resposta.status_code


def login_usuario(email, senha):
    return enviar_api("api/login", {
        "email": email,
        "senha": senha
    })


def cadastrar_usuario(dados):
    return enviar_api("cadastro_usuario", dados)


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


def get_alertas():
    return consultar_api("todos_alertas")


def post_galpao(nome, descricao, status):
    return enviar_api("api/cadastrar_galpoes", {
        "nome": nome,
        "descricao": descricao,
        "status": status
    })


def put_galpao(id_galpao, status):
    return enviar_api(
        f"api/editar_galpao/{id_galpao}",
        {"status": status},
        "PUT"
    )


def post_bloco(nome, id_galpao):
    return enviar_api("api/cadastrar_blocos", {
        "nome": nome,
        "id_galpao": id_galpao
    })


def post_setor(nome, id_insumo, id_bloco, capacidade, quantidade_atual):
    return enviar_api("api/cadastrar_setores", {
        "nome": nome,
        "id_insumo": id_insumo,
        "id_bloco": id_bloco,
        "capacidade": capacidade,
        "quantidade_atual": quantidade_atual
    })


def post_insumo(nome, tipo, umidade_max, umidade_min, temperatura_max,
                temperatura_min, quantidade, unidade_medida):

    return enviar_api("api/cadastrar_insumos", {
        "nome": nome,
        "tipo": tipo,
        "umidade_max": umidade_max,
        "umidade_min": umidade_min,
        "temperatura_max": temperatura_max,
        "temperatura_min": temperatura_min,
        "quantidade": quantidade,
        "unidade_medida": unidade_medida
    })


def post_sensor(id_setor):
    return enviar_api("api/cadastrar_sensores", {
        "id_setor": id_setor
    })
