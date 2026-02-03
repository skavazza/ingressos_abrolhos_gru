"""
Arquivo principal - Aplicação Abrolhos Ingressos
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from views.login_dialog import LoginDialog
from views.main_window import MainWindow


def main():
    """Função principal"""
    app = QApplication(sys.argv)
    app.setApplicationName('Abrolhos Ingressos')
    app.setOrganizationName('ICMBio')
    
    # Configurar estilo global
    app.setStyle('Fusion')
    
    # Tela de login
    login = LoginDialog()
    
    if login.exec():
        # Se login bem-sucedido, abre janela principal em tela cheia
        window = MainWindow(login.usuario_logado, is_admin=getattr(login, 'is_admin', False))
        window.showMaximized()
        sys.exit(app.exec())
    else:
        # Se cancelou login, fecha aplicação
        sys.exit(0)


if __name__ == '__main__':
    main()
