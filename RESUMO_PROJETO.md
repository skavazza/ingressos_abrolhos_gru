# SISTEMA ABROLHOS INGRESSOS - RESUMO DO PROJETO

## 📌 Visão Geral

Sistema desktop completo desenvolvido em Python com PyQt6 para gerenciar registros de visitação, empresas de turismo e embarcações no Parque Nacional Marinho dos Abrolhos (PARNA Abrolhos).

Substitui planilhas Excel e sistema web anterior, oferecendo uma solução offline, robusta e fácil de usar.

## ✨ Funcionalidades Implementadas

### 1. Sistema de Autenticação
- Login com usuário e senha
- Senhas criptografadas com bcrypt
- Usuário padrão: `admin` / `admin123`

### 2. Dashboard
- Estatísticas do mês atual
- Total de visitantes por categoria
- Receita acumulada
- Contadores de empresas e embarcações ativas

### 3. Gestão de Empresas
- Cadastro completo (CNPJ, contatos)
- Validação automática de CNPJ
- Máscaras de entrada para telefone
- Edição e desativação (soft delete)

### 4. Gestão de Embarcações
- Vinculação com empresas
- Tipos: Catamarã, Lancha, Barco, Escuna, Outro
- Capacidade e características técnicas

### 5. Tabela de Preços Histórica
- Preços por ano (2020-2025 pré-cadastrados)
- Categorias: Estrangeiro, Mercosul, Brasileiro, Entorno, Isento
- Faixas etárias opcionais (Maior/Menor 12 anos)
- Vigência configurável

### 6. Registros Diários de Visitação
- Formulário intuitivo com validações
- Seleção de empresa → carrega embarcações automaticamente
- Permanência (multiplicador: 1=aberto, 2=pernoite, etc.)
- **Cálculo automático em tempo real** do valor total
- Campos para cada tipo de visitante
- Botão "Salvar + Novo" para lançamentos em lote
- Edição e exclusão de registros
- Filtro por período

### 7. Relatórios e Exportação
- Exportação para CSV
- Exportação para Excel (.xlsx)
- Filtro por período customizável
- Dados completos: data, empresa, embarcação, quantidades, valores

### 8. Backup
- Backup simples do banco de dados
- Gera arquivo .db com data/hora
- Menu: Arquivo → Backup

## 🎯 Diferenciais

### Baseado nas Planilhas Fornecidas

O sistema foi desenvolvido analisando as planilhas Excel reais do PARNA Abrolhos:

1. **Fórmulas de Cálculo Replicadas**
   - Análise das fórmulas das colunas Q2 e R2
   - Implementação da lógica de permanência × valores
   - Busca automática da tabela de preços vigente

2. **Dados Reais Carregados**
   - 10 empresas reais cadastradas (Abrolhos Adventure, Apecatu, etc.)
   - 23 embarcações reais (Siriba, Netuno, Zeus, Jubarte, etc.)
   - Tabela de preços 2020-2025 com valores reais

3. **Estrutura Familiar**
   - Interface similar às planilhas Excel
   - Campos idênticos (Estrangeiros, Mercosul, Brasileiros, etc.)
   - Mesma lógica de permanência

## 🏗️ Arquitetura Técnica

### Estrutura do Projeto
```
abrolhos_ingressos/
├── models/              # Camada de dados
│   ├── database.py     # SQLAlchemy models
│   └── services.py     # CRUD operations
├── views/               # Camada de apresentação
│   ├── login_dialog.py
│   ├── main_window.py
│   ├── dashboard_tab.py
│   ├── registros_tab.py
│   ├── empresas_tab.py
│   ├── embarcacoes_tab.py
│   ├── precos_tab.py
│   └── relatorios_tab.py
├── utils/               # Utilitários
│   └── validators.py   # Validações e formatações
├── main.py             # Entry point
├── seed_data.py        # Dados iniciais
└── test_system.py      # Testes automatizados
```

### Tecnologias

- **PyQt6 6.7.0** - Interface gráfica moderna
- **SQLAlchemy 2.0.30** - ORM robusto
- **SQLite** - Banco embutido (arquivo único)
- **Pandas 2.2.2** - Exportação de dados
- **bcrypt 4.1.3** - Criptografia de senhas
- **Pydantic 2.7.1** - Validação de dados

### Banco de Dados

