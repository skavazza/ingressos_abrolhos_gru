"""
Script de teste para verificar se o sistema está funcionando corretamente
"""
import sys
from datetime import date

def test_imports():
    """Testa se todas as bibliotecas necessárias estão instaladas"""
    print("=== Testando Importações ===")
    
    try:
        import PyQt6
        print("✓ PyQt6")
    except ImportError:
        print("✗ PyQt6 não instalado")
        return False
    
    try:
        import sqlalchemy
        print("✓ SQLAlchemy")
    except ImportError:
        print("✗ SQLAlchemy não instalado")
        return False
    
    try:
        import pandas
        print("✓ Pandas")
    except ImportError:
        print("✗ Pandas não instalado")
        return False
    
    try:
        import bcrypt
        print("✓ bcrypt")
    except ImportError:
        print("✗ bcrypt não instalado")
        return False
    
    try:
        import openpyxl
        print("✓ openpyxl")
    except ImportError:
        print("✗ openpyxl não instalado")
        return False
    
    return True


def test_database():
    """Testa se o banco de dados funciona"""
    print("\n=== Testando Banco de Dados ===")
    
    try:
        from models.database import init_db
        from models.services import UsuarioService, EmpresaService
        
        # Cria banco temporário
        engine, SessionLocal = init_db('test_temp.db')
        session = SessionLocal()
        
        # Testa criação de usuário
        usuario = UsuarioService.criar_usuario(
            session, 
            'test_user', 
            'test_pass', 
            'Test User'
        )
        print(f"✓ Usuário criado: {usuario.username}")
        
        # Testa autenticação
        auth = UsuarioService.autenticar(session, 'test_user', 'test_pass')
        if auth:
            print("✓ Autenticação funcionando")
        else:
            print("✗ Erro na autenticação")
            return False
        
        # Testa criação de empresa
        empresa = EmpresaService.criar(
            session,
            nome='Empresa Teste',
            cnpj='12.345.678/0001-90'
        )
        print(f"✓ Empresa criada: {empresa.nome}")
        
        session.close()
        
        # Remove banco temporário
        import os
        os.remove('test_temp.db')
        
        return True
        
    except Exception as e:
        print(f"✗ Erro no banco de dados: {str(e)}")
        return False


def test_validators():
    """Testa validadores"""
    print("\n=== Testando Validadores ===")
    
    try:
        from utils.validators import Validadores, Formatadores
        
        # Testa CNPJ
        if Validadores.validar_cnpj('11.222.333/0001-81'):
            print("✓ Validação de CNPJ")
        else:
            print("✗ Validação de CNPJ")
            return False
        
        # Testa formatação
        cnpj_formatado = Formatadores.formatar_cnpj('11222333000181')
        if cnpj_formatado == '11.222.333/0001-81':
            print("✓ Formatação de CNPJ")
        else:
            print("✗ Formatação de CNPJ")
            return False
        
        # Testa moeda
        moeda = Formatadores.formatar_moeda(1234.56)
        if 'R$' in moeda and '1.234,56' in moeda:
            print("✓ Formatação de moeda")
        else:
            print("✗ Formatação de moeda")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Erro nos validadores: {str(e)}")
        return False


def test_calculation():
    """Testa cálculo de valores"""
    print("\n=== Testando Cálculo de Valores ===")
    
    try:
        from models.database import init_db
        from models.services import TabelaPrecoService, RegistroVisitaService
        
        engine, SessionLocal = init_db('test_calc.db')
        session = SessionLocal()
        
        # Cria tabela de preços
        tabela = TabelaPrecoService.criar(
            session,
            ano_inicio=2025,
            valores={
                'valor_estrangeiro': 100.0,
                'valor_mercosul': 75.0,
                'valor_brasileiro': 50.0,
                'valor_entorno': 10.0,
                'valor_isento': 0.0
            }
        )
        
        # Testa cálculo
        quantidades = {
            'qtde_estrangeiros': 2,
            'qtde_mercosul': 1,
            'qtde_brasileiros': 3,
            'qtde_entorno': 0,
            'qtde_isentos': 1
        }
        
        valor = RegistroVisitaService.calcular_valor_total(
            session,
            date(2025, 1, 15),
            quantidades,
            permanencia=1
        )
        
        # 2*100 + 1*75 + 3*50 + 0*10 + 1*0 = 200 + 75 + 150 = 425
        if valor == 425.0:
            print(f"✓ Cálculo correto: R$ {valor:.2f}")
        else:
            print(f"✗ Cálculo incorreto. Esperado: 425.00, Obtido: {valor:.2f}")
            return False
        
        session.close()
        
        # Remove banco temporário
        import os
        os.remove('test_calc.db')
        
        return True
        
    except Exception as e:
        print(f"✗ Erro no cálculo: {str(e)}")
        return False


def main():
    """Executa todos os testes"""
    print("╔═══════════════════════════════════════════╗")
    print("║   TESTE DO SISTEMA ABROLHOS INGRESSOS    ║")
    print("╚═══════════════════════════════════════════╝\n")
    
    tests = [
        ("Importações", test_imports),
        ("Banco de Dados", test_database),
        ("Validadores", test_validators),
        ("Cálculo de Valores", test_calculation),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Erro fatal em '{name}': {str(e)}")
            results.append((name, False))
    
    # Resumo
    print("\n" + "="*50)
    print("RESUMO DOS TESTES")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✓ PASSOU" if result else "✗ FALHOU"
        print(f"{name:.<30} {status}")
        if result:
            passed += 1
    
    print("="*50)
    print(f"Total: {passed}/{total} testes passaram")
    print("="*50)
    
    if passed == total:
        print("\n🎉 Todos os testes passaram! O sistema está pronto para uso.")
        print("\nPara iniciar o sistema, execute:")
        print("  python main.py")
        return 0
    else:
        print("\n❌ Alguns testes falharam. Verifique os erros acima.")
        print("\nPara instalar dependências faltantes:")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == '__main__':
    sys.exit(main())
