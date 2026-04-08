"""
Testes para validação de CPF e CNPJ.
"""

import pytest
from core.utils.cpf_cnpj import (
    validar_cpf,
    validar_cnpj,
    validar_cpf_ou_cnpj,
    formatar_cpf,
    formatar_cnpj,
    formatar_documento,
    apenas_numeros,
)


class TestValidarCPF:
    def test_cpf_valido(self):
        # CPF válido gerado com dígitos verificadores corretos
        assert validar_cpf("12345678909") is True
        assert validar_cpf("123.456.789-09") is True

    def test_cpf_invalido_digitos(self):
        # CPF com dígitos verificadores errados
        assert validar_cpf("12345678900") is False
        assert validar_cpf("123.456.789-00") is False

    def test_cpf_tamanho_invalido(self):
        assert validar_cpf("123456789") is False  # 9 dígitos
        assert validar_cpf("123456789090") is False  # 12 dígitos

    def test_cpf_todos_iguais(self):
        # CPFs com todos os dígitos iguais são inválidos
        assert validar_cpf("11111111111") is False
        assert validar_cpf("00000000000") is False

    def test_cpf_vazio(self):
        assert validar_cpf("") is False
        assert validar_cpf(None) is False


class TestValidarCNPJ:
    def test_cnpj_valido(self):
        # CNPJ válido com dígitos verificadores corretos
        assert validar_cnpj("11222333000181") is True
        assert validar_cnpj("11.222.333/0001-81") is True

    def test_cnpj_invalido_digitos(self):
        # CNPJ com dígitos verificadores errados
        assert validar_cnpj("11222333000100") is False
        assert validar_cnpj("11.222.333/0001-00") is False

    def test_cnpj_tamanho_invalido(self):
        assert validar_cnpj("11222333000") is False  # 11 dígitos
        assert validar_cnpj("1122233300018100") is False  # 16 dígitos

    def test_cnpj_todos_iguais(self):
        # CNPJs com todos os dígitos iguais são inválidos
        assert validar_cnpj("11111111111111") is False
        assert validar_cnpj("00000000000000") is False

    def test_cnpj_vazio(self):
        assert validar_cnpj("") is False
        assert validar_cnpj(None) is False


class TestValidarCpfOuCnpj:
    def test_cpf_valido(self):
        assert validar_cpf_ou_cnpj("12345678909") is True
        assert validar_cpf_ou_cnpj("123.456.789-09") is True

    def test_cnpj_valido(self):
        assert validar_cpf_ou_cnpj("11222333000181") is True
        assert validar_cpf_ou_cnpj("11.222.333/0001-81") is True

    def test_documento_invalido(self):
        assert validar_cpf_ou_cnpj("12345678900") is False
        assert validar_cpf_ou_cnpj("documento") is False
        assert validar_cpf_ou_cnpj("") is False
        assert validar_cpf_ou_cnpj(None) is False

    def test_tamanho_invalido(self):
        # Tamanhos que não são 11 (CPF) nem 14 (CNPJ)
        assert validar_cpf_ou_cnpj("1234567890") is False  # 10 dígitos
        assert validar_cpf_ou_cnpj("1234567890123") is False  # 13 dígitos


class TestFormatacao:
    def test_formatar_cpf_valido(self):
        assert formatar_cpf("12345678909") == "123.456.789-09"
        assert formatar_cpf("123.456.789-09") == "123.456.789-09"

    def test_formatar_cpf_invalido(self):
        assert formatar_cpf("12345678900") is None
        assert formatar_cpf("123") is None

    def test_formatar_cnpj_valido(self):
        assert formatar_cnpj("11222333000181") == "11.222.333/0001-81"
        assert formatar_cnpj("11.222.333/0001-81") == "11.222.333/0001-81"

    def test_formatar_cnpj_invalido(self):
        assert formatar_cnpj("11222333000100") is None
        assert formatar_cnpj("123") is None

    def test_formatar_documento_cpf(self):
        assert formatar_documento("12345678909") == "123.456.789-09"
        assert formatar_documento("12345678900") is None

    def test_formatar_documento_cnpj(self):
        assert formatar_documento("11222333000181") == "11.222.333/0001-81"
        assert formatar_documento("11222333000100") is None

    def test_formatar_documento_invalido(self):
        assert formatar_documento("") is None
        assert formatar_documento("123") is None
        assert formatar_documento(None) is None


class TestApenasNumeros:
    def test_cpf_com_mascara(self):
        assert apenas_numeros("123.456.789-09") == "12345678909"

    def test_cnpj_com_mascara(self):
        assert apenas_numeros("11.222.333/0001-81") == "11222333000181"

    def test_apenas_numeros_puros(self):
        assert apenas_numeros("12345678909") == "12345678909"
        assert apenas_numeros("11222333000181") == "11222333000181"

    def test_string_vazia(self):
        assert apenas_numeros("") == ""
        assert apenas_numeros(None) == ""

    def test_string_sem_numeros(self):
        assert apenas_numeros("abc") == ""
        assert apenas_numeros(".../---") == ""
