# Upload de Shapefile/KML — Guia de Implementação

## Visão Geral

O AgroSaaS agora suporta upload de arquivos geoespaciais (shapefile e KML) para cadastro automático de propriedades rurais com geometria e cálculo de área.

---

## 🎯 Funcionalidades

### 1. **Upload de Shapefile**

Processa arquivos shapefile (ZIP com .shp, .dbf, .shx, .prj) e retorna:
- Geometria em GeoJSON
- Área calculada em hectares
- Atributos da feature
- Sistema de referência espacial (CRS)

### 2. **Upload de KML/KMZ**

Processa arquivos KML/KMZ do Google Earth e retorna:
- Geometria em GeoJSON
- Área calculada em hectares
- Nomes dos placemarks

### 3. **Validação de Geometria**

Valida geometrias GeoJSON antes de salvar:
- Verifica tipo de geometria
- Calcula área
- Retorna bounds (limites)
- Lista erros de validação

---

## 📡 Endpoints

### 1. Upload de Shapefile

```http
POST /api/v1/fazendas/upload-shapefile
Authorization: Bearer <token>
Content-Type: multipart/form-data

arquivo: (ZIP com shapefile)
```

**Requisitos do Shapefile:**
- Deve ser ZIP contendo:
  - `.shp` (geometria) — obrigatório
  - `.dbf` (atributos) — obrigatório
  - `.shx` (índice) — obrigatório
  - `.prj` (projeção) — recomendado

**Retorno de Sucesso:**
```json
{
  "sucesso": true,
  "mensagem": "Shapefile processado com sucesso. 1 feature(s) encontrada(s).",
  "dados": {
    "geometria": {
      "type": "Polygon",
      "coordinates": [[[...]]]
    },
    "area_ha": 1234.5678,
    "propriedades": {
      "nome": "Fazenda Santa Maria",
      "codigo": "001"
    },
    "crs": "EPSG:4326",
    "total_features": 1
  }
}
```

**Retorno de Erro:**
```json
{
  "detail": "Shapefile inválido: arquivo .shp não encontrado"
}
```

---

### 2. Upload de KML/KMZ

```http
POST /api/v1/fazendas/upload-kml
Authorization: Bearer <token>
Content-Type: multipart/form-data

arquivo: (KML ou KMZ)
```

**Retorno de Sucesso:**
```json
{
  "sucesso": true,
  "mensagem": "KML processado com sucesso. 3 polígono(s) encontrado(s).",
  "dados": {
    "geometria": {
      "type": "MultiPolygon",
      "coordinates": [[[[...]]]]
    },
    "area_ha": 567.8910,
    "propriedades": {
      "nomes": ["Talhão A", "Talhão B", "Talhão C"],
      "total_poligonos": 3
    },
    "crs": "WGS84"
  }
}
```

---

### 3. Validar Geometria

```http
POST /api/v1/fazendas/validar-geometria
Authorization: Bearer <token>
Content-Type: application/json

{
  "type": "Polygon",
  "coordinates": [[[
    [-56.1234, -15.5678],
    [-56.1234, -15.6789],
    [-56.2345, -15.6789],
    [-56.2345, -15.5678],
    [-56.1234, -15.5678]
  ]]]
}
```

**Retorno (Válida):**
```json
{
  "valida": true,
  "area_ha": 156.7890,
  "bounds": {
    "min_lon": -56.2345,
    "min_lat": -15.6789,
    "max_lon": -56.1234,
    "max_lat": -15.5678
  }
}
```

**Retorno (Inválida):**
```json
{
  "valida": false,
  "erros": [
    "Geometria vazia",
    "Área calculada é zero ou negativa"
  ],
  "area_ha": 0.0
}
```

---

## 🧪 Testes Manuais

### Testar Upload de Shapefile

```bash
curl -X POST http://localhost:8000/api/v1/fazendas/upload-shapefile \
  -H "Authorization: Bearer SEU_TOKEN" \
  -F "arquivo=@fazenda_shapefile.zip"
```

### Testar Upload de KML

```bash
curl -X POST http://localhost:8000/api/v1/fazendas/upload-kml \
  -H "Authorization: Bearer SEU_TOKEN" \
  -F "arquivo=@fazenda.kml"
```

### Testar Validação de Geometria

```bash
curl -X POST http://localhost:8000/api/v1/fazendas/validar-geometria \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "Polygon",
    "coordinates": [[
      [
        [-56.1234, -15.5678],
        [-56.1234, -15.6789],
        [-56.2345, -15.6789],
        [-56.2345, -15.5678],
        [-56.1234, -15.5678]
      ]
    ]]
  }'
```

---

## 📊 Fluxo de Uso no Frontend

### Passo 1: Upload do Arquivo

```typescript
// apps/web/src/app/(dashboard)/fazendas/nova/page.tsx
async function handleUploadShapefile(file: File) {
  const formData = new FormData()
  formData.append('arquivo', file)
  
  const response = await fetch('/api/v1/fazendas/upload-shapefile', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    body: formData,
  })
  
  const result = await response.json()
  
  if (result.sucesso) {
    // Preencher formulário com dados retornados
    setFormData({
      ...formData,
      nome: result.dados.propriedades?.nome || '',
      area_total_ha: result.dados.area_ha,
      geometria: result.dados.geometria,
    })
  }
}
```

### Passo 2: Validar Geometria (Opcional)

