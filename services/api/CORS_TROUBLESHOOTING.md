# Guia de Solução de Problemas de CORS

## 📋 Problema Comum

**Erro:** `Access to fetch at 'http://localhost:8000/api/v1/...' from origin 'http://localhost:3000' has been blocked by CORS policy`

## 🔍 Causas Raízes

### 1. Servidor Backend Não Foi Reiniciado
**Causa mais comum!** Mudanças na configuração de CORS em `main.py` só são aplicadas após reiniciar o servidor.

**Solução:**
```bash
# Parar servidor atual
pkill -f "uvicorn main:app"

# Reiniciar usando o script
cd /opt/lampp/htdocs/farm/services/api
./start_server.sh
```

### 2. Frontend Rodando em URL Não Configurada
O backend só aceita requisições de origens específicas configuradas em `main.py`.

**Origens configuradas:**
- `http://localhost:3000`
- `http://localhost:3001`
- `http://127.0.0.1:3000`
- `http://127.0.0.1:3001`
- `http://192.168.0.2:3000`
- `http://192.168.0.2:3001`

**Verificar a URL do frontend:**
```bash
# No terminal onde o Next.js está rodando, verifique a mensagem:
# ▲ Next.js 16.x.x
# - Local:   http://localhost:3000  ← Deve estar nesta lista!
```

**Se a URL for diferente:**
1. Edite `/opt/lampp/htdocs/farm/services/api/main.py`
2. Adicione a nova origem na lista `allow_origins`
3. **IMPORTANTE:** Reinicie o servidor backend!

### 3. CORS Middleware Não É o Primeiro
O middleware de CORS **DEVE** ser o primeiro middleware registrado, antes de autenticação.

**Verificar em `main.py`:**
```python
# ✅ CORRETO - CORS é o PRIMEIRO
app.add_middleware(CORSMiddleware, ...)  # Linha ~50
# ... outros middlewares depois ...

# ❌ ERRADO - CORS depois de outros middlewares
app.add_middleware(AlgumOutroMiddleware, ...)
app.add_middleware(CORSMiddleware, ...)  # Tarde demais!
```

### 4. Backend Não Está Escutando em 0.0.0.0
Se o backend só escuta em `127.0.0.1`, pode ter problemas com algumas origens.

**Solução:**
```bash
# Iniciar com --host 0.0.0.0
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🛠️ Checklist de Diagnóstico

Quando encontrar erro de CORS, siga este checklist:

- [ ] **1. Verificar se o backend está rodando**
  ```bash
  curl http://localhost:8000/health
  # Deve retornar: {"status":"ok","message":"AgroSaaS is running!"}
  ```

- [ ] **2. Verificar URL do frontend**
  - Abra o navegador em `http://localhost:3000` (não `127.0.0.1:3000`)
  - Ou adicione a URL usada na lista de origens permitidas

- [ ] **3. Testar CORS manualmente**
  ```bash
  curl -X OPTIONS http://localhost:8000/api/v1/auth/login \
    -H "Origin: http://localhost:3000" \
    -H "Access-Control-Request-Method: POST" \
    -v 2>&1 | grep -E "(< HTTP|< access-control)"

  # Deve retornar headers access-control-*
  ```

- [ ] **4. Verificar logs do backend**
  ```bash
  tail -f /tmp/agrosaas-api.log
  # Ou veja o terminal onde uvicorn está rodando
  ```

- [ ] **5. Limpar cache do navegador**
  - Abra DevTools (F12)
  - Clique com botão direito no botão de reload
  - Selecione "Limpar cache e recarregar"

- [ ] **6. REINICIAR O SERVIDOR BACKEND**
  ```bash
  pkill -f "uvicorn main:app"
  cd /opt/lampp/htdocs/farm/services/api
  ./start_server.sh
  ```

## 🔧 Configuração Atual

Arquivo: `/opt/lampp/htdocs/farm/services/api/main.py` (linhas 48-66)

```python
# IMPORTANTE: CORS deve ser o PRIMEIRO middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://192.168.0.2:3000",
        "http://192.168.0.2:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)
```

## 📝 Adicionando Nova Origem

1. **Editar main.py:**
   ```python
   allow_origins=[
       # ... origens existentes ...
       "http://nova-origem:porta",  # ← Adicionar aqui
   ],
   ```

2. **REINICIAR servidor:**
   ```bash
   ./start_server.sh
   ```

3. **Testar:**
   ```bash
   curl -X OPTIONS http://localhost:8000/health \
     -H "Origin: http://nova-origem:porta" \
     -v 2>&1 | grep access-control-allow-origin
   ```

## 🚨 Erros Comuns

### Erro: "Credentials mode is 'include'"
**Causa:** `allow_credentials=True` requer origens específicas (não pode usar `*`)

**Solução:** Já configurado corretamente. Não use `allow_origins=["*"]`

### Erro: Headers não permitidos
**Causa:** Headers customizados não estão na lista

**Solução:** Já configurado com `allow_headers=["*"]`

### Erro: Método não permitido
**Causa:** Método HTTP não está permitido

**Solução:** Já configurado com `allow_methods=["*"]`

## 📌 Lembrete Importante

**SEMPRE QUE MODIFICAR `main.py`, REINICIE O SERVIDOR!**

```bash
# Use CTRL+C no terminal do uvicorn
# Ou execute:
pkill -f "uvicorn main:app" && ./start_server.sh
```

## 🔗 Referências

- [FastAPI CORS Docs](https://fastapi.tiangolo.com/tutorial/cors/)
- [MDN CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- Arquivo de configuração: `services/api/main.py`
- Script de inicialização: `services/api/start_server.sh`
