import { z } from "zod";

export const AnaliseSoloCreateSchema = z.object({
  talhao_id: z.string().uuid(),
  data_coleta: z.string().date(),
  laboratorio: z.string().max(150).optional().nullable(),
  codigo_amostra: z.string().max(50).optional().nullable(),
  profundidade_cm: z.number().int().positive().max(100).optional().nullable(),
  // Físicas
  argila_pct: z.number().min(0).max(100).optional().nullable(),
  silte_pct: z.number().min(0).max(100).optional().nullable(),
  areia_pct: z.number().min(0).max(100).optional().nullable(),
  // Químicas
  ph_agua: z.number().min(0).max(14).optional().nullable(),
  ph_cacl2: z.number().min(0).max(14).optional().nullable(),
  materia_organica_pct: z.number().min(0).max(100).optional().nullable(),
  fosforo_p: z.number().min(0).optional().nullable(),
  potassio_k: z.number().min(0).optional().nullable(),
  calcio_ca: z.number().min(0).optional().nullable(),
  magnesio_mg: z.number().min(0).optional().nullable(),
  aluminio_al: z.number().min(0).optional().nullable(),
  hidrogenio_al_hal: z.number().min(0).optional().nullable(),
  // Calculados
  ctc: z.number().min(0).optional().nullable(),
  v_pct: z.number().min(0).max(100).optional().nullable(),
  arquivo_laudo_url: z.string().url().optional().nullable(),
});

export const AnaliseSoloResponseSchema = AnaliseSoloCreateSchema.extend({
  id: z.string().uuid(),
  tenant_id: z.string().uuid(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

export type AnaliseSoloCreate = z.infer<typeof AnaliseSoloCreateSchema>;
export type AnaliseSoloResponse = z.infer<typeof AnaliseSoloResponseSchema>;
