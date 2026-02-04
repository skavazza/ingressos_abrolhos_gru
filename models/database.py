"""
Modelos de banco de dados para o sistema Abrolhos Ingressos
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Date, 
    DateTime, ForeignKey, CheckConstraint, Text, Boolean
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Usuario(Base):
    """Usuários do sistema"""
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nome_completo = Column(String(200))
    is_admin = Column(Boolean, default=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<Usuario(username='{self.username}', nome='{self.nome_completo}')>"


class Empresa(Base):
    """Empresas de turismo cadastradas"""
    __tablename__ = 'empresas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(200), unique=True, nullable=False)
    cnpj = Column(String(18))  # formato: XX.XXX.XXX/XXXX-XX
    contato_nome = Column(String(200))
    contato_telefone = Column(String(20))
    contato_email = Column(String(200))
    ativo = Column(Boolean, default=True)
    
    # Relacionamentos
    embarcacoes = relationship("Embarcacao", back_populates="empresa")
    registros_visita = relationship("RegistroVisita", back_populates="empresa")
    documentos_auditoria = relationship("DocumentoAuditoria", back_populates="empresa")
    
    def __repr__(self):
        return f"<Empresa(nome='{self.nome}', cnpj='{self.cnpj}')>"


class Embarcacao(Base):
    """Embarcações das empresas de turismo"""
    __tablename__ = 'embarcacoes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)
    nome = Column(String(200), nullable=False)
    tipo = Column(String(50))
    capacidade_pax = Column(Integer)
    comprimento_m = Column(Float)
    inscricao = Column(String(200))
    ativo = Column(Boolean, default=True)
    
    # Constraint para tipo de embarcação
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('Catamarã', 'Lancha', 'Barco', 'Escuna', 'Outro')",
            name='check_tipo_embarcacao'
        ),
    )
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="embarcacoes")
    registros_visita = relationship("RegistroVisita", back_populates="embarcacao")
    
    def __repr__(self):
        return f"<Embarcacao(nome='{self.nome}', tipo='{self.tipo}')>"


class TabelaPrecoIngresso(Base):
    """Tabela histórica de preços de ingressos por período/ano"""
    __tablename__ = 'tabela_preco_ingresso'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ano_inicio = Column(Integer, nullable=False)
    ano_fim = Column(Integer)
    data_inicio = Column(Date)
    data_fim = Column(Date)
    
    # Valores por categoria de visitante
    valor_estrangeiro = Column(Float, nullable=False, default=0.0)
    valor_mercosul = Column(Float, nullable=False, default=0.0)
    valor_brasileiro = Column(Float, nullable=False, default=0.0)
    valor_entorno = Column(Float, nullable=False, default=0.0)
    valor_isento = Column(Float, default=0.0)
    
    # Preços de permanência por TAMANHO da embarcação (Fundeio)
    valor_fundeio_ate8 = Column(Float, default=0.0)      # < 8m
    valor_fundeio_8a15 = Column(Float, default=0.0)      # 8-15m
    valor_fundeio_acima15 = Column(Float, default=0.0)   # > 15m
    
    observacao = Column(Text)
    ativo = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<TabelaPrecoIngresso(ano={self.ano_inicio}, estrangeiro=R${self.valor_estrangeiro})>"


class RegistroVisita(Base):
    """Registro diário de visitação"""
    __tablename__ = 'registros_visita'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    data = Column(Date, nullable=False)
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)
    embarcacao_id = Column(Integer, ForeignKey('embarcacoes.id'), nullable=False)
    
    # Código do registro e responsável
    cod_registro = Column(String(50))
    responsavel = Column(String(200))
    
    # Permanência: 1=aberto, 2=pernoite, etc.
    permanencia = Column(Integer, nullable=False, default=1)
    
    # Quantidades por tipo de visitante
    qtde_estrangeiros = Column(Integer, default=0)
    qtde_mercosul = Column(Integer, default=0)
    qtde_brasileiros = Column(Integer, default=0)
    qtde_entorno = Column(Integer, default=0)
    qtde_isentos = Column(Integer, default=0)
    
    # Quantidades opcionais por faixa etária
    qtde_maior12 = Column(Integer, default=0)
    qtde_menor12 = Column(Integer, default=0)
    
    # Valor total calculado
    valor_total = Column(Float, default=0.0)
    
    observacao = Column(Text)
    
    # Controle de timestamps
    criado_em = Column(DateTime, default=datetime.now)
    atualizado_em = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="registros_visita")
    embarcacao = relationship("Embarcacao", back_populates="registros_visita")
    
    def __repr__(self):
        return f"<RegistroVisita(data='{self.data}', empresa='{self.empresa.nome if self.empresa else 'N/A'}', total=R${self.valor_total})>"


class DocumentoAuditoria(Base):
    """Documentos enviados para auditoria"""
    __tablename__ = 'documentos_auditoria'

    id = Column(Integer, primary_key=True, autoincrement=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)
    registro_visita_id = Column(Integer, ForeignKey('registros_visita.id'))
    tipo = Column(String(50), nullable=False)  # nota, gru, relatorio, etc.
    nome_arquivo = Column(String(255), nullable=False)
    caminho_arquivo = Column(String(500), nullable=False)
    criado_em = Column(DateTime, default=datetime.now)

    empresa = relationship("Empresa", back_populates="documentos_auditoria")
    registro_visita = relationship("RegistroVisita")

    def __repr__(self):
        return f"<DocumentoAuditoria(empresa_id={self.empresa_id}, tipo='{self.tipo}', arquivo='{self.nome_arquivo}')>"


class LogAuditoria(Base):
    """Log de auditoria para rastreamento de alterações"""
    __tablename__ = 'log_auditoria'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario = Column(String(50))
    acao = Column(String(100))  # INSERT, UPDATE, DELETE
    tabela = Column(String(50))
    registro_id = Column(Integer)
    descricao = Column(Text)
    data_hora = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<LogAuditoria(usuario='{self.usuario}', acao='{self.acao}', tabela='{self.tabela}')>"


# Função para criar engine e sessão
def init_db(db_path: str = 'abrolhos_ingressos.db'):
    """
    Inicializa o banco de dados SQLite
    
    Args:
        db_path: Caminho para o arquivo do banco de dados
        
    Returns:
        tuple: (engine, SessionLocal)
    """
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    return engine, SessionLocal
