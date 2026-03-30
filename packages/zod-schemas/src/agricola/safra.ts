import { z } from "zod";

// ---- Enums sincronizados com o backend ----

export const SafraStatusEnum = z.enum([
  "PLANEJADA",
  "PREPARO_SOLO",
  "PLANTIO",
  "DESENVOLVIMENTO",
  "COLHEITA",
  "POS_COLHEITA",
  "ENCERRADA",
  "CANCELADA",
]);

export const SistemaPlantioEnum = z.enum([
  "PLANTIO_DIRETO",
  "CONVENCIONAL",
  "MINIMO_CULTIVO",
  "ORGANICO",
]);

// ---- Schemas ----

export const SafraCreateSchema = z.object({
  talhao_id: z.string().uuid({ message: "Talhão obrigatório" }),
  ano_safra: z
    .string()
    .min(4, "Ano safra inválido")
    .max(10)
    .regex(/^\d{4}(\/\d{4})?$/, "Formato: 2024 ou 2024/2025"),
  cultura: z.string().min(1, "Cultura obrigatória"),
  cultivar_id: z.string().uuid().optional().nullable(),
  cultivar_nome: z.string().max(100).optional().nullable(),
  commodity_id: z.string().uuid().optional().nullable(),
  sistema_plantio: SistemaPlantioEnum.optional().nullable(),
  data_plantio_prevista: z.string().date().optional().nullable(),
  data_plantio_real: z.string().date().optional().nullable(),
  data_colheita_prevista: z.string().date().optional().nullable(),
  data_colheita_real: z.string().date().optional().nullable(),
  populacao_prevista: z.number().int().positive().optional().nullable(),
  populacao_real: z.number().int().positive().optional().nullable(),
  espacamento_cm: z.number().int().positive().max(200).optional().nullable(),
  area_plantada_ha: z.number().positive().optional().nullable(),
  produtividade_meta_sc_ha: z.number().positive().optional().nullable(),
  produtividade_real_sc_ha: z.number().positive().optional().nullable(),
  preco_venda_previsto: z.number().positive().optional().nullable(),
  custo_previsto_ha: z.number().positive().optional().nullable(),
  custo_realizado_ha: z.number().positive().optional().nullable(),
  observacoes: z.string().max(2000).optional().nullable(),
});

export const SafraUpdateSchema = SafraCreateSchema.partial();

export const SafraResponseSchema = SafraCreateSchema.extend({
  id: z.string().uuid(),
  tenant_id: z.string().uuid(),
  status: SafraStatusEnum,
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

export const SafraFaseHistoricoSchema = z.object({
  id: z.string().uuid(),
  safra_id: z.string().uuid(),
  fase_anterior: SafraStatusEnum.nullable(),
  fase_nova: SafraStatusEnum,
  usuario_id: z.string().uuid().nullable(),
  observacao: z.string().nullable(),
  created_at: z.string().datetime(),
});

export const SafraAvancarFaseSchema = z.object({
  nova_fase: SafraStatusEnum,
  observacao: z.string().max(500).optional().nullable(),
  dados_fase: z.record(z.unknown()).optional().nullable(),
});

// ---- Tipos inferidos ----
export type SafraCreate = z.infer<typeof SafraCreateSchema>;
export type SafraUpdate = z.infer<typeof SafraUpdateSchema>;
export type SafraResponse = z.infer<typeof SafraResponseSchema>;
export type SafraFaseHistorico = z.infer<typeof SafraFaseHistoricoSchema>;
export type SafraAvancarFase = z.infer<typeof SafraAvancarFaseSchema>;
export type SafraStatus = z.infer<typeof SafraStatusEnum>;
