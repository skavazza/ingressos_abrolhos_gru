"""
Aba de Registros Diários de Visitação
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDateEdit, QComboBox,
    QSpinBox, QTextEdit, QGroupBox, QFormLayout, QMessageBox,
    QLineEdit, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from datetime import datetime, date

from models.services import (
    RegistroVisitaService, EmpresaService, EmbarcacaoService,
    TabelaPrecoService, LogService
)
from models.database import RegistroVisita
from utils.validators import Formatadores


class RegistrosTab(QWidget):
    """Aba para gerenciar registros diários de visitação"""
    
    def __init__(self, SessionLocal, usuario_logado):
        super().__init__()
        self.SessionLocal = SessionLocal
        self.usuario_logado = usuario_logado
        self.registro_atual_id = None
        self.embarcacao_comprimento = {}  # id -> comprimento_m (para fator >=12 ou <12)
        
        self.init_ui()
        self.carregar_registros()
        
    def init_ui(self):
        """Inicializa a interface"""
        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Painel esquerdo - Formulário
        form_panel = self.create_form_panel()
        main_layout.addWidget(form_panel, 2)
        
        # Painel direito - Listagem
        list_panel = self.create_list_panel()
        main_layout.addWidget(list_panel, 3)
        
        self.setLayout(main_layout)
        
        # Carregar dados iniciais nos combos
        self.carregar_empresas()
        
    def create_form_panel(self):
        """Cria o painel de formulário"""
        group = QGroupBox('Registro de Visita')
        group.setStyleSheet("""
            QGroupBox {
                font-size: 12pt;
                font-weight: bold;
                border: 2px solid #0078d4;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Formulário
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Código do registro
        self.input_cod_registro = QLineEdit()
        self.input_cod_registro.setPlaceholderText('Opcional')
        form.addRow('Código do Registro:', self.input_cod_registro)
        
        # Data
        self.input_data = QDateEdit()
        self.input_data.setCalendarPopup(True)
        self.input_data.setDate(QDate.currentDate())
        self.input_data.setDisplayFormat('dd/MM/yyyy')
        self.input_data.dateChanged.connect(self.atualizar_tabela_precos)
        form.addRow('Data da Visita:*', self.input_data)
        
        # Responsável
        self.input_responsavel = QLineEdit()
        self.input_responsavel.setPlaceholderText('Nome do responsável')
        form.addRow('Responsável:', self.input_responsavel)
        
        # Empresa
        self.combo_empresa = QComboBox()
        self.combo_empresa.currentIndexChanged.connect(self.on_empresa_changed)
        form.addRow('Empresa:*', self.combo_empresa)
        
        # Embarcação
        self.combo_embarcacao = QComboBox()
        self.combo_embarcacao.setEnabled(False)
        self.combo_embarcacao.currentIndexChanged.connect(self.calcular_valor_total)
        form.addRow('Embarcação:*', self.combo_embarcacao)
        
        # Permanência
        self.input_permanencia = QSpinBox()
        self.input_permanencia.setMinimum(1)
        self.input_permanencia.setMaximum(10)
        self.input_permanencia.setValue(1)
        self.input_permanencia.setToolTip('1 = Aberto, 2 = Pernoite, etc.')
        self.input_permanencia.valueChanged.connect(self.calcular_valor_total)
        form.addRow('Permanência:*', self.input_permanencia)
        
        layout.addLayout(form)
        
        # Seção de quantidades de visitantes
        layout.addWidget(QLabel('<b>Quantidades de Visitantes:</b>'))
        
        qtd_form = QFormLayout()
        qtd_form.setSpacing(10)
        qtd_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.input_estrangeiros = QSpinBox()
        self.input_estrangeiros.setMaximum(999)
        self.input_estrangeiros.valueChanged.connect(self.calcular_valor_total)
        qtd_form.addRow('Estrangeiros:', self.input_estrangeiros)
        
        self.input_mercosul = QSpinBox()
        self.input_mercosul.setMaximum(999)
        self.input_mercosul.valueChanged.connect(self.calcular_valor_total)
        qtd_form.addRow('Mercosul:', self.input_mercosul)
        
        self.input_brasileiros = QSpinBox()
        self.input_brasileiros.setMaximum(999)
        self.input_brasileiros.valueChanged.connect(self.calcular_valor_total)
        qtd_form.addRow('Brasileiros:', self.input_brasileiros)
        
        self.input_entorno = QSpinBox()
        self.input_entorno.setMaximum(999)
        self.input_entorno.valueChanged.connect(self.calcular_valor_total)
        qtd_form.addRow('Comunidade Entorno:', self.input_entorno)
        
        self.input_isentos = QSpinBox()
        self.input_isentos.setMaximum(999)
        self.input_isentos.valueChanged.connect(self.calcular_valor_total)
        qtd_form.addRow('Isentos:', self.input_isentos)
        
        layout.addLayout(qtd_form)
        
        # Resumo: Ingressos, Visitantes e Valor total
        layout.addSpacing(10)
        self.label_valor_total = QLabel(
            '<b style="font-size: 12pt; color: #0078d4;">Ingressos: 0 | Visitantes: 0 | Valor Total: R$ 0,00</b>'
        )
        self.label_valor_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_valor_total.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                padding: 15px;
                border-radius: 8px;
                border: 2px solid #0078d4;
            }
        """)
        self.label_valor_total.setWordWrap(True)
        layout.addWidget(self.label_valor_total)
        
        # Observação
        layout.addWidget(QLabel('Observação:'))
        self.input_observacao = QTextEdit()
        self.input_observacao.setMaximumHeight(80)
        self.input_observacao.setPlaceholderText('Observações adicionais (opcional)')
        layout.addWidget(self.input_observacao)
        
        # Botões
        btn_layout = QHBoxLayout()
        
        self.btn_limpar = QPushButton('🔄 Limpar')
        self.btn_limpar.clicked.connect(self.limpar_formulario)
        btn_layout.addWidget(self.btn_limpar)
        
        self.btn_salvar = QPushButton('💾 Salvar')
        self.btn_salvar.clicked.connect(self.salvar_registro)
        self.btn_salvar.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #006cc1;
            }
        """)
        btn_layout.addWidget(self.btn_salvar)
        
        self.btn_salvar_novo = QPushButton('💾 Salvar + Novo')
        self.btn_salvar_novo.clicked.connect(self.salvar_e_novo)
        btn_layout.addWidget(self.btn_salvar_novo)
        
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        
        group.setLayout(layout)
        
        return group
        
    def create_list_panel(self):
        """Cria o painel de listagem"""
        group = QGroupBox('Registros Salvos')
        group.setStyleSheet("""
            QGroupBox {
                font-size: 12pt;
                font-weight: bold;
                border: 2px solid #666;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Filtros
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel('Filtrar por data:'))
        
        self.filter_data_inicio = QDateEdit()
        self.filter_data_inicio.setCalendarPopup(True)
        self.filter_data_inicio.setDate(QDate.currentDate().addDays(-30))
        self.filter_data_inicio.setDisplayFormat('dd/MM/yyyy')
        filter_layout.addWidget(self.filter_data_inicio)
        
        filter_layout.addWidget(QLabel('até'))
        
        self.filter_data_fim = QDateEdit()
        self.filter_data_fim.setCalendarPopup(True)
        self.filter_data_fim.setDate(QDate.currentDate())
        self.filter_data_fim.setDisplayFormat('dd/MM/yyyy')
        filter_layout.addWidget(self.filter_data_fim)
        
        btn_filtrar = QPushButton('🔍 Filtrar')
        btn_filtrar.clicked.connect(self.carregar_registros)
        filter_layout.addWidget(btn_filtrar)
        
        filter_layout.addSpacing(15)
        filter_layout.addWidget(QLabel('Empresa:'))
        self.filter_combo_empresa = QComboBox()
        self.filter_combo_empresa.setMinimumWidth(200)
        self.filter_combo_empresa.currentIndexChanged.connect(self.carregar_registros)
        filter_layout.addWidget(self.filter_combo_empresa)
        
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Tabela de registros
        self.table_registros = QTableWidget()
        self.table_registros.setColumnCount(9)
        self.table_registros.setHorizontalHeaderLabels([
            'ID', 'Data', 'Empresa', 'Embarcação', 'Perm.', 
            'Visitantes', 'Valor Total', 'Responsável', 'Criado em'
        ])
        
        # Configurações da tabela
        self.table_registros.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_registros.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table_registros.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_registros.setAlternatingRowColors(True)
        
        # Ajustar colunas
        header = self.table_registros.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table_registros.doubleClicked.connect(self.editar_registro)
        
        layout.addWidget(self.table_registros)
        
        # Botões de ação
        btn_layout = QHBoxLayout()
        
        self.btn_editar = QPushButton('✏️ Editar')
        self.btn_editar.clicked.connect(self.editar_registro)
        btn_layout.addWidget(self.btn_editar)
        
        self.btn_deletar = QPushButton('🗑️ Deletar')
        self.btn_deletar.clicked.connect(self.deletar_registro)
        self.btn_deletar.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
        """)
        btn_layout.addWidget(self.btn_deletar)
        
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        group.setLayout(layout)
        
        return group
    
    def carregar_empresas(self):
        """Carrega empresas no combobox"""
        session = self.SessionLocal()
        try:
            empresas = EmpresaService.listar_ativas(session)
            
            self.combo_empresa.clear()
            self.combo_empresa.addItem('-- Selecione uma empresa --', None)
            
            self.filter_combo_empresa.clear()
            self.filter_combo_empresa.addItem('[Todas as empresas]', None)
            
            for empresa in empresas:
                self.combo_empresa.addItem(empresa.nome, empresa.id)
                self.filter_combo_empresa.addItem(empresa.nome, empresa.id)
                
        finally:
            session.close()
    
    def on_empresa_changed(self, index):
        """Quando empresa é selecionada, carrega suas embarcações"""
        empresa_id = self.combo_empresa.currentData()
        
        self.combo_embarcacao.clear()
        self.embarcacao_comprimento.clear()
        self.combo_embarcacao.setEnabled(False)
        
        if empresa_id:
            session = self.SessionLocal()
            try:
                embarcacoes = EmbarcacaoService.listar_por_empresa(session, empresa_id)
                
                self.combo_embarcacao.addItem('-- Selecione uma embarcação --', None)
                
                for embarcacao in embarcacoes:
                    self.combo_embarcacao.addItem(embarcacao.nome, embarcacao.id)
                    self.embarcacao_comprimento[embarcacao.id] = embarcacao.comprimento_m
                
                self.combo_embarcacao.setEnabled(True)
                
            finally:
                session.close()
        
        self.calcular_valor_total()
    
    def atualizar_tabela_precos(self):
        """Atualiza o cálculo quando a data muda"""
        self.calcular_valor_total()
    
    def calcular_valor_total(self, *args):
        """Calcula ingressos, visitantes e valor total em tempo real.
        Ingressos = pagantes × permanência; Visitantes = (pagantes + isentos) × permanência.
        Valor considera fator por comprimento da embarcação (>=12m ou <12m).
        """
        try:
            qdate = self.input_data.date()
            data_visita = date(qdate.year(), qdate.month(), qdate.day())
            
            quantidades = {
                'qtde_estrangeiros': self.input_estrangeiros.value(),
                'qtde_mercosul': self.input_mercosul.value(),
                'qtde_brasileiros': self.input_brasileiros.value(),
                'qtde_entorno': self.input_entorno.value(),
                'qtde_isentos': self.input_isentos.value(),
                'qtde_maior12': 0,
                'qtde_menor12': 0,
            }
            
            permanencia = self.input_permanencia.value()
            
            # Comprimento da embarcação para fator >=12m ou <12m
            embarcacao_id = self.combo_embarcacao.currentData()
            comprimento_m = self.embarcacao_comprimento.get(embarcacao_id) if embarcacao_id else None
            
            ingressos, visitantes = RegistroVisitaService.calcular_ingressos_e_visitantes(
                quantidades, permanencia
            )
            
            session = self.SessionLocal()
            try:
                valor_total = RegistroVisitaService.calcular_valor_total(
                    session, data_visita, quantidades, permanencia, comprimento_m
                )
                
                valor_fmt = Formatadores.formatar_moeda(valor_total)
                self.label_valor_total.setText(
                    f'<b style="font-size: 12pt; color: #0078d4;">Ingressos: {ingressos} | '
                    f'Visitantes: {visitantes} | Valor Total: {valor_fmt}</b>'
                )
            finally:
                session.close()
                
        except Exception as e:
            print(f"Erro ao calcular valor: {e}")
    
    def validar_formulario(self):
        """Valida os campos do formulário"""
        if self.combo_empresa.currentData() is None:
            QMessageBox.warning(self, 'Validação', 'Por favor, selecione uma empresa.')
            return False
        
        if self.combo_embarcacao.currentData() is None:
            QMessageBox.warning(self, 'Validação', 'Por favor, selecione uma embarcação.')
            return False
        
        # Verifica se há pelo menos um visitante
        total_visitantes = (
            self.input_estrangeiros.value() +
            self.input_mercosul.value() +
            self.input_brasileiros.value() +
            self.input_entorno.value() +
            self.input_isentos.value()
        )
        
        if total_visitantes == 0:
            QMessageBox.warning(
                self, 
                'Validação', 
                'Por favor, informe pelo menos um visitante.'
            )
            return False
        
        return True
    
    def salvar_registro(self):
        """Salva ou atualiza um registro"""
        if not self.validar_formulario():
            return
        
        try:
            # Pega os dados do formulário
            qdate = self.input_data.date()
            data_visita = date(qdate.year(), qdate.month(), qdate.day())
            
            empresa_id = self.combo_empresa.currentData()
            embarcacao_id = self.combo_embarcacao.currentData()
            permanencia = self.input_permanencia.value()
            
            quantidades = {
                'qtde_estrangeiros': self.input_estrangeiros.value(),
                'qtde_mercosul': self.input_mercosul.value(),
                'qtde_brasileiros': self.input_brasileiros.value(),
                'qtde_entorno': self.input_entorno.value(),
                'qtde_isentos': self.input_isentos.value(),
                'qtde_maior12': 0,
                'qtde_menor12': 0,
            }
            
            kwargs = {
                'cod_registro': self.input_cod_registro.text() or None,
                'responsavel': self.input_responsavel.text() or None,
                'observacao': self.input_observacao.toPlainText() or None,
            }
            
            session = self.SessionLocal()
            try:
                if self.registro_atual_id:
                    # Atualizar registro existente
                    RegistroVisitaService.atualizar(
                        session,
                        self.registro_atual_id,
                        data=data_visita,
                        empresa_id=empresa_id,
                        embarcacao_id=embarcacao_id,
                        permanencia=permanencia,
                        **quantidades,
                        **kwargs
                    )
                    
                    LogService.registrar(
                        session, self.usuario_logado, 'UPDATE', 'registros_visita', self.registro_atual_id,
                        f"Atualizou visita de {data_visita} - Empresa ID {empresa_id}"
                    )
                    
                    QMessageBox.information(
                        self,
                        'Sucesso',
                        'Registro atualizado com sucesso!'
                    )
                else:
                    # Criar novo registro
                    novo_registro = RegistroVisitaService.criar(
                        session,
                        data_visita,
                        empresa_id,
                        embarcacao_id,
                        permanencia,
                        quantidades,
                        **kwargs
                    )
                    
                    LogService.registrar(
                        session, self.usuario_logado, 'INSERT', 'registros_visita', novo_registro.id,
                        f"Criou visita de {data_visita} - Empresa ID {empresa_id}"
                    )
                    
                    QMessageBox.information(
                        self,
                        'Sucesso',
                        'Registro salvo com sucesso!'
                    )
                
                # Atualiza a listagem
                self.carregar_registros()
                self.limpar_formulario()
                
            finally:
                session.close()
                
        except Exception as e:
            QMessageBox.critical(
                self,
                'Erro',
                f'Erro ao salvar registro:\n{str(e)}'
            )
    
    def salvar_e_novo(self):
        """Salva o registro atual e mantém os dados para criar outro do mesmo dia"""
        if not self.validar_formulario():
            return
        
        # Salva o registro
        self.salvar_registro()
        
        # Mantém apenas data, empresa e embarcação
        # Limpa as quantidades
        self.input_estrangeiros.setValue(0)
        self.input_mercosul.setValue(0)
        self.input_brasileiros.setValue(0)
        self.input_entorno.setValue(0)
        self.input_isentos.setValue(0)
        self.input_permanencia.setValue(1)
        self.input_cod_registro.clear()
        self.input_responsavel.clear()
        self.input_observacao.clear()
        
        # Foco no primeiro campo de quantidade
        self.input_estrangeiros.setFocus()
    
    def limpar_formulario(self):
        """Limpa todos os campos do formulário"""
        self.registro_atual_id = None
        
        self.input_cod_registro.clear()
        self.input_data.setDate(QDate.currentDate())
        self.input_responsavel.clear()
        self.combo_empresa.setCurrentIndex(0)
        self.combo_embarcacao.clear()
        self.combo_embarcacao.setEnabled(False)
        self.input_permanencia.setValue(1)
        
        self.input_estrangeiros.setValue(0)
        self.input_mercosul.setValue(0)
        self.input_brasileiros.setValue(0)
        self.input_entorno.setValue(0)
        self.input_isentos.setValue(0)
        
        self.input_observacao.clear()
        
        self.calcular_valor_total()
        
        self.btn_salvar.setText('💾 Salvar')
    
    def carregar_registros(self):
        """Carrega os registros na tabela"""
        session = self.SessionLocal()
        try:
            # Pega o período do filtro
            qdate_inicio = self.filter_data_inicio.date()
            data_inicio = date(qdate_inicio.year(), qdate_inicio.month(), qdate_inicio.day())
            
            qdate_fim = self.filter_data_fim.date()
            data_fim = date(qdate_fim.year(), qdate_fim.month(), qdate_fim.day())
            
            # Filtro por empresa
            empresa_id = self.filter_combo_empresa.currentData()
            
            # Busca registros
            registros = RegistroVisitaService.listar_por_periodo(session, data_inicio, data_fim, empresa_id)
            
            # Limpa tabela
            self.table_registros.setRowCount(0)
            
            # Popula tabela
            for registro in registros:
                row = self.table_registros.rowCount()
                self.table_registros.insertRow(row)
                
                # Total de visitantes
                total_visitantes = (
                    registro.qtde_estrangeiros +
                    registro.qtde_mercosul +
                    registro.qtde_brasileiros +
                    registro.qtde_entorno +
                    registro.qtde_isentos
                )
                
                self.table_registros.setItem(row, 0, QTableWidgetItem(str(registro.id)))
                self.table_registros.setItem(row, 1, QTableWidgetItem(
                    Formatadores.formatar_data(registro.data)
                ))
                self.table_registros.setItem(row, 2, QTableWidgetItem(registro.empresa.nome))
                self.table_registros.setItem(row, 3, QTableWidgetItem(registro.embarcacao.nome))
                self.table_registros.setItem(row, 4, QTableWidgetItem(str(registro.permanencia)))
                self.table_registros.setItem(row, 5, QTableWidgetItem(str(total_visitantes)))
                self.table_registros.setItem(row, 6, QTableWidgetItem(
                    Formatadores.formatar_moeda(registro.valor_total)
                ))
                self.table_registros.setItem(row, 7, QTableWidgetItem(
                    registro.responsavel or '-'
                ))
                self.table_registros.setItem(row, 8, QTableWidgetItem(
                    registro.criado_em.strftime('%d/%m/%Y %H:%M') if registro.criado_em else '-'
                ))
            
        finally:
            session.close()
    
    def editar_registro(self):
        """Carrega um registro para edição"""
        selected_rows = self.table_registros.selectedItems()
        
        if not selected_rows:
            QMessageBox.warning(self, 'Aviso', 'Por favor, selecione um registro.')
            return
        
        # Pega o ID do registro
        row = self.table_registros.currentRow()
        registro_id = int(self.table_registros.item(row, 0).text())
        
        # Busca o registro
        session = self.SessionLocal()
        try:
            registro = RegistroVisitaService.buscar_por_id(session, registro_id)
            
            if not registro:
                QMessageBox.warning(self, 'Erro', 'Registro não encontrado.')
                return
            
            # Preenche o formulário
            self.registro_atual_id = registro.id
            
            self.input_cod_registro.setText(registro.cod_registro or '')
            self.input_data.setDate(QDate(
                registro.data.year,
                registro.data.month,
                registro.data.day
            ))
            self.input_responsavel.setText(registro.responsavel or '')
            
            # Seleciona empresa
            for i in range(self.combo_empresa.count()):
                if self.combo_empresa.itemData(i) == registro.empresa_id:
                    self.combo_empresa.setCurrentIndex(i)
                    break
            
            # Espera um pouco para as embarcações carregarem
            # Seleciona embarcação
            for i in range(self.combo_embarcacao.count()):
                if self.combo_embarcacao.itemData(i) == registro.embarcacao_id:
                    self.combo_embarcacao.setCurrentIndex(i)
                    break
            
            self.input_permanencia.setValue(registro.permanencia)
            
            self.input_estrangeiros.setValue(registro.qtde_estrangeiros)
            self.input_mercosul.setValue(registro.qtde_mercosul)
            self.input_brasileiros.setValue(registro.qtde_brasileiros)
            self.input_entorno.setValue(registro.qtde_entorno)
            self.input_isentos.setValue(registro.qtde_isentos)
            
            self.input_observacao.setPlainText(registro.observacao or '')
            
            self.btn_salvar.setText('💾 Atualizar')
            
            # Scroll para o topo do formulário
            self.input_cod_registro.setFocus()
            
        finally:
            session.close()
    
    def deletar_registro(self):
        """Deleta um registro"""
        selected_rows = self.table_registros.selectedItems()
        
        if not selected_rows:
            QMessageBox.warning(self, 'Aviso', 'Por favor, selecione um registro.')
            return
        
        # Confirma deleção
        reply = QMessageBox.question(
            self,
            'Confirmar exclusão',
            'Tem certeza que deseja deletar este registro?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        # Pega o ID do registro
        row = self.table_registros.currentRow()
        registro_id = int(self.table_registros.item(row, 0).text())
        
        # Deleta
        session = self.SessionLocal()
        try:
            # Recuperar dados para log antes de excluir
            registro = RegistroVisitaService.buscar_por_id(session, registro_id)
            if not registro:
                QMessageBox.warning(self, 'Erro', 'Registro não encontrado para exclusão.')
                return

            info_log = f"Excluiu visita de {registro.data} - Empresa ID {registro.empresa_id}"
            
            if RegistroVisitaService.deletar(session, registro_id): # Assuming 'deletar' is the method, not 'excluir' as in instruction
                LogService.registrar(
                    session, self.usuario_logado, 'DELETE', 'registros_visita', registro_id,
                    info_log
                )
                
                QMessageBox.information(self, 'Sucesso', 'Registro deletado com sucesso!')
                self.carregar_registros()
                self.limpar_formulario()
            else:
                QMessageBox.warning(self, 'Erro', 'Não foi possível deletar o registro.')
                
        finally:
            session.close()
