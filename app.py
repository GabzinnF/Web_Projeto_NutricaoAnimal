import datetime

from flask import Flask, render_template, url_for, flash, request, redirect, session
from sqlalchemy.exc import SQLAlchemyError
import requests
from sqlalchemy import select, and_, func
from flask_login import LoginManager, login_required, logout_user, current_user, login_user, UserMixin

app = Flask(__name__)
app.config["SECRET_KEY"] = "leite_gato"

api_url = "http://10.135.232.19:5000"

DESVIAR_PROXY = {"http" : None, "https" : None}
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Para visualizar essa pagina faça o login'

class UserSession(UserMixin):
    def __init__(self, id, nome=None):
        self.id = id
        self.nome = nome

@login_manager.user_loader
def load_user(user_id):
    user_name = session.get('user_name')
    return UserSession(id=user_id, nome=user_name)
@app.route('/')
def home():
    if "usuario_logado" in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # return redirect(url_for('dashboard'))
        return render_template('dashboard.html')
    if request.method == "POST":
        credenciais = {
            "email" : request.form.get("form_email"),
            "senha" : request.form.get("form_senha")
        }
        try:
            resposta = requests.post(f"{api_url}/login", json=credenciais, timeout=5, proxies=DESVIAR_PROXY)
            if resposta.status_code == 200:
                dados_resposta = resposta.json()
                user_id = dados_resposta.get("user_id")
                user_name = dados_resposta.get("user_name")

                session['user_name'] = user_name
                session.modified = True

                user = UserSession(id=user_id, nome=user_name)
                login_user(user)

                flash('Login com sucesso', 'success')
                return redirect(url_for('dashboard'))
            else:
                dados_erro = resposta.json()
                erro = dados_erro.get('error') or dados_erro.get('erro') or 'Credenciais inválidas'
                flash(erro, 'danger')
        except requests.exceptions.RequestException as e:
            print(f"\n[ERRO DE CONEXION] : {e}\n")
            flash('Erro de conexão com o servidor central (API fora do ar).', 'danger')
    return render_template('dashboard.html')


@app.route('/cadastrar', methods=['POST', 'GET'])
def cadastrar():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == "POST":
        dados_usuario = {
        "nome" : request.form.get('form_nome'),
        "cpf" : request.form.get('form_cpf'),
        "email" : request.form.get('form_email'),
        "senha" : request.form.get('form_senha')
        }
        try:
            dados = requests.post(f"{api_url}/usuarios", json=dados_usuario, timeout=5, proxies=DESVIAR_PROXY)
            if dados.status_code == 201:
                flash( 'Cadastro realizado com sucesso', 'success')
                return redirect(url_for('login'))
            else:
                dados_erro = dados.json()
                erro = dados_erro('error') or dados_erro.get('erro') or 'Erro ao cadastrar'
                flash(erro, 'danger')
        except requests.exceptions.RequestException as e:
            print(f"\n[ERRO DE CONEXÃO NO CADASTRO] : {e}\n")
            flash('Erro de conexão com o servidor central (API fora de ar)', 'danger')

    return render_template('login.html')




@app.route("/logout")
def logout():
    logout_user()
    flash('Logout com sucesso', 'success')
    return redirect(url_for("home"))


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/galpoes', methods=['POST'])
def galpoes():
    if request.method == "POST":
        nome = request.form.get("form_nome")
        descricao = request.form.get("form_descricao")

    return render_template('galpoes.html')


@app.route('/blocos')
def blocos():
    if request.method == "POST":
        nome = request.form.get("form_nome")

    return render_template('blocos.html')


@app.route('/insumos')
def insumos():
    if request.method == "POST":
        tipo = request.form.get("form_tipo")
        nome = request.form.get("form_nome")
        umidade_max = request.form.get("form_umidade_max")
        umidade_min = request.form.get("form_umidade_min")
        temperatura_max = request.form.get("form_temperatura_max")
        temperatura_min = request.form.get("form_temperatura_min")
        quantidade = request.form.get("form_quantidade")
        unidade_medida = request.form.get("form_unidade_medida")

    return render_template('insumos.html')


@app.route('/sensores')
def sensores():
    if request.method == "POST":
        nome = request.form.get("form_nome")
        capacidade = request.form.get("form_capacidade")

    return render_template('sensores.html')


@app.route('/alertas')
def alertas():
    return render_template('alertas.html')


if __name__ == '__main__':
    app.run(debug=True, port=5007)
