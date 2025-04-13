from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query, Path
from fastapi.responses import FileResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import  Session
import pandas as pd
from fastapi import Query
from sqlalchemy import func
from models import SessionLocal, PacienteModel, MedicaoModel, Paciente
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Desafio Anlix - API de Pacientes e Mediões",
    description="API para consulta de dados de pacientes e medições clínicas, com persistência em PostgreSQL e validação aprimorada.",
    version="1.0.0"
)

# Ativando CORS para front-end

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# GET ( http://127.0.0.1:8000/pacientes?nome=Rebeca ) ou ( http://127.0.0.1:8000/pacientes )
@app.get("/pacientes", response_model=List[Paciente])
def get_pacientes(
    nome: Optional[str] = Query(None, description="Filtra pacientes contendo essa substring no nome"),
    db: Session = Depends(get_db)
):
    """
    Busca todos os pacientes cadastrados ou filtra por nome.

    - *nome*: (opcional) parte do nome do paciente para filtrar.
    """
    try:
        query = db.query(PacienteModel)
        if nome:
            query = query.filter(PacienteModel.nome.ilike(f"%{nome}%"))
        pacientes = query.all()
        return pacientes
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Erro no banco de dados: {str(e)}")

# GET ( http://127.0.0.1:8000/pacientes/529.310.074-20 )
@app.get("/pacientes/{cpf}", response_model=Paciente)
def get_paciente_by_cpf(
    cpf: str = Path(..., description="CPF do paciente (formato: 974.642.524-20)"),
    db: Session = Depends(get_db)
):
    """
    Busca um paciente pelo CPF.

    - *cpf*: CPF do paciente.
    """

    cpf_limpo = cpf.replace(".", "").replace("-", "")

    paciente = db.query(PacienteModel).filter(
        func.replace(func.replace(PacienteModel.cpf, ".", ""), "-", "") == cpf_limpo
    ).first()

    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return paciente

# GET ( http://127.0.0.1:8000/pacientes/529.310.074-20/caracteristicas )
@app.get("/pacientes/{cpf}/caracteristicas")
def get_ultimas_caracteristicas(
    cpf: str = Path(..., description="CPF do paciente"),
    db: Session = Depends(get_db)
):
    cpf_limpo = cpf.replace(".", "").replace("-", "")
    resultado = {}

    for tipo in ["ind_card", "ind_pulm"]:
        medicao = db.query(MedicaoModel).filter(
            MedicaoModel.cpf == cpf_limpo,
            MedicaoModel.tipo == tipo
        ).order_by(MedicaoModel.epoch.desc()).first()

        if medicao:
            resultado[tipo] = {
                "epoch": medicao.epoch,
                "valor": medicao.valor,
                "data": datetime.fromtimestamp(medicao.epoch).strftime("%d/%m/%Y %H:%M:%S")
            }
        else:
            resultado[tipo] = None

    return resultado

# GET ( http://127.0.0.1:8000/export )
@app.get("/export", response_class=FileResponse)
def export_csv(
    cpfs: Optional[str] = Query(None, description="Lista de CPFs separados por vírgula. Se omitido, exporta todos os dados."),
    db: Session = Depends(get_db)
):
    """
    Exporta os dados das medições para um arquivo CSV.

    - *cpfs*: (opcional) CPFs separados por vírgula para filtrar os dados.
    """
    try:
        if cpfs:
            cpf_list = [cpf.strip().replace(".", "").replace("-", "") for cpf in cpfs.split(",")]
            query = db.query(MedicaoModel).filter(
                func.replace(func.replace(MedicaoModel.cpf, ".", ""), "-", "").in_(cpf_list)
            )
        else:
            query = db.query(MedicaoModel)
        medicoes = query.all()
        if not medicoes:
            raise HTTPException(status_code=404, detail="Nenhum dado para exportar.")
        
        # Monta lista de dicionários para gerar DataFrame
        dados = [{
            "cpf": m.cpf,
            "tipo": m.tipo,
            "epoch": m.epoch,
            "valor": m.valor,
            "data": datetime.fromtimestamp(m.epoch).strftime("%d/%m/%Y %H:%M:%S")
        } for m in medicoes]
        
        df = pd.DataFrame(dados)
        output_file = "export.csv"
        df.to_csv(output_file, index=False, encoding="utf-8")
        return FileResponse(path=output_file, filename=output_file, media_type='text/csv')
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao exportar dados: {str(e)}")

