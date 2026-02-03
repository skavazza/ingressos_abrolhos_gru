"""
Serviços e operações CRUD para o banco de dados
"""
from datetime import datetime, date
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, extract
import bcrypt

from models.database import (
    Usuario, Empresa, Embarcacao, TabelaPrecoIngresso, 
    RegistroVisita, LogAuditoria
)


class UsuarioService:
    """Serviços para gerenciamento de usuários"""
    
    @staticmethod
    def criar_usuario(session: Session, username: str, password: str, 
                      nome_completo: str = None, is_admin: bool = False) -> Usuario:
        """Cria um novo usuário com senha criptografada"""
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        usuario = Usuario(
            username=username,
            password_hash=password_hash.decode('utf-8'),
            nome_completo=nome_completo,
            is_admin=is_admin
        )
        session.add(usuario)
        session.commit()
        return usuario
    
    @staticmethod
    def autenticar(session: Session, username: str, password: str) -> Optional[Usuario]:
        """Autentica um usuário"""
        usuario = session.query(Usuario).filter_by(username=username, ativo=True).first()
        if usuario and bcrypt.checkpw(password.encode('utf-8'), usuario.password_hash.encode('utf-8')):
            return usuario
        return None

    @staticmethod
    def listar_usuarios(session: Session) -> List[Usuario]:
        """Lista todos os usuários"""
        return session.query(Usuario).order_by(Usuario.username).all()
    
    @staticmethod
    def buscar_por_id(session: Session, user_id: int) -> Optional[Usuario]:
        """Busca usuário por ID"""
        return session.query(Usuario).filter_by(id=user_id).first()
    
    @staticmethod
    def atualizar_usuario(session: Session, user_id: int, **kwargs) -> Optional[Usuario]:
        """Atualiza dados de um usuário"""
        usuario = session.query(Usuario).filter_by(id=user_id).first()
        if usuario:
            for key, value in kwargs.items():
                if key != 'password': # Senha deve ser atualizada via atualizar_senha
                    setattr(usuario, key, value)
            session.commit()
        return usuario
    
    @staticmethod
    def atualizar_senha(session: Session, user_id: int, nova_senha: str) -> bool:
        """Atualiza a senha de um usuário"""
        usuario = session.query(Usuario).filter_by(id=user_id).first()
        if usuario:
            password_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt())
            usuario.password_hash = password_hash.decode('utf-8')
            session.commit()
            return True
        return False
        
    @staticmethod
    def desativar_usuario(session: Session, user_id: int) -> bool:
        """Desativa um usuário"""
        usuario = session.query(Usuario).filter_by(id=user_id).first()
        if usuario:
            usuario.ativo = False
            session.commit()
            return True
        return False


class EmpresaService:
    """Serviços para gerenciamento de empresas"""
    
    @staticmethod
    def criar(session: Session, nome: str, cnpj: str = None, **kwargs) -> Empresa:
        """Cria uma nova empresa"""
        empresa = Empresa(nome=nome, cnpj=cnpj, **kwargs)
        session.add(empresa)
        session.commit()
        return empresa
    
    @staticmethod
    def listar_ativas(session: Session) -> List[Empresa]:
        """Lista todas as empresas ativas"""
        return session.query(Empresa).filter_by(ativo=True).order_by(Empresa.nome).all()
    
    @staticmethod
    def buscar_por_id(session: Session, empresa_id: int) -> Optional[Empresa]:
        """Busca empresa por ID"""
        return session.query(Empresa).filter_by(id=empresa_id).first()
    
    @staticmethod
    def atualizar(session: Session, empresa_id: int, **kwargs) -> Optional[Empresa]:
        """Atualiza dados de uma empresa"""
        empresa = session.query(Empresa).filter_by(id=empresa_id).first()
        if empresa:
            for key, value in kwargs.items():
                setattr(empresa, key, value)
            session.commit()
        return empresa
    
    @staticmethod
    def desativar(session: Session, empresa_id: int) -> bool:
        """Desativa uma empresa (soft delete)"""
        empresa = session.query(Empresa).filter_by(id=empresa_id).first()
        if empresa:
            empresa.ativo = False
            session.commit()
            return True
        return False


