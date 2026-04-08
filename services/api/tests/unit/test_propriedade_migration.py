"""Testes para verificar a estrutura do migration C-06."""
import pytest


def test_migration_import():
    """Migration deve importar sem erro."""
    from migrations.versions.add_propriedade_exploracao_rural import (
        upgrade,
        downgrade,
        revision,
        down_revision,
    )
    assert revision == 'add_propriedade_exploracao_rural'
    assert down_revision == '8c2e891d6ba9'


def test_migration_functions_exist():
    """Funções upgrade e downgrade devem existir."""
    from migrations.versions.add_propriedade_exploracao_rural import (
        upgrade,
        downgrade,
    )
    assert callable(upgrade)
    assert callable(downgrade)


def test_migration_structure():
    """Migration deve ter estrutura correta."""
    import inspect
    from migrations.versions.add_propriedade_exploracao_rural import upgrade
    
    source = inspect.getsource(upgrade)
    
    # Verificar se cria as 3 tabelas
    assert 'cadastros_propriedades' in source
    assert 'cadastros_exploracoes_rurais' in source
    assert 'cadastros_documentos_exploracao' in source
    
    # Verificar se cria índices
    assert 'ix_propriedades_tenant' in source
    assert 'ix_exploracoes_tenant' in source
    assert 'ix_exploracoes_vigencia' in source
