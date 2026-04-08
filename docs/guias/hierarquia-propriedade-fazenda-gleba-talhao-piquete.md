# Guia de Associação: Propriedade → Fazenda → Gleba → Talhão → Piquete

## Visão Geral

O sistema utiliza uma **hierarquia de áreas rurais** para organizar as subdivisões espaciais de uma propriedade econômica. Cada propriedade econômica pode estar vinculada a múltiplas fazendas, e cada fazenda possui uma estrutura hierárquica de áreas.

## Hierarquia Suportada

```
Propriedade Econômica (cadastros_propriedades)
│
└─ Exploração Rural (vínculo lógico com Fazenda)
   │
   └─ Fazenda (fazendas)
      │
      └─ AreaRural (cadastros_areas_rurais)
         │
         ├─ PROPRIEDADE / GLEBA (nível raiz)
         │  ├─ APP (Área de Preservação Permanente)
         │  ├─ RESERVA_LEGAL
         │  └─ UNIDADE_PRODUTIVA
         │     ├─ AREA
         │     │  ├─ TALHAO
         │     │  └─ PASTAGEM
         │     │     └─ PIQUETE
         │     └─ TALHAO (direto)
         │
         ├─ ARMAZEM / SEDE / INFRAESTRUTURA (sem filhos)
```

## Regras de Hierarquia

### O que pode ser filho de quê?

| Tipo Pai | Tipos Filhos Permitidos |
|----------|------------------------|
| **PROPRIEDADE** | Gleba, Unidade Produtiva, Armazém, Sede, Infraestrutura |
| **GLEBA** | APP, Reserva Legal, Unidade Produtiva |
| **UNIDADE_PRODUTIVA** | Área, Talhão, Pastagem |
| **ÁREA** | Talhão, Pastagem |
| **PASTAGEM** | Piquete |
| **TALHAO** | _(nenhum - folha)_ |
| **PIQUETE** | _(nenhum - folha)_ |
| **APP** | _(nenhum - folha)_ |
| **RESERVA_LEGAL** | _(nenhum - folha)_ |

## Como Usar no Frontend

### 1. Acessar a Página de Detalhe

```
http://localhost:3000/cadastros/propriedades-econ/{id}
```

### 2. Aba "Fazendas Vinculadas"

Nesta aba você verá:

- **Lista de Explorações**: tabela com fazendas vinculadas
- **Botão "Nova Exploração"**: cria vínculo com fazenda
- **Árvore Hierárquica**: visualização completa da estrutura

### 3. Adicionar uma Gleba

1. Clique no botão **"+ Nova Área"** no topo da árvore
2. Selecione o tipo **GLEBA**
3. Preencha nome, código e área
4. Salve

### 4. Adicionar um Talhão dentro de uma Gleba

1. Passe o mouse sobre a Gleba pai
2. Clique no ícone **"+"** que aparece
3. Selecione o tipo **TALHAO**
4. Preencha os dados
5. O sistema automaticamente define o `parent_id` como o ID da Gleba

### 5. Adicionar um Piquete dentro de uma Pastagem

1. Expanda a Pastagem clicando na seta **▶**
2. Clique no ícone **"+"** na Pastagem
3. Selecione o tipo **PIQUETE**
4. Preencha os dados

## Exemplo Prático

### Cenário: Fazenda São João

```
Propriedade Econômica: "Grupo Agrícola ABC"
│
└─ Exploração: Fazenda São João (natureza: própria)
   │
   ├─ Gleba "Matrícula 1234" (500 ha)
   │  ├─ APP "Rio das Pedras" (50 ha)
   │  ├─ Reserva Legal "Mata Norte" (100 ha)
   │  └─ Unidade Produtiva "Bloco Norte" (300 ha)
   │     ├─ Talhão "T-01" (50 ha) - Soja
   │     ├─ Talhão "T-02" (50 ha) - Milho
   │     └─ Pastagem "P-01" (200 ha)
   │        ├─ Piquete "PQ-01" (50 ha)
   │        ├─ Piquete "PQ-02" (50 ha)
   │        ├─ Piquete "PQ-03" (50 ha)
   │        └─ Piquete "PQ-04" (50 ha)
   │
   └─ Gleba "Matrícula 5678" (400 ha)
      ├─ Talhão "T-03" (150 ha) - Café
      └─ Pastagem "P-02" (200 ha)
         └─ Piquete "PQ-05" (200 ha)
```

## Endpoints da API

### Obter hierarquia completa

```http
GET /cadastros/propriedades/{propriedade_id}/hierarquia
```

Retorna a propriedade com todas as fazendas e suas árvores de áreas rurais.

### Listar áreas de uma fazenda

```http
GET /cadastros/propriedades/{propriedade_id}/fazendas/{fazenda_id}/areas
```

### Criar área rural

```http
POST /cadastros/propriedades/{propriedade_id}/fazendas/{fazenda_id}/areas
Content-Type: application/json

{
  "nome": "Talhão T-01",
  "tipo": "TALHAO",
  "codigo": "T-01",
  "parent_id": "uuid-da-gleba-ou-unidade",
  "area_hectares": 50.5,
  "descricao": "Talhão com soja"
}
```

### Atualizar área rural

```http
PATCH /cadastros/fazendas/{fazenda_id}/areas/{area_id}
Content-Type: application/json

{
  "nome": "Talhão T-01 Atualizado",
  "area_hectares": 55.0
}
```

