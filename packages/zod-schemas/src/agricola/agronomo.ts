import { z } from "zod";

export const ConstatacaoSchema = z.object({
  nome: z.string().min(1, "Nome é obrigatório"),
  tipo: z.enum(["PRAGA", "DOENCA", "PLANTA_DANINHA", "DEFICIENCIA_NUTRICIONAL"]),
  nivel: z.enum(["BAIXO", "MEDIO", "ALTO"]),
  posicao_planta: z.string().nullable().optional(),
  fotos: z.array(z.string()).default([]),
});

export const RelatorioTecnicoCreateSchema = z.object({
  safra_id: z.string().uuid("Safra inválida"),
  talhao_id: z.string().uuid("Talhão inválido"),
  data_visita: z.string().optional().nullable(),
  estadio_fenologico: z.string().optional().nullable(),
  condicao_climatica: z.record(z.string(), z.any()).optional().nullable(),
  observacoes_gerais: z.string().optional().nullable(),
  recomendacoes: z.string().optional().nullable(),
  constatacoes: z.array(ConstatacaoSchema).default([]),
  status: z.enum(["RASCUNHO", "FINALIZADO"]).default("RASCUNHO"),
});

export const RelatorioTecnicoUpdateSchema = RelatorioTecnicoCreateSchema.partial();

export type Constatacao = z.infer<typeof ConstatacaoSchema>;
export type RelatorioTecnicoCreate = z.infer<typeof RelatorioTecnicoCreateSchema>;
export type RelatorioTecnicoUpdate = z.infer<typeof RelatorioTecnicoUpdateSchema>;
