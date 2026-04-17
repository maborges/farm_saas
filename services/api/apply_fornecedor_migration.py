#!/usr/bin/env python3
"""
Script para aplicar migration do Fornecedor diretamente ao SQLite
sem depender do Alembic ou das dependências completas.
"""
import sqlite3
import sys

def apply_migration():
    db_path = './agrosaas.db'

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("Conectado ao banco de dados...")

        # Verificar se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='compras_fornecedores'")
        table_exists = cursor.fetchone()

        if not table_exists:
            print("❌ Tabela compras_fornecedores não existe. Rodando migrations primeiro...")
            return False

        print("✅ Tabela compras_fornecedores encontrada")

        # Get current columns
        cursor.execute("PRAGMA table_info(compras_fornecedores)")
        columns = cursor.fetchall()
        col_names = [col[1] for col in columns]
        print(f"Colunas atuais: {col_names}")

        # Columns to add
        new_columns = {
            'email': 'VARCHAR(100)',
            'telefone': 'VARCHAR(20)',
            'condicoes_pagamento': 'VARCHAR(100)',
            'prazo_entrega_dias': 'INTEGER',
            'avaliacao': 'REAL'
        }

        added_count = 0
        for col_name, col_type in new_columns.items():
            if col_name not in col_names:
                try:
                    cursor.execute(f"ALTER TABLE compras_fornecedores ADD COLUMN {col_name} {col_type}")
                    print(f"✅ Coluna adicionada: {col_name}")
                    added_count += 1
                except sqlite3.OperationalError as e:
                    print(f"⚠️  Erro ao adicionar {col_name}: {e}")
            else:
                print(f"ℹ️  Coluna {col_name} já existe")

        # Update alembic_version
        cursor.execute("INSERT OR IGNORE INTO alembic_version (version_num) VALUES ('add_fornecedor_fields')")

        conn.commit()
        conn.close()

        if added_count > 0:
            print(f"\n✅ Migration completada! {added_count} coluna(s) adicionada(s)")
            return True
        else:
            print("\n✅ Nenhuma coluna para adicionar (já existem)")
            return True

    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == '__main__':
    success = apply_migration()
    sys.exit(0 if success else 1)
