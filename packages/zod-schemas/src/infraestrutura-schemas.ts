import { z } from "zod";

export const TIPOS_INFRAESTRUTURA = ["sede", "silo", "curral", "galpao", "oficina", "outro"] as const;
export type TipoInfraestrutura = (typeof TIPOS_INFRAESTRUTURA)[number];

export const createInfraestruturaSchema = z.object({
  area_rural_id: z.string().uuid("ID da área inválido"),
  nome: z.string().min(1, "Nome obrigatório").max(100, "Nome muito longo"),
  tipo: z.enum(TIPOS_INFRAESTRUTURA, { errorMap: () => ({ message: "Tipo inválido" }) }),
  capacidade: z.coerce.number().positive("Capacidade deve ser positiva").optional().nullable(),
  unidade_capacidade: z.string().max(20).optional().nullable(),
  latitude: z.coerce.number().min(-90).max(90).optional().nullable(),
  longitude: z.coerce.number().min(-180).max(180).optional().nullable(),
  observacoes: z.string().max(1000).optional().nullable(),
});

export const updateInfraestruturaSchema = z.object({
  nome: z.string().min(1).max(100).optional(),
  tipo: z.enum(TIPOS_INFRAESTRUTURA).optional(),
  capacidade: z.coerce.number().positive().optional().nullable(),
  unidade_capacidade: z.string().max(20).optional().nullable(),
  latitude: z.coerce.number().min(-90).max(90).optional().nullable(),
  longitude: z.coerce.number().min(-180).max(180).optional().nullable(),
  observacoes: z.string().max(1000).optional().nullable(),
  is_active: z.boolean().optional(),
});

export const infraestruturaResponseSchema = z.object({
  id: z.string().uuid(),
  tenant_id: z.string().uuid(),
  area_rural_id: z.string().uuid(),
  nome: z.string(),
  tipo: z.string(),
  capacidade: z.number().nullable(),
  unidade_capacidade: z.string().nullable(),
  latitude: z.number().nullable(),
  longitude: z.number().nullable(),
  observacoes: z.string().nullable(),
  is_active: z.boolean(),
  created_at: z.string(),
});

export type CreateInfraestruturaInput = z.infer<typeof createInfraestruturaSchema>;
export type UpdateInfraestruturaInput = z.infer<typeof updateInfraestruturaSchema>;
export type InfraestruturaResponse = z.infer<typeof infraestruturaResponseSchema>;