6 tabelas principais:
- `usuarios` - Sistema de login
- `empresas` - Empresas de turismo
- `embarcacoes` - Embarcações
- `tabela_preco_ingresso` - Histórico de preços
- `registros_visita` - Registros diários
- `log_auditoria` - Auditoria (opcional)

## 📊 Fluxo de Uso Principal

1. **Login** → admin / admin123
2. **Verificar empresas e embarcações** → Já vem cadastradas
3. **Verificar tabela de preços** → 2020-2025 pré-configurados
4. **Registrar visita:**
   - Selecionar data
   - Escolher empresa
   - Escolher embarcação (carrega automaticamente)
   - Definir permanência
   - Preencher quantidades
   - **Valor calcula automaticamente**
   - Salvar
5. **Gerar relatórios** → Exportar para Excel

## 🚀 Como Executar

### Primeira vez

```bash
# Instalar dependências
pip install -r requirements.txt

# Popular banco com dados iniciais
python seed_data.py

# Executar sistema
python main.py
```

### Testes

```bash
python test_system.py
```

### Gerar Executável

```bash
pip install pyinstaller
pyinstaller abrolhos_ingressos.spec
```

Executável em: `dist/AbrolhosIngressos.exe`

## 📖 Documentação Incluída

1. **README.md** - Documentação completa
2. **INSTALL.md** - Guia de instalação passo a passo
3. **test_system.py** - Testes automatizados
4. **abrolhos_ingressos.spec** - Configuração do PyInstaller

## ✅ Validações Implementadas

- **CNPJ:** Dígitos verificadores
- **Email:** Formato válido
- **Telefone:** 10 ou 11 dígitos
- **Datas:** Formato brasileiro
- **Quantidades:** Não negativos
- **Formulários:** Campos obrigatórios

## 🎨 Interface

- Design moderno e limpo
- Cores institucionais (azul #0078d4)
- Máscaras de entrada automáticas
- Feedback visual (hover, seleção)
- Responsivo e redimensionável
- Ícones emoji para melhor UX

## 💾 Dados de Exemplo Incluídos

### Empresas (10)
- Abrolhos Adventure
- Apecatu Expedições
- Horizonte Aberto
- L.S de Oliveira
- Sanuk Turismo
- Danimar Turismo
- Scuba Turismo
- Essenatur
- JV Calheiros
- Máximus Turismo

### Embarcações (23)
Tipos variados: Catamarãs, Lanchas, Barcos, Escunas
Capacidades de 8 a 50 passageiros

### Preços (2020-2025)
Valores reais baseados nas planilhas fornecidas

## 🔐 Segurança

- Senhas bcrypt (não reversíveis)
- SQL injection protected (SQLAlchemy)
- Soft delete (dados não são perdidos)
- Backup integrado

## 📈 Escalabilidade

- Multi-usuário ready (estrutura preparada)
- Log de auditoria (tabela criada)
- Modular (fácil adicionar novas funcionalidades)
- Exportação flexível (CSV, Excel)

## 🎯 Diferenças do Sistema Antigo

| Aspecto | Sistema Antigo | Sistema Novo |
|---------|----------------|--------------|
| Tecnologia | Web/Popup | Desktop (PyQt6) |
| Dependência | Internet | Offline total |
| Dados | Planilha Excel | SQLite |
| Cálculos | Manuais/Fórmulas | Automáticos |
| Backup | Copiar Excel | Botão integrado |
| Histórico | Difícil | Fácil consulta |
| Validação | Limitada | Completa |
| Relatórios | Manual | Export automático |

## 💡 Próximos Passos Sugeridos

1. **Customizar usuário admin** → Trocar senha
2. **Testar fluxo completo** → Criar alguns registros
3. **Fazer backup inicial** → Menu Arquivo
4. **Gerar executável** → Para distribuir
5. **Treinar usuários** → Interface intuitiva

## 📞 Suporte

Para dúvidas:
- Consultar README.md
- Executar test_system.py
- Verificar INSTALL.md

## 🏆 Conclusão

Sistema completo, funcional e pronto para produção. Substitui com vantagens o sistema anterior, mantendo familiaridade com as planilhas Excel existentes mas com validações robustas, cálculos automáticos e gestão profissional de dados.

---

**Desenvolvido para:** ICMBio - Parque Nacional Marinho dos Abrolhos  
**Data:** Fevereiro 2025  
**Versão:** 1.0
