"""
Aba de gerenciamento de Usuários
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QDialog, QFormLayout, QLineEdit, QMessageBox, QLabel, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from models.services import UsuarioService, LogService

class UsuarioDialog(QDialog):
    """Dialog para criar/editar usuário"""
    
    def __init__(self, parent=None, usuario=None):
        super().__init__(parent)
        self.usuario = usuario
        self.init_ui()
        
        if usuario:
            self.preencher_dados()
    
    def init_ui(self):
        """Inicializa interface"""
        self.setWindowTitle('Cadastro de Usuário')
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText('Login do usuário')
        form.addRow('Usuário:*', self.input_username)
        
        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText('Nome completo')
        form.addRow('Nome Completo:', self.input_nome)
        
        # Senha
        self.input_senha = QLineEdit()
        self.input_senha.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_senha.setPlaceholderText('Senha')
        form.addRow('Senha:*', self.input_senha)
        
        self.input_confirma_senha = QLineEdit()
        self.input_confirma_senha.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_confirma_senha.setPlaceholderText('Confirmar Senha')
        form.addRow('Confirmar Senha:*', self.input_confirma_senha)
        
        # Checkbox Ativo
        self.check_ativo = QCheckBox("Usuário Ativo")
        self.check_ativo.setChecked(True)
        form.addRow('', self.check_ativo)
        
        # Checkbox Admin
        self.check_admin = QCheckBox("Administrador")
        form.addRow('', self.check_admin)
        
        layout.addLayout(form)
        
        if self.usuario:
            self.input_username.setReadOnly(True) # Não permite alterar username
            self.input_senha.setPlaceholderText('Deixe em branco para manter')
            self.input_confirma_senha.setPlaceholderText('Deixe em branco para manter')
            form.labelForField(self.input_senha).setText('Senha (Opcional):')
            form.labelForField(self.input_confirma_senha).setText('Confirmar (Opcional):')
        
        # Botões
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
        """Preenche dados para edição"""
        self.input_username.setText(self.usuario.username)
        self.input_nome.setText(self.usuario.nome_completo or '')
        self.check_ativo.setChecked(self.usuario.ativo)
        self.check_admin.setChecked(self.usuario.is_admin)
        
    def get_dados(self):
        """Retorna os dados do formulário"""
        return {
            'username': self.input_username.text().strip(),
            'nome_completo': self.input_nome.text().strip() or None,
            'senha': self.input_senha.text(),
            'ativo': self.check_ativo.isChecked(),
            'is_admin': self.check_admin.isChecked()
        }
        
    def validar(self):
        """Valida os dados"""
        if not self.input_username.text().strip():
            QMessageBox.warning(self, 'Validação', 'Usuário é obrigatório.')
            return False
            
        senha = self.input_senha.text()
        confirma = self.input_confirma_senha.text()
        
        if self.usuario:
            # Edição: Senha é opcional
            if senha or confirma:
                if senha != confirma:
                    QMessageBox.warning(self, 'Validação', 'As senhas não conferem.')
                    return False
        else:
            # Criação: Senha é obrigatória
            if not senha:
                QMessageBox.warning(self, 'Validação', 'Senha é obrigatória.')
                return False
            if senha != confirma:
                QMessageBox.warning(self, 'Validação', 'As senhas não conferem.')
                return False
                
        return True


class UsuariosTab(QWidget):
    """Aba de gerenciamento de usuários"""
    
    def __init__(self, SessionLocal, usuario_logado):
        super().__init__()
        self.SessionLocal = SessionLocal
        self.usuario_logado = usuario_logado
        
        self.init_ui()
        self.carregar_usuarios()
    
    def init_ui(self):
        """Inicializa interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Título
        title = QLabel('Gerenciamento de Usuários')
        title.setStyleSheet('font-size: 14pt; font-weight: bold;')
        layout.addWidget(title)
        
        # Botões de ação
        btn_layout = QHBoxLayout()
        
        self.btn_novo = QPushButton('➕ Novo Usuário')
        self.btn_novo.clicked.connect(self.novo_usuario)
        btn_layout.addWidget(self.btn_novo)
        
        self.btn_editar = QPushButton('✏️ Editar')
        self.btn_editar.clicked.connect(self.editar_usuario)
        btn_layout.addWidget(self.btn_editar)
        
        self.btn_desativar = QPushButton('🗑️ Desativar')
        self.btn_desativar.setStyleSheet('background-color: #d9534f; color: white;')
        self.btn_desativar.clicked.connect(self.desativar_usuario)
        btn_layout.addWidget(self.btn_desativar)
        
        btn_layout.addStretch()
        
        self.btn_atualizar = QPushButton('🔄 Atualizar Lista')
        self.btn_atualizar.clicked.connect(self.carregar_usuarios)
        btn_layout.addWidget(self.btn_atualizar)
        
        layout.addLayout(btn_layout)
        
        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Usuário', 'Nome Completo', 'Admin', 'Status'
        ])
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        self.table.doubleClicked.connect(self.editar_usuario)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def carregar_usuarios(self):
        """Carrega usuários na tabela"""
        session = self.SessionLocal()
        try:
            usuarios = UsuarioService.listar_usuarios(session)
            
            self.table.setRowCount(0)
            
            for u in usuarios:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                self.table.setItem(row, 0, QTableWidgetItem(str(u.id)))
                self.table.setItem(row, 1, QTableWidgetItem(u.username))
                self.table.setItem(row, 2, QTableWidgetItem(u.nome_completo or '-'))
                
                # Admin check
                admin_item = QTableWidgetItem('Sim' if u.is_admin else 'Não')
                if u.is_admin:
                    admin_item.setFont(QFont('Arial', 9, QFont.Weight.Bold))
                self.table.setItem(row, 3, admin_item)
                
                status_item = QTableWidgetItem('Ativo' if u.ativo else 'Inativo')
                if not u.ativo:
                    status_item.setForeground(Qt.GlobalColor.red)
                else:
                    status_item.setForeground(Qt.GlobalColor.green)
                self.table.setItem(row, 4, status_item)
        finally:
            session.close()
            
    def novo_usuario(self):
        """Cria novo usuário"""
        dialog = UsuarioDialog(self)
        if dialog.exec() and dialog.validar():
            dados = dialog.get_dados()
            
            session = self.SessionLocal()
            try:
                # Verifica se usuário já existe
                from models.database import Usuario
                if session.query(Usuario).filter_by(username=dados['username']).first():
                    QMessageBox.warning(self, 'Erro', 'Usuário já existe!')
                    return
                
                novo_user = UsuarioService.criar_usuario(
                    session, 
                    username=dados['username'], 
                    password=dados['senha'], 
                    nome_completo=dados['nome_completo'],
                    is_admin=dados['is_admin']
                )
                
                # Log
                LogService.registrar(
                    session, self.usuario_logado, 'INSERT', 'usuarios', novo_user.id,
                    f"Criou usuário: {dados['username']}"
                )
                
                QMessageBox.information(self, 'Sucesso', 'Usuário criado com sucesso!')
                self.carregar_usuarios()
            except Exception as e:
                QMessageBox.critical(self, 'Erro', f'Erro ao criar usuário: {e}')
            finally:
                session.close()

    def editar_usuario(self):
        """Edita usuário selecionado"""
        if not self.table.selectedItems():
            return
            
        row = self.table.currentRow()
        user_id = int(self.table.item(row, 0).text())
        
        session = self.SessionLocal()
        try:
            usuario = UsuarioService.buscar_por_id(session, user_id)
            if not usuario:
                return
                
            dialog = UsuarioDialog(self, usuario)
            if dialog.exec() and dialog.validar():
                dados = dialog.get_dados()
                
                # Atualizar dados básicos
                UsuarioService.atualizar_usuario(
                    session, 
                    user_id, 
                    nome_completo=dados['nome_completo'],
                    ativo=dados['ativo'],
                    is_admin=dados['is_admin']
                )
                
                desc_log = f"Atualizou usuário {usuario.username}. "
                
                # Atualizar senha se fornecida
                if dados['senha']:
                    UsuarioService.atualizar_senha(session, user_id, dados['senha'])
                    desc_log += "Senha alterada."
                
                # Log
                LogService.registrar(
                    session, self.usuario_logado, 'UPDATE', 'usuarios', user_id, desc_log
                )
                    
                QMessageBox.information(self, 'Sucesso', 'Usuário atualizado!')
                self.carregar_usuarios()
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Erro ao atualizar: {e}')
        finally:
            session.close()

    def desativar_usuario(self):
        """Desativa o usuário selecionado"""
        if not self.table.selectedItems():
            QMessageBox.warning(self, 'Aviso', 'Selecione um usuário para desativar.')
            return
            
        row = self.table.currentRow()
        user_id = int(self.table.item(row, 0).text())
        username = self.table.item(row, 1).text()
        
        confirm = QMessageBox.question(
            self, 'Confirmar', 
            f'Tem certeza que deseja desativar o usuário "{username}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            session = self.SessionLocal()
            try:
                UsuarioService.desativar_usuario(session, user_id)
                
                LogService.registrar(
                    session, self.usuario_logado, 'Ativo=False', 'usuarios', user_id,
                    f"Desativou usuário: {username}"
                )
                
                self.carregar_usuarios()
                QMessageBox.information(self, 'Sucesso', 'Usuário desativado.')
            except Exception as e:
                QMessageBox.critical(self, 'Erro', f'Erro ao desativar: {e}')
            finally:
                session.close()