```typescript
async function validarGeometria(geometria: GeoJSON) {
  const response = await fetch('/api/v1/fazendas/validar-geometria', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(geometria),
  })
  
  const result = await response.json()
  
  if (result.valida) {
    console.log(`Área: ${result.area_ha} ha`)
    console.log(`Bounds: ${result.bounds}`)
  } else {
    console.error('Erros:', result.erros)
  }
}
```

### Passo 3: Salvar Fazenda

```typescript
async function salvarFazenda() {
  const response = await fetch('/api/v1/fazendas', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      nome: formData.nome,
      cnpj: formData.cnpj,
      area_total_ha: formData.area_total_ha,
      geometria: formData.geometria,
    }),
  })
  
  return await response.json()
}
```

---

## 🔧 Dependências

### Bibliotecas Python Necessárias

```bash
# Instalar dependências geoespaciais
pip install fiona shapely pyproj

# Ou via poetry
poetry add fiona shapely pyproj
```

### Verificar Disponibilidade

O sistema verifica automaticamente:

```python
try:
    import fiona
    from shapely.geometry import shape
    GEOSPATIAL_LIBS_AVAILABLE = True
except ImportError:
    GEOSPATIAL_LIBS_AVAILABLE = False
    logger.warning("Funcionalidades geoespaciais limitadas")
```

---

## 📝 Formatos Suportados

### Shapefile

| Extensão | Obrigatório | Descrição |
|----------|-------------|-----------|
| `.shp` | ✅ | Geometria |
| `.dbf` | ✅ | Atributos |
| `.shx` | ✅ | Índice |
| `.prj` | ⚠️ | Projeção (recomendado) |

### KML/KMZ

| Tipo | Descrição |
|------|-----------|
| KML | XML do Google Earth |
| KMZ | KML compactado (ZIP) |

**Elementos KML suportados:**
- `<Placemark>` com `<Polygon>`
- `<Placemark>` com `<LineString>`
- `<name>` (extraído como propriedade)

---

## 🗺️ Sistemas de Referência (CRS)

### Suportados

| CRS | EPSG | Descrição |
|-----|------|-----------|
| WGS84 | EPSG:4326 | Padrão (lat/lon) |
| UTM (todas zonas) | EPSG:327xx (sul) / 326xx (norte) | Projeção Universal Transversa de Mercator |
| SIRGAS 2000 | EPSG:4674 | Sistema brasileiro |

### Conversão Automática

O sistema converte automaticamente para WGS84 e calcula área em hectares.

---

## ⚠️ Limitações e Validações

### Validações de Geometria

- ✅ Tipo deve ser válido (Polygon, MultiPolygon, etc.)
- ✅ Área deve ser positiva
- ✅ Polígono deve ter pelo menos 3 vértices
- ✅ Coordenadas devem estar em graus (-180 a 180, -90 a 90)

### Limitações

- Tamanho máximo do arquivo: 50 MB (configurável)
- Shapefile: apenas 1 layer por ZIP
- KML: máximo de 1000 Placemarks

---

## 🔒 Segurança

### Isolamento Multi-Tenant

- ✅ Geometrias são vinculadas ao `tenant_id`
- ✅ Uploads são processados em memória (sem salvar em disco)
- ✅ Validação de tipo de arquivo antes de processar

### Validações

```python
# Validar extensão
if not arquivo.filename.lower().endswith('.zip'):
    raise HTTPException(status_code=400, detail="Arquivo deve ser ZIP")

# Validar conteúdo
try:
    resultado = await svc.processar_shapefile(conteudo)
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

---

## 📊 Exemplo de Uso Completo

### Frontend (React/Next.js)

```typescript
// apps/web/src/components/fazendas/upload-geometria.tsx
"use client"

import { useState } from 'react'

export function UploadGeometria({ onGeometryLoaded }: Props) {
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    
    setUploading(true)
    setError(null)
    
    const formData = new FormData()
    formData.append('arquivo', file)
    
    try {
      const response = await fetch('/api/v1/fazendas/upload-shapefile', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: formData,
      })
      
      const result = await response.json()
      
      if (!response.ok) {
        throw new Error(result.detail)
      }
      
      if (result.sucesso) {
        // Callback com geometria e área
        onGeometryLoaded({
          geometria: result.dados.geometria,
          area_ha: result.dados.area_ha,
          propriedades: result.dados.propriedades,
        })
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao processar arquivo')
    } finally {
      setUploading(false)
    }
  }
  
  return (
    <div>
      <input
        type="file"
        accept=".zip,.kml,.kmz"
        onChange={handleFileChange}
        disabled={uploading}
      />
      {uploading && <p>Processando...</p>}
      {error && <p className="text-red-500">{error}</p>}
    </div>
  )
}
```

---

## 📝 Próximos Passos

### Melhorias Futuras:
1. [ ] Suporte a GeoJSON direto (upload)
2. [ ] Desenho de polígono no mapa (Leaflet/MapLibre)
3. [ ] Validação de sobreposição com APP/Reserva Legal
4. [ ] Histórico de alterações de geometria
5. [ ] Exportar geometria para shapefile/KML

---

## 🔗 Links Relacionados

- [Service Implementation](services/api/core/services/geoprocessamento_service.py)
- [Router Implementation](services/api/core/routers/fazendas.py)
- [Especificação de Cadastro](docs/contexts/core/cadastro-propriedade.md)

---

**Documento gerado em:** 2026-04-01  
**Responsável:** Tech Lead  
**Status:** ✅ Implementado e funcional
