"""
Aba de Dashboard com resumo e estatísticas
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from datetime import datetime, date
from calendar import monthrange

from models.services import RegistroVisitaService
from models.database import Empresa, Embarcacao, TabelaPrecoIngresso, RegistroVisita


class StatCard(QFrame):
    """Card para exibir uma estatística"""
    
    def __init__(self, title: str, value: str, icon: str = "📊"):
        super().__init__()
        
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setLineWidth(1)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Ícone e título
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_font = QFont()
        icon_font.setPointSize(24)
        icon_label.setFont(icon_font)
        header_layout.addWidget(icon_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet('color: #666; font-size: 11pt;')
        layout.addWidget(title_label)
        
        # Valor
        value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(20)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setStyleSheet('color: #0078d4;')
        layout.addWidget(value_label)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            StatCard {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #ddd;
            }
        """)


class DashboardTab(QWidget):
    """Aba de Dashboard"""
    
    def __init__(self, SessionLocal):
        super().__init__()
        self.SessionLocal = SessionLocal
        
        self.init_ui()
        self.carregar_dados()
        
    def init_ui(self):
        """Inicializa a interface"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title_label = QLabel('Dashboard - Visão Geral')
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Data atual
        hoje = datetime.now()
        date_label = QLabel(hoje.strftime('%B de %Y').capitalize())
        date_label.setStyleSheet('color: #666; font-size: 12pt;')
        layout.addWidget(date_label)
        
        layout.addSpacing(10)
        
        # Grid de cards
        cards_layout = QGridLayout()
        cards_layout.setSpacing(15)
        
        # Cards de estatísticas (serão populados em carregar_dados)
        self.card_visitantes_mes = StatCard('Visitantes este mês', '0', '👥')
        self.card_receita_mes = StatCard('Receita este mês', 'R$ 0,00', '💰')
        self.card_empresas = StatCard('Empresas ativas', '0', '🏢')
        self.card_embarcacoes = StatCard('Embarcações ativas', '0', '⛵')
        
        cards_layout.addWidget(self.card_visitantes_mes, 0, 0)
        cards_layout.addWidget(self.card_receita_mes, 0, 1)
        cards_layout.addWidget(self.card_empresas, 1, 0)
        cards_layout.addWidget(self.card_embarcacoes, 1, 1)
        
        layout.addLayout(cards_layout)
        
        # Resumo detalhado
        layout.addSpacing(20)
        
        detail_title = QLabel('Detalhamento do mês atual')
        detail_title.setStyleSheet('font-size: 13pt; font-weight: bold;')
        layout.addWidget(detail_title)
        
        # Frame com detalhes
        self.detail_frame = QFrame()
        self.detail_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        self.detail_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #ddd;
                padding: 20px;
            }
        """)
        
        detail_layout = QVBoxLayout()
        detail_layout.setSpacing(10)
        
        self.label_estrangeiros = QLabel('Estrangeiros: 0')
        self.label_mercosul = QLabel('Mercosul: 0')
        self.label_brasileiros = QLabel('Brasileiros: 0')
        self.label_entorno = QLabel('Comunidade do Entorno: 0')
        self.label_isentos = QLabel('Isentos: 0')
        self.label_total_registros = QLabel('Total de registros: 0')
        
        for label in [self.label_estrangeiros, self.label_mercosul, 
                     self.label_brasileiros, self.label_entorno, 
                     self.label_isentos, self.label_total_registros]:
            label.setStyleSheet('font-size: 11pt; padding: 5px;')
            detail_layout.addWidget(label)
        
        self.detail_frame.setLayout(detail_layout)
        layout.addWidget(self.detail_frame)
        
        # Botão de atualizar
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_atualizar = QPushButton('🔄 Atualizar Dashboard')
        self.btn_atualizar.setMinimumHeight(40)
        self.btn_atualizar.setMinimumWidth(200)
        self.btn_atualizar.clicked.connect(self.carregar_dados)
        self.btn_atualizar.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #006cc1;
            }
        """)
        btn_layout.addWidget(self.btn_atualizar)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
    def carregar_dados(self):
        """Carrega os dados do dashboard"""
        session = self.SessionLocal()
        
        try:
            # Data atual
            hoje = date.today()
            ano = hoje.year
            mes = hoje.month
            
            # Buscar resumo mensal
            resumo = RegistroVisitaService.relatorio_mensal(session, ano, mes)
            
            # Atualizar cards (ícone=0, título=1, valor=2)
            labels_visitantes = self.card_visitantes_mes.findChildren(QLabel)
            labels_visitantes[2].setText(f"{resumo['total_visitantes']:,}".replace(',', '.'))
            
            labels_receita = self.card_receita_mes.findChildren(QLabel)
            labels_receita[2].setText(f"R$ {resumo['receita_total']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            
            # Contar empresas e embarcações ativas
            qtd_empresas = session.query(Empresa).filter_by(ativo=True).count()
            qtd_embarcacoes = session.query(Embarcacao).filter_by(ativo=True).count()
            
            labels_empresas = self.card_empresas.findChildren(QLabel)
            labels_empresas[2].setText(str(qtd_empresas))
            
            labels_embarcacoes = self.card_embarcacoes.findChildren(QLabel)
            labels_embarcacoes[2].setText(str(qtd_embarcacoes))
            
            # Atualizar detalhes
            self.label_estrangeiros.setText(
                f"Estrangeiros: {resumo['total_estrangeiros']:,}".replace(',', '.')
            )
            self.label_mercosul.setText(
                f"Mercosul: {resumo['total_mercosul']:,}".replace(',', '.')
            )
            self.label_brasileiros.setText(
                f"Brasileiros: {resumo['total_brasileiros']:,}".replace(',', '.')
            )
            self.label_entorno.setText(
                f"Comunidade do Entorno: {resumo['total_entorno']:,}".replace(',', '.')
            )
            self.label_isentos.setText(
                f"Isentos: {resumo['total_isentos']:,}".replace(',', '.')
            )
            self.label_total_registros.setText(
                f"Total de registros: {resumo['quantidade_registros']:,}".replace(',', '.')
            )
            
        except Exception as e:
            print(f"Erro ao carregar dados do dashboard: {e}")
        finally:
            session.close()
