from sqlalchemy import create_engine, Column, Integer, String, Float, BigInteger
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic import BaseModel, Field
from properties import DATABASE_URL

# Configuração do SQLAlchemy
engine = create_engine(DATABASE_URL, echo=True)  # echo=True para log das queries
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Criar as tabelas no banco de dados (utilize migrações em produção)
Base.metadata.create_all(bind=engine)


# Modelos do Banco de Dados
class PacienteModel(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    idade = Column(Integer)
    cpf = Column(String, unique=True, index=True)
    rg = Column(String)
    data_nasc = Column(String)
    sexo = Column(String)
    signo = Column(String)
    mae = Column(String)
    pai = Column(String)
    email = Column(String)
    senha = Column(String)
    cep = Column(String)
    endereco = Column(String)
    numero = Column(Integer)
    bairro = Column(String)
    cidade = Column(String)
    estado = Column(String)
    telefone_fixo = Column(String)
    celular = Column(String)
    altura = Column(String)
    peso = Column(Integer)
    tipo_sanguineo = Column(String)
    cor = Column(String)

class MedicaoModel(Base):
    __tablename__ = "medicoes"

    id = Column(Integer, primary_key=True, index=True)
    cpf = Column(String, index=True)
    tipo = Column(String, index=True)  # ex: "indice_cardiaco", "indice_pulmonar"
    epoch = Column(BigInteger, index=True)
    valor = Column(Float)

# Modelos de resposta e entrada com Pydantic
class Paciente(BaseModel):
    nome: str = Field(..., example="Alexandre Caleb Costa")
    idade: int = Field(..., example=55)
    cpf: str = Field(..., example="974.642.524-20")
    rg: str = Field(..., example="22.107.246-9")
    data_nasc: str = Field(..., example="19/01/1967")
    sexo: str = Field(..., example="Masculino")
    signo: str = Field(..., example="Capricórnio")
    mae: str = Field(..., example="Beatriz Alícia")
    pai: str = Field(..., example="Nelson Heitor Costa")
    email: str = Field(..., example="aalexandrecalebcosta@br.loreal.com")
    senha: str = Field(..., example="6eXIFok6iQ")
    cep: str = Field(..., example="69309-415")
    endereco: str = Field(..., example="Rua das Palmas de Santa Rita")
    numero: int = Field(..., example=765)
    bairro: str = Field(..., example="Pricumã")
    cidade: str = Field(..., example="Boa Vista")
    estado: str = Field(..., example="RR")
    telefone_fixo: str = Field(..., example="(95) 3783-9661")
    celular: str = Field(..., example="(95) 99359-1588")
    altura: str = Field(..., example="1,96")
    peso: int = Field(..., example=63)
    tipo_sanguineo: str = Field(..., example="A-")
    cor: str = Field(..., example="laranja")

    class Config:
        orm_mode = True

class Medicao(BaseModel):
    cpf: str = Field(..., example="974.642.524-20")
    tipo: str = Field(..., example="indice_cardiaco")
    epoch: int = Field(..., example=1622563699)
    valor: float = Field(..., example=0.715997)

    class Config:
        orm_mode = True


