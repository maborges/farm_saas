# Configuração do PostgreSQL para AgroSaaS

## Passo 1: Conectar ao PostgreSQL como superusuário

```bash
# Conectar ao PostgreSQL no servidor remoto
psql -h 192.168.0.2 -U postgres
```

## Passo 2: Criar o banco de dados e usuário

```sql
-- Criar o banco de dados
CREATE DATABASE farms;

-- Criar o usuário (se não existir)
CREATE USER borgus WITH PASSWORD 'nusmey01';

-- Ou, se o usuário já existe, atualizar a senha:
ALTER USER borgus WITH PASSWORD 'numsey01';

-- Conceder todos os privilégios no banco farms ao usuário borgus
GRANT ALL PRIVILEGES ON DATABASE farms TO borgus;

-- Conectar ao banco farms
\c farms

-- Conceder privilégios no schema public
GRANT ALL PRIVILEGES ON SCHEMA public TO borgus;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO borgus;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO borgus;

-- Garantir que privilégios futuros também sejam concedidos
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO borgus;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO borgus;
```

## Passo 3: Verificar a conexão

```bash
# Testar conexão
PGPASSWORD='num$sey01' psql -h 192.168.0.2 -U borgus -d farms -c "SELECT version();"
```

## Passo 4: Verificar pg_hba.conf

O arquivo `pg_hba.conf` do PostgreSQL precisa permitir conexões MD5 ou SCRAM:

```conf
# IPv4 local connections:
host    all             all             192.168.0.0/24          md5
```

Após modificar `pg_hba.conf`, reinicie o PostgreSQL:

```bash
sudo systemctl reload postgresql
# ou
sudo pg_ctlcluster <version> main reload
```

## Alternativa: Senha Simples para Teste

Se a senha com `$` estiver causando problemas, você pode temporariamente usar uma senha mais simples:

```sql
ALTER USER borgus WITH PASSWORD 'numsey01';
```

E atualizar o `.env.local`:

```env
DATABASE_URL=postgresql+asyncpg://borgus:numsey01@192.168.0.2/farms
```

## Troubleshooting

### Erro: "password authentication failed"

1. Verifique se a senha está correta
2. Verifique se o usuário existe: `\du` no psql
3. Verifique o método de autenticação em `pg_hba.conf`
4. Verifique se o PostgreSQL está aceitando conexões remotas em `postgresql.conf`:
   ```conf
   listen_addresses = '*'  # ou '192.168.0.2'
   ```

### Erro: "database does not exist"

```sql
CREATE DATABASE farms;
```

### Erro: "role does not exist"

```sql
CREATE USER borgus WITH PASSWORD 'numsey01';
```
