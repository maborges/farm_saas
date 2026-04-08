"""
Utilitários para validação e formatação de CPF e CNPJ.
"""

import re
from typing import Optional


def _calcular_digitos_verificadores(numeros_base: str, pesos: list[int]) -> str:
    """Calcula dígitos verificadores para CPF ou CNPJ."""
    total = 0
    for i, peso in enumerate(pesos):
        total += int(numeros_base[i]) * peso
    
    resto = total % 11
    digito = 0 if resto < 2 else 11 - resto
    return str(digito)


def validar_cpf(cpf: str) -> bool:
    """
    Valida CPF usando algoritmo oficial.
    Aceita formatos: 12345678900 ou 123.456.789-00
    """
    if not cpf:
        return False
    
    # Remove caracteres não numéricos
    numeros = re.sub(r'\D', '', cpf)
    
    # Verifica tamanho
    if len(numeros) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais (ex: 111.111.111-11)
    if len(set(numeros)) == 1:
        return False
    
    # Calcula primeiro dígito verificador
    pesos_1 = [10, 9, 8, 7, 6, 5, 4, 3, 2]
    digito_1 = _calcular_digitos_verificadores(numeros[:9], pesos_1)
    
    # Calcula segundo dígito verificador
    pesos_2 = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
    digito_2 = _calcular_digitos_verificadores(numeros[:9] + digito_1, pesos_2)
    
    # Verifica se os dígitos calculados conferem com os dígitos informados
    return numeros[-2:] == digito_1 + digito_2


def validar_cnpj(cnpj: str) -> bool:
    """
    Valida CNPJ usando algoritmo oficial.
    Aceita formatos: 12345678000100 ou 12.345.678/0001-00
    """
    if not cnpj:
        return False
    
    # Remove caracteres não numéricos
    numeros = re.sub(r'\D', '', cnpj)
    
    # Verifica tamanho
    if len(numeros) != 14:
        return False
    
    # Verifica se todos os dígitos são iguais
    if len(set(numeros)) == 1:
        return False
    
    # Calcula primeiro dígito verificador
    pesos_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digito_1 = _calcular_digitos_verificadores(numeros[:12], pesos_1)
    
    # Calcula segundo dígito verificador
    pesos_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digito_2 = _calcular_digitos_verificadores(numeros[:12] + digito_1, pesos_2)
    
    # Verifica se os dígitos calculados conferem com os dígitos informados
    return numeros[-2:] == digito_1 + digito_2


def validar_cpf_ou_cnpj(documento: str) -> bool:
    """
    Valida CPF ou CNPJ automaticamente baseado no tamanho.
    Retorna True se for um CPF ou CNPJ válido.
    """
    if not documento:
        return False
    
    numeros = re.sub(r'\D', '', documento)
    
    if len(numeros) == 11:
        return validar_cpf(numeros)
    elif len(numeros) == 14:
        return validar_cnpj(numeros)
    else:
        return False


def formatar_cpf(cpf: str) -> Optional[str]:
    """
    Formata CPF no padrão XXX.XXX.XXX-XX.
    Retorna None se o CPF for inválido.
    """
    if not validar_cpf(cpf):
        return None
    
    numeros = re.sub(r'\D', '', cpf)
    return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"


def formatar_cnpj(cnpj: str) -> Optional[str]:
    """
    Formata CNPJ no padrão XX.XXX.XXX/XXXX-XX.
    Retorna None se o CNPJ for inválido.
    """
    if not validar_cnpj(cnpj):
        return None
    
    numeros = re.sub(r'\D', '', cnpj)
    return f"{numeros[:2]}.{numeros[2:5]}.{numeros[5:8]}/{numeros[8:12]}-{numeros[12:]}"


def formatar_documento(documento: str) -> Optional[str]:
    """
    Formata CPF ou CNPJ automaticamente.
    Retorna None se o documento for inválido.
    """
    if not documento:
        return None
    
    numeros = re.sub(r'\D', '', documento)
    
    if len(numeros) == 11:
        return formatar_cpf(numeros)
    elif len(numeros) == 14:
        return formatar_cnpj(numeros)
    else:
        return None


def apenas_numeros(documento: str) -> str:
    """Remove todos os caracteres não numéricos do documento."""
    return re.sub(r'\D', '', documento) if documento else ""
