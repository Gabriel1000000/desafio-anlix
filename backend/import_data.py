import os
import json
import pandas as pd
from sqlalchemy.orm import Session
from models import PacienteModel, MedicaoModel, SessionLocal

def normalizar_cpf(cpf: str) -> str:
    return cpf.replace(".", "").replace("-", "")

def importar_pacientes(session: Session):
    with open("dados/pacientes.json", encoding="utf-8") as f:
        pacientes = json.load(f)

        for p in pacientes:
            cpf = normalizar_cpf(p["cpf"])
            existe = session.query(PacienteModel).filter_by(cpf=cpf).first()
            if not existe:
                paciente = PacienteModel(
                    nome=p["nome"],
                    cpf=cpf,
                    idade=p.get("idade"),
                    rg=p.get("rg"),
                    data_nasc=p.get("data_nasc"),
                    sexo=p.get("sexo"),
                    signo=p.get("signo"),
                    mae=p.get("mae"),
                    pai=p.get("pai"),
                    email=p.get("email"),
                    senha=p.get("senha"),
                    cep=p.get("cep"),
                    endereco=p.get("endereco"),
                    numero=p.get("numero"),
                    bairro=p.get("bairro"),
                    cidade=p.get("cidade"),
                    estado=p.get("estado"),
                    telefone_fixo=p.get("telefone_fixo"),
                    celular=p.get("celular"),
                    altura=p.get("altura"),
                    peso=p.get("peso"),
                    tipo_sanguineo=p.get("tipo_sanguineo"),
                    cor=p.get("cor")
                )
                session.add(paciente)
        session.commit()
        print("Pacientes importados")

def importar_medicoes(session: Session, pasta: str, tipo: str):
    print(f"Lendo arquivos da pasta {pasta} como tipo {tipo}")
    for arquivo in os.listdir(pasta):
        
        caminho = os.path.join(pasta, arquivo)
        if os.path.isfile(caminho): 
            print(f"  → Importando: {arquivo}")
            df = pd.read_csv(caminho, delim_whitespace=True, dtype={"CPF": str})
            df["CPF"] = df["CPF"].str.replace(r"[.-]", "", regex=True)

            for _, row in df.iterrows():
                cpf = row["CPF"]
                paciente = session.query(PacienteModel).filter_by(cpf=cpf).first()
                if paciente:
                    medicao = MedicaoModel(
                        cpf=cpf,
                        tipo=tipo,
                        epoch=int(row["EPOCH"]),
                        valor=float(row[tipo]) 
                    )
                    session.add(medicao)
        try:
            session.commit()
        except Exception as e:
            print(f"Erro ao inserir medições de {arquivo}: {e}")
            session.rollback()
    print(f"Medições de {tipo} importadas com sucesso.")



def importar_tudo():
    with SessionLocal() as session:
        importar_pacientes(session)
        importar_medicoes(session, "dados/indice_cardiaco", "ind_card")
        importar_medicoes(session, "dados/indice_pulmonar", "ind_pulm")

if __name__ == "__main__":
    importar_tudo()
