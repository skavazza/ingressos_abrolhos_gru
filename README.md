# Abrolhos Ingressos - Sistema de Gestão

Sistema desktop completo para gerenciamento de empresas de turismo, embarcações e registros de visitação no Parque Nacional Marinho dos Abrolhos (PARNA Abrolhos).

## 📋 Características

- ✅ **Interface Gráfica Premium**: Interface moderna, intuitiva e responsiva (PyQt6) com suporte a rolagem em telas menores.
- ✅ **Automação de GRU (Exclusivo)**: Emissão automatizada de GRU em segundo plano (Headless) com preenchimento via Selenium e download automático gerenciado.
- ✅ **Gestão de Preços Simplificada**: Controle direto de valores por categoria e taxas de embarcação.
- ✅ **Filtros Avançados**: Filtragem de registros por empresa e período.
- ✅ **Exportação Inteligente**: Gera notas de pagamento e relatórios completos em Excel e CSV.
- ✅ **Banco de Dados SQLite**: Armazenamento local seguro e backup integrado.
- ✅ **Cálculo Automático**: Valores calculados com precisão conforme as regras do ICMBio.

## 🚀 Instalação

### Pré-requisitos

- Python 3.10 ou superior
- Google Chrome instalado (para a automação da GRU)
- pip (gerenciador de pacotes do Python)

### Passo a passo

1. **Clone ou baixe o projeto**

2. **Crie um ambiente virtual (recomendado)**

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
```

3. **Instale as dependências**

```bash
pip install -r requirements.txt
```

4. **Inicialize o banco de dados**

```bash
python seed_data.py
```

Isso criará:
- Usuário admin (login: `admin`, senha: `admin123`)
- Empresas e embarcações de exemplo
- Tabela de preços atualizada

## 📊 Como Usar

### Executar o sinal

```bash
python main.py
```

### Modo Servidor (Sincronização)

Para operar no modelo **App Servidor / App Cliente**, execute a API de sincronização
em uma máquina central com acesso ao banco de dados:

```bash
export ABROLHOS_DB_PATH=abrolhos_ingressos.db
export ABROLHOS_UPLOAD_DIR=uploads
uvicorn server.api:app --host 0.0.0.0 --port 8000
```

Endpoints principais:
- `GET /precos/ativo`: retorna a tabela de preços vigente.
- `POST /registros`: recebe registros de visita (clientes).
- `POST /documentos`: recebe documentos para auditoria (nota/GRU).

No app cliente, use o `utils/sync_client.py` para puxar preços, enviar registros
e documentos para o servidor central.

### Funcionalidades em Destaque

#### 1. Emissão de GRU (Segundo Plano)
Na aba **Relatórios**, selecione a empresa e o período, então clique em **🚀 Emitir GRU (Portal)**. O sistema irá:
- Abrir o Chrome em modo invisível.
- Preencher todos os campos (CNPJ, Nome, Competência, Vencimento, Valores).
- Baixar o PDF com nome personalizado (`GRU_Empresa_Periodo.pdf`).
- Salvar em `Downloads/GRU` e abrir a pasta automaticamente.

#### 2. Tabela de Preços
Gerencie facilmente os valores cobrados por categoria (Estrangeiros, Brasileiros, Entorno, etc.) e as taxas de embarcação por porte (<12m ou >=12m).

#### 3. Registros Diários
Acompanhe as visitas, filtrando por empresa para facilitar a gestão. O sistema calcula automaticamente os totais e as taxas devidas.

## 🔧 Gerar Executável (.exe)

O projeto já inclui um arquivo `.spec` configurado para o PyInstaller.

```bash
pip install pyinstaller
pyinstaller abrolhos_ingressos.spec
```

O executável completo com ícone e recursos estará na pasta `dist/`.

## 📁 Estrutura do Projeto

```
abrolhos_ingressos/
│
├── models/             # Modelos de dados e lógica SQL (SQLAlchemy)
├── views/              # Interfaces gráficas (PyQt6)
├── utils/              # Utilitários, validações e automação Selenium
├── assets/             # Ícones e recursos visuais
├── main.py             # Arquivo de entrada do sistema
├── seed_data.py        # Script de população inicial do banco
└── requirements.txt    # Lista de bibliotecas necessárias
```

## 🛠️ Tecnologias Utilizadas

- **Python 3.12+**
- **PyQt6** (Interface Gráfica)
- **Selenium** (Automação Web)
- **SQLAlchemy** (Banco de Dados ORM)
- **SQLite** (Armazenamento Local)
- **Pandas** (Processamento de Dados e Excel)
- **Webdriver-manager** (Gestão automática de drivers do Chrome)

---

**Versão:** 1.0  
**Desenvolvido para:** NGI ICMBio Abrolhos  
**Desenvolvido por:** Alberto Rodrigues (`betorodrigues@msn.com`)  
**Copyright:** © 2026 Alberto Rodrigues  
