import { z } from "zod";

const TurnoEnum = z.enum(["MANHA", "TARDE", "NOITE"]);
const DestinoEnum = z.enum(["ARMAZEM", "TERCEIRO", "COOPERATIVA", "INDUSTRIA", "OUTRO"]);

export const RomaneioCreateSchema = z.object({
  safra_id: z.string().uuid(),
  talhao_id: z.string().uuid(),
  numero_romaneio: z.string().max(30).optional().nullable(),
  data_colheita: z.string().date(),
  turno: TurnoEnum.optional().nullable(),
  maquina_colhedora_id: z.string().uuid().optional().nullable(),
  operador_id: z.string().uuid().optional().nullable(),
  peso_bruto_kg: z.number().positive({ message: "Peso bruto obrigatório" }),
  tara_kg: z.number().min(0).optional().nullable(),
  umidade_pct: z.number().min(0).max(100).optional().nullable(),
  impureza_pct: z.number().min(0).max(100).optional().nullable(),
  avariados_pct: z.number().min(0).max(100).optional().nullable(),
  destino: DestinoEnum.optional().nullable(),
  armazem_id: z.string().uuid().optional().nullable(),
  preco_saca: z.number().positive().optional().nullable(),
  observacoes: z.string().max(2000).optional().nullable(),
});

export const RomaneioResponseSchema = RomaneioCreateSchema.extend({
  id: z.string().uuid(),
  tenant_id: z.string().uuid(),
  peso_liquido_kg: z.number().nullable(),
  desconto_umidade_kg: z.number().nullable(),
  desconto_impureza_kg: z.number().nullable(),
  peso_liquido_padrao_kg: z.number().nullable(),
  sacas_60kg: z.number().nullable(),
  produtividade_sc_ha: z.number().nullable(),
  receita_total: z.number().nullable(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

export type RomaneioCreate = z.infer<typeof RomaneioCreateSchema>;
export type RomaneioResponse = z.infer<typeof RomaneioResponseSchema>;
