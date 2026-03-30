import { z } from "zod";

// ---- Schemas de Fenologia ----

export const FenologiaEscalaResponseSchema = z.object({
  id: z.string().uuid(),
  cultura: z.string(),
  codigo: z.string(),
  nome: z.string(),
  descricao: z.string().nullable(),
  ordem: z.number().int(),
  is_system: z.boolean(),
  ativo: z.boolean(),
});

export const FenologiaRegistroCreateSchema = z.object({
  safra_id: z.string().uuid(),
  talhao_id: z.string().uuid(),
  escala_id: z.string().uuid(),
  grupo_id: z.string().uuid().optional().nullable(),
  data_observacao: z.string().date(),
  observacao: z.string().max(1000).optional().nullable(),
  dados_extras: z.record(z.unknown()).optional().nullable(),
});

export const FenologiaRegistroResponseSchema = FenologiaRegistroCreateSchema.extend({
  id: z.string().uuid(),
  tenant_id: z.string().uuid(),
  usuario_id: z.string().uuid().nullable(),
  created_at: z.string().datetime(),
  escala: FenologiaEscalaResponseSchema,
});

export const SafraTalhaoGrupoCreateSchema = z.object({
  safra_id: z.string().uuid({ message: "Safra obrigatória" }),
  nome: z.string().min(1, "Nome do grupo obrigatório").max(100),
  cor: z
    .string()
    .regex(/^#[0-9A-Fa-f]{6}$/, "Cor deve ser hexadecimal (#RRGGBB)")
    .optional()
    .nullable(),
});

export const SafraTalhaoGrupoResponseSchema = SafraTalhaoGrupoCreateSchema.extend({
  id: z.string().uuid(),
  tenant_id: z.string().uuid(),
  ordem: z.number().int(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

// ---- Tipos inferidos ----
export type FenologiaEscalaResponse = z.infer<typeof FenologiaEscalaResponseSchema>;
export type FenologiaRegistroCreate = z.infer<typeof FenologiaRegistroCreateSchema>;
export type FenologiaRegistroResponse = z.infer<typeof FenologiaRegistroResponseSchema>;
export type SafraTalhaoGrupoCreate = z.infer<typeof SafraTalhaoGrupoCreateSchema>;
export type SafraTalhaoGrupoResponse = z.infer<typeof SafraTalhaoGrupoResponseSchema>;