# GET ( http://localhost:8000/pacientes/974.642.524-20/caracteristicas/ind_card?de=2021-06-01&ate=2021-06-21 )
@app.get("/pacientes/{cpf}/caracteristicas/{tipo}")
def get_caracteristica_por_intervalo(
    cpf: str = Path(..., description="CPF do paciente"),
    tipo: str = Path(..., description="Tipo da característica (ex: ind_card, ind_pulm)"),
    de: str = Query(..., description="Data início no formato yyyy-mm-dd"),
    ate: str = Query(..., description="Data fim no formato yyyy-mm-dd"),
    db: Session = Depends(get_db)
):
    try:
        
        cpf_limpo = cpf.replace(".", "").replace("-", "")

        # Converte datas para epoch
        data_inicio = int(datetime.strptime(de, "%Y-%m-%d").timestamp())
        data_fim = int(datetime.strptime(ate, "%Y-%m-%d").timestamp())

        medicoes = db.query(MedicaoModel).filter(
            MedicaoModel.cpf == cpf_limpo,
            MedicaoModel.tipo == tipo,
            MedicaoModel.epoch >= data_inicio,
            MedicaoModel.epoch <= data_fim
        ).order_by(MedicaoModel.epoch.asc()).all()

        if not medicoes:
            raise HTTPException(status_code=404, detail="Nenhuma medição encontrada nesse intervalo")

        
        return [
            {
                "epoch": m.epoch,
                "valor": m.valor,
                "tipo":m.tipo,
                "data": datetime.fromtimestamp(m.epoch).strftime("%d/%m/%Y %H:%M:%S")
            } for m in medicoes
        ]
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de data inválido. Use yyyy-mm-dd.")



# GET ( http://127.0.0.1:8000/caracteristicas/21/06/2021?skip=1&limit=5 )
@app.get("/caracteristicas/{dia}/{mes}/{ano}")
def get_caracteristicas_por_data(
    dia: int = Path(..., ge=1, le=31),
    mes: int = Path(..., ge=1, le=12),
    ano: int = Path(..., ge=1900),
    skip: int = Query(0, ge=0, description="Número de registros a pular (offset)"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros a retornar"),
    db: Session = Depends(get_db)
):
    """
    Consulta todas as características registradas na data especificada, com paginação.
    """
    try:
        # Converte a data para timestamps (epoch)
        data_inicial = datetime(ano, mes, dia)
        data_final = datetime(ano, mes, dia, 23, 59, 59)

        epoch_inicio = int(data_inicial.timestamp())
        epoch_fim = int(data_final.timestamp())

        medicoes = db.query(MedicaoModel).filter(
            MedicaoModel.epoch >= epoch_inicio,
            MedicaoModel.epoch <= epoch_fim
        ).offset(skip).limit(limit).all()

        if not medicoes:
            raise HTTPException(status_code=404, detail="Nenhuma característica encontrada para essa data.")

        
        resultado = {}
        for m in medicoes:
            cpf = m.cpf
            if cpf not in resultado:
                resultado[cpf] = {}
            resultado[cpf][m.tipo] = {
                "epoch": m.epoch,
                "valor": m.valor,
                "data": datetime.fromtimestamp(m.epoch).strftime("%d/%m/%Y %H:%M:%S")
            }

        return {
            "skip": skip,
            "limit": limit,
            "total_registros": len(medicoes),
            "dados": resultado
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Data inválida.")

# GET ( http://127.0.0.1:8000/pacientes/529.310.074-20/caracteristica/ind_card/valor?valor_min=0.3&valor_max=0.7 )
@app.get("/pacientes/{cpf}/caracteristica/{tipo}/valor")
def get_ultima_caracteristica_por_valor(
    cpf: str = Path(..., description="CPF do paciente"),
    tipo: str = Path(..., description="Tipo da característica, ex: ind_card"),
    valor_min: float = Query(..., description="Valor mínimo da característica"),
    valor_max: float = Query(..., description="Valor máximo da característica"),
    db: Session = Depends(get_db)
):
    """
    Retorna o valor mais recente de uma característica de um paciente,
    que esteja dentro de um intervalo de valores numéricos.
    """
    try:
        cpf_limpo = cpf.replace(".", "").replace("-", "")

        medicao = db.query(MedicaoModel).filter(
            MedicaoModel.cpf == cpf_limpo,
            MedicaoModel.tipo == tipo,
            MedicaoModel.valor >= valor_min,
            MedicaoModel.valor <= valor_max
        ).order_by(MedicaoModel.epoch.desc()).first()

        if not medicao:
            raise HTTPException(status_code=404, detail="Nenhuma medição encontrada para os critérios informados.")

        return {
            "cpf": medicao.cpf,
            "tipo": medicao.tipo,
            "valor": medicao.valor,
            "epoch": medicao.epoch,
            "data": datetime.fromtimestamp(medicao.epoch).strftime("%d/%m/%Y %H:%M:%S")
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Erro na consulta: {str(e)}")


if __name__=="__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)