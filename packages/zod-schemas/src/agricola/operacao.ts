import { z } from "zod";

export const OperacaoStatusEnum = z.enum(["PLANEJADA", "EM_ANDAMENTO", "REALIZADA", "CANCELADA"]);

export const InsumoOperacaoCreateSchema = z.object({
  produto_id: z.string().uuid(),
  lote_insumo: z.string().max(50).optional().nullable(),
  dose_por_ha: z.number().positive({ message: "Dose por hectare obrigatória" }),
  unidade: z.string().min(1).max(20),
  area_aplicada: z.number().positive().optional().nullable(),
  quantidade_total: z.number().positive().optional().nullable(),
  custo_unitario: z.number().positive().optional().nullable(),
  custo_total: z.number().positive().optional().nullable(),
  carencia_dias: z.number().int().min(0).optional().nullable(),
  data_reentrada: z.string().date().optional().nullable(),
  epi_necessario: z.array(z.string()).optional().nullable(),
});

export const OperacaoAgricolaCreateSchema = z.object({
  safra_id: z.string().uuid(),
  talhao_id: z.string().uuid(),
  tipo: z.string().min(1, "Tipo obrigatório").max(30),
  subtipo: z.string().max(50).optional().nullable(),
  descricao: z.string().min(1, "Descrição obrigatória").max(1000),
  data_prevista: z.string().date().optional().nullable(),
  data_realizada: z.string().date(),
  hora_inicio: z.string().regex(/^([01]\d|2[0-3]):?([0-5]\d)(:?([0-5]\d))?$/).optional().nullable(),
  hora_fim: z.string().regex(/^([01]\d|2[0-3]):?([0-5]\d)(:?([0-5]\d))?$/).optional().nullable(),
  area_aplicada_ha: z.number().positive().optional().nullable(),
  maquina_id: z.string().uuid().optional().nullable(),
  implemento: z.string().max(100).optional().nullable(),
  operador_id: z.string().uuid().optional().nullable(),
  temperatura_c: z.number().min(-50).max(80).optional().nullable(),
  umidade_rel: z.number().min(0).max(100).optional().nullable(),
  vento_kmh: z.number().min(0).max(200).optional().nullable(),
  direcao_vento: z.string().max(10).optional().nullable(),
  condicao_clima: z.string().max(30).optional().nullable(),
  latitude: z.number().min(-90).max(90).optional().nullable(),
  longitude: z.number().min(-180).max(180).optional().nullable(),
  custo_total: z.number().min(0).optional().default(0),
  custo_por_ha: z.number().min(0).optional().default(0),
  fase_safra: z.string().max(30).optional().nullable(),
  status: OperacaoStatusEnum.optional().default("REALIZADA"),
  observacoes: z.string().max(2000).optional().nullable(),
  fotos: z.array(z.string().url()).optional().default([]),
  insumos: z.array(InsumoOperacaoCreateSchema).optional().default([]),
});

export const InsumoOperacaoResponseSchema = InsumoOperacaoCreateSchema.extend({
  id: z.string().uuid(),
  operacao_id: z.string().uuid(),
  tenant_id: z.string().uuid(),
});

export const OperacaoAgricolaResponseSchema = OperacaoAgricolaCreateSchema.extend({
  id: z.string().uuid(),
  tenant_id: z.string().uuid(),
  insumos: z.array(InsumoOperacaoResponseSchema),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

export type InsumoOperacaoCreate = z.infer<typeof InsumoOperacaoCreateSchema>;
export type InsumoOperacaoResponse = z.infer<typeof InsumoOperacaoResponseSchema>;
export type OperacaoAgricolaCreate = z.infer<typeof OperacaoAgricolaCreateSchema>;
export type OperacaoAgricolaResponse = z.infer<typeof OperacaoAgricolaResponseSchema>;
