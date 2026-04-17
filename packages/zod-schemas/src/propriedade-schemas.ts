// packages/zod-schemas/src/propriedade-schemas.ts
// Schemas de validação para Propriedades e Explorações Rurais

import { z } from "zod";

// Enums
export const NaturezaVinculo = {
  PROPRIA: "propria",
  ARRENDAMENTO: "arrendamento",
  PARCERIA: "parceria",
  COMODATO: "comodato",
  POSSE: "posse",
} as const;

export const NaturezaVinculoValues = Object.values(NaturezaVinculo) as [string, ...string[]];

export const TipoDocumentoExploracao = {
  CONTRATO_ARRENDAMENTO: "contrato_arrendamento",
  CONTRATO_PARCERIA: "contrato_parceria",
  CONTRATO_COMODATO: "contrato_comodato",
  ESCRITURA: "escritura",
  MATRICULA: "matricula",
  CCIR: "ccir",
  ITR: "itr",
  CAR: "car",
  OUTRO: "outro",
} as const;

export const TipoDocumentoExploracaoValues = Object.values(TipoDocumentoExploracao) as [string, ...string[]];

// Propriedade schemas
export const createPropriedadeSchema = z.object({
  nome: z.string().min(2, "Nome deve ter pelo menos 2 caracteres").max(200, "Nome muito longo"),
  cpf_cnpj: z.string().max(18, "CPF/CNPJ inválido").optional().or(z.literal("")),
  inscricao_estadual: z.string().max(50, "Inscrição estadual muito longa").optional().or(z.literal("")),
  ie_isento: z.boolean().default(false),
  email: z.string().email("Email inválido").max(200).optional().or(z.literal("")),
  telefone: z.string().max(30, "Telefone muito longo").optional().or(z.literal("")),
  nome_fantasia: z.string().max(200, "Nome fantasia muito longo").optional().or(z.literal("")),
  regime_tributario: z.string().max(30).optional().or(z.literal("")),
  cor: z.string().max(7, "Cor inválida").optional().or(z.literal("")),
  icone: z.string().max(50, "Ícone muito grande").optional().or(z.literal("")),
  ordem: z.number().int().default(0),
  observacoes: z.string().optional().or(z.literal("")),
});

export const updatePropriedadeSchema = createPropriedadeSchema.partial().extend({
  nome: z.string().min(2).max(200).optional(),
  ativo: z.boolean().optional(),
});

