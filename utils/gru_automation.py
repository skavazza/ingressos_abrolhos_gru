import time
import os
from datetime import date, datetime
from typing import Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class GRUAutomation:
    """Automatiza o preenchimento da GRU no portal PagTesouro"""
    
    BASE_URL = "https://pagtesouro.tesouro.gov.br/portal-gru/#/emissao-gru/formulario?ug=443032&codigoRecolhimento=20343-2"
    REFERENCIA_FIXA = "02148074436287087"

    @staticmethod
    def preencher_gru_portal(dados: Dict[str, Any], headless: bool = True, log_callback=None):
        """
        Abre o navegador e preenche o formulário com os dados fornecidos.
        
        dados deve conter:
        - cnpj: str
        - nome_contribuinte: str
        - competencia: str (MM/AAAA)
        - vencimento: str (DD/MM/AAAA)
        - valor: float
        - download_dir: str (opcional)
        """
        def log(msg):
            print(msg)
            if log_callback:
                log_callback(msg)

        download_dir = dados.get('download_dir')
        if not download_dir:
            download_dir = os.path.join(os.path.expanduser("~"), "Downloads", "GRU")
        
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        log(f"Iniciando automação ('{'Headless' if headless else 'Visível'}')...")
        
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless=new")
        
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            log(f"Acessando Portal PagTesouro...")
            driver.get(GRUAutomation.BASE_URL)
            wait = WebDriverWait(driver, 40)
            
            time.sleep(5)
            
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            if iframes:
                log("Entrando no frame do formulário...")
                driver.switch_to.frame(iframes[0])
            
            def find_and_fill(labels, value, name):
                for label in labels:
                    try:
                        xpath = f"//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label.lower()}')] | " \
                                f"//input[contains(translate(@id, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label.lower()}')] | " \
                                f"//input[contains(translate(@name, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label.lower()}')]"
                        field = driver.find_element(By.XPATH, xpath)
                        if field.is_displayed():
                            field.clear()
                            field.send_keys(value)
                            log(f"Preenchido: {name}")
                            return field
                    except:
                        continue
                log(f"Aviso: Campo '{name}' não localizado.")
                return None

            # Preencher campos
            find_and_fill(['CNPJ', 'contribuinte'], dados['cnpj'], "CNPJ")
            find_and_fill(['nome'], dados['nome_contribuinte'], "Nome")
            find_and_fill(['Referência', 'referencia'], GRUAutomation.REFERENCIA_FIXA, "Referência")
            find_and_fill(['Competência', 'competencia'], dados['competencia'], "Competência")
            find_and_fill(['Vencimento', 'vencimento'], dados['vencimento'], "Vencimento")
            
            valor_str = f"{dados['valor']:.2f}".replace('.', ',')
            find_and_fill(['Valor Principal', 'valor_principal'], valor_str, "Valor Principal")
            
            log("Finalizando e emitindo GRU...")
            try:
                emitir_xpath = "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'emitir gru')]"
                btn_emitir = wait.until(EC.element_to_be_clickable((By.XPATH, emitir_xpath)))
                
                files_before = set(os.listdir(download_dir))
                btn_emitir.click()
                log("Aguardando download do arquivo PDF...")
                
                start_time = time.time()
                while time.time() - start_time < 30:
                    files_after = set(os.listdir(download_dir))
                    new_files = files_after - files_before
                    if new_files:
                        if not any(f.endswith('.crdownload') for f in new_files):
                            downloaded_file = list(new_files)[0]
                            log(f"Arquivo recebido: {downloaded_file}")
                            
                            # Renomear arquivo
                            try:
                                empresa_clean = "".join([c if c.isalnum() else "_" for c in dados['nome_contribuinte']])
                                comp_clean = dados['competencia'].replace('/', '_')
                                novo_nome = f"GRU_{empresa_clean}_{comp_clean}.pdf"
                                old_path = os.path.join(download_dir, downloaded_file)
                                new_path = os.path.join(download_dir, novo_nome)
                                
                                # Se já existe, remover ou renomear com timestamp
                                if os.path.exists(new_path):
                                    os.remove(new_path)
                                os.rename(old_path, new_path)
                                log(f"Arquivo renomeado para: {novo_nome}")
                                return novo_nome
                            except Exception as re_err:
                                log(f"Aviso ao renomear: {re_err}")
                                return downloaded_file
                    time.sleep(1)
                
                log("Erro: Download não detectado no tempo limite.")
            except Exception as e:
                log(f"Erro no clique final: {e}")
                if headless: raise e
            
        except Exception as e:
            log(f"Falha na automação: {str(e)}")
            raise e
        finally:
            if headless:
                driver.quit()
                log("Navegador encerrado.")

    @staticmethod
    def calcular_vencimento(data_referencia: date) -> date:
        """Calcula o vencimento (dia 10, dois meses após)"""
        mes_venc = (data_referencia.month + 2) % 12
        ano_venc = data_referencia.year + (data_referencia.month + 2 > 12)
        if mes_venc == 0: mes_venc = 12
        
        return date(ano_venc, mes_venc, 10)
