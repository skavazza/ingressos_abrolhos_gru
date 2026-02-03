# Guia Rápido de Instalação - Abrolhos Ingressos

## Windows

### Opção 1: Executável (Sem Python)

1. Baixe o arquivo `AbrolhosIngressos_Setup.exe`
2. Dê duplo clique no arquivo
3. Use **admin** / **admin123** para fazer login
4. Pronto!

### Opção 2: Com Python

**Passo 1:** Instale o Python 3.10 ou superior
- Baixe de: https://www.python.org/downloads/
- ✅ Marque "Add Python to PATH" durante a instalação

**Passo 2:** Abra o Prompt de Comando (cmd) na pasta do projeto

**Passo 3:** Crie ambiente virtual (opcional mas recomendado)
```cmd
python -m venv venv
venv\Scripts\activate
```

**Passo 4:** Instale as dependências
```cmd
pip install -r requirements.txt
```

**Passo 5:** Popule o banco de dados
```cmd
python seed_data.py
```

**Passo 6:** Execute o sistema
```cmd
python main.py
```

## Linux / Mac

**Passo 1:** Certifique-se de ter Python 3.10+
```bash
python3 --version
```

**Passo 2:** Crie ambiente virtual
```bash
python3 -m venv venv
source venv/bin/activate
```

**Passo 3:** Instale dependências
```bash
pip install -r requirements.txt
```

**Passo 4:** Popule o banco
```bash
python seed_data.py
```

**Passo 5:** Execute
```bash
python main.py
```

## Credenciais Padrão

- **Usuário:** admin
- **Senha:** admin123

⚠️ **IMPORTANTE:** Troque a senha após o primeiro acesso!

## Problemas Comuns

### "Python não é reconhecido como comando"
- Reinstale o Python marcando "Add to PATH"
- Ou use `python3` ao invés de `python`

### "ModuleNotFoundError"
- Execute: `pip install -r requirements.txt`
- Certifique-se de estar no ambiente virtual ativado

### "Erro ao inicializar banco de dados"
- Delete o arquivo `abrolhos_ingressos.db` (se existir)
- Execute `python seed_data.py` novamente

### Tela muito pequena
- Clique no botão de maximizar
- O sistema se ajusta automaticamente

## Gerar Executável

Para criar um arquivo .exe:

```cmd
pip install pyinstaller
pyinstaller abrolhos_ingressos.spec
```

O executável estará em `dist/AbrolhosIngressos.exe`

## Estrutura de Arquivos Necessária

Para distribuir o sistema:
- `AbrolhosIngressos.exe` (ou pasta com todos os arquivos .py)
- `abrolhos_ingressos.db` (criado automaticamente)

## Localização dos Dados

- **Banco de dados:** `abrolhos_ingressos.db` (mesma pasta do executável)
- **Relatórios exportados:** Onde você escolher salvar

## Fazer Backup

1. Abra o sistema
2. Menu: **Arquivo → Backup do Banco de Dados**
3. Escolha onde salvar
4. Ou copie manualmente o arquivo `abrolhos_ingressos.db`

---

Para mais informações, consulte o **README.md**
