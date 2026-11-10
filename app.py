
from flask import Flask, render_template, url_for, flash, request, redirect, session
from functools import wraps
import requests

from routes import (
    login_usuario,
    get_galpoes,
    get_bloco,
    get_setor,
    get_insumo,
    get_sensor,
    get_leitura,
    get_usuario,
    get_alertas,
    post_galpao,
    post_bloco,
    post_setor,
    post_insumo,
    post_sensor,
    post_leitura
)


app = Flask(__name__)

app.config["SECRET_KEY"] = "leite_gato"


# VERIFICA SE O USUARIO ESTA LOGADO
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "usuario_logado" not in session:
            flash("Faça login para acessar essa página.", "warning")
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated_function


# FUNÇÃO PARA PEGAR LISTAS DA API
def pegar_lista(dados, chave):

    if isinstance(dados, dict):
        return dados.get(chave, [])

    if isinstance(dados, list):
        return dados

    return []


# FUNÇÃO PARA MOSTRAR RESULTADO DOS CADASTROS
def verificar_cadastro(resultado):

    dados, status = resultado

    if status in [200, 201]:
        flash(dados.get("msg", "Cadastro realizado com sucesso!"), "success")
        return True

    flash(dados.get("msg", "Erro ao realizar cadastro."), "danger")
    return False


# HOME
@app.route('/')
def home():

    if "usuario_logado" in session:
        return redirect(url_for("dashboard"))

    return render_template('home.html')


# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == "GET":
        return render_template('login.html')

    email = request.form.get("form_email")
    senha = request.form.get("form_senha")

    if not email or not senha:
        flash("Preencha o e-mail e a senha.", "danger")
        return render_template("login.html")

    try:
        dados, status = login_usuario(email, senha)

        if status == 200:

            usuario = dados.get("usuario")

            if usuario is None:
                usuario = dados.get("Usuario", dados)

            session["usuario_logado"] = usuario
            session["token"] = dados.get("access_token")

            flash("Login realizado com sucesso!", "success")

            return redirect(url_for("dashboard"))

        flash(dados.get("msg", "E-mail ou senha incorretos."), "danger")

    except requests.exceptions.RequestException as erro:
        print("ERRO DE CONEXÃO:", erro)
        flash("Erro ao conectar com a API.", "danger")

    except ValueError:
        flash("Resposta inválida da API.", "danger")

    return render_template("login.html")


# CADASTRO DE USUARIO
@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():

    if request.method == "GET":
        return render_template('cadastro.html')

    dados = {
        "nome": request.form.get("form_nome"),
        "cpf": request.form.get("form_cpf"),
        "email": request.form.get("form_email"),
        "senha": request.form.get("form_senha")
    }

    try:
        resposta = requests.post(
            "http://10.135.232.25:5000/cadastro_usuario",
            json=dados,
            timeout=10
        )

        if resposta.status_code in [200, 201]:
            flash("Cadastro realizado com sucesso!", "success")
            return redirect(url_for("login"))

        flash("Erro ao cadastrar usuário.", "danger")

    except requests.exceptions.RequestException:
        flash("Não foi possível conectar com a API.", "danger")

    return render_template("cadastro.html")


# LOGOUT
@app.route('/logout')
def logout():

    session.clear()

    flash("Logout realizado com sucesso!", "success")

    return redirect(url_for("home"))


# DASHBOARD
@app.route('/dashboard')
@login_required
def dashboard():

    return render_template(
        'dashboard.html',
        usuario=session["usuario_logado"]
    )


