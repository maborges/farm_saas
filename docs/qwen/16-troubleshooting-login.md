# 🔧 Troubleshooting - Erro "Failed to fetch" no Login

**Data:** 2026-06-06  
**Status:** ✅ **CORRIGIDO**

---

## 🎯 Problema

Erro ao fazer login:
```
Failed to fetch
const response = await fetch(`${API_BASE_URL}${endpoint}`, {
```

---

## ✅ Soluções

### 1. Verificar se o Backend está Rodando

```bash
# Testar se a API está respondendo
curl http://localhost:8000/api/v1/health

# Deve retornar:
# {"status": "ok", "message": "AgroSaaS is running!"}
```

### 2. Iniciar o Backend

```bash
# Navegar até a pasta da API
cd /opt/lampp/htdocs/farm/services/api

# Ativar ambiente virtual (se existir)
source .venv/bin/activate

# Iniciar o servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Verificar Configuração do .env.local

O arquivo `apps/web/.env.local` deve conter:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 4. Casos Especiais

#### WSL (Windows Subsystem for Linux)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

#### Docker
```env
NEXT_PUBLIC_API_URL=http://host.docker.internal:8000/api/v1
```

#### Rede Local (acesso de outros dispositivos)
```env
NEXT_PUBLIC_API_URL=http://192.168.0.108:8000/api/v1
```

---

## 🔍 Diagnóstico

### O arquivo `api.ts` foi atualizado para:

1. **Log de requisições** - Mostra URL e método sendo chamado
2. **Tratamento de erro de rede** - Mensagem clara quando API está offline
3. **Instruções de troubleshooting** - Erro amigável para o usuário

### Código Atualizado

```typescript
try {
    const response = await fetch(url, { ...options, headers });
    
    if (!response.ok) {
        // Erro HTTP
        throw new Error(errorData.detail || errorData.message);
    }
    
    return response.json();
} catch (error: any) {
    // Erro de rede (Failed to fetch)
    if (error.message === "Failed to fetch" || error.name === "TypeError") {
        throw new Error(
            "Não foi possível conectar ao servidor. Verifique se:\n" +
            "1. O backend está rodando (http://localhost:8000)\n" +
            "2. A URL da API está correta no arquivo .env.local\n" +
            "3. Não há bloqueio de CORS"
        );
    }
    throw error;
}
```

---

## 📝 Passos para Resolver

### Passo 1: Verificar Backend
```bash
# Verificar se há algum processo rodando na porta 8000
lsof -i :8000

# Ou usar netstat
netstat -tlnp | grep 8000
```

### Passo 2: Iniciar Backend (se não estiver rodando)
```bash
cd /opt/lampp/htdocs/farm/services/api

# Instalar dependências (se necessário)
pip install -r requirements.txt

# Iniciar servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Passo 3: Verificar Frontend
```bash
# Navegar até pasta do frontend
cd /opt/lampp/htdocs/farm/apps/web

# Verificar .env.local
cat .env.local

# Reiniciar servidor de desenvolvimento (se necessário)
npm run dev
# ou
pnpm dev
# ou
bun dev
```

### Passo 4: Testar Login
1. Abrir navegador em `http://localhost:3000`
2. Abrir DevTools (F12)
3. Ir para Console
4. Tentar login
5. Ver logs de erro/sucesso

---

## 🎯 Erros Comuns

### Erro: "Failed to fetch"
**Causa:** Backend não está rodando  
**Solução:** Iniciar backend com `uvicorn main:app --reload`

### Erro: "CORS policy"
**Causa:** Backend não está configurado para aceitar requisições do frontend  
**Solução:** Verificar middleware CORS no `main.py` do backend

### Erro: "404 Not Found"
**Causa:** URL da API incorreta  
**Solução:** Verificar `NEXT_PUBLIC_API_URL` no `.env.local`

### Erro: "Connection refused"
**Causa:** Porta 8000 bloqueada ou backend em outra porta  
**Solução:** Verificar se backend está rodando na porta 8000

---

## ✅ Validação

- [x] Backend rodando em `http://localhost:8000`
- [x] Endpoint `/api/v1/health` respondendo
- [x] `.env.local` configurado corretamente
- [x] Frontend reiniciado após mudanças no .env
- [x] CORS configurado no backend
- [x] Login funcionando

---

**Corrigido por:** _______________________  
**Data:** 2026-06-06
