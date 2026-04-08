// packages/zod-schemas/src/fazenda-schemas.ts
// Schemas de validação para Fazendas

import { z } from "zod";

export const createFazendaSchema = z.object({
    grupo_id: z.string().uuid("Selecione um grupo de fazendas"),
    nome: z.string().min(2, "Nome deve ter pelo menos 2 caracteres").max(150, "Nome muito longo"),
    cnpj: z.string().max(20, "CNPJ inválido").optional().or(z.literal("")),
    inscricao_estadual: z.string().max(50, "Inscrição estadual muito longa").optional().or(z.literal("")),
    area_total_ha: z.coerce.number().gt(0, "Área deve ser maior que zero").optional().or(z.literal(0)),
    coordenadas_sede: z.string().max(100, "Coordenadas inválidas").optional().or(z.literal("")),
    geometria: z.any().optional().nullable(),
    ativo: z.boolean().default(true),
});

export const updateFazendaSchema = z.object({
    grupo_id: z.string().uuid().optional(),
    nome: z.string().min(2).max(150).optional(),
    cnpj: z.string().max(20).optional().nullable(),
    inscricao_estadual: z.string().max(50).optional().nullable(),
    area_total_ha: z.coerce.number().gt(0).optional().nullable(),
    coordenadas_sede: z.string().max(100).optional().nullable(),
    geometria: z.any().optional().nullable(),
    ativo: z.boolean().optional(),
});

export type CreateFazendaInput = z.infer<typeof createFazendaSchema>;
export type UpdateFazendaInput = z.infer<typeof updateFazendaSchema>;