# GALPOES
@app.route('/galpoes', methods=['GET', 'POST'])
@login_required
def galpoes():

    try:

        if request.method == "POST":

            resultado = post_galpao(
                request.form.get("form_nome"),
                request.form.get("form_descricao")
            )

            if verificar_cadastro(resultado):
                return redirect(url_for("galpoes"))

        # Busca os galpões e os blocos na API
        dados_galpoes = get_galpoes()
        dados_blocos = get_bloco()

        lista_galpoes = pegar_lista(dados_galpoes, "Galpoes")
        lista_blocos = pegar_lista(dados_blocos, "Blocos")

        # Conta quantos blocos pertencem a cada galpão
        for p in lista_galpoes:

            quantidade = 0

            for b in lista_blocos:

                if str(b.get("id_galpao")) == str(p.get("id")):
                    quantidade += 1

            p["quantidade_blocos"] = quantidade

        # Calcula o total de blocos
        total_blocos = len(lista_blocos)

        return render_template(
            'galpoes.html',
            galpoes=lista_galpoes,
            total_blocos=total_blocos
        )

    except requests.exceptions.RequestException as erro:

        print("ERRO:", erro)

        flash("Erro ao buscar galpões ou blocos na API.", "danger")

        return render_template(
            'galpoes.html',
            galpoes=[],
            total_blocos=0
        )


# BLOCOS
@app.route('/blocos', methods=['GET', 'POST'])
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

        galpoes = get_galpoes()
        blocos = get_bloco()

        return render_template(
            'blocos.html',
            galpoes=pegar_lista(galpoes, "Galpoes"),
            blocos=pegar_lista(blocos, "Blocos")
        )

    except requests.exceptions.RequestException as erro:
        print("ERRO:", erro)
        flash("Erro ao buscar blocos.", "danger")

        return render_template(
            'blocos.html',
            galpoes=[],
            blocos=[]
        )


# INSUMOS
@app.route('/insumos', methods=['GET', 'POST'])
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

        dados = get_insumo()

        return render_template(
            'insumos.html',
            insumos=pegar_lista(dados, "Insumos")
        )

    except requests.exceptions.RequestException as erro:
        print("ERRO:", erro)
        flash("Erro ao buscar insumos.", "danger")

        return render_template('insumos.html', insumos=[])


# SENSORES
@app.route('/sensores', methods=['GET', 'POST'])
@login_required
def sensores():

    try:

        if request.method == "POST":

            resultado = post_sensor(
                request.form.get("form_id_setor")
            )

            if verificar_cadastro(resultado):
                return redirect(url_for("sensores"))

        setores = get_setor()
        sensores = get_sensor()

        return render_template(
            'sensores.html',
            setores=pegar_lista(setores, "Setores"),
            sensores=pegar_lista(sensores, "Sensores")
        )

    except requests.exceptions.RequestException as erro:
        print("ERRO:", erro)
        flash("Erro ao buscar sensores.", "danger")

        return render_template(
            'sensores.html',
            setores=[],
            sensores=[]
        )


# SETORES
@app.route('/setores', methods=['GET', 'POST'])
@login_required
def setores():

    try:

        if request.method == "POST":

            resultado = post_setor(
                request.form.get("form_nome"),
                request.form.get("form_id_insumo"),
                request.form.get("form_id_bloco"),
                request.form.get("form_capacidade")
            )

            if verificar_cadastro(resultado):
                return redirect(url_for("setores"))

        insumos = get_insumo()
        blocos = get_bloco()
        setores = get_setor()

        return render_template(
            'setores.html',
            insumos=pegar_lista(insumos, "Insumos"),
            blocos=pegar_lista(blocos, "Blocos"),
            setores=pegar_lista(setores, "Setores")
        )

    except requests.exceptions.RequestException as erro:
        print("ERRO:", erro)
        flash("Erro ao buscar setores.", "danger")

        return render_template(
            'setores.html',
            insumos=[],
            blocos=[],
            setores=[]
        )


# ALERTAS
@app.route('/alertas')
@login_required
def alertas():

    try:
        dados = get_alertas()

        return render_template(
            'alertas.html',
            alertas=pegar_lista(dados, "Alerta")
        )

    except requests.exceptions.RequestException as erro:
        print("ERRO:", erro)
        flash("Erro ao buscar alertas.", "danger")

        return render_template('alertas.html', alertas=[])


# LEITURAS
@app.route('/leituras')
@login_required
def leituras():

    try:
        dados = get_leitura()

        return render_template(
            'leituras.html',
            leituras=pegar_lista(dados, "Leitura")
        )

    except requests.exceptions.RequestException as erro:
        print("ERRO:", erro)
        flash("Erro ao buscar leituras.", "danger")

        return render_template('leituras.html', leituras=[])



if __name__ == '__main__':
    app.run(debug=True, port=5007)
