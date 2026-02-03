"""
Tela de login do sistema
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap

from models.database import init_db
from models.services import UsuarioService


class LoginDialog(QDialog):
    """Dialog de login"""
    
    login_successful = pyqtSignal(str)  # Emite o username quando login é bem-sucedido
    
    def __init__(self, db_path: str = 'abrolhos_ingressos.db'):
        super().__init__()
        self.db_path = db_path
        self.engine, self.SessionLocal = init_db(db_path)
        self.usuario_logado = None
        
        self.init_ui()
        
    def init_ui(self):
        """Inicializa a interface do usuário"""
        self.setWindowTitle('Abrolhos Ingressos - Login')
        self.setObjectName("LoginDialog")  # Nome para o stylesheet
        self.setFixedSize(450, 500)
        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint) # Remove ? button
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)  # Força pintura do background
        self.setModal(True)
        
        # Layout principal
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Logo (Placeholder)
        # Se houver um arquivo de logo, ele seria carregado aqui
        logo_label = QLabel()
        pixmap = QPixmap('assets/logo.png') 
        logo_label.setPixmap(pixmap.scaled(140, 140, Qt.AspectRatioMode.KeepAspectRatio))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)
        
        # Título
        title_label = QLabel('BEM-VINDO')
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Subtítulo
        subtitle_label = QLabel('Sistema de Registro de Ingressos\nParque Nacional Marinho dos Abrolhos')
        subtitle_label.setObjectName("subtitle_label")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setWordWrap(True)
        layout.addWidget(subtitle_label)
        
        layout.addSpacing(30)
        
        # Container do formulário
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(10)
        
        # Campo de usuário
        user_label = QLabel('USUÁRIO')
        user_label.setObjectName("field_label")
        form_layout.addWidget(user_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Digite seu usuário')
        self.username_input.setMinimumHeight(45)
        form_layout.addWidget(self.username_input)
        
        # Campo de senha
        password_label = QLabel('SENHA')
        password_label.setObjectName("field_label")
        form_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Digite sua senha')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(45)
        self.password_input.returnPressed.connect(self.do_login)
        form_layout.addWidget(self.password_input)
        
        layout.addWidget(form_container)
        
        layout.addSpacing(20)
        
        # Botões
        self.login_button = QPushButton('ENTRAR')
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.setMinimumHeight(50)
        self.login_button.setDefault(True)
        self.login_button.clicked.connect(self.do_login)
        layout.addWidget(self.login_button)
        
        self.cancel_button = QPushButton('Cancelar')
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_button.setFlat(True)
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.cancel_button)
        
        layout.addStretch()
        
        # Informação de versão
        version_label = QLabel('v1.0 - ICMBio/PARNA Abrolhos')
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setObjectName("version_label")
        layout.addWidget(version_label)
        
        self.setLayout(layout)
        
        # Aplicar estilo
        self.apply_style()
        
        # Foco inicial no campo de usuário
        self.username_input.setFocus()
    
    def apply_style(self):
        """Aplica estilo visual ao dialog"""
        self.setStyleSheet("""
            #LoginDialog {
                background-color: #ffffff;
            }
            QLabel#title_label {
                color: #1a1a1a;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel#subtitle_label {
                color: #666666;
                font-size: 14px;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel#field_label {
                color: #555555;
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }
            QLabel#version_label {
                color: #999999;
                font-size: 10px;
            }
            QLineEdit {
                padding: 0 15px;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: #f9f9f9;
                font-size: 14px;
                color: #333;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton#cancel_button {
                background-color: transparent;
                color: #666666;
                font-size: 13px;
                font-weight: normal;
                border: none;
            }
            QPushButton#cancel_button:hover {
                color: #333333;
                text-decoration: underline;
            }
        """)
        
        self.cancel_button.setObjectName('cancel_button')
    
    def do_login(self):
        """Executa o processo de login"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(
                self,
                'Campos obrigatórios',
                'Por favor, preencha usuário e senha.'
            )
            return
        
        # Tenta autenticar
        session = self.SessionLocal()
        try:
            usuario = UsuarioService.autenticar(session, username, password)
            
            if usuario:
                self.usuario_logado = usuario.username
                self.is_admin = usuario.is_admin
                self.login_successful.emit(usuario.username)
                self.accept()
            else:
                QMessageBox.critical(
                    self,
                    'Erro de autenticação',
                    'Usuário ou senha inválidos.'
                )
                self.password_input.clear()
                self.password_input.setFocus()
        except Exception as e:
            QMessageBox.critical(
                self,
                'Erro',
                f'Erro ao autenticar: {str(e)}'
            )
        finally:
            session.close()
