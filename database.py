from flask_login import UserMixin, login_manager
from sqlalchemy import create_engine, func, column, DateTime, Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash

engine = create_engine('mysql+pymysql://root:senaisp@localhost:3306/monitoramento_nutricao_animal')

db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

class Usuario(Base, UserMixin):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String,nullable=False)
    cpf = Column(String,nullable=False)
    email = Column(String,nullable=False,unique=True)
    senha = Column(String(255),nullable=False)

    def __repr__(self):
        return f'<Usuario: {self.nome}>'

    def serialize(self):
        return {
            "id_usuario": self.id_usuario,
            "nome": self.nome,
            "cpf": self.cpf,
            "email": self.email
        }

    def save(self, session=db_session):
        try:
            session.add(self)
            session.commit()
        except SQLAlchemyError as e:
            print(f'SQLAlchemy Error: {e}')
            session.rollback()







