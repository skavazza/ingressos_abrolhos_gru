"""
Aba de gerenciamento de Empresas
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QDialog, QFormLayout, QLineEdit, QMessageBox, QLabel
)
from PyQt6.QtCore import Qt


from models.services import EmpresaService, EmbarcacaoService
from utils.validators import Validadores, Formatadores, MascaraInput


class EmbarcacaoDialog(QDialog):
    """Dialog para criar/editar embarcação"""
    
    def __init__(self, parent=None, embarcacao=None):
        super().__init__(parent)
        self.embarcacao = embarcacao
        self.init_ui()
        
        if embarcacao:
            self.preencher_dados()
            
    def init_ui(self):
        self.setWindowTitle('Dados da Embarcação')
        layout = QVBoxLayout()
        form = QFormLayout()
        
        self.input_nome = QLineEdit()
        form.addRow('Nome:*', self.input_nome)
        
        self.input_tipo = QLineEdit()
        self.input_tipo.setPlaceholderText('Ex: Lancha, Catamarã, Escuna')
        form.addRow('Tipo:', self.input_tipo)
        
        self.input_capacidade = QLineEdit()
        self.input_capacidade.setPlaceholderText('Nº Passageiros')
        form.addRow('Capacidade (PAX):', self.input_capacidade)
        
        self.input_comprimento = QLineEdit()
        self.input_comprimento.setPlaceholderText('Em metros')
        form.addRow('Comprimento (m):', self.input_comprimento)
        
        self.input_inscricao = QLineEdit()
        form.addRow('Inscrição:', self.input_inscricao)
        
        layout.addLayout(form)
        
        btn_layout = QHBoxLayout()
        btn_cancelar = QPushButton('Cancelar')
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)
        
        btn_salvar = QPushButton('Salvar')
        btn_salvar.clicked.connect(self.accept)
        btn_layout.addWidget(btn_salvar)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
    def preencher_dados(self):
        self.input_nome.setText(self.embarcacao.nome)
        self.input_tipo.setText(self.embarcacao.tipo or '')
        self.input_capacidade.setText(str(self.embarcacao.capacidade_pax or ''))
        self.input_comprimento.setText(str(self.embarcacao.comprimento_m or ''))
        self.input_inscricao.setText(self.embarcacao.inscricao or '')
        
    def get_dados(self):
        capacidade = self.input_capacidade.text().strip()
        comprimento = self.input_comprimento.text().strip().replace(',', '.')
        
        return {
            'nome': self.input_nome.text().strip(),
            'tipo': self.input_tipo.text().strip() or None,
            'capacidade_pax': int(capacidade) if capacidade.isdigit() else None,
            'comprimento_m': float(comprimento) if comprimento else None,
            'inscricao': self.input_inscricao.text().strip() or None
        }


class EmpresaDialog(QDialog):
    """Dialog para criar/editar empresa"""
    
    def __init__(self, parent=None, empresa=None, session=None):
        super().__init__(parent)
        self.empresa = empresa
        self.session = session # Sessão do banco para gerenciar embarcações
        self.init_ui()
        
        if empresa:
            self.preencher_dados()
            self.carregar_embarcacoes()
        else:
            # Se for nova empresa, desabilita aba de embarcações
            self.tab_embarcacoes.setEnabled(False)
            self.label_aviso_emb.setVisible(True)
    
    def init_ui(self):
        """Inicializa interface"""
        self.setWindowTitle('Cadastro de Empresa')
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        
        layout = QVBoxLayout()
        
        # --- Formulário da Empresa ---
        form_group = QDialog(self) # Usando QDialog como container ou QWidget
        # Vou usar um GroupBox para separar
        from PyQt6.QtWidgets import QGroupBox, QTabWidget
        
        self.tabs = QTabWidget()
        
        # Aba 1: Dados da Empresa
        tab_empresa = QWidget()
        form_layout = QVBoxLayout()
        
        form = QFormLayout()
        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText('Nome da empresa')
        form.addRow('Nome:*', self.input_nome)
        
        self.input_cnpj = QLineEdit()
        self.input_cnpj.setPlaceholderText('XX.XXX.XXX/XXXX-XX')
        self.input_cnpj.textChanged.connect(self.on_cnpj_changed)
        form.addRow('CNPJ:', self.input_cnpj)
        
        self.input_contato_nome = QLineEdit()
        form.addRow('Contato (Nome):', self.input_contato_nome)
        
        self.input_contato_telefone = QLineEdit()
        self.input_contato_telefone.setPlaceholderText('(XX) XXXXX-XXXX')
        self.input_contato_telefone.textChanged.connect(self.on_telefone_changed)
        form.addRow('Telefone:', self.input_contato_telefone)
        
        self.input_contato_email = QLineEdit()
        self.input_contato_email.setPlaceholderText('email@exemplo.com')
        form.addRow('E-mail:', self.input_contato_email)
        
        form_layout.addLayout(form)
        form_layout.addStretch()
        tab_empresa.setLayout(form_layout)
        
        self.tabs.addTab(tab_empresa, "Dados da Empresa")
        
        # Aba 2: Embarcações
        self.tab_embarcacoes = QWidget()
        emb_layout = QVBoxLayout()
        
        self.label_aviso_emb = QLabel("Salve a empresa primeiro para adicionar embarcações.")
        self.label_aviso_emb.setStyleSheet("color: gray; font-style: italic;")
        self.label_aviso_emb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_aviso_emb.setVisible(False)
        emb_layout.addWidget(self.label_aviso_emb)
        
        # Tabela de embarcações
        self.table_emb = QTableWidget()
        self.table_emb.setColumnCount(4)
        self.table_emb.setHorizontalHeaderLabels(['ID', 'Nome', 'Tipo', 'Capacidade'])
        self.table_emb.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_emb.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table_emb.setAlternatingRowColors(True)
        self.table_emb.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_emb.doubleClicked.connect(self.editar_embarcacao)
        emb_layout.addWidget(self.table_emb)
        
        # Botões de embarcação
        btn_emb_layout = QHBoxLayout()
        self.btn_add_emb = QPushButton('➕ Adicionar')
        self.btn_add_emb.clicked.connect(self.nova_embarcacao)
        btn_emb_layout.addWidget(self.btn_add_emb)
        
        self.btn_edit_emb = QPushButton('✏️ Editar')
        self.btn_edit_emb.clicked.connect(self.editar_embarcacao)
        btn_emb_layout.addWidget(self.btn_edit_emb)
        
        self.btn_del_emb = QPushButton('🗑️ Remover')
        self.btn_del_emb.clicked.connect(self.remover_embarcacao)
        btn_emb_layout.addWidget(self.btn_del_emb)
        
        emb_layout.addLayout(btn_emb_layout)
        self.tab_embarcacoes.setLayout(emb_layout)
        
        self.tabs.addTab(self.tab_embarcacoes, "Embarcações")
        
        layout.addWidget(self.tabs)
        
        # Botões Globais
        btn_layout = QHBoxLayout()
        
        btn_cancelar = QPushButton('Cancelar')
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)
        
        btn_salvar = QPushButton('Salvar Empresa')
        btn_salvar.clicked.connect(self.accept)
        btn_salvar.setStyleSheet("font-weight: bold;")
        btn_layout.addWidget(btn_salvar)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def on_cnpj_changed(self, text):
        """Aplica máscara ao CNPJ"""
        cursor_pos = self.input_cnpj.cursorPosition()
        formatted = MascaraInput.aplicar_mascara_cnpj(text)
        self.input_cnpj.setText(formatted)
        self.input_cnpj.setCursorPosition(min(cursor_pos + 1, len(formatted)))
    
    def on_telefone_changed(self, text):
        """Aplica máscara ao telefone"""
        cursor_pos = self.input_contato_telefone.cursorPosition()
        formatted = MascaraInput.aplicar_mascara_telefone(text)
        self.input_contato_telefone.setText(formatted)
        self.input_contato_telefone.setCursorPosition(min(cursor_pos + 1, len(formatted)))
    
    def preencher_dados(self):
        """Preenche dados da empresa para edição"""
        self.input_nome.setText(self.empresa.nome)
        self.input_cnpj.setText(self.empresa.cnpj or '')
        self.input_contato_nome.setText(self.empresa.contato_nome or '')
        self.input_contato_telefone.setText(self.empresa.contato_telefone or '')
        self.input_contato_email.setText(self.empresa.contato_email or '')
        
    def carregar_embarcacoes(self):
        """Carrega lista de embarcações"""
        if not self.empresa or not self.session:
            return
            
        embarcacoes = EmbarcacaoService.listar_por_empresa(self.session, self.empresa.id)
        
        self.table_emb.setRowCount(0)
        for emb in embarcacoes:
            row = self.table_emb.rowCount()
            self.table_emb.insertRow(row)
            self.table_emb.setItem(row, 0, QTableWidgetItem(str(emb.id)))
            self.table_emb.setItem(row, 1, QTableWidgetItem(emb.nome))
            self.table_emb.setItem(row, 2, QTableWidgetItem(emb.tipo or '-'))
            self.table_emb.setItem(row, 3, QTableWidgetItem(str(emb.capacidade_pax or '-')))
            
    def nova_embarcacao(self):
        """Adiciona nova embarcação"""
        dialog = EmbarcacaoDialog(self)
        if dialog.exec():
            dados = dialog.get_dados()
            try:
                EmbarcacaoService.criar(self.session, self.empresa.id, **dados)
                self.carregar_embarcacoes()
                QMessageBox.information(self, 'Sucesso', 'Embarcação adicionada!')
            except Exception as e:
                QMessageBox.critical(self, 'Erro', f'Erro ao adicionar embarcação: {e}')

    def editar_embarcacao(self):
        """Edita embarcação selecionada"""
        if not self.table_emb.selectedItems():
            return
            
        row = self.table_emb.currentRow()
        emb_id = int(self.table_emb.item(row, 0).text())
        
        embarcacao = EmbarcacaoService.buscar_por_id(self.session, emb_id)
        if not embarcacao:
            return
            
        dialog = EmbarcacaoDialog(self, embarcacao)
        if dialog.exec():
            dados = dialog.get_dados()
            try:
                EmbarcacaoService.atualizar(self.session, emb_id, **dados)
                self.carregar_embarcacoes()
                QMessageBox.information(self, 'Sucesso', 'Embarcação atualizada!')
            except Exception as e:
                QMessageBox.critical(self, 'Erro', f'Erro ao atualizar: {e}')

    def remover_embarcacao(self):
        """Remove embarcação (inativa)"""
        if not self.table_emb.selectedItems():
            return
            
        row = self.table_emb.currentRow()
        emb_id = int(self.table_emb.item(row, 0).text())
        emb_nome = self.table_emb.item(row, 1).text()
        
        reply = QMessageBox.question(
            self, 'Confirmar', 
            f'Tem certeza que deseja remover a embarcação "{emb_nome}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Soft delete
                EmbarcacaoService.atualizar(self.session, emb_id, ativo=False)
                self.carregar_embarcacoes()
            except Exception as e:
                QMessageBox.critical(self, 'Erro', f'Erro ao remover: {e}')
    
    def validar(self):
        """Valida os dados"""
        if not self.input_nome.text().strip():
            QMessageBox.warning(self, 'Validação', 'Nome da empresa é obrigatória.')
            self.tabs.setCurrentIndex(0) # Volta para aba 1
            self.input_nome.setFocus()
            return False
        
        cnpj = self.input_cnpj.text().strip()
        if cnpj and not Validadores.validar_cnpj(cnpj):
            QMessageBox.warning(self, 'Validação', 'CNPJ inválido.')
            self.tabs.setCurrentIndex(0)
            self.input_cnpj.setFocus()
            return False
        
        email = self.input_contato_email.text().strip()
        if email and not Validadores.validar_email(email):
            QMessageBox.warning(self, 'Validação', 'E-mail inválido.')
            self.tabs.setCurrentIndex(0)
            self.input_contato_email.setFocus()
            return False
        
        return True
    
    def get_dados(self):
        """Retorna os dados do formulário"""
        return {
            'nome': self.input_nome.text().strip(),
            'cnpj': self.input_cnpj.text().strip() or None,
            'contato_nome': self.input_contato_nome.text().strip() or None,
            'contato_telefone': self.input_contato_telefone.text().strip() or None,
            'contato_email': self.input_contato_email.text().strip() or None,
        }


from models.services import EmpresaService, EmbarcacaoService, LogService
from utils.validators import Validadores


class EmpresasTab(QWidget):
    """Aba de gerenciamento de empresas"""
    
    def __init__(self, SessionLocal, usuario_logado):
        super().__init__()
        self.SessionLocal = SessionLocal
        self.usuario_logado = usuario_logado
        
        self.init_ui()
        self.carregar_empresas()
    
    def init_ui(self):
        """Inicializa interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Título
        title = QLabel('Gerenciamento de Empresas')
        title.setStyleSheet('font-size: 14pt; font-weight: bold;')
        layout.addWidget(title)
        
        # Botões de ação
        btn_layout = QHBoxLayout()
        
        self.btn_nova = QPushButton('➕ Nova Empresa')
        self.btn_nova.clicked.connect(self.nova_empresa)
        btn_layout.addWidget(self.btn_nova)
        
        self.btn_editar = QPushButton('✏️ Editar')
        self.btn_editar.clicked.connect(self.editar_empresa)
        btn_layout.addWidget(self.btn_editar)
        
        self.btn_desativar = QPushButton('🚫 Desativar')
        self.btn_desativar.clicked.connect(self.excluir_empresa)
        btn_layout.addWidget(self.btn_desativar)
        
        btn_layout.addStretch()
        
        self.btn_atualizar = QPushButton('🔄 Atualizar')
        self.btn_atualizar.clicked.connect(self.carregar_empresas)
        btn_layout.addWidget(self.btn_atualizar)
        
        layout.addLayout(btn_layout)
        
        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Nome', 'CNPJ', 'Contato', 'Telefone', 'E-mail'
        ])
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(0, 50)  # ID
        self.table.setColumnWidth(1, 250) # Nome
        self.table.setColumnWidth(2, 150) # CNPJ
        self.table.setColumnWidth(3, 150) # Contato
        self.table.setColumnWidth(4, 120) # Telefone
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch) # E-mail stretch to fill
        
        self.table.doubleClicked.connect(self.editar_empresa)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def carregar_empresas(self):
        """Carrega empresas na tabela"""
        session = self.SessionLocal()
        try:
            empresas = EmpresaService.listar_ativas(session)
            
            self.table.setRowCount(0)
            
            for empresa in empresas:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                self.table.setItem(row, 0, QTableWidgetItem(str(empresa.id)))
                self.table.setItem(row, 1, QTableWidgetItem(empresa.nome))
                self.table.setItem(row, 2, QTableWidgetItem(empresa.cnpj or '-'))
                self.table.setItem(row, 3, QTableWidgetItem(empresa.contato_nome or '-'))
                self.table.setItem(row, 4, QTableWidgetItem(empresa.contato_telefone or '-'))
                self.table.setItem(row, 5, QTableWidgetItem(empresa.contato_email or '-'))
        finally:
            session.close()
    
    def nova_empresa(self):
        """Abre dialog para criar nova empresa"""
        dialog = EmpresaDialog(self)
        if dialog.exec() and dialog.validar():
            dados = dialog.get_dados()
            
            session = self.SessionLocal()
            try:
                nova_empresa = EmpresaService.criar(session, **dados)
                
                LogService.registrar(
                    session, self.usuario_logado, 'INSERT', 'empresas', nova_empresa.id,
                    f"Criou empresa: {dados['nome']}"
                )
                
                self.carregar_empresas()
                QMessageBox.information(self, 'Sucesso', 'Empresa cadastrada com sucesso!')
            except Exception as e:
                QMessageBox.critical(self, 'Erro', f'Erro ao salvar: {e}')
            finally:
                session.close()
    
    def editar_empresa(self):
        """Edita empresa selecionada"""
        if not self.table.selectedItems():
            QMessageBox.warning(self, 'Aviso', 'Selecione uma empresa.')
            return
        
        row = self.table.currentRow()
        empresa_id = int(self.table.item(row, 0).text())
        
        session = self.SessionLocal()
        try:
            empresa = EmpresaService.buscar_por_id(session, empresa_id)
            
            # Passando a sessão para o diálogo poder gerenciar as embarcações
            dialog = EmpresaDialog(self, empresa, session=session)
            
            if dialog.exec() and dialog.validar():
                dados = dialog.get_dados()
                EmpresaService.atualizar(session, empresa_id, **dados)
                
                LogService.registrar(
                    session, self.usuario_logado, 'UPDATE', 'empresas', empresa_id,
                    f"Atualizou empresa: {dados['nome']}"
                )
                
                self.carregar_empresas()
                QMessageBox.information(self, 'Sucesso', 'Empresa atualizada!')
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Erro ao atualizar: {e}')
        finally:
            session.close()
    
    def excluir_empresa(self): # Renamed from desativar_empresa
        """Exclui (desativa) empresa selecionada"""
        if not self.table.selectedItems():
            QMessageBox.warning(self, 'Aviso', 'Selecione uma empresa.')
            return
        
        row = self.table.currentRow()
        empresa_id = int(self.table.item(row, 0).text())
        nome = self.table.item(row, 1).text() # Added to get company name
        
        reply = QMessageBox.question(
            self, 'Confirmar Exclusão', # Changed title
            f'Tem certeza que deseja excluir a empresa "{nome}"?', # Changed message
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            session = self.SessionLocal()
            try:
                if EmpresaService.desativar(session, empresa_id): # Added if condition
                    
                    LogService.registrar(
                        session, self.usuario_logado, 'DELETE', 'empresas', empresa_id,
                        f"Desativou empresa: {nome}"
                    )
                    
                    QMessageBox.information(self, 'Sucesso', 'Empresa excluída com sucesso!') # Changed message
                    self.carregar_empresas()
                else: # Added else block
                    QMessageBox.warning(self, 'Erro', 'Empresa não encontrada.')
            except Exception as e:
                QMessageBox.critical(self, 'Erro', f'Erro ao excluir: {e}') # Changed message
            finally:
                session.close()
