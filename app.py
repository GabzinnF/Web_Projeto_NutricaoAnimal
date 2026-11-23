from flask import Flask, render_template, url_for, flash, request, redirect, session
from functools import wraps
import requests
from routes import (login_usuario, get_galpoes, get_bloco, get_setor, get_insumo, get_sensor, get_leitura, get_alertas, post_galpao, put_galpao, post_bloco, post_setor, post_insumo, post_sensor, cadastrar_usuario)

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


def verificar_cadastro(resultado):
    dados, status = resultado
    if status in [200, 201]:
        flash(dados.get("msg", "Cadastro realizado!"), "success")
        return True
    flash(dados.get("msg", "Não foi possível realizar o cadastro."), "danger")
    return False


def dados_vazios():
    return {
        "galpoes": [],
        "blocos": [],
        "setores": [],
        "insumos": [],
        "sensores": [],
        "leituras": [],
        "alertas": []
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

    email = request.form.get("form_email", "").strip()
    senha = request.form.get("form_senha", "")

    if not email or not senha:
        flash("Preencha todos os campos.", "danger")
        return render_template("login.html")

    try:
        dados, status = login_usuario(email, senha)

        if status == 200:
            session["usuario_logado"] = dados.get("usuario", {})
            session["token"] = dados.get("access_token")

            flash("Login realizado!", "success")
            return redirect(url_for("dashboard"))

        flash(dados.get("msg", "E-mail ou senha incorretos."), "danger")

    except requests.exceptions.RequestException:
        flash("Erro ao conectar com a API.", "danger")

    return render_template("login.html")


@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if request.method == "GET":
        return render_template("cadastro.html")

    dados = {
        "nome": request.form.get("form_nome", "").strip(),
        "cpf": request.form.get("form_cpf", "").strip(),
        "email": request.form.get("form_email", "").strip(),
        "senha": request.form.get("form_senha", "")
    }

    try:
        resultado = cadastrar_usuario(dados)

        if verificar_cadastro(resultado):
            return redirect(url_for("login"))

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
        dados = carregar_dados()

        return render_template("dashboard.html", usuario=session["usuario_logado"], total_galpoes=len(dados["galpoes"]), total_blocos=len(dados["blocos"]), total_setores=len(dados["setores"]), total_insumos=len(dados["insumos"]), total_sensores=len(dados["sensores"]), total_alertas=len(dados["alertas"]), total_leituras=len(dados["leituras"]), **dados)

    except requests.exceptions.RequestException:
        flash("Não foi possível atualizar os dados.", "danger")
        dados = dados_vazios()

        return render_template(
            "dashboard.html",
            usuario=session["usuario_logado"],
            total_galpoes=0,
            total_blocos=0,
            total_setores=0,
            total_insumos=0,
            total_sensores=0,
            total_alertas=0,
            total_leituras=0,
            **dados
        )


@app.route("/galpoes", methods=["GET", "POST"])
@login_required
def galpoes():
    try:
        if request.method == "POST":

            id_editar = request.form.get("form_id_galpao_editar")

            if id_editar:
                resultado = put_galpao(
                    id_editar,
                    request.form.get("form_status")
                )
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

        total_blocos = len(dados["blocos"])

        return render_template(
            "galpoes.html",
            total_blocos=total_blocos,
            **dados
        )

    except requests.exceptions.RequestException:
        flash("Erro ao carregar galpões.", "danger")

        return render_template(
            "galpoes.html",
            total_blocos=0,
            **dados_vazios()
        )


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

        return render_template("blocos.html", **carregar_dados())

    except requests.exceptions.RequestException:
        flash("Erro ao carregar blocos.", "danger")
        return render_template("blocos.html", **dados_vazios())


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

        return render_template("setores.html", **carregar_dados())

    except requests.exceptions.RequestException:
        flash("Erro ao carregar setores.", "danger")
        return render_template("setores.html", **dados_vazios())


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

        return render_template("insumos.html", **carregar_dados())

    except requests.exceptions.RequestException:
        flash("Erro ao carregar insumos.", "danger")
        return render_template("insumos.html", **dados_vazios())


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

        setores_por_id = {
            str(s["id_setor"]): s for s in dados["setores"]
        }

        for sensor in dados["sensores"]:
            setor = setores_por_id.get(str(sensor.get("id_setor")))
            quantidade = float(
                (setor or {}).get("quantidade_atual") or 0
            )

            sensor["status_sensor"] = (
                "Ativo" if quantidade > 0 else "Inativo"
            )

        return render_template("sensores.html", **dados)

    except requests.exceptions.RequestException:
        flash("Erro ao carregar sensores.", "danger")
        return render_template("sensores.html", **dados_vazios())


@app.route("/leituras")
@login_required
def leituras():
    try:
        return render_template(
            "leituras.html",
            **carregar_dados()
        )

    except requests.exceptions.RequestException:
        flash("Erro ao carregar leituras.", "danger")
        return render_template("leituras.html", **dados_vazios())


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
            total_ativos=len(ativos),
            total_resolvidos=len(resolvidos),
            **dados
        )

    except requests.exceptions.RequestException:
        flash("Erro ao carregar alertas.", "danger")

        return render_template(
            "alertas.html",
            **dados_vazios(),
            total_ativos=0,
            total_resolvidos=0
        )


if __name__ == "__main__":
    app.run(debug=True, port=5007)
