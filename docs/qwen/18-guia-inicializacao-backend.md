# 🚀 Guia de Inicialização do Backend

**Data:** 2026-06-06  
**Status:** ✅ **CRIADO**

---

## 🎯 Problema

Erro no login:
```
POST http://localhost:8000/api/v1/auth/login net::ERR_CONNECTION_REFUSED
```

**Causa:** Backend não está rodando.

---

## ✅ Soluções

### Opção 1: Script Automático (Recomendado)

```bash
# Navegar até pasta da API
cd /opt/lampp/htdocs/farm/services/api

# Executar script de inicialização
bash start_backend.sh
```

### Opção 2: Manual com Python3

```bash
# Navegar até pasta da API
cd /opt/lampp/htdocs/farm/services/api

# Ativar ambiente virtual (se existir)
source .venv/bin/activate

# Instalar dependências (se necessário)
pip install uvicorn fastapi sqlalchemy aiosqlite

# Iniciar servidor
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Opção 3: Com Venv Automático

```bash
cd /opt/lampp/htdocs/farm/services/api

# Criar venv se não existir
python3 -m venv .venv

# Ativar
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Iniciar
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🔍 Verificar se Backend está Rodando

### Terminal 1 (Backend)
```bash
# Deve mostrar:
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Terminal 2 (Teste)
```bash
# Testar endpoint de health
curl http://localhost:8000/api/v1/health

# Deve retornar:
# {"status":"ok","message":"AgroSaaS is running!"}
```

### Navegador
```
http://localhost:8000/docs
```
Deve abrir o Swagger UI da API.

---

## 📝 Comandos Úteis

### Verificar Porta 8000
```bash
# Linux
lsof -i :8000
# ou
netstat -tlnp | grep 8000

# Windows
netstat -ano | findstr :8000
```

### Matar Processo na Porta 8000
```bash
# Linux
kill -9 $(lsof -t -i:8000)

# Windows
taskkill /PID <PID> /F
```

### Reiniciar Backend
```bash
# Parar (Ctrl+C no terminal do backend)

# Iniciar novamente
cd /opt/lampp/htdocs/farm/services/api
bash start_backend.sh
```

---

## 🐛 Erros Comuns

### "python: command not found"
**Solução:** Usar `python3` ao invés de `python`

### "No module named 'uvicorn'"
**Solução:**
```bash
pip3 install uvicorn fastapi sqlalchemy
```

### "Address already in use"
**Solução:**
```bash
# Matar processo na porta 8000
kill -9 $(lsof -t -i:8000)

# Iniciar novamente
```

### "Permission denied" no script
**Solução:**
```bash
chmod +x start_backend.sh
./start_backend.sh
```

---

## ✅ Validação

- [x] Script `start_backend.sh` criado
- [x] Backend inicia com `bash start_backend.sh`
- [x] Endpoint `/api/v1/health` responde
- [x] Swagger UI acessível em `/docs`
- [x] Login funciona

---

## 🎯 Fluxo Completo

### 1. Iniciar Backend
```bash
cd /opt/lampp/htdocs/farm/services/api
bash start_backend.sh
```

### 2. Verificar Backend
```bash
# Em outro terminal
curl http://localhost:8000/api/v1/health
```

### 3. Iniciar Frontend
```bash
cd /opt/lampp/htdocs/farm/apps/web
npm run dev
```

### 4. Testar Login
1. Abrir `http://localhost:3000`
2. Fazer login
3. Deve funcionar!

---

**Criado por:** _______________________  
**Data:** 2026-06-06
