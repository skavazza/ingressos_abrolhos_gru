"""
Janela principal do sistema Abrolhos Ingressos
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QMenuBar, QMenu, QStatusBar, QMessageBox, QLabel, QPushButton,
    QFileDialog
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QFont, QIcon
from datetime import datetime
import shutil
import os

from models.database import init_db


class MainWindow(QMainWindow):
    """Janela principal do sistema"""
    
    def __init__(self, usuario_logado: str, is_admin: bool = False, db_path: str = 'abrolhos_ingressos.db'):
        super().__init__()
        
        self.usuario_logado = usuario_logado
        self.is_admin = is_admin
        self.db_path = db_path
        self.engine, self.SessionLocal = init_db(db_path)
        
        self.init_ui()
        
    def init_ui(self):
        """Inicializa a interface do usuário"""
        self.setWindowTitle('Abrolhos Ingressos - Sistema de Gestão')
        self.setMinimumSize(1200, 700)
        
        # Definir Ícone
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Criar menu bar
        self.create_menu_bar()
        
        # Widget central com tabs
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Criar abas principais
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        
        # Importar e adicionar as abas
        from views.dashboard_tab import DashboardTab
        from views.empresas_tab import EmpresasTab
        from views.embarcacoes_tab import EmbarcacoesTab
        from views.precos_tab import PrecosTab
        from views.registros_tab import RegistrosTab
        from views.relatorios_tab import RelatoriosTab
        from views.usuarios_tab import UsuariosTab
        
        self.dashboard_tab = DashboardTab(self.SessionLocal)
        self.empresas_tab = EmpresasTab(self.SessionLocal, self.usuario_logado)
        self.embarcacoes_tab = EmbarcacoesTab(self.SessionLocal, self.usuario_logado)
        self.precos_tab = PrecosTab(self.SessionLocal, self.usuario_logado)
        self.registros_tab = RegistrosTab(self.SessionLocal, self.usuario_logado)
        self.relatorios_tab = RelatoriosTab(self.SessionLocal) # Relatórios apenas leitura ou log interno
        self.usuarios_tab = UsuariosTab(self.SessionLocal, self.usuario_logado)
        
        self.tabs.addTab(self.dashboard_tab, '📊 Dashboard')
        self.tabs.addTab(self.registros_tab, '📝 Registros Diários')
        self.tabs.addTab(self.empresas_tab, '🏢 Empresas')
        self.tabs.addTab(self.embarcacoes_tab, '⛵ Embarcações')
        self.tabs.addTab(self.precos_tab, '💰 Tabela de Preços')
        self.tabs.addTab(self.relatorios_tab, '📈 Relatórios')
        
        if self.is_admin:
            self.tabs.addTab(self.usuarios_tab, '👥 Usuários')
        
        layout.addWidget(self.tabs)
        self.central_widget.setLayout(layout)
        
        # Criar status bar
        self.create_status_bar()
        
        # Aplicar estilo
        self.apply_style()
        
    def create_menu_bar(self):
        """Cria a barra de menu"""
        menubar = self.menuBar()
        
        # Menu Arquivo
        file_menu = menubar.addMenu('&Arquivo')
        
        backup_action = QAction('&Backup do Banco de Dados', self)
        backup_action.setShortcut('Ctrl+B')
        backup_action.triggered.connect(self.fazer_backup)
        file_menu.addAction(backup_action)

        import_action = QAction('&Importar Registros (CSV)', self)
        import_action.setShortcut('Ctrl+I')
        import_action.triggered.connect(self.importar_csv)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('&Sair', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Ferramentas
        tools_menu = menubar.addMenu('&Ferramentas')
        
        atualizar_action = QAction('&Atualizar Dados', self)
        atualizar_action.setShortcut('F5')
        atualizar_action.triggered.connect(self.atualizar_dados)
        tools_menu.addAction(atualizar_action)
        
        # Menu Ajuda
        help_menu = menubar.addMenu('&Ajuda')
        
        about_action = QAction('&Sobre', self)
        about_action.triggered.connect(self.mostrar_sobre)
        help_menu.addAction(about_action)
        
    def create_status_bar(self):
        """Cria a barra de status"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Label do usuário
        user_label = QLabel(f'Usuário: {self.usuario_logado}')
        user_label.setStyleSheet('padding: 5px;')
        self.statusBar.addPermanentWidget(user_label)
        
        # Label da data/hora
        self.datetime_label = QLabel()
        self.datetime_label.setStyleSheet('padding: 5px;')
        self.statusBar.addPermanentWidget(self.datetime_label)
        
        # Atualizar data/hora a cada segundo
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)
        self.update_datetime()
        
        self.statusBar.showMessage('Sistema iniciado com sucesso')
        
    def update_datetime(self):
        """Atualiza o label de data/hora"""
        now = datetime.now()
        self.datetime_label.setText(now.strftime('%d/%m/%Y %H:%M:%S'))
        
    def fazer_backup(self):
        """Realiza backup do banco de dados"""
        try:
            # Abre dialog para escolher onde salvar
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                'Salvar Backup do Banco de Dados',
                f'abrolhos_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db',
                'Database Files (*.db)'
            )
            
            if file_path:
                # Copia o arquivo do banco
                shutil.copy2(self.db_path, file_path)
                
                QMessageBox.information(
                    self,
                    'Backup realizado',
                    f'Backup salvo com sucesso em:\n{file_path}'
                )
                
                self.statusBar.showMessage(f'Backup realizado: {os.path.basename(file_path)}', 5000)
                
        except Exception as e:
            QMessageBox.critical(
                self,
                'Erro no backup',
                f'Erro ao realizar backup:\n{str(e)}'
            )
            
    def atualizar_dados(self):
        """Atualiza os dados em todas as abas"""
        try:
            # Atualiza cada aba
            self.dashboard_tab.carregar_dados()
            self.empresas_tab.carregar_empresas()
            self.embarcacoes_tab.carregar_embarcacoes()
            self.precos_tab.carregar_precos()
            self.registros_tab.carregar_registros()
            
            self.statusBar.showMessage('Dados atualizados', 3000)
            
        except Exception as e:
            QMessageBox.warning(
                self,
                'Erro ao atualizar',
                f'Erro ao atualizar dados:\n{str(e)}'
            )
            
    def mostrar_sobre(self):
        """Mostra dialog sobre o sistema"""
        about_text = """
        <h2>Sistema de Registro de Ingressos</h2>
        <h3>Parque Nacional Marinho dos Abrolhos</h3>
        <p><b>Versão:</b> 1.0</p>
        <p><b>Desenvolvido para:</b> NGI ICMBio Abrolhos</p>
        <p><b>Desenvolvido por:</b> Alberto Rodrigues</p>
        <p><b>Contato:</b> betorodrigues@msn.com</p>
        <p>Sistema desktop para gerenciamento de empresas de turismo, 
        embarcações e registros de visitação no PARNA Abrolhos.</p>
        <p><b>Copyright:</b> (C) 2026 Alberto Rodrigues</p>
        <p><b>Tecnologias:</b><br>
        - Python 3.10+<br>
        - PyQt6<br>
        - SQLAlchemy<br>
        - SQLite</p>
        """
        
        QMessageBox.about(self, 'Sobre o Sistema', about_text)
        
    def apply_style(self):
        """Aplica estilo visual à janela"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #ccc;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #0078d4;
            }
            QTabBar::tab:hover {
                background-color: #d0d0d0;
            }
            QMenuBar {
                background-color: #f0f0f0;
                padding: 5px;
            }
            QMenuBar::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QStatusBar {
                background-color: #e0e0e0;
                color: #333;
            }
        """)
        
    def closeEvent(self, event):
        """Sobrescreve o evento de fechamento"""
        reply = QMessageBox.question(
            self,
            'Confirmar saída',
            'Deseja realmente sair do sistema?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def importar_csv(self):
        """Importa registros de um arquivo CSV"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                'Importar Registros (CSV)',
                '',
                'Arquivos CSV (*.csv);;Todos os Arquivos (*)'
            )
            
            if not file_path:
                return
                
            # Importar pandas aqui para não pesar na inicialização se não for usado
            import pandas as pd
            from models.database import Empresa, Embarcacao
            from models.services import RegistroVisitaService
            from sqlalchemy import func
            
            # Ler CSV
            try:
                df = pd.read_csv(file_path)
            except Exception as e:
                QMessageBox.critical(self, 'Erro ao ler arquivo', f'Não foi possível ler o arquivo CSV:\n{str(e)}')
                return
            
            # Normalizar colunas (remover espaços e converter para minúsculas para verificação)
            df.columns = df.columns.str.strip().str.lower()
            
            # Mapeamento de colunas esperadas para colunas internas
            colunas_map = {
                'data': 'data',
                'empresa': 'empresa',
                'embarcacao': 'embarcacao', # ou embarcação
                'embarcação': 'embarcacao',
                'permanencia': 'permanencia', # ou permanência
                'permanência': 'permanencia',
                'estrangeiros': 'qtde_estrangeiros',
                'mercosul': 'qtde_mercosul',
                'brasileiros': 'qtde_brasileiros',
                'entorno': 'qtde_entorno',
                'isentos': 'qtde_isentos'
            }
            
            # Verificar colunas obrigatórias
            colunas_encontradas = {}
            for col_csv in df.columns:
                if col_csv in colunas_map:
                    colunas_encontradas[colunas_map[col_csv]] = col_csv
            
            required = ['data', 'empresa', 'embarcacao', 'permanencia']
            missing = [req for req in required if req not in colunas_encontradas]
            
            if missing:
                QMessageBox.warning(
                    self, 
                    'Colunas faltando', 
                    f'O arquivo CSV deve conter as colunas:\n{", ".join(missing)}\n\n'
                    f'Colunas encontradas: {", ".join(df.columns)}'
                )
                return
            
            session = self.SessionLocal()
            sucessos = 0
            erros = []
            
            # Para rastrear o intervalo de datas importado
            min_date = None
            max_date = None
            
            try:
                for index, row in df.iterrows():
                    linha = index + 2  # +1 do header, +1 do índice 0-based
                    
                    try:
                        # 1. Parse Data
                        data_str = str(row[colunas_encontradas['data']])
                        try:
                            # Tenta dd/mm/yyyy
                            data_visita = datetime.strptime(data_str, '%d/%m/%Y').date()
                        except ValueError:
                            try:
                                # Tenta yyyy-mm-dd
                                data_visita = datetime.strptime(data_str, '%Y-%m-%d').date()
                            except ValueError:
                                raise ValueError(f"Formato de data inválido: {data_str}. Use DD/MM/YYYY.")
                        
                        # Atualiza range de datas
                        if min_date is None or data_visita < min_date:
                            min_date = data_visita
                        if max_date is None or data_visita > max_date:
                            max_date = data_visita
                            
                        # 2. Buscar Empresa (Case insensitive)
                        nome_empresa = str(row[colunas_encontradas['empresa']]).strip()
                        empresa = session.query(Empresa).filter(
                            func.lower(Empresa.nome) == nome_empresa.lower()
                        ).first()
                        
                        if not empresa:
                            raise ValueError(f"Empresa não encontrada: {nome_empresa}")
                        
                        # 3. Buscar Embarcação (Case insensitive, na empresa encontrada)
                        nome_embarcacao = str(row[colunas_encontradas['embarcacao']]).strip()
                        embarcacao = session.query(Embarcacao).filter(
                            func.lower(Embarcacao.nome) == nome_embarcacao.lower(),
                            Embarcacao.empresa_id == empresa.id
                        ).first()
                        
                        if not embarcacao:
                            raise ValueError(f"Embarcação não encontrada nesta empresa: {nome_embarcacao}")
                        
                        # 4. Dados numéricos
                        try:
                            permanencia = int(row[colunas_encontradas['permanencia']])
                        except:
                            permanencia = 1
                            
                        def get_int(key):
                            if key in colunas_encontradas:
                                try:
                                    val = row[colunas_encontradas[key]]
                                    return int(val) if pd.notna(val) else 0
                                except:
                                    return 0
                            return 0
                            
                        quantidades = {
                            'qtde_estrangeiros': get_int('qtde_estrangeiros'),
                            'qtde_mercosul': get_int('qtde_mercosul'),
                            'qtde_brasileiros': get_int('qtde_brasileiros'),
                            'qtde_entorno': get_int('qtde_entorno'),
                            'qtde_isentos': get_int('qtde_isentos')
                        }
                        
                        # 5. Criar Registro
                        RegistroVisitaService.criar(
                            session,
                            data=data_visita,
                            empresa_id=empresa.id,
                            embarcacao_id=embarcacao.id,
                            permanencia=permanencia,
                            quantidades=quantidades
                        )
                        sucessos += 1
                        
                    except Exception as row_error:
                        erros.append(f"Linha {linha}: {str(row_error)}")
                
                # Feedback Final
                msg = f"Importação concluída.\n\nRegistros importados com sucesso: {sucessos}"
                if erros:
                    msg += f"\n\nErros ({len(erros)}):\n" + "\n".join(erros[:10])
                    if len(erros) > 10:
                        msg += f"\n... e mais {len(erros)-10} erros."
                    QMessageBox.warning(self, 'Importação com avisos', msg)
                else:
                    QMessageBox.information(self, 'Sucesso', msg)
                
                # Atualizar filtro de data na aba de registros se necessário
                if sucessos > 0 and min_date and max_date:
                    from PyQt6.QtCore import QDate
                    
                    # Se data mínima for menor que o filtro atual, atualiza
                    current_min = self.registros_tab.filter_data_inicio.date().toPyDate()
                    if min_date < current_min:
                        self.registros_tab.filter_data_inicio.setDate(QDate(min_date.year, min_date.month, min_date.day))
                    
                    # Se data máxima for maior que o filtro atual, atualiza
                    current_max = self.registros_tab.filter_data_fim.date().toPyDate()
                    if max_date > current_max:
                        self.registros_tab.filter_data_fim.setDate(QDate(max_date.year, max_date.month, max_date.day))
                
                # Atualizar dados na interface
                self.atualizar_dados()
                
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
                
        except Exception as e:
            QMessageBox.critical(self, 'Erro Fatal', f'Erro durante importação:\n{str(e)}')
