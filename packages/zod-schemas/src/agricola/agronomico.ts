import { z } from "zod";

// ---- Tipo de Solo (Lookup) ----
export const TipoSoloSchema = z.object({
  id: z.string().uuid(),
  nome: z.string().min(1).max(50), // Arenoso, Médio, Argiloso
  retencao_agua: z.enum(["BAIXA", "MEDIA", "ALTA"]),
  lixiviacao: z.enum(["BAIXA", "MEDIA", "ALTA"]),
  ctc_resumo: z.enum(["BAIXA", "MEDIA", "ALTA"]),
  descricao: z.string().optional().nullable(),
});

// ---- Tipo de Irrigação (Lookup) ----
export const TipoIrrigacaoSchema = z.object({
  id: z.string().uuid(),
  nome: z.string().min(1).max(50), // Gotejamento, Pivô Central, etc.
  metodo: z.string().optional().nullable(),
  descricao: z.string().optional().nullable(),
});

// ---- Regra Agronômica (Motor de Decisão) ----
export const RegraAgronomicaSchema = z.object({
  id: z.string().uuid(),
  nome: z.string().min(1).max(100),
  descricao: z.string().optional().nullable(),
  // A condição e a ação são armazenadas como JSON para flexibilidade
  condicao_json: z.record(z.string(), z.unknown()), 
  acao_json: z.record(z.string(), z.unknown()),
  prioridade: z.number().int().default(0),
  ativo: z.boolean().default(true),
  tenant_id: z.string().uuid().optional().nullable(), // Nullable se for global do SaaS
});

export type TipoSolo = z.infer<typeof TipoSoloSchema>;
export type TipoIrrigacao = z.infer<typeof TipoIrrigacaoSchema>;
export type RegraAgronomica = z.infer<typeof RegraAgronomicaSchema>;
