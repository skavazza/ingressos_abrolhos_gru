"""Aba de Embarcações"""
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from models.services import EmbarcacaoService, EmpresaService

class EmbarcacoesTab(QWidget):
    def __init__(self, SessionLocal, usuario_logado):
        super().__init__()
        self.SessionLocal = SessionLocal
        self.usuario_logado = usuario_logado
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Embarcações'))
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(['ID', 'Empresa', 'Nome', 'Tipo', 'Capacidade', 'Comprimento', 'Inscrição'])
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.carregar_embarcacoes()
    
    def carregar_embarcacoes(self):
        session = self.SessionLocal()
        try:
            embarcacoes = EmbarcacaoService.listar_ativas(session)
            self.table.setRowCount(0)
            for emb in embarcacoes:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(emb.id)))
                self.table.setItem(row, 1, QTableWidgetItem(emb.empresa.nome if emb.empresa else '-'))
                self.table.setItem(row, 2, QTableWidgetItem(emb.nome))
                self.table.setItem(row, 3, QTableWidgetItem(emb.tipo or '-'))
                self.table.setItem(row, 4, QTableWidgetItem(str(emb.capacidade_pax or '-')))
                self.table.setItem(row, 5, QTableWidgetItem(str(emb.comprimento_m or '-')))
                self.table.setItem(row, 6, QTableWidgetItem(emb.inscricao or '-'))
        finally:
            session.close()