class EmbarcacaoService:
    """Serviços para gerenciamento de embarcações"""
    
    @staticmethod
    def criar(session: Session, empresa_id: int, nome: str, tipo: str, **kwargs) -> Embarcacao:
        """Cria uma nova embarcação"""
        embarcacao = Embarcacao(empresa_id=empresa_id, nome=nome, tipo=tipo, **kwargs)
        session.add(embarcacao)
        session.commit()
        return embarcacao
    
    @staticmethod
    def listar_por_empresa(session: Session, empresa_id: int, apenas_ativas: bool = True) -> List[Embarcacao]:
        """Lista embarcações de uma empresa"""
        query = session.query(Embarcacao).filter_by(empresa_id=empresa_id)
        if apenas_ativas:
            query = query.filter_by(ativo=True)
        return query.order_by(Embarcacao.nome).all()
    
    @staticmethod
    def listar_ativas(session: Session) -> List[Embarcacao]:
        """Lista todas as embarcações ativas"""
        return session.query(Embarcacao).filter_by(ativo=True).order_by(Embarcacao.nome).all()
    
    @staticmethod
    def buscar_por_id(session: Session, embarcacao_id: int) -> Optional[Embarcacao]:
        """Busca embarcação por ID"""
        return session.query(Embarcacao).filter_by(id=embarcacao_id).first()
    
    @staticmethod
    def atualizar(session: Session, embarcacao_id: int, **kwargs) -> Optional[Embarcacao]:
        """Atualiza dados de uma embarcação"""
        embarcacao = session.query(Embarcacao).filter_by(id=embarcacao_id).first()
        if embarcacao:
            for key, value in kwargs.items():
                setattr(embarcacao, key, value)
            session.commit()
        return embarcacao


class TabelaPrecoService:
    """Serviços para gerenciamento de tabela de preços"""
    
    @staticmethod
    def criar(session: Session, ano_inicio: int, valores: dict, **kwargs) -> TabelaPrecoIngresso:
        """Cria uma nova tabela de preços"""
        tabela = TabelaPrecoIngresso(ano_inicio=ano_inicio, **valores, **kwargs)
        session.add(tabela)
        session.commit()
        return tabela
    
    @staticmethod
    def listar_ativas(session: Session) -> List[TabelaPrecoIngresso]:
        """Lista todas as tabelas de preços ativas"""
        return session.query(TabelaPrecoIngresso).filter_by(ativo=True).order_by(
            TabelaPrecoIngresso.ano_inicio.desc()
        ).all()
    
    @staticmethod
    def buscar_por_data(session: Session, data_referencia: date) -> Optional[TabelaPrecoIngresso]:
        """
        Busca a tabela de preços vigente para uma data específica
        
        Args:
            session: Sessão do SQLAlchemy
            data_referencia: Data para buscar a tabela de preços
            
        Returns:
            TabelaPrecoIngresso ou None
        """
        ano = data_referencia.year
        
        # Busca por ano ou por data específica
        tabela = session.query(TabelaPrecoIngresso).filter(
            and_(
                TabelaPrecoIngresso.ativo == True,
                TabelaPrecoIngresso.ano_inicio <= ano,
                or_(
                    TabelaPrecoIngresso.ano_fim.is_(None),
                    TabelaPrecoIngresso.ano_fim >= ano
                )
            )
        ).first()
        
        return tabela
    
    @staticmethod
    def atualizar(session: Session, tabela_id: int, **kwargs) -> Optional[TabelaPrecoIngresso]:
        """Atualiza uma tabela de preços"""
        tabela = session.query(TabelaPrecoIngresso).filter_by(id=tabela_id).first()
        if tabela:
            for key, value in kwargs.items():
                setattr(tabela, key, value)
            session.commit()
        return tabela


