"""
Script para popular o banco de dados com dados iniciais
"""
from datetime import date, datetime
from models.database import init_db, Usuario, Empresa, Embarcacao, TabelaPrecoIngresso
from models.services import UsuarioService, EmpresaService, EmbarcacaoService, TabelaPrecoService


def seed_database(db_path: str = 'abrolhos_ingressos.db'):
    """
    Popula o banco de dados com dados de exemplo
    
    Args:
        db_path: Caminho para o arquivo do banco de dados
    """
    print("Inicializando banco de dados...")
    engine, SessionLocal = init_db(db_path)
    session = SessionLocal()
    
    try:
        # Criar usuário admin padrão
        print("\n1. Criando usuário admin...")
        if not session.query(Usuario).filter_by(username='admin').first():
            UsuarioService.criar_usuario(
                session, 
                username='admin', 
                password='admin123',
                nome_completo='Administrador do Sistema',
                is_admin=True
            )
            print("   ✓ Usuário 'admin' criado (senha: admin123)")
        else:
            print("   ℹ Usuário 'admin' já existe")
        
        # Criar tabelas de preços históricas
        print("\n2. Criando tabelas de preços...")
        # Limpar tabelas existentes para garantir a nova estrutura
        session.query(TabelaPrecoIngresso).delete()
        session.commit()

        tabelas_precos = [
            {
                'ano_inicio': 2020, 'ano_fim': 2020,
                'valor_estrangeiro': 92.00, 'valor_mercosul': 69.00, 'valor_brasileiro': 46.00, 'valor_entorno': 9.20,
                'valor_fundeio_ate8': 21.00, 'valor_fundeio_8a15': 28.00, 'valor_fundeio_acima15': 41.00,
                'observacao': 'Tabela 2020'
            },
            {
                'ano_inicio': 2021, 'ano_fim': 2021,
                'valor_estrangeiro': 96.00, 'valor_mercosul': 72.00, 'valor_brasileiro': 48.00, 'valor_entorno': 9.60,
                'valor_fundeio_ate8': 23.00, 'valor_fundeio_8a15': 35.00, 'valor_fundeio_acima15': 62.00,
                'observacao': 'Tabela 2021'
            },
            {
                'ano_inicio': 2022, 'ano_fim': 2022,
                'valor_estrangeiro': 104.00, 'valor_mercosul': 78.00, 'valor_brasileiro': 52.00, 'valor_entorno': 10.40,
                'valor_fundeio_ate8': 25.00, 'valor_fundeio_8a15': 38.00, 'valor_fundeio_acima15': 67.00,
                'observacao': 'Tabela 2022'
            },
            {
                'ano_inicio': 2023, 'ano_fim': 2023,
                'valor_estrangeiro': 104.00, 'valor_mercosul': 78.00, 'valor_brasileiro': 52.00, 'valor_entorno': 10.40,
                'valor_fundeio_ate8': 26.00, 'valor_fundeio_8a15': 39.00, 'valor_fundeio_acima15': 69.00,
                'observacao': 'Tabela 2023'
            },
            {
                'ano_inicio': 2024, 'ano_fim': 2024,
                'valor_estrangeiro': 108.00, 'valor_mercosul': 81.00, 'valor_brasileiro': 54.00, 'valor_entorno': 10.80,
                'valor_fundeio_ate8': 26.00, 'valor_fundeio_8a15': 39.00, 'valor_fundeio_acima15': 69.00,
                'observacao': 'Tabela 2024'
            },
            {
                'ano_inicio': 2025, 'ano_fim': None,
                'valor_estrangeiro': 111.00, 'valor_mercosul': 83.25, 'valor_brasileiro': 55.50, 'valor_entorno': 11.10,
                'valor_fundeio_ate8': 27.00, 'valor_fundeio_8a15': 41.00, 'valor_fundeio_acima15': 73.00,
                'observacao': 'Tabela 2025 em diante'
            }
        ]
        
        for tabela_data in tabelas_precos:
            ano_inicio = tabela_data['ano_inicio']
            valores = {k: v for k, v in tabela_data.items() if k.startswith('valor_')}
            # Remover isento se não estiver na lista acima ou garantir que exista padrão
            valores['valor_isento'] = 0.0
            
            kwargs = {k: v for k, v in tabela_data.items() if k != 'ano_inicio' and not k.startswith('valor_')}
            TabelaPrecoService.criar(session, ano_inicio, valores, **kwargs)
            print(f"   ✓ Tabela de preços {tabela_data['ano_inicio']} criada")
        
        # Criar empresas de exemplo
        print("\n3. Criando empresas...")
        empresas_data = [
            {
                'nome': 'Abrolhos Adventure',
                'cnpj': '12.345.678/0001-90',
                'contato_nome': 'João Silva',
                'contato_telefone': '(73) 99999-1111',
                'contato_email': 'contato@abrolhosadventure.com.br'
            },
            {
                'nome': 'Apecatu Expedições',
                'cnpj': '23.456.789/0001-01',
                'contato_nome': 'Maria Santos',
                'contato_telefone': '(73) 99999-2222',
                'contato_email': 'contato@apecatu.com.br'
            },
            {
                'nome': 'Horizonte Aberto',
                'cnpj': '34.567.890/0001-12',
                'contato_nome': 'Pedro Costa',
                'contato_telefone': '(73) 99999-3333',
                'contato_email': 'contato@horizonteaberto.com.br'
            },
            {
                'nome': 'L.S de Oliveira',
                'cnpj': '45.678.901/0001-23',
                'contato_nome': 'Lucas Oliveira',
                'contato_telefone': '(73) 99999-4444',
                'contato_email': 'contato@lsoliveira.com.br'
            },
            {
                'nome': 'Sanuk Turismo',
                'cnpj': '56.789.012/0001-34',
                'contato_nome': 'Ana Paula',
                'contato_telefone': '(73) 99999-5555',
                'contato_email': 'contato@sanukturismo.com.br'
            },
            {
                'nome': 'Danimar Turismo',
                'cnpj': '67.890.123/0001-45',
                'contato_nome': 'Daniel Marinho',
                'contato_telefone': '(73) 99999-6666',
                'contato_email': 'contato@danimarturismo.com.br'
            },
            {
                'nome': 'Scuba Turismo',
                'cnpj': '78.901.234/0001-56',
                'contato_nome': 'Roberto Dias',
                'contato_telefone': '(73) 99999-7777',
                'contato_email': 'contato@scubaturismo.com.br'
            },
            {
                'nome': 'Escamatur',
                'cnpj': '89.012.345/0001-67',
                'contato_nome': 'Fernanda Lima',
                'contato_telefone': '(73) 99999-8888',
                'contato_email': 'contato@essenatur.com.br'
            },
            {
                'nome': 'JV Calheiros',
                'cnpj': '90.123.456/0001-78',
                'contato_nome': 'João Victor',
                'contato_telefone': '(73) 99999-9999',
                'contato_email': 'contato@jvcalheiros.com.br'
            },
            {
                'nome': 'Máximus Turismo',
                'cnpj': '01.234.567/0001-89',
                'contato_nome': 'Márcio Silva',
                'contato_telefone': '(73) 99999-0000',
                'contato_email': 'contato@maximusturismo.com.br'
            }
        ]
        
        empresas_criadas = {}
        for emp_data in empresas_data:
            empresa = session.query(Empresa).filter_by(nome=emp_data['nome']).first()
            if not empresa:
                empresa = EmpresaService.criar(session, **emp_data)
                print(f"   ✓ Empresa '{emp_data['nome']}' criada")
            else:
                print(f"   ℹ Empresa '{emp_data['nome']}' já existe")
            empresas_criadas[emp_data['nome']] = empresa
        
        # Criar embarcações de exemplo
        print("\n4. Criando embarcações...")
        embarcacoes_data = [
            # Abrolhos Adventure
            {'empresa': 'Abrolhos Adventure', 'nome': 'Siriba', 'tipo': 'Lancha', 'capacidade_pax': 10, 'comprimento_m': 11.0},
            {'empresa': 'Abrolhos Adventure', 'nome': 'Siriba II', 'tipo': 'Lancha', 'capacidade_pax': 10, 'comprimento_m': 11.0},
            {'empresa': 'Abrolhos Adventure', 'nome': 'Pegasus I', 'tipo': 'Catamarã', 'capacidade_pax': 50, 'comprimento_m': 18.0},
            
            # Apecatu Expedições
            {'empresa': 'Apecatu Expedições', 'nome': 'Netuno', 'tipo': 'Catamarã', 'capacidade_pax': 12, 'comprimento_m': 13.0},
            {'empresa': 'Apecatu Expedições', 'nome': 'Zeus', 'tipo': 'Catamarã', 'capacidade_pax': 12, 'comprimento_m': 13.0},
            
            # Horizonte Aberto
            {'empresa': 'Horizonte Aberto', 'nome': 'Andarilho', 'tipo': 'Catamarã', 'capacidade_pax': 10, 'comprimento_m': 12.0},
            {'empresa': 'Horizonte Aberto', 'nome': 'Horizonte Aberto', 'tipo': 'Catamarã', 'capacidade_pax': 18, 'comprimento_m': 13.0},
            {'empresa': 'Horizonte Aberto', 'nome': 'Imagine', 'tipo': 'Catamarã', 'capacidade_pax': 12, 'comprimento_m': 11.0},
            
            # L.S de Oliveira
            {'empresa': 'L.S de Oliveira', 'nome': 'Jubarte', 'tipo': 'Catamarã', 'capacidade_pax': 30, 'comprimento_m': 14.0},
            {'empresa': 'L.S de Oliveira', 'nome': 'Oceano', 'tipo': 'Catamarã', 'capacidade_pax': 30, 'comprimento_m': 14.0},
            
            # Sanuk Turismo
            {'empresa': 'Sanuk Turismo', 'nome': 'Sanuk', 'tipo': 'Barco', 'capacidade_pax': 16, 'comprimento_m': 13.0},
            {'empresa': 'Sanuk Turismo', 'nome': 'Sanuk Star', 'tipo': 'Catamarã', 'capacidade_pax': 12, 'comprimento_m': 12.0},
            
            # Danimar Turismo
            {'empresa': 'Danimar Turismo', 'nome': 'Danimar', 'tipo': 'Barco', 'capacidade_pax': 8, 'comprimento_m': 11.0},
            {'empresa': 'Danimar Turismo', 'nome': 'Rafaela 3R', 'tipo': 'Barco', 'capacidade_pax': 11, 'comprimento_m': 12.0},
            {'empresa': 'Danimar Turismo', 'nome': 'Rafaela II', 'tipo': 'Lancha', 'capacidade_pax': 8, 'comprimento_m': 12.0},
            {'empresa': 'Danimar Turismo', 'nome': 'Drigor', 'tipo': 'Lancha', 'capacidade_pax': 8, 'comprimento_m': 12.0},
            {'empresa': 'Danimar Turismo', 'nome': 'Filena Star', 'tipo': 'Escuna', 'capacidade_pax': 12, 'comprimento_m': 12.0},
            
            # Scuba Turismo
            {'empresa': 'Scuba Turismo', 'nome': 'Terra Mater', 'tipo': 'Barco', 'capacidade_pax': 15, 'comprimento_m': 12.0},
            
            # Essenatur
            {'empresa': 'Escamatur', 'nome': 'Let It Be', 'tipo': 'Escuna', 'capacidade_pax': 12, 'comprimento_m': 12.0},
            
            # JV Calheiros
            {'empresa': 'JV Calheiros', 'nome': 'Comendador', 'tipo': 'Barco', 'capacidade_pax': 15, 'comprimento_m': 12.0},
            {'empresa': 'JV Calheiros', 'nome': 'Gideão', 'tipo': 'Barco', 'capacidade_pax': 20, 'comprimento_m': 12.0},
            
            # Máximus Turismo
            {'empresa': 'Máximus Turismo', 'nome': 'Máximus', 'tipo': 'Barco', 'capacidade_pax': 10, 'comprimento_m': 14.0},
        ]
        
        for emb_data in embarcacoes_data:
            empresa_nome = emb_data.pop('empresa')
            empresa = empresas_criadas.get(empresa_nome)
            
            if empresa:
                embarcacao = session.query(Embarcacao).filter_by(
                    nome=emb_data['nome'],
                    empresa_id=empresa.id
                ).first()
                
                if not embarcacao:
                    EmbarcacaoService.criar(session, empresa.id, **emb_data)
                    print(f"   ✓ Embarcação '{emb_data['nome']}' ({empresa_nome}) criada")
                else:
                    print(f"   ℹ Embarcação '{emb_data['nome']}' já existe")
        
        print("\n✅ Banco de dados populado com sucesso!")
        print("\n📋 Resumo:")
        print(f"   - Usuários: {session.query(Usuario).count()}")
        print(f"   - Empresas: {session.query(Empresa).count()}")
        print(f"   - Embarcações: {session.query(Embarcacao).count()}")
        print(f"   - Tabelas de Preços: {session.query(TabelaPrecoIngresso).count()}")
        
    except Exception as e:
        print(f"\n❌ Erro ao popular banco de dados: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == '__main__':
    seed_database()
