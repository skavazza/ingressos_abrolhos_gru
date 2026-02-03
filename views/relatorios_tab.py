"""Aba de Relatórios com exportação e geração de nota de pagamento"""
from PyQt6.QtWidgets import *
from PyQt6.QtCore import QDate, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import date, datetime
import pandas as pd
from models.services import RegistroVisitaService, EmpresaService
from models.database import Empresa
from utils.validators import Formatadores
from utils.gru_automation import GRUAutomation
import threading
import subprocess
import os


class RelatoriosTab(QWidget):
    # Sinais para comunicação entre threads
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str)  # Nome do arquivo ou erro
    error_signal = pyqtSignal(str)

    def __init__(self, SessionLocal):
        super().__init__()
        self.SessionLocal = SessionLocal
        
        # Conectar sinais
        self.log_signal.connect(self.add_log_ui)
        self.finished_signal.connect(self.on_automation_finished)
        self.error_signal.connect(self.on_automation_error)
        
        self.init_ui()
        self.carregar_empresas()
    
    def init_ui(self):
        # Layout principal da aba
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll Area para garantir que tudo apareça em telas menores
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = QLabel('Geração de Relatórios')
        title.setStyleSheet('font-size: 14pt; font-weight: bold;')
        layout.addWidget(title)
        
        # === SEÇÃO 1: Relatório Geral ===
        group_geral = QGroupBox('📊 Relatório Geral de Registros')
        group_geral.setStyleSheet('QGroupBox { font-weight: bold; }')
        geral_layout = QVBoxLayout()
        
        form_geral = QFormLayout()
        self.data_inicio = QDateEdit()
        self.data_inicio.setCalendarPopup(True)
        self.data_inicio.setDate(QDate.currentDate().addMonths(-1))
        self.data_inicio.setDisplayFormat('dd/MM/yyyy')
        form_geral.addRow('Data Início:', self.data_inicio)
        
        self.data_fim = QDateEdit()
        self.data_fim.setCalendarPopup(True)
        self.data_fim.setDate(QDate.currentDate())
        self.data_fim.setDisplayFormat('dd/MM/yyyy')
        form_geral.addRow('Data Fim:', self.data_fim)
        
        geral_layout.addLayout(form_geral)
        
        btn_layout_geral = QHBoxLayout()
        btn_csv = QPushButton('📄 Exportar CSV')
        btn_csv.clicked.connect(self.exportar_csv)
        btn_layout_geral.addWidget(btn_csv)
        
        btn_xlsx = QPushButton('📊 Exportar Excel')
        btn_xlsx.clicked.connect(self.exportar_excel)
        btn_layout_geral.addWidget(btn_xlsx)
        btn_layout_geral.addStretch()
        
        geral_layout.addLayout(btn_layout_geral)
        group_geral.setLayout(geral_layout)
        layout.addWidget(group_geral)
        
        # === SEÇÃO 2: Nota de Pagamento por Empresa ===
        group_nota = QGroupBox('💰 Nota de Pagamento por Empresa')
        group_nota.setStyleSheet('QGroupBox { font-weight: bold; }')
        nota_layout = QVBoxLayout()
        
        form_nota = QFormLayout()
        
        self.combo_empresa = QComboBox()
        self.combo_empresa.setMinimumWidth(300)
        form_nota.addRow('Empresa:', self.combo_empresa)
        
        self.nota_data_inicio = QDateEdit()
        self.nota_data_inicio.setCalendarPopup(True)
        self.nota_data_inicio.setDate(QDate.currentDate().addMonths(-1))
        self.nota_data_inicio.setDisplayFormat('dd/MM/yyyy')
        form_nota.addRow('Período de:', self.nota_data_inicio)
        
        self.nota_data_fim = QDateEdit()
        self.nota_data_fim.setCalendarPopup(True)
        self.nota_data_fim.setDate(QDate.currentDate())
        self.nota_data_fim.setDisplayFormat('dd/MM/yyyy')
        form_nota.addRow('Até:', self.nota_data_fim)
        
        nota_layout.addLayout(form_nota)
        
        # Botões de geração de nota
        btn_layout_nota = QHBoxLayout()
        
        btn_preview = QPushButton('👁️ Visualizar Nota')
        btn_preview.clicked.connect(self.visualizar_nota)
        btn_layout_nota.addWidget(btn_preview)
        
        btn_gerar_excel = QPushButton('📊 Gerar Nota Excel')
        btn_gerar_excel.clicked.connect(self.gerar_nota_excel)
        btn_layout_nota.addWidget(btn_gerar_excel)
        
        btn_gerar_txt = QPushButton('📝 Gerar Nota Texto')
        btn_gerar_txt.clicked.connect(self.gerar_nota_texto)
        btn_layout_nota.addWidget(btn_gerar_txt)
        
        btn_layout_nota.addSpacing(20)
        
        self.btn_gru = QPushButton('🚀 Emitir GRU (Portal)')
        self.btn_gru.clicked.connect(self.emitir_gru_portal)
        self.btn_gru.setStyleSheet("""
            QPushButton {
                background-color: #2e7d32;
                color: white;
                font-weight: bold;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #1b5e20;
            }
        """)
        btn_layout_nota.addWidget(self.btn_gru)
        
        btn_layout_nota.addStretch()
        nota_layout.addLayout(btn_layout_nota)
        
        group_nota.setLayout(nota_layout)
        layout.addWidget(group_nota)
        
        # === SEÇÃO 3: Preview da Nota ===
        group_preview = QGroupBox('📋 Prévia da Nota de Pagamento')
        group_preview.setStyleSheet('QGroupBox { font-weight: bold; }')
        preview_layout = QVBoxLayout()
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMinimumHeight(300)
        self.preview_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 10pt;
                background-color: white;
                border: 1px solid #ccc;
            }
        """)
        preview_layout.addWidget(self.preview_text)
        
        group_preview.setLayout(preview_layout)
        layout.addWidget(group_preview)
        
        # === SEÇÃO 4: Logs de Processamento ===
        self.group_logs = QGroupBox('📝 Log do Processo de Emissão')
        self.group_logs.setStyleSheet('QGroupBox { font-weight: bold; }')
        logs_layout = QVBoxLayout()
        
        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(150)
        self.log_output.setStyleSheet("""
            QPlainTextEdit {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 9pt;
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                color: #333;
            }
        """)
        logs_layout.addWidget(self.log_output)
        
        self.group_logs.setLayout(logs_layout)
        layout.addWidget(self.group_logs)
        
        layout.addStretch()
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def add_log_ui(self, msg):
        """Atualiza a UI com uma nova mensagem de log (chamado via sinal)"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_output.appendPlainText(f"[{timestamp}] {msg}")
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )

    def on_automation_finished(self, arquivo):
        """Finalização com sucesso (chamado via sinal)"""
        self.btn_gru.setEnabled(True)
        self.btn_gru.setText('🚀 Emitir GRU (Portal)')
        self.add_log_ui("✅ Processo concluído com sucesso!")
        
        download_dir = os.path.join(os.path.expanduser("~"), "Downloads", "GRU")
        QMessageBox.information(
            self, "Sucesso", 
            f"GRU gerada e salva com sucesso em:\n{download_dir}\n\nArquivo: {arquivo}"
        )
        if os.path.exists(download_dir):
            os.startfile(download_dir)

    def on_automation_error(self, err_msg):
        """Erro na automação (chamado via sinal)"""
        self.btn_gru.setEnabled(True)
        self.btn_gru.setText('🚀 Emitir GRU (Portal)')
        self.add_log_ui(f"❌ ERRO: {err_msg}")
        QMessageBox.critical(self, "Erro na Automação", f"Falha ao gerar GRU:\n{err_msg}")
    
    def carregar_empresas(self):
        """Carrega as empresas no combobox"""
        session = self.SessionLocal()
        try:
            empresas = EmpresaService.listar_ativas(session)
            self.combo_empresa.clear()
            self.combo_empresa.addItem('-- Selecione uma empresa --', None)
            for emp in empresas:
                self.combo_empresa.addItem(emp.nome, emp.id)
        finally:
            session.close()
    
    def get_periodo(self):
        qd1 = self.data_inicio.date()
        qd2 = self.data_fim.date()
        return date(qd1.year(), qd1.month(), qd1.day()), date(qd2.year(), qd2.month(), qd2.day())
    
    def get_periodo_nota(self):
        qd1 = self.nota_data_inicio.date()
        qd2 = self.nota_data_fim.date()
        return date(qd1.year(), qd1.month(), qd1.day()), date(qd2.year(), qd2.month(), qd2.day())
    
    def exportar_csv(self):
        inicio, fim = self.get_periodo()
        filepath, _ = QFileDialog.getSaveFileName(
            self, 'Salvar CSV', 
            f'relatorio_{inicio.strftime("%Y%m%d")}_{fim.strftime("%Y%m%d")}.csv', 
            'CSV (*.csv)'
        )
        if filepath:
            self.gerar_relatorio(inicio, fim, filepath, 'csv')
    
    def exportar_excel(self):
        inicio, fim = self.get_periodo()
        filepath, _ = QFileDialog.getSaveFileName(
            self, 'Salvar Excel', 
            f'relatorio_{inicio.strftime("%Y%m%d")}_{fim.strftime("%Y%m%d")}.xlsx', 
            'Excel (*.xlsx)'
        )
        if filepath:
            self.gerar_relatorio(inicio, fim, filepath, 'excel')
    
    def gerar_relatorio(self, inicio, fim, filepath, formato):
        session = self.SessionLocal()
        try:
            registros = RegistroVisitaService.listar_por_periodo(session, inicio, fim)
            
            dados = []
            for r in registros:
                dados.append({
                    'Data': Formatadores.formatar_data(r.data),
                    'Empresa': r.empresa.nome,
                    'Embarcação': r.embarcacao.nome,
                    'Permanência': r.permanencia,
                    'Estrangeiros': r.qtde_estrangeiros,
                    'Mercosul': r.qtde_mercosul,
                    'Brasileiros': r.qtde_brasileiros,
                    'Entorno': r.qtde_entorno,
                    'Isentos': r.qtde_isentos,
                    'Valor Total': r.valor_total
                })
            
            df = pd.DataFrame(dados)
            
            if formato == 'csv':
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
            else:
                df.to_excel(filepath, index=False, engine='openpyxl')
            
            QMessageBox.information(self, 'Sucesso', f'Relatório exportado:\n{filepath}')
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Erro ao exportar:\n{str(e)}')
        finally:
            session.close()
    
    def gerar_dados_nota(self):
        """Gera os dados para a nota de pagamento"""
        empresa_id = self.combo_empresa.currentData()
        
        if not empresa_id:
            QMessageBox.warning(self, 'Aviso', 'Por favor, selecione uma empresa.')
            return None
        
        inicio, fim = self.get_periodo_nota()
        
        session = self.SessionLocal()
        try:
            # Buscar empresa
            empresa_obj = EmpresaService.buscar_por_id(session, empresa_id)
            
            # Extrair dados da empresa antes de fechar sessão
            empresa = {
                'nome': empresa_obj.nome,
                'cnpj': empresa_obj.cnpj,
                'contato_nome': empresa_obj.contato_nome,
                'contato_telefone': empresa_obj.contato_telefone,
                'contato_email': empresa_obj.contato_email
            }
            
            # Buscar registros da empresa no período
            registros_obj = RegistroVisitaService.listar_por_periodo(session, inicio, fim)
            registros_empresa = [r for r in registros_obj if r.empresa_id == empresa_id]
            
            if not registros_empresa:
                QMessageBox.warning(
                    self, 'Aviso', 
                    f'Nenhum registro encontrado para {empresa["nome"]}\n'
                    f'no período de {Formatadores.formatar_data(inicio)} a {Formatadores.formatar_data(fim)}.'
                )
                return None
            
            # Extrair dados dos registros antes de fechar sessão
            registros = []
            for r in registros_empresa:
                registros.append({
                    'data': r.data,
                    'embarcacao_nome': r.embarcacao.nome,
                    'permanencia': r.permanencia,
                    'qtde_estrangeiros': r.qtde_estrangeiros,
                    'qtde_mercosul': r.qtde_mercosul,
                    'qtde_brasileiros': r.qtde_brasileiros,
                    'qtde_entorno': r.qtde_entorno,
                    'qtde_isentos': r.qtde_isentos,
                    'qtde_maior12': r.qtde_maior12,
                    'qtde_menor12': r.qtde_menor12,
                    'valor_total': r.valor_total
                })
            
            # Calcular totais
            totais = {
                'estrangeiros': sum(r['qtde_estrangeiros'] for r in registros),
                'mercosul': sum(r['qtde_mercosul'] for r in registros),
                'brasileiros': sum(r['qtde_brasileiros'] for r in registros),
                'entorno': sum(r['qtde_entorno'] for r in registros),
                'isentos': sum(r['qtde_isentos'] for r in registros),
                'maior12': sum(r['qtde_maior12'] for r in registros),
                'menor12': sum(r['qtde_menor12'] for r in registros),
                'valor_total': sum(r['valor_total'] for r in registros),
                'qtd_registros': len(registros)
            }
            
            totais['total_visitantes'] = (
                totais['estrangeiros'] + totais['mercosul'] + totais['brasileiros'] +
                totais['entorno'] + totais['isentos'] + totais['maior12'] + totais['menor12']
            )
            
            return {
                'empresa': empresa,
                'registros': registros,
                'totais': totais,
                'periodo_inicio': inicio,
                'periodo_fim': fim,
                'data_geracao': datetime.now()
            }
        finally:
            session.close()
    
    def formatar_nota_texto(self, dados):
        """Formata a nota de pagamento como texto"""
        empresa = dados['empresa']
        totais = dados['totais']
        registros = dados['registros']
        
        linha = "=" * 70
        linha2 = "-" * 70
        
        texto = f"""
{linha}
                    NOTA DE PAGAMENTO - INGRESSOS
              Parque Nacional Marinho dos Abrolhos
                           ICMBio
{linha}

DADOS DA EMPRESA:
{linha2}
Nome: {empresa['nome']}
CNPJ: {empresa['cnpj'] or 'Não informado'}
Contato: {empresa['contato_nome'] or 'Não informado'}
Telefone: {empresa['contato_telefone'] or 'Não informado'}
E-mail: {empresa['contato_email'] or 'Não informado'}

PERÍODO DE REFERÊNCIA:
{linha2}
De: {Formatadores.formatar_data(dados['periodo_inicio'])}
Até: {Formatadores.formatar_data(dados['periodo_fim'])}

DETALHAMENTO DOS REGISTROS:
{linha2}
{'Data':<12} {'Embarcação':<20} {'Perm.':<6} {'Visit.':<8} {'Valor':>12}
{linha2}
"""
        
        for r in registros:
            total_visit = (r['qtde_estrangeiros'] + r['qtde_mercosul'] + r['qtde_brasileiros'] + 
                          r['qtde_entorno'] + r['qtde_isentos'] + r['qtde_maior12'] + r['qtde_menor12'])
            texto += f"{Formatadores.formatar_data(r['data']):<12} {r['embarcacao_nome'][:20]:<20} {r['permanencia']:<6} {total_visit:<8} {Formatadores.formatar_moeda(r['valor_total']):>12}\n"
        
        texto += f"""
{linha2}

RESUMO POR CATEGORIA DE VISITANTE:
{linha2}
Estrangeiros:              {totais['estrangeiros']:>8}
Mercosul:                  {totais['mercosul']:>8}
Brasileiros:               {totais['brasileiros']:>8}
Cidades do Entorno:        {totais['entorno']:>8}
Isentos:                   {totais['isentos']:>8}
{linha2}
TOTAL DE VISITANTES:       {totais['total_visitantes']:>8}

{linha}
VALOR TOTAL A PAGAR:       {Formatadores.formatar_moeda(totais['valor_total']):>15}
{linha}

Quantidade de registros: {totais['qtd_registros']}
Data de geração: {dados['data_geracao'].strftime('%d/%m/%Y %H:%M:%S')}

INSTRUÇÕES DE PAGAMENTO:
{linha2}
O pagamento deve ser realizado através de GRU (Guia de Recolhimento
da União) no site: https://pagtesouro.tesouro.gov.br/portal-gru/


Unidade Gestora Arrecadadora: 443032
Código de Recolhimento: 20343-2
Gestão: 44207

{linha}
            PARNA Abrolhos - Sistema de Gestão de Ingressos
{linha}
"""
        return texto
    
    def visualizar_nota(self):
        """Visualiza a prévia da nota de pagamento"""
        dados = self.gerar_dados_nota()
        if dados:
            texto = self.formatar_nota_texto(dados)
            self.preview_text.setPlainText(texto)
    
    def gerar_nota_texto(self):
        """Gera a nota de pagamento como arquivo de texto"""
        dados = self.gerar_dados_nota()
        if not dados:
            return
        
        empresa = dados['empresa']
        inicio = dados['periodo_inicio']
        fim = dados['periodo_fim']
        
        nome_arquivo = f"nota_pagamento_{empresa['nome'].replace(' ', '_')}_{inicio.strftime('%Y%m%d')}_{fim.strftime('%Y%m%d')}.txt"
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, 'Salvar Nota de Pagamento', 
            nome_arquivo, 
            'Arquivo de Texto (*.txt)'
        )
        
        if filepath:
            try:
                texto = self.formatar_nota_texto(dados)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(texto)
                QMessageBox.information(self, 'Sucesso', f'Nota de pagamento gerada:\n{filepath}')
            except Exception as e:
                QMessageBox.critical(self, 'Erro', f'Erro ao gerar nota:\n{str(e)}')
    
    def gerar_nota_excel(self):
        """Gera a nota de pagamento como arquivo Excel"""
        dados = self.gerar_dados_nota()
        if not dados:
            return
        
        empresa = dados['empresa']
        totais = dados['totais']
        registros = dados['registros']
        inicio = dados['periodo_inicio']
        fim = dados['periodo_fim']
        
        nome_arquivo = f"nota_pagamento_{empresa['nome'].replace(' ', '_')}_{inicio.strftime('%Y%m%d')}_{fim.strftime('%Y%m%d')}.xlsx"
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, 'Salvar Nota de Pagamento', 
            nome_arquivo, 
            'Excel (*.xlsx)'
        )
        
        if not filepath:
            return
        
        try:
            # Criar arquivo Excel com múltiplas abas
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Aba 1: Resumo
                resumo_data = {
                    'Campo': [
                        'Empresa', 'CNPJ', 'Contato', 'Telefone', 'E-mail',
                        '', 'Período Início', 'Período Fim', 'Data Geração',
                        '', 'Total Estrangeiros', 'Total Mercosul', 'Total Brasileiros',
                        'Total Entorno', 'Total Isentos',
                        '', 'TOTAL VISITANTES', 'VALOR TOTAL A PAGAR'
                    ],
                    'Valor': [
                        empresa['nome'], empresa['cnpj'] or '', empresa['contato_nome'] or '',
                        empresa['contato_telefone'] or '', empresa['contato_email'] or '',
                        '', Formatadores.formatar_data(inicio), Formatadores.formatar_data(fim),
                        dados['data_geracao'].strftime('%d/%m/%Y %H:%M'),
                        '', totais['estrangeiros'], totais['mercosul'], totais['brasileiros'],
                        totais['entorno'], totais['isentos'],
                        '', totais['total_visitantes'], Formatadores.formatar_moeda(totais['valor_total'])
                    ]
                }
                df_resumo = pd.DataFrame(resumo_data)
                df_resumo.to_excel(writer, sheet_name='Resumo', index=False)
                
                # Aba 2: Detalhamento
                detalhe_data = []
                for r in registros:
                    total_visit = (r['qtde_estrangeiros'] + r['qtde_mercosul'] + r['qtde_brasileiros'] + 
                                  r['qtde_entorno'] + r['qtde_isentos'] + r['qtde_maior12'] + r['qtde_menor12'])
                    detalhe_data.append({
                        'Data': Formatadores.formatar_data(r['data']),
                        'Embarcação': r['embarcacao_nome'],
                        'Permanência': r['permanencia'],
                        'Estrangeiros': r['qtde_estrangeiros'],
                        'Mercosul': r['qtde_mercosul'],
                        'Brasileiros': r['qtde_brasileiros'],
                        'Entorno': r['qtde_entorno'],
                        'Isentos': r['qtde_isentos'],
                        'Total Visitantes': total_visit,
                        'Valor': r['valor_total']
                    })
                
                df_detalhe = pd.DataFrame(detalhe_data)
                df_detalhe.to_excel(writer, sheet_name='Detalhamento', index=False)
            
            QMessageBox.information(self, 'Sucesso', f'Nota de pagamento gerada:\n{filepath}')
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Erro ao gerar nota:\n{str(e)}')

    def emitir_gru_portal(self):
        """Coleta dados e executa a automação em segundo plano"""
        dados_nota = self.gerar_dados_nota()
        if not dados_nota:
            return
            
        # Preparar dados para a automação
        empresa = dados_nota['empresa']
        inicio = dados_nota['periodo_inicio']
        competencia = inicio.strftime('%m/%Y')
        vencimento_dt = GRUAutomation.calcular_vencimento(inicio)
        vencimento_str = vencimento_dt.strftime('%d/%m/%Y')
        valor_total = dados_nota['totais']['valor_total']
        
        # Pasta de download
        download_dir = os.path.join(os.path.expanduser("~"), "Downloads", "GRU")
        
        dados_gru = {
            'cnpj': empresa['cnpj'].replace('.', '').replace('/', '').replace('-', ''),
            'nome_contribuinte': empresa['nome'],
            'competencia': competencia,
            'vencimento': vencimento_str,
            'valor': valor_total,
            'download_dir': download_dir
        }
        
        # Desabilitar botão e mostrar status
        self.btn_gru.setEnabled(False)
        self.btn_gru.setText('⏳ Gerando GRU...')
        self.log_output.clear()
        self.add_log_ui("Iniciando processo...")
        
        def worker():
            try:
                # O callback agora emite o sinal da classe
                arquivo = GRUAutomation.preencher_gru_portal(
                    dados_gru, 
                    headless=True, 
                    log_callback=self.log_signal.emit
                )
                self.finished_signal.emit(arquivo)
            except Exception as e:
                self.error_signal.emit(str(e))

        # Iniciar thread
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
