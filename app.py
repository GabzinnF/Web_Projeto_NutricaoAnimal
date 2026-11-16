
from flask import Flask, render_template, url_for, flash, request, redirect, session
from functools import wraps
import requests

from routes import (login_usuario, get_galpoes, get_bloco, get_setor, get_insumo, get_sensor, get_leitura, get_alertas, post_galpao, put_galpao, post_bloco, post_setor, post_insumo, post_sensor)

app = Flask(__name__)
app.config["SECRET_KEY"] = "leite_gato"


def login_required(f):
    @wraps(f)
    def verificar_login(*args, **kwargs):
        if "usuario_logado" not in session:
            flash("Faça login para acessar.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return verificar_login


def pegar_lista(dados, chave):
    if isinstance(dados, dict):
        return dados.get(chave, [])

    if isinstance(dados, list):
        return dados

    return []


def verificar_cadastro(resultado):
    dados, status = resultado

    if status in [200, 201]:
        flash(dados.get("msg", "Cadastro realizado!"), "success")
        return True

    flash(dados.get("msg", "Erro no cadastro."), "danger")
    return False


def carregar_dados():
    return {
        "galpoes": pegar_lista(get_galpoes(), "Galpoes"),
        "blocos": pegar_lista(get_bloco(), "Blocos"),
        "setores": pegar_lista(get_setor(), "Setores"),
        "insumos": pegar_lista(get_insumo(), "Insumos"),
        "sensores": pegar_lista(get_sensor(), "Sensores"),
        "leituras": pegar_lista(get_leitura(), "Leitura"),
        "alertas": pegar_lista(get_alertas(), "Alerta")
    }


@app.route("/")
def home():
    if "usuario_logado" in session:
        return redirect(url_for("dashboard"))
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    email = request.form.get("form_email")
    senha = request.form.get("form_senha")
    if not email or not senha:
        flash("Preencha todos os campos.", "danger")
        return render_template("login.html")
    try:
        dados, status = login_usuario(email, senha)
        if status == 200:
            session["usuario_logado"] = dados.get("usuario")
            session["token"] = dados.get("access_token")
            flash("Login realizado!", "success")
            return redirect(url_for("dashboard"))
        flash(dados.get("msg", "Login inválido."), "danger")
    except requests.exceptions.RequestException:
        flash("Erro ao conectar com a API.", "danger")
    return render_template("login.html")


@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if request.method == "GET":
        return render_template("cadastro.html")
    dados = {
        "nome": request.form.get("form_nome"),
        "cpf": request.form.get("form_cpf"),
        "email": request.form.get("form_email"),
        "senha": request.form.get("form_senha")
    }
    try:
        resposta = requests.post("http://10.135.232.34:5000/cadastro_usuario", json=dados, timeout=10)

        resultado = resposta.json()

        if resposta.status_code == 201:
            flash("Cadastro realizado!", "success")
            return redirect(url_for("login"))

        flash(resultado.get("msg", "Erro no cadastro."), "danger")

    except requests.exceptions.RequestException:
        flash("Erro ao conectar com a API.", "danger")

    return render_template("cadastro.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))



@app.route("/dashboard")
@login_required
def dashboard():
    try:
        galpoes = pegar_lista(get_galpoes(), "Galpoes")
        blocos = pegar_lista(get_bloco(), "Blocos")
        insumos = pegar_lista(get_insumo(), "Insumos")
        sensores = pegar_lista(get_sensor(), "Sensores")
        alertas = pegar_lista(get_alertas(), "Alerta")
        leituras = pegar_lista(get_leitura(), "Leitura")

        return render_template(
            "dashboard.html",
            usuario=session["usuario_logado"],
            total_galpoes=len(galpoes),
            total_blocos=len(blocos),
            total_insumos=len(insumos),
            total_sensores=len(sensores),
            total_alertas=len(alertas),
            total_leituras=len(leituras),
            leituras=leituras,   # <-- FALTAVA ISSO
            alertas=alertas      # <-- E ISSO TAMBÉM É ÚTIL
        )

    except requests.exceptions.RequestException as erro:
        print("Erro no dashboard:", erro)
        flash("Não foi possível atualizar os dados.", "danger")

        return render_template(
            "dashboard.html",
            usuario=session["usuario_logado"],
            total_galpoes=0,
            total_blocos=0,
            total_insumos=0,
            total_sensores=0,
            total_alertas=0,
            total_leituras=0,
            leituras=[],   # <-- GARANTE QUE O TEMPLATE NÃO QUEBRE
            alertas=[]
        )


@app.route("/galpoes", methods=["GET", "POST"])
@login_required
def galpoes():
    try:
        if request.method == "POST":
            id_editar = request.form.get("form_id_galpao_editar")
            if id_editar:
                resultado = put_galpao(id_editar, request.form.get("form_status"))
            else:
                resultado = post_galpao(
                    request.form.get("form_nome"),
                    request.form.get("form_descricao"),
                    request.form.get("form_status")
                )

            if verificar_cadastro(resultado):
                return redirect(url_for("galpoes"))

        dados = carregar_dados()

        for galpao in dados["galpoes"]:
            galpao["quantidade_blocos"] = sum(
                1 for bloco in dados["blocos"]
                if str(bloco.get("id_galpao")) == str(galpao.get("id"))
            )

        return render_template("galpoes.html", **dados)

    except requests.exceptions.RequestException:
        flash("Erro ao carregar galpões.", "danger")
        return render_template("galpoes.html", galpoes=[], blocos=[], setores=[], insumos=[], sensores=[], leituras=[],alertas=[])


@app.route("/blocos", methods=["GET", "POST"])
@login_required
def blocos():
    try:
        if request.method == "POST":

            resultado = post_bloco(
                request.form.get("form_nome"),
                request.form.get("form_id_galpao")
            )

            if verificar_cadastro(resultado):
                return redirect(url_for("blocos"))

        dados = carregar_dados()

        return render_template(
            "blocos.html",
            **dados
        )

    except requests.exceptions.RequestException:
        flash("Erro ao carregar blocos.", "danger")
        return render_template(
            "blocos.html",
            galpoes=[],
            blocos=[],
            setores=[],
            insumos=[],
            sensores=[],
            leituras=[],
            alertas=[]
        )


@app.route("/insumos", methods=["GET", "POST"])
@login_required
def insumos():

    try:
        if request.method == "POST":

            resultado = post_insumo(
                request.form.get("form_nome"),
                request.form.get("form_tipo"),
                request.form.get("form_umidade_max"),
                request.form.get("form_umidade_min"),
                request.form.get("form_temperatura_max"),
                request.form.get("form_temperatura_min"),
                request.form.get("form_quantidade"),
                request.form.get("form_unidade_medida")
            )

            if verificar_cadastro(resultado):
                return redirect(url_for("insumos"))

        dados = carregar_dados()

        return render_template(
            "insumos.html",
            **dados
        )

    except requests.exceptions.RequestException:
        flash("Erro ao carregar insumos.", "danger")
        return render_template(
            "insumos.html",
            galpoes=[],
            blocos=[],
            setores=[],
            insumos=[],
            sensores=[],
            leituras=[],
            alertas=[]
        )


@app.route("/setores", methods=["GET", "POST"])
@login_required
def setores():

    try:
        if request.method == "POST":

            resultado = post_setor(
                request.form.get("form_nome"),
                request.form.get("form_id_insumo"),
                request.form.get("form_id_bloco"),
                request.form.get("form_capacidade"),
                request.form.get("form_quantidade_atual")
            )

            if verificar_cadastro(resultado):
                return redirect(url_for("setores"))

        dados = carregar_dados()

        return render_template(
            "setores.html",
            **dados
        )

    except requests.exceptions.RequestException:
        flash("Erro ao carregar setores.", "danger")
        return render_template(
            "setores.html",
            galpoes=[],
            blocos=[],
            setores=[],
            insumos=[],
            sensores=[],
            leituras=[],
            alertas=[]
        )


@app.route("/sensores", methods=["GET", "POST"])
@login_required
def sensores():

    try:
        if request.method == "POST":

            resultado = post_sensor(
                request.form.get("form_id_setor")
            )

            if verificar_cadastro(resultado):
                return redirect(url_for("sensores"))

        dados = carregar_dados()

        return render_template(
            "sensores.html",
            **dados
        )

    except requests.exceptions.RequestException:
        flash("Erro ao carregar sensores.", "danger")
        return render_template(
            "sensores.html",
            galpoes=[],
            blocos=[],
            setores=[],
            insumos=[],
            sensores=[],
            leituras=[],
            alertas=[]
        )


@app.route("/leituras")
@login_required
def leituras():

    try:
        dados = carregar_dados()

        return render_template(
            "leituras.html",
            **dados
        )

    except requests.exceptions.RequestException:
        flash("Erro ao carregar leituras.", "danger")
        return render_template("leituras.html", leituras=[])


@app.route("/alertas")
@login_required
def alertas():

    try:
        dados = carregar_dados()

        ativos = [
            a for a in dados["alertas"]
            if a.get("status_") != "RESOLVIDO"
        ]

        resolvidos = [
            a for a in dados["alertas"]
            if a.get("status_") == "RESOLVIDO"
        ]

        return render_template(
            "alertas.html",
            **dados,
            total_ativos=len(ativos),
            total_resolvidos=len(resolvidos)
        )

    except requests.exceptions.RequestException:
        flash("Erro ao carregar alertas.", "danger")
        return render_template(
            "alertas.html",
            alertas=[],
            total_ativos=0,
            total_resolvidos=0
        )


if __name__ == "__main__":
    app.run(debug=True, port=5007)
