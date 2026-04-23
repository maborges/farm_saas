import { z } from "zod";

// ---- Schemas de Talhão (AreaRural) ----

export const TalhaoCreateSchema = z.object({
  propriedade_id: z.string().uuid({ message: "Propriedade obrigatória" }),
  nome: z.string().min(1, "Nome do talhão obrigatório").max(100),
  area_ha: z.number().positive({ message: "Área em hectares obrigatória" }),
  cultura_predominante: z.string().max(50).optional().nullable(),
  tipo_solo_id: z.string().uuid().optional().nullable(),
  irrigado: z.boolean().default(false),
  tipo_irrigacao_id: z.string().uuid().optional().nullable(),
  observacoes: z.string().max(2000).optional().nullable(),
  // GeoJSON opcional para exibição no mapa
  geometry: z.record(z.string(), z.unknown()).optional().nullable(),
});

export const TalhaoUpdateSchema = TalhaoCreateSchema.partial();

export const TalhaoResponseSchema = TalhaoCreateSchema.extend({
  id: z.string().uuid(),
  tenant_id: z.string().uuid(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

export type TalhaoCreate = z.infer<typeof TalhaoCreateSchema>;
export type TalhaoUpdate = z.infer<typeof TalhaoUpdateSchema>;
export type TalhaoResponse = z.infer<typeof TalhaoResponseSchema>;
