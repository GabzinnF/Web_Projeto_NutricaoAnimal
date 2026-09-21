import datetime

from flask import Flask, render_template, url_for, flash, request, redirect, session
from sqlalchemy.exc import SQLAlchemyError

from database import db_session, Usuarios
from sqlalchemy import select, and_, func
from flask_login import LoginManager, login_required, logout_user, current_user, login_user

app = Flask(__name__)
app.config["SECRET_KEY"] = "leite_gato"

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_massage = 'Para visualizar essa pagina faça o login'


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@login_manager.user_loader
def load_user(user_id):
    user = select(Usuarios).where(Usuarios.id == int(user_id))
    resultado = db_session.execute(user).scalar_one_or_none()
    return resultado


@app.route('/')
def home():
    if "usuario_logado" in session:
        return redirect(url_for('dashboard'))
    return render_template('dashboard.html')


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
                    flash(f'login efetuado com sucesso', 'success')
                    print('logado com sucesso')
                    return redirect(url_for('dashboard'))

                else:
                    flash('Senha incorreta', 'alert-danger')
                    return render_template(url_for('login'))
            else:
                flash(f'Email não encontrado', 'alert-danger')
                return render_template(url_for('login'))
    else:
        return render_template('login.html')


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
    return render_template('galpoes.html')


@app.route('/insumos')
def insumos():
    return render_template('insumos.html')


@app.route('/sensores')
def sensores():
    return render_template('sensores.html')


@app.route('/alertas')
def alertas():
    return render_template('alertas.html')


if __name__ == '__main__':
    app.run(debug=True, port=5007)
