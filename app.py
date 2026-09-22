import datetime

from flask import Flask, render_template, url_for, flash, request, redirect, session
from sqlalchemy.exc import SQLAlchemyError

from database import db_session, Usuarios, Insumos, Galpoes, Blocos, Sensores
from sqlalchemy import select, and_, func
from flask_login import LoginManager, login_required, logout_user, current_user, login_user

app = Flask(__name__)
app.config["SECRET_KEY"] = "leite_gato"

# login_manager = LoginManager(app)
# login_manager.login_view = 'login'
# login_manager.login_massage = 'Para visualizar essa pagina faça o login'


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


# @login_manager.user_loader
# def load_user(user_id):
#     user = select(Usuarios).where(Usuarios.id == int(user_id))
#     resultado = db_session.execute(user).scalar_one_or_none()
#     return resultado


@app.route('/')
def home():
    if "usuario_logado" in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("form_email")
        senha = request.form.get("form_senha")

        if email and senha:
            verificar_email = select(Usuarios).where(Usuarios.email == email)
            resultado_email = db_session.execute(verificar_email).scalar_one_or_none()

            if resultado_email:
                if resultado_email.check_password(senha):
                    login_user(resultado_email)
                    flash('Login efetuado com sucesso', 'success')
                    print('Logado com sucesso')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Senha incorreta', 'alert-danger')
                    return render_template('login.html')
            else:
                flash('Email não encontrado', 'alert-danger')
                return render_template('login.html')
        else:
            flash('Preencha todos os campos', 'alert-danger')
            return render_template('login.html')
    else:
        return redirect(url_for('dashboard'))


@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    if request.method == "POST":
        nome = request.form.get("form_nome")
        cpf = request.form.get("form_cpf")
        email = request.form.get("form_email")
        senha = request.form.get("form_senha")

        usuario = Usuarios(
            nome=nome,
            cpf=cpf,
            email=email,
            senha=senha,
        )

        db_session.add(usuario)
        db_session.commit()


        return redirect(url_for("login"))

    return render_template("cadastro.html")


@app.route("/logout")
def logout():
    logout_user()
    flash('Logout com sucesso', 'success')
    return redirect(url_for("home"))


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/galpoes')
def galpoes():
    if request.method == "POST":
        nome = request.form.get("form_nome")
        descricao = request.form.get("form_descricao")

        galpoes = Galpoes(
            nome=nome,
            descricao=descricao,
        )

        db_session.add(galpoes)
        db_session.commit()

    return render_template('galpoes.html')

@app.route('/blocos')
def blocos():
    if request.method == "POST":
        nome = request.form.get("form_nome")

        blocos = Blocos(
            nome=nome,
        )

        db_session.add(blocos)
        db_session.commit()

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

        insumo = Insumos(
            tipo=tipo,
            nome=nome,
            umidade_max=umidade_max,
            umidade_min=umidade_min,
            temperatura_max=temperatura_max,
            temperatura_min=temperatura_min,
            quantidade=quantidade,
            unidade_medida=unidade_medida,
        )

        db_session.add(insumo)
        db_session.commit()

    return render_template('insumos.html')


@app.route('/sensores')
def sensores():
    if request.method == "POST":
        nome = request.form.get("form_nome")
        capacidade = request.form.get("form_capacidade")

        sensores = Sensores(
            nome=nome,
            capacidade=capacidade,
        )

        db_session.add(sensores)
        db_session.commit()

    return render_template('sensores.html')


@app.route('/alertas')
def alertas():
    return render_template('alertas.html')


if __name__ == '__main__':
    app.run(debug=True, port=5007)