### Remover área rural (soft delete)

```http
DELETE /cadastros/fazendas/{fazenda_id}/areas/{area_id}
```

**Nota**: Ao remover uma área, todos os seus filhos também serão removidos (cascade).

## Componentes Frontend Disponíveis

### AreaTree

Componente principal para exibir a árvore hierárquica:

```tsx
import { AreaTree } from "@/components/shared/area-tree";
import type { AreaRuralTree } from "@agrosaas/zod-schemas";

function MinhaPagina() {
  const [areas, setAreas] = useState<AreaRuralTree[]>([]);

  return (
    <AreaTree
      areas={areas}
      onSelect={(area) => console.log("Selecionada:", area)}
      onAdd={(parentId, parentType) => console.log("Adicionar filho em:", parentId)}
      onEdit={(area) => console.log("Editar:", area)}
      onDelete={(area) => console.log("Remover:", area)}
    />
  );
}
```

### AreaTreeItem

Componente individual de cada nó (usado internamente pelo AreaTree).

## Schemas Zod Disponíveis

```typescript
import {
  TipoAreaRural,           // Enum de tipos
  TipoAreaRuralValues,     // Array de valores
  AREA_HIERARQUIA,         // Regras de hierarquia
  areaRuralSchema,         // Schema de uma área
  areaRuralTreeSchema,     // Schema recursivo com filhos
  createAreaRuralSchema,   // Schema para criar
  updateAreaRuralSchema,   // Schema para atualizar
} from "@agrosaas/zod-schemas";
```

## Validações Automáticas

O sistema valida automaticamente:

1. ✅ **Tipo filho permitido**: Não permite criar um PIQUETE como filho de uma GLEBA
2. ✅ **Área positiva**: Área em hectares deve ser > 0
3. ✅ **Nome obrigatório**: Mínimo 2 caracteres
4. ✅ **Código único** (opcional): Se informado, valida unicidade
5. ✅ **Cascade delete**: Ao remover pai, remove todos os filhos

## Fluxo Completo de Criação

### Passo a passo: Criar estrutura do zero

1. **Criar Propriedade Econômica**
   - Acesse `/cadastros/propriedades-econ`
   - Clique em "Nova Propriedade"
   - Preencha dados

2. **Vincular Fazenda**
   - Acesse detalhe da propriedade
   - Aba "Fazendas Vinculadas"
   - Clique "Nova Exploração"
   - Selecione a fazenda e natureza do vínculo

3. **Criar Gleba**
   - Na árvore hierárquica, clique "+ Nova Área"
   - Tipo: GLEBA
   - Nome: "Matrícula 1234"
   - Área: 500 ha

4. **Criar Talhão dentro da Gleba**
   - Passe mouse na Gleba
   - Clique no ícone "+"
   - Tipo: TALHAO
   - Nome: "T-01"
   - Área: 50 ha

5. **Criar Pastagem**
   - Clique "+" na Gleba novamente
   - Tipo: PASTAGEM
   - Nome: "P-01"
   - Área: 200 ha

6. **Criar Piquetes dentro da Pastagem**
   - Expanda a Pastagem (clique na seta)
   - Clique "+" na Pastagem
   - Tipo: PIQUETE
   - Nome: "PQ-01"
   - Área: 50 ha
   - Repita para PQ-02, PQ-03, PQ-04

## Boas Práticas

1. **Organize por matrículas**: Use Glebas para separar áreas com matrículas cartoriais diferentes
2. **Use códigos**: Mantenha códigos curtos e consistentes (ex: T-01, P-01, PQ-01)
3. **Preencha áreas**: Sempre registre a área em hectares para cálculos futuros
4. **Respeite a hierarquia**: Não pule níveis (ex: não crie PIQUETE direto na Gleba)
5. **Documente**: Use o campo `descricao` para informações relevantes (cultura atual, tipo de solo, etc.)

## Troubleshooting

### "Fazenda não vinculada a esta propriedade"

**Causa**: Você está tentando acessar áreas de uma fazenda que não tem exploração ativa com esta propriedade.

**Solução**: Crie primeiro uma exploração rural na aba "Fazendas Vinculadas".

### "Tipo inválido. Valores aceitos: [...]"

**Causa**: O tipo de área informado não é um dos valores válidos.

**Solução**: Use um dos tipos: `PROPRIEDADE`, `GLEBA`, `UNIDADE_PRODUTIVA`, `AREA`, `TALHAO`, `PASTAGEM`, `PIQUETE`, `APP`, `RESERVA_LEGAL`, `ARMAZEM`, `SEDE`, `INFRAESTRUTURA`.

### "Não é possível inativar uma área que possui subáreas ativas"

**Causa**: Você está tentando remover uma área que tem filhos.

**Solução**: Remova primeiro todos os filhos ou aceite que o sistema fará um cascade delete.

## Próximos Passos

Funcionalidades futuras planejadas:

- [ ] Upload de arquivos geoespaciais (SHP, KML, GeoJSON) para gerar áreas automaticamente
- [ ] Visualização em mapa das áreas (integração com Google Maps/Leaflet)
- [ ] Relatórios de área total por tipo (APP, Reserva Legal, lavoura, pastagem)
- [ ] Exportação de estrutura hierárquica em PDF/Excel
- [ ] Histórico de mudanças na estrutura
