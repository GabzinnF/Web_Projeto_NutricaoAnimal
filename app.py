from flask import Flask, render_template, url_for, flash, request, redirect, session
from sqlalchemy.exc import SQLAlchemyError

from database import db_session, Usuario
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
    user = select(Usuario).where(Usuario.id == int(user_id))
    resultado = db_session.execute(user).scalar_one_or_none()
    return resultado


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
            verificar_email = select(Usuario).where(Usuario.email == email)
            resultado_email = db_session.execute(verificar_email).scalar_one_or_none()
            if resultado_email:
                if resultado_email.check_password(senha):
                    login_user(resultado_email)
                    flash(f'login efetuado com sucesso', 'success')
                    print('logado com sucesso')
                    return redirect(url_for('dashboard'))

                else:
                    flash('Senha incorreta', 'alert-danger')
                    return redirect(url_for('login'))
            else:
                flash(f'Email não encontrado', 'alert-danger')
                return redirect(url_for('login'))
    else:
        return render_template('home.html')


@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form.get("form_nome")
        cpf = request.form.get("form_cpf")
        email = request.form.get("form_email")
        senha = request.form.get("form_senha")
        if not nome or not email or not senha:
            flash('Por favor preencha todos os campos', 'danger')
            return render_template('home.html')
        vericar_email = select(Usuario).where(Usuario.email == email)
        existe_email = db_session.execute(vericar_email).scalar_one_or_none()
        vericar_cpf = select(Usuario).where(Usuario.cpf == cpf)
        existe_cpf = db_session.execute(vericar_cpf).scalar_one_or_none()
        if existe_email:
            flash(f'Email {email} ja existente', 'danger')
            return render_template('home.html')
        if existe_cpf:
            flash(f'Email {cpf} ja existente', 'danger')
            return render_template('home.html')
        try:
            novo_Usuario = Usuario(nome=nome, cpf=cpf, email=email, senha=senha, )
            novo_Usuario.set_password(senha)
            db_session.add(novo_Usuario)
            db_session.commit()
            flash(f'Usuario {nome} cadastrado com sucesso', 'success')
            return redirect(url_for('login'))
        except SQLAlchemyError as e:
            flash(f'Erro na base de dados ao cadastrar usuario', 'danger')
            print(f'Erro na base de dados: {e}')
            return redirect(url_for('cadastrar'))
        except Exception as e:
            flash(f'Erro ao cadastrar usuario', 'danger')
            print(f'Erro ao cadastrar: {e}')
            return redirect(url_for('cadastrar'))
    return render_template('home.html')


@app.route("/logout")
def logout():
    logout_user()
    flash('Logout com sucesso', 'success')
    return redirect(url_for("home"))


@app.route('/dashboard')
def dashboard():
    if "usuario_logado" not in session:
        return redirect(url_for('home'))
    return render_template('dashboard.html')


@app.route('/galpoes')
def galpoes():
    if "usuario_logado" not in session:
        return redirect(url_for('home'))
    return render_template('galpoes.html')


@app.route('/estrutura')
def estrutura():
    if "usuario_logado" not in session:
        return redirect(url_for('home'))
    return render_template('estrutura.html')


@app.route('/insumos')
def insumos():
    if "usuario_logado" not in session:
        return redirect(url_for('home'))
    return render_template('insumos.html')


@app.route('/sensores')
def sensores():
    if "usuario_logado" not in session:
        return redirect(url_for('home'))
    return render_template('sensores.html')


if __name__ == '__main__':
    app.run(debug=True, port=5002)