export const propriedadeResponseSchema = z.object({
  id: z.string().uuid(),
  tenant_id: z.string().uuid(),
  nome: z.string(),
  cpf_cnpj: z.string().nullable(),
  inscricao_estadual: z.string().nullable(),
  ie_isento: z.boolean(),
  email: z.string().nullable(),
  telefone: z.string().nullable(),
  nome_fantasia: z.string().nullable(),
  regime_tributario: z.string().nullable(),
  cor: z.string().nullable(),
  icone: z.string().nullable(),
  ordem: z.number(),
  ativo: z.boolean(),
  observacoes: z.string().nullable(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

// Exploração Rural schemas
export const createExploracaoSchema = z.object({
  fazenda_id: z.string().uuid("Selecione uma fazenda"),
  natureza: z.enum(NaturezaVinculoValues, { message: "Natureza inválida" }),
  data_inicio: z.string().date("Data inválida"),
  data_fim: z.string().date("Data inválida").optional().or(z.literal("")),
  numero_contrato: z.string().max(100).optional().or(z.literal("")),
  valor_anual: z.coerce.number().gt(0, "Valor deve ser maior que zero").optional().or(z.literal(0)),
  percentual_producao: z.coerce.number().gt(0, "Percentual deve ser maior que zero").lte(100, "Percentual máximo: 100").optional().or(z.literal(0)),
  area_explorada_ha: z.coerce.number().gt(0, "Área deve ser maior que zero").optional().or(z.literal(0)),
  observacoes: z.string().optional().or(z.literal("")),
});

export const updateExploracaoSchema = createExploracaoSchema.partial().extend({
  natureza: z.enum(NaturezaVinculoValues).optional(),
  data_inicio: z.string().date().optional(),
  data_fim: z.string().date().optional().nullable(),
  ativo: z.boolean().optional(),
});

export const exploracaoResponseSchema = z.object({
  id: z.string().uuid(),
  propriedade_id: z.string().uuid(),
  fazenda_id: z.string().uuid(),
  natureza: z.string(),
  data_inicio: z.string().date(),
  data_fim: z.string().date().nullable(),
  numero_contrato: z.string().nullable(),
  valor_anual: z.number().nullable(),
  percentual_producao: z.number().nullable(),
  area_explorada_ha: z.number().nullable(),
  documento_s3_key: z.string().nullable(),
  documento_tipo: z.string().nullable(),
  ativo: z.boolean(),
  observacoes: z.string().nullable(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

// Documento Exploração schemas
export const createDocumentoExploracaoSchema = z.object({
  tipo: z.enum(TipoDocumentoExploracaoValues, { message: "Tipo de documento inválido" }),
  nome_arquivo: z.string().min(1, "Nome do arquivo obrigatório").max(255),
  storage_path: z.string().min(1, "Caminho de storage obrigatório"),
  storage_backend: z.string().default("local"),
  tamanho_bytes: z.number().int().gt(0, "Tamanho deve ser maior que zero"),
  mime_type: z.string().max(100).optional().or(z.literal("")),
  data_emissao: z.string().date().optional().or(z.literal("")),
  data_validade: z.string().date().optional().or(z.literal("")),
  numero_documento: z.string().max(100).optional().or(z.literal("")),
  orgao_expedidor: z.string().max(100).optional().or(z.literal("")),
  observacoes: z.string().optional().or(z.literal("")),
});

export const documentoExploracaoResponseSchema = z.object({
  id: z.string().uuid(),
  exploracao_id: z.string().uuid(),
  tipo: z.string(),
  nome_arquivo: z.string(),
  storage_path: z.string(),
  storage_backend: z.string(),
  tamanho_bytes: z.number(),
  mime_type: z.string().nullable(),
  data_emissao: z.string().date().nullable(),
  data_validade: z.string().date().nullable(),
  numero_documento: z.string().nullable(),
  orgao_expedidor: z.string().nullable(),
  ativo: z.boolean(),
  created_at: z.string().datetime(),
});

// Types
export type CreatePropriedadeInput = z.infer<typeof createPropriedadeSchema>;
export type UpdatePropriedadeInput = z.infer<typeof updatePropriedadeSchema>;
export type PropriedadeResponse = z.infer<typeof propriedadeResponseSchema>;

export type CreateExploracaoInput = z.infer<typeof createExploracaoSchema>;
export type UpdateExploracaoInput = z.infer<typeof updateExploracaoSchema>;
export type ExploracaoResponse = z.infer<typeof exploracaoResponseSchema>;

export type CreateDocumentoExploracaoInput = z.infer<typeof createDocumentoExploracaoSchema>;
export type DocumentoExploracaoResponse = z.infer<typeof documentoExploracaoResponseSchema>;

// ---------------------------------------------------------------------------
// Hierarquia de Áreas Rurais (Gleba → Talhão → Piquete)
// ---------------------------------------------------------------------------

export const TipoAreaRural = {
  // Raiz — filhos diretos de UnidadeProdutiva
  AREA_RURAL:       "AREA_RURAL",
  INFRAESTRUTURA:   "INFRAESTRUTURA",
  // Filhos de AREA_RURAL
  GLEBA:            "GLEBA",
  // Filhos de GLEBA
  TALHAO:           "TALHAO",
  AREA_AMBIENTAL:   "AREA_AMBIENTAL",
  // Filhos de TALHAO
  AREA_OPERACIONAL: "AREA_OPERACIONAL",
  // Filhos de AREA_OPERACIONAL
  PIQUETE:          "PIQUETE",
  ZONA_MANEJO:      "ZONA_MANEJO",
  SUBTALHAO:        "SUBTALHAO",
  // Filhos de AREA_AMBIENTAL
  APP:              "APP",
  RESERVA_LEGAL:    "RESERVA_LEGAL",
  // Filhos de INFRAESTRUTURA
  SEDE:             "SEDE",
  ARMAZEM:          "ARMAZEM",
  CURRAL:           "CURRAL",
  OUTROS:           "OUTROS",
} as const;

export const TipoAreaRuralValues = Object.values(TipoAreaRural) as [string, ...string[]];

// Hierarquia: null = raiz da UnidadeProdutiva
export const AREA_HIERARQUIA: Record<string, readonly string[]> = {
  __raiz__:         ["AREA_RURAL", "INFRAESTRUTURA"],
  AREA_RURAL:       ["GLEBA"],
  GLEBA:            ["TALHAO", "AREA_AMBIENTAL"],
  TALHAO:           ["AREA_OPERACIONAL"],
  AREA_OPERACIONAL: ["PIQUETE", "ZONA_MANEJO", "SUBTALHAO"],
  AREA_AMBIENTAL:   ["APP", "RESERVA_LEGAL"],
  INFRAESTRUTURA:   ["SEDE", "ARMAZEM", "CURRAL", "OUTROS"],
  // folhas
  PIQUETE:          [],
  ZONA_MANEJO:      [],
  SUBTALHAO:        [],
  APP:              [],
  RESERVA_LEGAL:    [],
  SEDE:             [],
  ARMAZEM:          [],
  CURRAL:           [],
  OUTROS:           [],
};

export const areaRuralSchema = z.object({
  id: z.string().uuid(),
  tenant_id: z.string().uuid(),
  fazenda_id: z.string().uuid(),
  parent_id: z.string().uuid().nullable(),
  tipo: z.enum(TipoAreaRuralValues),
  nome: z.string().min(2, "Nome deve ter pelo menos 2 caracteres").max(200),
  codigo: z.string().max(50).optional().nullable(),
  descricao: z.string().optional().nullable(),
  area_hectares: z.number().gt(0).optional().nullable(),
  area_hectares_manual: z.number().gt(0).optional().nullable(),
  geometria: z.any().optional().nullable(),
  centroide_lat: z.number().optional().nullable(),
  centroide_lng: z.number().optional().nullable(),
  dados_extras: z.record(z.any()).optional().nullable(),
  ativo: z.boolean(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

export const areaRuralTreeSchema: z.ZodType<any> = areaRuralSchema.extend({
  filhos: z.lazy(() => areaRuralTreeSchema.array()).default([]),
});

export const fazendaHierarquiaResponseSchema = z.object({
  fazenda_id: z.string().uuid(),
  exploracao_id: z.string().uuid(),
  natureza: z.string(),
  data_inicio: z.string().datetime(),
  data_fim: z.string().datetime().nullable(),
  areas: areaRuralTreeSchema.array(),
});

export const propriedadeComHierarquiaResponseSchema = z.object({
  propriedade: propriedadeResponseSchema,
  fazendas: fazendaHierarquiaResponseSchema.array(),
});

export const createAreaRuralSchema = z.object({
  nome: z.string().min(2, "Nome deve ter pelo menos 2 caracteres").max(200),
  tipo: z.enum(TipoAreaRuralValues, { message: "Tipo de área inválido" }),
  codigo: z.string().max(50).optional(),
  descricao: z.string().optional(),
  parent_id: z.string().uuid().optional().nullable(),
  area_hectares: z.number().gt(0).optional().nullable(),
  area_hectares_manual: z.number().gt(0).optional().nullable(),
  dados_extras: z.record(z.any()).optional().nullable(),
});

export const updateAreaRuralSchema = createAreaRuralSchema.partial();

// Types
export type AreaRuralResponse = z.infer<typeof areaRuralSchema>;
export type AreaRuralTree = z.infer<typeof areaRuralTreeSchema>;
export type FazendaHierarquiaResponse = z.infer<typeof fazendaHierarquiaResponseSchema>;
export type PropriedadeComHierarquiaResponse = z.infer<typeof propriedadeComHierarquiaResponseSchema>;
export type CreateAreaRuralInput = z.infer<typeof createAreaRuralSchema>;
export type UpdateAreaRuralInput = z.infer<typeof updateAreaRuralSchema>;