class RegistroVisitaService:
    """Serviços para gerenciamento de registros de visita"""
    
    @staticmethod
    def calcular_valor_total(session: Session, data: date, quantidades: dict,
                            permanencia: int = 1,
                            comprimento_embarcacao_m: Optional[float] = None) -> float:
        """
        Calcula o valor total do ingresso baseado na tabela de preços vigente.
        
        Regra: Ingressos = visitantes PAGANTES × permanência (isentos não cobram).
        Valor = (preço dos pagantes) × permanência × fator por tamanho da embarcação.
        valor_maior12/valor_menor12 na tabela de preços = preços de permanência por TAMANHO (≥12m / <12m), não por idade.
        
        Args:
            session: Sessão do SQLAlchemy
            data: Data da visita
            quantidades: Dict com qtde_estrangeiros, qtde_mercosul, qtde_brasileiros, etc.
            permanencia: Número de dias/permanência (1=aberto, 2=pernoite, etc.)
            comprimento_embarcacao_m: Comprimento da embarcação em metros (≥12m ou <12m)
            
        Returns:
            float: Valor total calculado
        """
        tabela_preco = TabelaPrecoService.buscar_por_data(session, data)
        
        if not tabela_preco:
            return 0.0
        
        # Subtotal: visitantes PAGANTES + Taxa de Embarcação
        # Ingressos = visitantes PAGANTES * valor_categoria
        
        subtotal_visitantes = 0.0
        subtotal_visitantes += quantidades.get('qtde_estrangeiros', 0) * tabela_preco.valor_estrangeiro
        subtotal_visitantes += quantidades.get('qtde_mercosul', 0) * tabela_preco.valor_mercosul
        subtotal_visitantes += quantidades.get('qtde_brasileiros', 0) * tabela_preco.valor_brasileiro
        subtotal_visitantes += quantidades.get('qtde_entorno', 0) * tabela_preco.valor_entorno
        subtotal_visitantes += quantidades.get('qtde_isentos', 0) * tabela_preco.valor_isento
        
        # Taxa da embarcação (Fundeio)
        taxa_embarcacao = 0.0
        if comprimento_embarcacao_m is not None:
            if comprimento_embarcacao_m < 8:
                taxa_embarcacao = tabela_preco.valor_fundeio_ate8 or 0.0
            elif comprimento_embarcacao_m <= 15:
                taxa_embarcacao = tabela_preco.valor_fundeio_8a15 or 0.0
            else:
                taxa_embarcacao = tabela_preco.valor_fundeio_acima15 or 0.0
        
        # Valor base diário = Soma dos ingressos + Taxa da embarcação
        valor_diario = subtotal_visitantes + taxa_embarcacao
        
        # Valor Total = Valor diário * permanência
        valor_total = valor_diario * permanencia
        return round(valor_total, 2)
    
    @staticmethod
    def calcular_ingressos_e_visitantes(quantidades: dict, permanencia: int) -> tuple:
        """
        Retorna (ingressos, visitantes) conforme a regra:
        - Ingressos = visitantes PAGANTES × permanência (isentos não contam como ingresso pago)
        - Visitantes = (pagantes + isentos) × permanência
        """
        pagantes = (
            quantidades.get('qtde_estrangeiros', 0) +
            quantidades.get('qtde_mercosul', 0) +
            quantidades.get('qtde_brasileiros', 0) +
            quantidades.get('qtde_entorno', 0)
        )
        isentos = quantidades.get('qtde_isentos', 0)
        ingressos = pagantes * permanencia
        visitantes = (pagantes + isentos) * permanencia
        return ingressos, visitantes
    
    @staticmethod
    def criar(session: Session, data: date, empresa_id: int, embarcacao_id: int,
             permanencia: int, quantidades: dict, **kwargs) -> RegistroVisita:
        """Cria um novo registro de visita"""
        # Comprimento da embarcação para fator de permanência (>=12m ou <12m)
        embarcacao = EmbarcacaoService.buscar_por_id(session, embarcacao_id)
        comprimento_m = embarcacao.comprimento_m if embarcacao else None
        
        valor_total = RegistroVisitaService.calcular_valor_total(
            session, data, quantidades, permanencia, comprimento_m
        )
        
        registro = RegistroVisita(
            data=data,
            empresa_id=empresa_id,
            embarcacao_id=embarcacao_id,
            permanencia=permanencia,
            valor_total=valor_total,
            **quantidades,
            **kwargs
        )
        session.add(registro)
        session.commit()
        return registro
    
    @staticmethod
    def listar_por_periodo(session: Session, data_inicio: date, 
                          data_fim: date, empresa_id: Optional[int] = None) -> List[RegistroVisita]:
        """Lista registros em um período, opcionalmente filtrando por empresa"""
        query = session.query(RegistroVisita).filter(
            and_(
                RegistroVisita.data >= data_inicio,
                RegistroVisita.data <= data_fim
            )
        )
        
        if empresa_id:
            query = query.filter(RegistroVisita.empresa_id == empresa_id)
            
        return query.order_by(RegistroVisita.data.desc()).all()
    
    @staticmethod
    def listar_por_data(session: Session, data: date) -> List[RegistroVisita]:
        """Lista registros de uma data específica"""
        return session.query(RegistroVisita).filter_by(data=data).order_by(
            RegistroVisita.criado_em.desc()
        ).all()
    
    @staticmethod
    def buscar_por_id(session: Session, registro_id: int) -> Optional[RegistroVisita]:
        """Busca registro por ID"""
        return session.query(RegistroVisita).filter_by(id=registro_id).first()
    
    @staticmethod
    def atualizar(session: Session, registro_id: int, **kwargs) -> Optional[RegistroVisita]:
        """Atualiza um registro de visita"""
        registro = session.query(RegistroVisita).filter_by(id=registro_id).first()
        if registro:
            # Se houver mudança nas quantidades ou permanência, recalcula o valor
            if any(k.startswith('qtde_') or k == 'permanencia' for k in kwargs.keys()):
                quantidades = {
                    'qtde_estrangeiros': kwargs.get('qtde_estrangeiros', registro.qtde_estrangeiros),
                    'qtde_mercosul': kwargs.get('qtde_mercosul', registro.qtde_mercosul),
                    'qtde_brasileiros': kwargs.get('qtde_brasileiros', registro.qtde_brasileiros),
                    'qtde_entorno': kwargs.get('qtde_entorno', registro.qtde_entorno),
                    'qtde_isentos': kwargs.get('qtde_isentos', registro.qtde_isentos),
                    'qtde_maior12': 0,
                    'qtde_menor12': 0,
                }
                permanencia = kwargs.get('permanencia', registro.permanencia)
                embarcacao = registro.embarcacao
                comprimento_m = embarcacao.comprimento_m if embarcacao else None
                kwargs['valor_total'] = RegistroVisitaService.calcular_valor_total(
                    session, registro.data, quantidades, permanencia, comprimento_m
                )
            
            for key, value in kwargs.items():
                setattr(registro, key, value)
            
            registro.atualizado_em = datetime.now()
            session.commit()
        return registro
    
    @staticmethod
    def deletar(session: Session, registro_id: int) -> bool:
        """Deleta um registro de visita"""
        registro = session.query(RegistroVisita).filter_by(id=registro_id).first()
        if registro:
            session.delete(registro)
            session.commit()
            return True
        return False
    
    @staticmethod
    def relatorio_mensal(session: Session, ano: int, mes: int) -> dict:
        """
        Gera relatório resumido do mês
        
        Returns:
            dict com totais de visitantes e receita
        """
        registros = session.query(RegistroVisita).filter(
            and_(
                extract('year', RegistroVisita.data) == ano,
                extract('month', RegistroVisita.data) == mes
            )
        ).all()
        
        resumo = {
            'total_visitantes': 0,
            'total_estrangeiros': 0,
            'total_mercosul': 0,
            'total_brasileiros': 0,
            'total_entorno': 0,
            'total_isentos': 0,
            'receita_total': 0.0,
            'quantidade_registros': len(registros)
        }
        
        for r in registros:
            resumo['total_estrangeiros'] += r.qtde_estrangeiros
            resumo['total_mercosul'] += r.qtde_mercosul
            resumo['total_brasileiros'] += r.qtde_brasileiros
            resumo['total_entorno'] += r.qtde_entorno
            resumo['total_isentos'] += r.qtde_isentos
            resumo['receita_total'] += r.valor_total
        
        resumo['total_visitantes'] = (
            resumo['total_estrangeiros'] + 
            resumo['total_mercosul'] + 
            resumo['total_brasileiros'] + 
            resumo['total_entorno'] + 
            resumo['total_isentos']
        )
        
        return resumo


class LogService:
    """Serviços para log de auditoria"""
    
    @staticmethod
    def registrar(session: Session, usuario: str, acao: str, tabela: str, 
                 registro_id: int = None, descricao: str = None):
        """Registra uma ação de auditoria"""
        log = LogAuditoria(
            usuario=usuario,
            acao=acao,
            tabela=tabela,
            registro_id=registro_id,
            descricao=descricao
        )
        session.add(log)
        session.commit()
