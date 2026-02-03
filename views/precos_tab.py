"""Aba de Tabela de Preços com ajuste rápido anual"""
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from datetime import datetime
from models.services import TabelaPrecoService, LogService
from utils.validators import Formatadores

class PrecosTab(QWidget):
    def __init__(self, SessionLocal, usuario_logado):
        super().__init__()
        self.SessionLocal = SessionLocal
        self.usuario_logado = usuario_logado
        self.init_ui()
        self.carregar_precos()
    
    def init_ui(self):
        main_layout = QHBoxLayout()
        
        # --- Lado Esquerdo: Histórico ---
        list_layout = QVBoxLayout()
        list_layout.addWidget(QLabel('<b>Histórico de Preços</b>'))
        list_layout.addWidget(QLabel('As tabelas são aplicadas conforme o ano da visita.'))
        
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            'Ano Início', 'Ano Fim', 'Estrangeiro', 'Mercosul',
            'Brasileiro', 'Entorno', 'Fundeio <8m', 'Fundeio 8-15m', 'Fundeio >15m'
        ])
        header = self.table.horizontalHeader()
        for i in range(9):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            
        list_layout.addWidget(self.table)
        main_layout.addLayout(list_layout, 3)
        
        # --- Lado Direito: Ajuste Rápido ---
        form_group = QGroupBox("⚡ Ajuste Rápido de Preços")
        form_group.setFixedWidth(300)
        form_layout = QFormLayout()
        
        self.input_ano = QSpinBox()
        self.input_ano.setRange(2020, 2100)
        self.input_ano.setValue(datetime.now().year)
        form_layout.addRow("Ano Vigente:", self.input_ano)
        
        self.input_estrangeiro = QDoubleSpinBox()
        self.input_estrangeiro.setRange(0, 9999)
        self.input_estrangeiro.setPrefix("R$ ")
        self.input_estrangeiro.setDecimals(2)
        form_layout.addRow("Estrangeiro:", self.input_estrangeiro)
        
        self.input_mercosul = QDoubleSpinBox()
        self.input_mercosul.setRange(0, 9999)
        self.input_mercosul.setPrefix("R$ ")
        self.input_mercosul.setDecimals(2)
        form_layout.addRow("Mercosul:", self.input_mercosul)
        
        self.input_brasileiro = QDoubleSpinBox()
        self.input_brasileiro.setRange(0, 9999)
        self.input_brasileiro.setPrefix("R$ ")
        self.input_brasileiro.setDecimals(2)
        form_layout.addRow("Brasileiro:", self.input_brasileiro)
        
        self.input_entorno = QDoubleSpinBox()
        self.input_entorno.setRange(0, 9999)
        self.input_entorno.setPrefix("R$ ")
        self.input_entorno.setDecimals(2)
        form_layout.addRow("Entorno:", self.input_entorno)
        
        self.input_fundeio_ate8 = QDoubleSpinBox()
        self.input_fundeio_ate8.setRange(0, 9999)
        self.input_fundeio_ate8.setPrefix("R$ ")
        self.input_fundeio_ate8.setDecimals(2)
        form_layout.addRow("Fundeio < 8m:", self.input_fundeio_ate8)
        
        self.input_fundeio_8a15 = QDoubleSpinBox()
        self.input_fundeio_8a15.setRange(0, 9999)
        self.input_fundeio_8a15.setPrefix("R$ ")
        self.input_fundeio_8a15.setDecimals(2)
        form_layout.addRow("Fundeio 8-15m:", self.input_fundeio_8a15)
        
        self.input_fundeio_acima15 = QDoubleSpinBox()
        self.input_fundeio_acima15.setRange(0, 9999)
        self.input_fundeio_acima15.setPrefix("R$ ")
        self.input_fundeio_acima15.setDecimals(2)
        form_layout.addRow("Fundeio > 15m:", self.input_fundeio_acima15)
        
        self.btn_salvar = QPushButton("✅ Aplicar Novos Preços")
        self.btn_salvar.setStyleSheet("background-color: #0078d4; color: white; font-weight: bold; padding: 8px;")
        self.btn_salvar.clicked.connect(self.aplicar_precos)
        form_layout.addRow(self.btn_salvar)
        
        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)
        
        self.setLayout(main_layout)

    def carregar_precos(self):
        session = self.SessionLocal()
        try:
            precos = TabelaPrecoService.listar_ativas(session)
            self.table.setRowCount(0)
            
            # Preencher formulário com os valores mais recentes se houver
            if precos:
                p_atual = precos[0]
                self.input_estrangeiro.setValue(p_atual.valor_estrangeiro)
                self.input_mercosul.setValue(p_atual.valor_mercosul)
                self.input_brasileiro.setValue(p_atual.valor_brasileiro)
                self.input_entorno.setValue(p_atual.valor_entorno)
                self.input_fundeio_ate8.setValue(p_atual.valor_fundeio_ate8 or 0)
                self.input_fundeio_8a15.setValue(p_atual.valor_fundeio_8a15 or 0)
                self.input_fundeio_acima15.setValue(p_atual.valor_fundeio_acima15 or 0)

            for p in precos:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(p.ano_inicio)))
                self.table.setItem(row, 1, QTableWidgetItem(str(p.ano_fim) if p.ano_fim else 'Atual'))
                self.table.setItem(row, 2, QTableWidgetItem(Formatadores.formatar_moeda(p.valor_estrangeiro)))
                self.table.setItem(row, 3, QTableWidgetItem(Formatadores.formatar_moeda(p.valor_mercosul)))
                self.table.setItem(row, 4, QTableWidgetItem(Formatadores.formatar_moeda(p.valor_brasileiro)))
                self.table.setItem(row, 5, QTableWidgetItem(Formatadores.formatar_moeda(p.valor_entorno)))
                self.table.setItem(row, 6, QTableWidgetItem(Formatadores.formatar_moeda(p.valor_fundeio_ate8) if p.valor_fundeio_ate8 else '-'))
                self.table.setItem(row, 7, QTableWidgetItem(Formatadores.formatar_moeda(p.valor_fundeio_8a15) if p.valor_fundeio_8a15 else '-'))
                self.table.setItem(row, 8, QTableWidgetItem(Formatadores.formatar_moeda(p.valor_fundeio_acima15) if p.valor_fundeio_acima15 else '-'))
        finally:
            session.close()

    def aplicar_precos(self):
        ano_novo = self.input_ano.value()
        
        reply = QMessageBox.question(self, 'Confirmar Alteração', 
                                   f"Deseja aplicar estes preços como tabela vigente para {ano_novo}?\n"
                                   "Isso encerrará a tabela anterior.",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.No:
            return
            
        session = self.SessionLocal()
        try:
            # 1. Buscar tabela atual e encerrar se for ano diferente
            todas = TabelaPrecoService.listar_ativas(session)
            if todas:
                p_anterior = todas[0]
                if p_anterior.ano_inicio == ano_novo:
                    # Apenas atualizar se for o mesmo ano
                    TabelaPrecoService.atualizar(session, p_anterior.id, 
                        valor_estrangeiro=self.input_estrangeiro.value(),
                        valor_mercosul=self.input_mercosul.value(),
                        valor_brasileiro=self.input_brasileiro.value(),
                        valor_entorno=self.input_entorno.value(),
                        valor_fundeio_ate8=self.input_fundeio_ate8.value(),
                        valor_fundeio_8a15=self.input_fundeio_8a15.value(),
                        valor_fundeio_acima15=self.input_fundeio_acima15.value()
                    )
                else:
                    # Encerrar anterior e criar nova
                    if p_anterior.ano_fim is None:
                        TabelaPrecoService.atualizar(session, p_anterior.id, ano_fim=ano_novo-1)
                    
                    valores = {
                        'valor_estrangeiro': self.input_estrangeiro.value(),
                        'valor_mercosul': self.input_mercosul.value(),
                        'valor_brasileiro': self.input_brasileiro.value(),
                        'valor_entorno': self.input_entorno.value(),
                        'valor_fundeio_ate8': self.input_fundeio_ate8.value(),
                        'valor_fundeio_8a15': self.input_fundeio_8a15.value(),
                        'valor_fundeio_acima15': self.input_fundeio_acima15.value()
                    }
                    TabelaPrecoService.criar(session, ano_novo, valores)
            else:
                # Primeira tabela
                valores = {
                    'valor_estrangeiro': self.input_estrangeiro.value(),
                    'valor_mercosul': self.input_mercosul.value(),
                    'valor_brasileiro': self.input_brasileiro.value(),
                    'valor_entorno': self.input_entorno.value(),
                    'valor_fundeio_ate8': self.input_fundeio_ate8.value(),
                    'valor_fundeio_8a15': self.input_fundeio_8a15.value(),
                    'valor_fundeio_acima15': self.input_fundeio_acima15.value()
                }
                TabelaPrecoService.criar(session, ano_novo, valores)

            LogService.registrar(session, self.usuario_logado, 'UPDATE', 'tabela_preco_ingresso', 
                               descricao=f"Ajustou preços para o ano {ano_novo}")
            
            QMessageBox.information(self, "Sucesso", "Tabela de preços atualizada!")
            self.carregar_precos()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao aplicar preços:\n{str(e)}")
        finally:
            session.close()
