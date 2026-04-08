# Validação de CPF/CNPJ no Cadastro de Assinante

## Resumo

Implementada validação completa de CPF/CNPJ na página "Crie sua Conta" para verificar se o documento já está cadastrado e validar seu formato.

## Mudanças Realizadas

### 1. Backend - Utilitário de Validação

**Arquivo:** `services/api/core/utils/cpf_cnpj.py` (novo)

- `validar_cpf(cpf)`: Valida CPF usando algoritmo oficial com dígitos verificadores
- `validar_cnpj(cnpj)`: Valida CNPJ usando algoritmo oficial com dígitos verificadores
- `validar_cpf_ou_cnpj(documento)`: Valida automaticamente baseado no tamanho (11=CPF, 14=CNPJ)
- `formatar_cpf(cpf)`: Formata no padrão XXX.XXX.XXX-XX
- `formatar_cnpj(cnpj)`: Formata no padrão XX.XXX.XXX/XXXX-XX
- `formatar_documento(documento)`: Formata automaticamente CPF ou CNPJ
- `apenas_numeros(documento)`: Remove caracteres não numéricos

### 2. Backend - Schema Pydantic

**Arquivo:** `services/api/core/schemas/onboarding_schemas.py`

- Adicionado `field_validator` no campo `cnpj_tenant` do schema `AssinanteRegisterRequest`
- Valida formato do CPF/CNPJ antes de processar a requisição
- Normaliza o documento para apenas números antes do armazenamento

### 3. Backend - Service

**Arquivo:** `services/api/core/services/onboarding_service.py`

- Adicionada verificação de CPF/CNPJ duplicado no método `register_new_tenant`
- Retorna HTTP 400 com mensagem clara se documento já estiver cadastrado

### 4. Backend - Endpoint de Verificação

**Arquivo:** `services/api/core/routers/onboarding.py`

- **Novo endpoint:** `GET /onboarding/verificar-documento/{documento}`
- Permite validação em tempo real pelo frontend
- Retorna:
  ```json
  {
    "disponivel": true,
    "mensagem": null
  }
  ```
  ou
  ```json
  {
    "disponivel": false,
    "mensagem": "Este CPF ou CNPJ já está cadastrado no sistema."
  }
  ```

### 5. Frontend - Formulário de Registro

**Arquivo:** `apps/web/src/components/auth/register-form.tsx`

- Adicionada validação assíncrona com debounce de 800ms
- Feedback visual em tempo real:
  - "Verificando..." com spinner enquanto valida
  - "CPF/CNPJ disponível ✓" em verde quando disponível
  - Mensagem de erro em vermelho quando já cadastrado ou inválido
- Botão de submit desabilitado quando:
  - Documento está sendo verificado
  - Documento está indisponível
- Impede envio do formulário se houver erro no documento

## Fluxo de Validação

```
Usuário digita CPF/CNPJ
    ↓
Aguarda 800ms (debounce)
    ↓
Frontend chama: GET /onboarding/verificar-documento/{doc}
    ↓
Backend valida formato (algoritmo oficial)
    ↓
Backend consulta banco de dados
    ↓
Retorna se está disponível ou não
    ↓
Frontend exibe feedback visual
    ↓
Se disponível → habilita botão de submit
Se indisponível → desabilita botão e mostra erro
```

## Testes

### Testes Unitários

**Arquivo:** `services/api/tests/test_cpf_cnpj.py`

Testes abrangentes para:
- Validação de CPF válido/inválido
- Validação de CNPJ válido/inválido
- Formatação de documentos
- Remoção de caracteres não numéricos

### Testes Manuais

Execute no ambiente virtual:

```bash
cd /opt/lampp/htdocs/farm/services/api
../../.venv/bin/python -c "
from core.schemas.onboarding_schemas import AssinanteRegisterRequest

# CPF válido
data = AssinanteRegisterRequest(
    email='teste@email.com',
    username='testuser',
    nome_completo='João Silva',
    senha='senha123',
    cnpj_tenant='12345678909',
    nome_grupo='Grupo Teste'
)
print(f'✅ CPF normalizado: {data.cnpj_tenant}')

# CNPJ válido com máscara
data = AssinanteRegisterRequest(
    email='teste@email.com',
    username='testuser',
    nome_completo='João Silva',
    senha='senha123',
    cnpj_tenant='11.222.333/0001-81',
    nome_grupo='Grupo Teste'
)
print(f'✅ CNPJ normalizado: {data.cnpj_tenant}')
"
```

## Segurança

- Validação no **schema Pydantic** (camada de entrada)
- Validação no **service** (camada de negócio)
- Unique constraint no **banco de dados** (camada de persistência)
- Triple proteção contra duplicatas

## Mensagens de Erro

| Cenário | Mensagem |
|---------|----------|
| CPF inválido | "CPF ou CNPJ inválido. Verifique os dados informados." |
| CNPJ inválido | "CPF ou CNPJ inválido. Verifique os dados informados." |
| CPF já cadastrado | "Este CPF ou CNPJ já está cadastrado no sistema." |
| CNPJ já cadastrado | "Este CPF ou CNPJ já está cadastrado no sistema." |
| Formulário submetido com erro | "Corrija o CPF/CNPJ antes de continuar." |

## Notas

- O documento é armazenado apenas com números no banco de dados
- A validação usa os algoritmos oficiais de CPF e CNPJ (dígitos verificadores)
- CPFs/CNPJs com todos os dígitos iguais são rejeitados automaticamente
- O debounce de 800ms evita requisições excessivas durante a digitação
