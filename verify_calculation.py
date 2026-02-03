from datetime import date
from models.database import init_db
from models.services import TabelaPrecoService, RegistroVisitaService

def verify():
    # Setup in-memory db
    engine, SessionLocal = init_db(':memory:')
    session = SessionLocal()
    
    try:
        # Create pricing table (using 2025 values from seed_data logic)
        TabelaPrecoService.criar(
            session,
            ano_inicio=2026,
            valores={
                'valor_estrangeiro': 96.00,
                'valor_mercosul': 72.00,
                'valor_brasileiro': 5.00,
                'valor_entorno': 13.00,
                'valor_isento': 0.00,
                'valor_maior12': 43.00,
                'valor_menor12': 28.00
            }
        )
        
        print("=== Verification Results ===")
        
        # Scenario 1: Boat < 12m, 0 Visitors
        # Expected: 28.00 (boat fee only)
        val1 = RegistroVisitaService.calcular_valor_total(
            session, date(2026, 2, 2), {}, 
            permanencia=1, comprimento_embarcacao_m=11.0
        )
        print(f"Scenario 1 (<12m, 0 pax): Ex: 28.00 | Got: {val1} -> {'PASS' if val1 == 28.0 else 'FAIL'}")
        
        # Scenario 2: Boat >= 12m, 0 Visitors
        # Expected: 43.00
        val2 = RegistroVisitaService.calcular_valor_total(
            session, date(2026, 2, 2), {}, 
            permanencia=1, comprimento_embarcacao_m=12.0
        )
        print(f"Scenario 2 (>=12m, 0 pax): Ex: 43.00 | Got: {val2} -> {'PASS' if val2 == 43.0 else 'FAIL'}")
        
        # Scenario 3: Boat < 12m, 1 Brasileiro (5.00)
        # Expected: 28.00 + 5.00 = 33.00
        qtde = {'qtde_brasileiros': 1}
        val3 = RegistroVisitaService.calcular_valor_total(
            session, date(2026, 2, 2), qtde, 
            permanencia=1, comprimento_embarcacao_m=11.0
        )
        print(f"Scenario 3 (<12m, 1 Bra): Ex: 33.00 | Got: {val3} -> {'PASS' if val3 == 33.0 else 'FAIL'}")
        
    finally:
        session.close()

if __name__ == "__main__":
    verify()
