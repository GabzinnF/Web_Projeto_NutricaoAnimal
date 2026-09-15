from sqlalchemy import create_engine, String, Integer, Column, DateTime, ForeignKey, func
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from sqlalchemy.exc import SQLAlchemyError

# Base de Dados
engine = create_engine('mysql+pymysql://root:senaisp@localhost:3306/monitoramento_nutricao_animal')

db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class Usuario(Base):
    __tablename__ = 'usuarios'
    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)

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
            raise


class Setor(Base):
    __tablename__ = 'setores'
    id_setor = Column(Integer, primary_key=True, autoincrement=True)
    id_insumos = Column(Integer, ForeignKey('insumos.id_insumo', name='FK_Setores_Insumos'), nullable=False)
    id_bloco = Column(Integer, ForeignKey('blocos.id_bloco', name='FK_Setores_Blocos'), nullable=False)

    def __repr__(self):
        return f'<Setor ID: {self.id_setor}>'

    def serialize(self):
        return {
            "id_setor": self.id_setor,
            "id_insumos": self.id_insumos,
            "id_bloco": self.id_bloco
        }

    def save(self, session=db_session):
        try:
            session.add(self)
            session.commit()
        except SQLAlchemyError as e:
            print(f'SQLAlchemy Error: {e}')
            session.rollback()
            raise


class Insumo(Base):
    __tablename__ = 'insumos'
    id_insumo = Column(Integer, primary_key=True, autoincrement=True)
    id_setor = Column(Integer, ForeignKey('setores.id_setor', use_alter=True, name='FK_Insumos_Setores'))
    tipo = Column(Integer)
    nome = Column(String(100), nullable=False)
    umid_max = Column(Integer)
    temp_max = Column(Integer)
    umid_min = Column(Integer)

    def __repr__(self):
        return f'<Insumo: {self.nome}>'

    def serialize(self):
        return {
            "id_insumo": self.id_insumo,
            "id_setor": self.id_setor,
            "tipo": self.tipo,
            "nome": self.nome,
            "umid_max": self.umid_max,
            "temp_max": self.temp_max,
            "umid_min": self.umid_min
        }

    def save(self, session=db_session):
        try:
            session.add(self)
            session.commit()
        except SQLAlchemyError as e:
            print(f'SQLAlchemy Error: {e}')
            session.rollback()
            raise


class Galpao(Base):
    __tablename__ = 'galpoes'
    id_galpao = Column(Integer, primary_key=True, autoincrement=True)
    descricao = Column(String(255))
    nome = Column(String(100), nullable=False)
    id_insumo = Column(Integer, ForeignKey('insumos.id_insumo'))

    def __repr__(self):
        return f'<Galpao: {self.nome}>'

    def serialize(self):
        return {
            "id_galpao": self.id_galpao,
            "descricao": self.descricao,
            "nome": self.nome,
            "id_insumo": self.id_insumo
        }

    def save(self, session=db_session):
        try:
            session.add(self)
            session.commit()
        except SQLAlchemyError as e:
            print(f'SQLAlchemy Error: {e}')
            session.rollback()
            raise


class Bloco(Base):
    __tablename__ = 'blocos'
    id_bloco = Column(Integer, primary_key=True, autoincrement=True)
    id_insumo = Column(Integer, ForeignKey('insumos.id_insumo'), nullable=False)
    id_galpao = Column(Integer, ForeignKey('galpoes.id_galpao'), nullable=False)
    nome = Column(String(100))

    def __repr__(self):
        return f'<Bloco: {self.nome}>'

    def serialize(self):
        return {
            "id_bloco": self.id_bloco,
            "id_insumo": self.id_insumo,
            "id_galpao": self.id_galpao,
            "nome": self.nome
        }

    def save(self, session=db_session):
        try:
            session.add(self)
            session.commit()
        except SQLAlchemyError as e:
            print(f'SQLAlchemy Error: {e}')
            session.rollback()
            raise


class Sensor(Base):
    __tablename__ = 'sensor'
    id_sensor = Column(Integer, primary_key=True, autoincrement=True)
    id_setor = Column(Integer, ForeignKey('setores.id_setor'), nullable=False)
    id_insumo = Column(Integer, ForeignKey('insumos.id_insumo'), nullable=False)

    def __repr__(self):
        return f'<Sensor ID: {self.id_sensor}>'

    def serialize(self):
        return {
            "id_sensor": self.id_sensor,
            "id_setor": self.id_setor,
            "id_insumo": self.id_insumo
        }

    def save(self, session=db_session):
        try:
            session.add(self)
            session.commit()
        except SQLAlchemyError as e:
            print(f'SQLAlchemy Error: {e}')
            session.rollback()
            raise


class Leitura(Base):
    __tablename__ = 'leitura'
    id_leitura = Column(Integer, primary_key=True, autoincrement=True)
    id_sensor = Column(Integer, ForeignKey('sensor.id_sensor'), nullable=False)
    valor_leitura = Column(Integer, nullable=False)
    data_hora = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f'<Leitura ID: {self.id_leitura} - Valor: {self.valor_leitura}>'

    def serialize(self):
        return {
            "id_leitura": self.id_leitura,
            "id_sensor": self.id_sensor,
            "valor_leitura": self.valor_leitura,
            "data_hora": self.data_hora.isoformat() if self.data_hora else None
        }

    def save(self, session=db_session):
        try:
            session.add(self)
            session.commit()
        except SQLAlchemyError as e:
            print(f'SQLAlchemy Error: {e}')
            session.rollback()
            raise


class AlertaOcorrencia(Base):
    __tablename__ = 'alertas_ocorrencias'
    id_alerta = Column(Integer, primary_key=True, autoincrement=True)
    id_leitura = Column(Integer, ForeignKey('leitura.id_leitura'), nullable=False)
    valor_registrado = Column(Integer, nullable=False)
    data_hora_inicio = Column(DateTime, server_default=func.now())
    data_hora_fim = Column(DateTime)
    tipo_alerta = Column(Integer)

    def __repr__(self):
        return f'<Alerta ID: {self.id_alerta} - Tipo: {self.tipo_alerta}>'

    def serialize(self):
        return {
            "id_alerta": self.id_alerta,
            "id_leitura": self.id_leitura,
            "valor_registrado": self.valor_registrado,
            "data_hora_inicio": self.data_hora_inicio.isoformat() if self.data_hora_inicio else None,
            "data_hora_fim": self.data_hora_fim.isoformat() if self.data_hora_fim else None,
            "tipo_alerta": self.tipo_alerta
        }

    def save(self, session=db_session):
        try:
            session.add(self)
            session.commit()
        except SQLAlchemyError as e:
            print(f'SQLAlchemy Error: {e}')
            session.rollback()
            raise



















Usuarios = Usuario
Insumos = Insumo
Galpoes = Galpao
Blocos = Bloco
Setores = Setor
AlertasOcorrencias = AlertaOcorrencia
AlertaOcorrencias = AlertaOcorrencia