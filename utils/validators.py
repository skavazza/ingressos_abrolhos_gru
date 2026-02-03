"""
Utilitários para validação e formatação de dados
"""
import re
from datetime import datetime, date
from typing import Optional


class Validadores:
    """Validadores de dados"""
    
    @staticmethod
    def validar_cnpj(cnpj: str) -> bool:
        """
        Valida um CNPJ
        
        Args:
            cnpj: CNPJ no formato XX.XXX.XXX/XXXX-XX ou apenas números
            
        Returns:
            bool: True se válido
        """
        # Remove caracteres não numéricos
        cnpj = re.sub(r'[^0-9]', '', cnpj)
        
        # Verifica se tem 14 dígitos
        if len(cnpj) != 14:
            return False
        
        # Verifica se todos os dígitos são iguais
        if cnpj == cnpj[0] * 14:
            return False
        
        # Calcula primeiro dígito verificador
        soma = 0
        peso = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        for i in range(12):
            soma += int(cnpj[i]) * peso[i]
        
        digito1 = 11 - (soma % 11)
        if digito1 >= 10:
            digito1 = 0
        
        if int(cnpj[12]) != digito1:
            return False
        
        # Calcula segundo dígito verificador
        soma = 0
        peso = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        for i in range(13):
            soma += int(cnpj[i]) * peso[i]
        
        digito2 = 11 - (soma % 11)
        if digito2 >= 10:
            digito2 = 0
        
        if int(cnpj[13]) != digito2:
            return False
        
        return True
    
    @staticmethod
    def validar_email(email: str) -> bool:
        """Valida um endereço de email"""
        if not email:
            return True  # Email é opcional
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validar_telefone(telefone: str) -> bool:
        """Valida um número de telefone brasileiro"""
        if not telefone:
            return True  # Telefone é opcional
        
        # Remove caracteres não numéricos
        numeros = re.sub(r'[^0-9]', '', telefone)
        
        # Aceita 10 ou 11 dígitos (com ou sem 9 na frente)
        return len(numeros) in [10, 11]


class Formatadores:
    """Formatadores de dados"""
    
    @staticmethod
    def formatar_cnpj(cnpj: str) -> str:
        """
        Formata CNPJ para o padrão XX.XXX.XXX/XXXX-XX
        
        Args:
            cnpj: CNPJ sem formatação
            
        Returns:
            str: CNPJ formatado
        """
        # Remove caracteres não numéricos
        cnpj = re.sub(r'[^0-9]', '', cnpj)
        
        if len(cnpj) != 14:
            return cnpj
        
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    
    @staticmethod
    def formatar_telefone(telefone: str) -> str:
        """
        Formata telefone para o padrão (XX) XXXXX-XXXX ou (XX) XXXX-XXXX
        
        Args:
            telefone: Telefone sem formatação
            
        Returns:
            str: Telefone formatado
        """
        # Remove caracteres não numéricos
        numeros = re.sub(r'[^0-9]', '', telefone)
        
        if len(numeros) == 11:  # Celular com 9
            return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
        elif len(numeros) == 10:  # Fixo
            return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
        else:
            return telefone
    
    @staticmethod
    def formatar_moeda(valor: float) -> str:
        """
        Formata valor para moeda brasileira
        
        Args:
            valor: Valor numérico
            
        Returns:
            str: Valor formatado como R$ X.XXX,XX
        """
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    @staticmethod
    def formatar_data(data: date, formato: str = "%d/%m/%Y") -> str:
        """
        Formata data
        
        Args:
            data: Objeto date
            formato: Formato desejado
            
        Returns:
            str: Data formatada
        """
        if isinstance(data, str):
            return data
        return data.strftime(formato)
    
    @staticmethod
    def parse_data(data_str: str, formato: str = "%d/%m/%Y") -> Optional[date]:
        """
        Converte string para date
        
        Args:
            data_str: String com a data
            formato: Formato da string
            
        Returns:
            date ou None
        """
        try:
            return datetime.strptime(data_str, formato).date()
        except (ValueError, AttributeError):
            return None


class MascaraInput:
    """Máscaras para campos de entrada"""
    
    CNPJ = "99.999.999/9999-99"
    TELEFONE_CELULAR = "(99) 99999-9999"
    TELEFONE_FIXO = "(99) 9999-9999"
    DATA = "99/99/9999"
    
    @staticmethod
    def aplicar_mascara_cnpj(texto: str) -> str:
        """Aplica máscara de CNPJ durante digitação"""
        numeros = re.sub(r'[^0-9]', '', texto)
        
        if len(numeros) <= 2:
            return numeros
        elif len(numeros) <= 5:
            return f"{numeros[:2]}.{numeros[2:]}"
        elif len(numeros) <= 8:
            return f"{numeros[:2]}.{numeros[2:5]}.{numeros[5:]}"
        elif len(numeros) <= 12:
            return f"{numeros[:2]}.{numeros[2:5]}.{numeros[5:8]}/{numeros[8:]}"
        else:
            return f"{numeros[:2]}.{numeros[2:5]}.{numeros[5:8]}/{numeros[8:12]}-{numeros[12:14]}"
    
    @staticmethod
    def aplicar_mascara_telefone(texto: str) -> str:
        """Aplica máscara de telefone durante digitação"""
        numeros = re.sub(r'[^0-9]', '', texto)
        
        if len(numeros) <= 2:
            return numeros
        elif len(numeros) <= 6:
            return f"({numeros[:2]}) {numeros[2:]}"
        elif len(numeros) <= 10:
            return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
        else:
            return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:11]}"
