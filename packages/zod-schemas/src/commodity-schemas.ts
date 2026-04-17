import { z } from "zod";

/**
 * Schemas de validação para Commodities no frontend.
 * Espelham os schemas Pydantic do backend.
 */

const TIPOS_COMMODITY = ["AGRICOLA", "PECUARIA", "FLORESTAL"] as const;
const UNIDADES_COMMODITY = [
  "SACA_60KG", "TONELADA", "KG", "ARROBA", "CABECA", "LITRO", "M3", "UNIDADE",
] as const;

const UNIDADES_PESO_FIXO = new Set(["SACA_60KG", "TONELADA", "KG", "ARROBA"]);
const UNIDADES_SEM_PESO_FIXO = new Set(["CABECA", "LITRO", "M3", "UNIDADE"]);

export const CommoditySchema = z.object({
  id: z.string().uuid().optional(),
  nome: z.string().min(1, "Nome é obrigatório").max(150),
  codigo: z.string().min(1, "Código é obrigatório").max(50).toUpperCase(),
  descricao: z.string().max(500).optional().or(z.literal("")),
  tipo: z.enum(TIPOS_COMMODITY, { message: "Tipo é obrigatório" }),
  unidade_padrao: z.enum(UNIDADES_COMMODITY, { message: "Unidade é obrigatória" }),
  peso_unidade: z.coerce.number().nullable(),
  umidade_padrao_pct: z.coerce.number().nullable(),
  impureza_padrao_pct: z.coerce.number().nullable(),
  possui_cotacao: z.boolean().default(false),
  bolsa_referencia: z.string().max(100).optional().or(z.literal("")),
  codigo_bolsa: z.string().max(100).optional().or(z.literal("")),
  ativo: z.boolean().default(true),
  sistema: z.boolean().default(false).optional(),
  created_at: z.string().datetime().optional(),
  updated_at: z.string().datetime().optional(),
});

export const CommodityCreateSchema = CommoditySchema.pick({
  nome: true, codigo: true, descricao: true, tipo: true, unidade_padrao: true,
  peso_unidade: true, umidade_padrao_pct: true, impureza_padrao_pct: true,
  possui_cotacao: true, bolsa_referencia: true, codigo_bolsa: true, ativo: true,
});

export const CommodityUpdateSchema = CommodityCreateSchema.partial();

export const ClassificacaoSchema = z.object({
  id: z.string().uuid().optional(),
  commodity_id: z.string().uuid(),
  classe: z.string().min(1, "Classe é obrigatória").max(50),
  descricao: z.string().max(200).optional().or(z.literal("")),
  umidade_max_pct: z.coerce.number().nullable(),
  impureza_max_pct: z.coerce.number().nullable(),
  avariados_max_pct: z.coerce.number().nullable(),
  ardidos_max_pct: z.coerce.number().nullable(),
  esverdeados_max_pct: z.coerce.number().nullable(),
  quebrados_max_pct: z.coerce.number().nullable(),
  desconto_umidade_por_ponto: z.coerce.number().nullable(),
  desconto_impureza_por_ponto: z.coerce.number().nullable(),
  parametros_extras: z.record(z.unknown()).optional().nullable(),
  ativo: z.boolean().default(true),
});

export function validatePesoUnidade(data: { unidade_padrao: string; peso_unidade: number | null }) {
  const errors: Record<string, string> = {};
  if (UNIDADES_PESO_FIXO.has(data.unidade_padrao) && (data.peso_unidade == null || data.peso_unidade <= 0)) {
    errors.peso_unidade = `Peso é obrigatório para ${data.unidade_padrao}`;
  }
  if (UNIDADES_SEM_PESO_FIXO.has(data.unidade_padrao) && data.peso_unidade != null && data.peso_unidade > 0) {
    errors.peso_unidade = `Peso não deve ser usado com ${data.unidade_padrao}`;
  }
  return errors;
}

export type CommodityType = z.infer<typeof CommoditySchema>;
export type ClassificacaoType = z.infer<typeof ClassificacaoSchema>;
export const COMMODITY_TIPOS = TIPOS_COMMODITY;
export const COMMODITY_UNIDADES = UNIDADES_COMMODITY;
