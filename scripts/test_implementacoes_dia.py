#!/usr/bin/env python3
"""
Script de Testes Integrados — Implementações do Dia 2026-04-01

Testa todas as funcionalidades implementadas:
1. Validação de Limites
2. Notificações + Alertas Automáticos
3. Configurações Globais (conversão de unidades, categorias)
4. Upload de Shapefile/KML

Uso:
    python scripts/test_implementacoes_dia.py

Requisitos:
    - Backend rodando em http://localhost:8000
    - Token JWT válido de admin
"""
import requests
import json
import sys
from typing import Optional

# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

BASE_URL = "http://localhost:8000/api/v1"

# Tentar obter token do ambiente ou usar placeholder
import os
TOKEN = os.environ.get("AGROSAAS_TOKEN", "SEU_TOKEN_AQUI")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

def testar_backend_online():
    """Verifica se backend está online."""
    try:
        response = requests.get(f"{BASE_URL}/config/unidades-area", timeout=5)
        return response.status_code == 200
    except Exception:
        return False

# =============================================================================
# TESTE 1: VALIDAÇÃO DE LIMITES
# =============================================================================

def testar_validacao_limites():
    """Testa endpoint de limites do tenant."""
    print("\n" + "="*60)
    print("TESTE 1: Validação de Limites")
    print("="*60)
    
    # Testar GET /billing/limits
    try:
        response = requests.get(
            f"{BASE_URL}/billing/limits",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            dados = response.json()
            print("✅ GET /billing/limits — SUCESSO")
            print(f"   max_fazendas: {dados['max_fazendas']['atual']}/{dados['max_fazendas']['limite']}")
            print(f"   max_usuarios: {dados['max_usuarios']['atual']}/{dados['max_usuarios']['limite']}")
            print(f"   storage: {dados['storage']['atual']}/{dados['storage']['limite']} MB")
            return True
        else:
            print(f"❌ GET /billing/limits — ERRO {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False


# =============================================================================
# TESTE 2: NOTIFICAÇÕES
# =============================================================================

def testar_notificacoes():
    """Testa sistema de notificações."""
    print("\n" + "="*60)
    print("TESTE 2: Notificações")
    print("="*60)
    
    testes_passaram = True
    
    # Teste 2.1: Listar notificações
    try:
        response = requests.get(
            f"{BASE_URL}/notificacoes/?limit=5",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            notificacoes = response.json()
            print(f"✅ Listar notificações — {len(notificacoes)} notificações")
        else:
            print(f"❌ Listar notificações — ERRO {response.status_code}")
            testes_passaram = False
            
    except Exception as e:
        print(f"❌ Listar notificações — ERRO: {e}")
        testes_passaram = False
    
    # Teste 2.2: Contar não lidas
    try:
        response = requests.get(
            f"{BASE_URL}/notificacoes/nao-lidas-count",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            dados = response.json()
            print(f"✅ Contar não lidas — {dados['count']} não lidas")
        else:
            print(f"❌ Contar não lidas — ERRO {response.status_code}")
            testes_passaram = False
            
    except Exception as e:
        print(f"❌ Contar não lidas — ERRO: {e}")
        testes_passaram = False
    
    # Teste 2.3: Criar notificação de teste
    try:
        response = requests.post(
            f"{BASE_URL}/notificacoes/",
            headers=HEADERS,
            json={
                "tipo": "TESTE_AUTOMATIZADO",
                "titulo": "Teste de Notificação",
                "mensagem": "Esta é uma notificação de teste automatizado",
                "meta": {"teste": True, "data": "2026-04-01"}
            }
        )
        
        if response.status_code == 201:
            print("✅ Criar notificação — SUCESSO")
        else:
            print(f"❌ Criar notificação — ERRO {response.status_code}")
            testes_passaram = False
            
    except Exception as e:
        print(f"❌ Criar notificação — ERRO: {e}")
        testes_passaram = False
    
    # Teste 2.4: Gerar demo (se admin)
    try:
        response = requests.post(
            f"{BASE_URL}/notificacoes/demo",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            dados = response.json()
            print(f"✅ Demo notificações — {dados['message']}")
        else:
            print(f"⚠️  Demo notificações — ERRO {response.status_code} (pode ser normal)")
            
    except Exception as e:
        print(f"⚠️  Demo notificações — ERRO: {e}")
    
    return testes_passaram


# =============================================================================
# TESTE 3: CONFIGURAÇÕES GLOBAIS
# =============================================================================

def testar_configuracoes_globais():
    """Testa configurações globais e conversão de unidades."""
    print("\n" + "="*60)
    print("TESTE 3: Configurações Globais")
    print("="*60)
    
    testes_passaram = True
    
    # Teste 3.1: Obter configurações gerais
    try:
        response = requests.get(
            f"{BASE_URL}/config/geral",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            configs = response.json()
            print("✅ GET /config/geral — SUCESSO")
            print(f"   ano_agricola: {configs['ano_agricola']}")
            print(f"   unidade_area: {configs['unidade_area']}")
            print(f"   moeda: {configs['moeda']}")
        else:
            print(f"❌ GET /config/geral — ERRO {response.status_code}")
            testes_passaram = False
            
    except Exception as e:
        print(f"❌ GET /config/geral — ERRO: {e}")
        testes_passaram = False
    
    # Teste 3.2: Listar unidades de área
    try:
        response = requests.get(
            f"{BASE_URL}/config/unidades-area",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            unidades = response.json()
            print(f"✅ Listar unidades — {len(unidades)} unidades disponíveis")
            for u in unidades[:3]:
                print(f"   - {u['nome']} ({u['codigo']})")
        else:
            print(f"❌ Listar unidades — ERRO {response.status_code}")
            testes_passaram = False
            
    except Exception as e:
        print(f"❌ Listar unidades — ERRO: {e}")
        testes_passaram = False
    
    # Teste 3.3: Converter área (100 alqueires paulistas → hectares)
    try:
        response = requests.post(
            f"{BASE_URL}/config/converter-area",
            headers=HEADERS,
            json={
                "valor": 100,
                "unidade_origem": "ALQUEIRE_PAULISTA",
                "unidade_destino": "HA"
            }
        )
        
        if response.status_code == 200:
            dados = response.json()
            print(f"✅ Converter área — 100 alq. paulista = {dados['valor_convertido']} ha")
            
            # Validar resultado esperado (100 * 2.42 = 242)
            if abs(dados['valor_convertido'] - 242.0) < 0.01:
                print("   ✅ Valor correto!")
            else:
                print(f"   ⚠️  Valor esperado: 242.0, obtido: {dados['valor_convertido']}")
        else:
            print(f"❌ Converter área — ERRO {response.status_code}")
            testes_passaram = False
            
    except Exception as e:
        print(f"❌ Converter área — ERRO: {e}")
        testes_passaram = False
    
    # Teste 3.4: Listar categorias
    try:
        response = requests.get(
            f"{BASE_URL}/config/categorias/despesa",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            dados = response.json()
            print(f"✅ Listar categorias — {dados['total']} categorias de despesa")
        else:
            print(f"❌ Listar categorias — ERRO {response.status_code}")
            testes_passaram = False
            
    except Exception as e:
        print(f"❌ Listar categorias — ERRO: {e}")
        testes_passaram = False
    
    return testes_passaram


# =============================================================================
# TESTE 4: UPLOAD DE SHAPEFILE/KML
# =============================================================================

def testar_upload_geometria():
    """Testa upload de arquivos geoespaciais."""
    print("\n" + "="*60)
    print("TESTE 4: Upload de Shapefile/KML")
    print("="*60)
    
    testes_passaram = True
    
    # Teste 4.1: Validar geometria simples (quadrado)
    try:
        geometria_teste = {
            "type": "Polygon",
            "coordinates": [[
                [-56.1234, -15.5678],
                [-56.1234, -15.6789],
                [-56.2345, -15.6789],
                [-56.2345, -15.5678],
                [-56.1234, -15.5678]
            ]]
        }
        
        response = requests.post(
            f"{BASE_URL}/fazendas/validar-geometria",
            headers=HEADERS,
            json=geometria_teste
        )
        
        if response.status_code == 200:
            dados = response.json()
            print(f"✅ Validar geometria — válida: {dados['valida']}")
            if dados['valida']:
                print(f"   área: {dados['area_ha']} ha")
                print(f"   bounds: lat {dados['bounds']['min_lat']:.4f} a {dados['bounds']['max_lat']:.4f}")
        else:
            print(f"❌ Validar geometria — ERRO {response.status_code}")
            testes_passaram = False
            
    except Exception as e:
        print(f"❌ Validar geometria — ERRO: {e}")
        testes_passaram = False
    
    # Teste 4.2: Upload de shapefile (se arquivo existir)
    import os
    arquivo_shapefile = "testes/fazenda_exemplo.zip"
    
    if os.path.exists(arquivo_shapefile):
        try:
            with open(arquivo_shapefile, 'rb') as f:
                files = {'arquivo': ('fazenda.zip', f, 'application/zip')}
                response = requests.post(
                    f"{BASE_URL}/fazendas/upload-shapefile",
                    headers={"Authorization": f"Bearer {TOKEN}"},
                    files=files
                )
                
                if response.status_code == 200:
                    dados = response.json()
                    print(f"✅ Upload shapefile — {dados['mensagem']}")
                    print(f"   área: {dados['dados']['area_ha']} ha")
                else:
                    print(f"❌ Upload shapefile — ERRO {response.status_code}")
                    print(f"   {response.text}")
                    
        except Exception as e:
            print(f"❌ Upload shapefile — ERRO: {e}")
    else:
        print(f"⚠️  Upload shapefile — Arquivo de teste não encontrado ({arquivo_shapefile})")
    
    # Teste 4.3: Upload de KML (se arquivo existir)
    arquivo_kml = "testes/fazenda_exemplo.kml"
    
    if os.path.exists(arquivo_kml):
        try:
            with open(arquivo_kml, 'rb') as f:
                files = {'arquivo': ('fazenda.kml', f, 'application/xml')}
                response = requests.post(
                    f"{BASE_URL}/fazendas/upload-kml",
                    headers={"Authorization": f"Bearer {TOKEN}"},
                    files=files
                )
                
                if response.status_code == 200:
                    dados = response.json()
                    print(f"✅ Upload KML — {dados['mensagem']}")
                    print(f"   área: {dados['dados']['area_ha']} ha")
                else:
                    print(f"❌ Upload KML — ERRO {response.status_code}")
                    print(f"   {response.text}")
                    
        except Exception as e:
            print(f"❌ Upload KML — ERRO: {e}")
    else:
        print(f"⚠️  Upload KML — Arquivo de teste não encontrado ({arquivo_kml})")
    
    return testes_passaram


# =============================================================================
# RESUMO DOS TESTES
# =============================================================================

def main():
    """Executa todos os testes."""
    print("\n" + "="*60)
    print("SCRIPT DE TESTES INTEGRADOS — AGROSAAS")
    print("Data: 2026-04-01")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Token: {'***' + TOKEN[-10:] if TOKEN and TOKEN != 'SEU_TOKEN_AQUI' else 'NÃO CONFIGURADO'}")
    
    # Verificar se backend está online
    print("\nVerificando backend...")
    if testar_backend_online():
        print("✅ Backend está online em http://localhost:8000")
    else:
        print("❌ Backend NÃO está online!")
        print("\nPara iniciar o backend:")
        print("  cd services/api && ./start_server.sh")
        print("\nOu manualmente:")
        print("  cd services/api && uvicorn main:app --reload")
        return 1
    
    # Verificar token
    if TOKEN == "SEU_TOKEN_AQUI":
        print("\n⚠️  ATENÇÃO: Token não configurado!")
        print("\nPara obter um token:")
        print("  1. Faça login no sistema")
        print("  2. Copie o token JWT")
        print("  3. Execute: export AGROSAAS_TOKEN='seu_token_aqui'")
        print("\nOs testes que requerem autenticação irão falhar (401).")
        print("Continuando apenas com testes públicos...\n")
    
    resultados = {
        "Validação de Limites": testar_validacao_limites(),
        "Notificações": testar_notificacoes(),
        "Configurações Globais": testar_configuracoes_globais(),
        "Upload de Geometria": testar_upload_geometria(),
    }
    
    # Resumo final
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    
    total = len(resultados)
    passaram = sum(1 for v in resultados.values() if v)
    
    for teste, passou in resultados.items():
        status = "✅ PASSOU" if passou else "❌ FALHOU"
        print(f"  {status}: {teste}")
    
    print(f"\nTotal: {passaram}/{total} testes passaram")
    
    if passaram == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        return 0
    else:
        print(f"\n⚠️  {total - passaram} teste(s) falharam")
        return 1


if __name__ == "__main__":
    sys.exit(main())
