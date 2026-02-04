"""
API para sincronização entre app servidor e app cliente.
"""
from __future__ import annotations

import os
from datetime import date
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models.database import init_db, TabelaPrecoIngresso
from models.services import (
    DocumentoAuditoriaService,
    RegistroVisitaService,
    TabelaPrecoService,
)

DB_PATH = os.getenv("ABROLHOS_DB_PATH", "abrolhos_ingressos.db")
UPLOAD_DIR = Path(os.getenv("ABROLHOS_UPLOAD_DIR", "uploads"))

engine, SessionLocal = init_db(DB_PATH)

app = FastAPI(title="Abrolhos Ingressos Sync API")


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


class TabelaPrecoResponse(BaseModel):
    id: int
    ano_inicio: int
    ano_fim: Optional[int]
    data_inicio: Optional[date]
    data_fim: Optional[date]
    valor_estrangeiro: float
    valor_mercosul: float
    valor_brasileiro: float
    valor_entorno: float
    valor_isento: float
    valor_fundeio_ate8: float
    valor_fundeio_8a15: float
    valor_fundeio_acima15: float
    observacao: Optional[str]


class RegistroVisitaPayload(BaseModel):
    data: date
    empresa_id: int
    embarcacao_id: int
    permanencia: int = 1
    cod_registro: Optional[str] = None
    responsavel: Optional[str] = None
    qtde_estrangeiros: int = 0
    qtde_mercosul: int = 0
    qtde_brasileiros: int = 0
    qtde_entorno: int = 0
    qtde_isentos: int = 0
    observacao: Optional[str] = None


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.get("/precos/ativo", response_model=TabelaPrecoResponse)
def obter_tabela_preco(session: Session = Depends(get_session)) -> TabelaPrecoIngresso:
    tabela = TabelaPrecoService.listar_ativas(session)
    if not tabela:
        raise HTTPException(status_code=404, detail="Nenhuma tabela de preços ativa encontrada.")
    return tabela[0]


@app.post("/registros")
def criar_registro(payload: RegistroVisitaPayload, session: Session = Depends(get_session)) -> dict:
    quantidades = {
        "qtde_estrangeiros": payload.qtde_estrangeiros,
        "qtde_mercosul": payload.qtde_mercosul,
        "qtde_brasileiros": payload.qtde_brasileiros,
        "qtde_entorno": payload.qtde_entorno,
        "qtde_isentos": payload.qtde_isentos,
        "qtde_maior12": 0,
        "qtde_menor12": 0,
    }
    registro = RegistroVisitaService.criar(
        session,
        data=payload.data,
        empresa_id=payload.empresa_id,
        embarcacao_id=payload.embarcacao_id,
        permanencia=payload.permanencia,
        quantidades=quantidades,
        cod_registro=payload.cod_registro,
        responsavel=payload.responsavel,
        observacao=payload.observacao,
    )
    return {"id": registro.id, "valor_total": registro.valor_total}


@app.post("/documentos")
def enviar_documento(
    empresa_id: int = Form(...),
    tipo: str = Form(...),
    arquivo: UploadFile = File(...),
    registro_visita_id: Optional[int] = Form(None),
    session: Session = Depends(get_session),
) -> dict:
    if not arquivo.filename:
        raise HTTPException(status_code=400, detail="Arquivo inválido.")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    destino_dir = UPLOAD_DIR / f"empresa_{empresa_id}"
    destino_dir.mkdir(parents=True, exist_ok=True)

    nome_seguro = f"{uuid4().hex}_{Path(arquivo.filename).name}"
    destino = destino_dir / nome_seguro

    with destino.open("wb") as buffer:
        buffer.write(arquivo.file.read())

    documento = DocumentoAuditoriaService.criar(
        session,
        empresa_id=empresa_id,
        registro_visita_id=registro_visita_id,
        tipo=tipo,
        nome_arquivo=arquivo.filename,
        caminho_arquivo=str(destino),
    )
    return {"id": documento.id, "arquivo": documento.nome_arquivo}
