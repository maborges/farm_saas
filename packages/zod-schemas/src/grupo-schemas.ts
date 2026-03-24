// packages/zod-schemas/src/grupo-schemas.ts
// Schemas de validação para Grupos de Fazendas

import { z } from "zod";

export const createGrupoSchema = z.object({
    nome: z.string().min(2, "Nome deve ter pelo menos 2 caracteres").max(60, "Nome muito longo"),
    descricao: z.string().max(200, "Descrição muito longa").nullable().optional(),
    cor: z.string().regex(/^#[0-9a-fA-F]{6}$/, "Cor deve ser hexadecimal (#RRGGBB)").default("#16a34a"),
    icone: z.string().max(30, "Ícone muito longo").default("folder"),
});

export const updateGrupoSchema = z.object({
    nome: z.string().min(2).max(60).optional(),
    descricao: z.string().max(200).nullable().optional(),
    cor: z.string().regex(/^#[0-9a-fA-F]{6}$/).optional(),
    icone: z.string().max(30).optional(),
    ordem: z.number().int().nonnegative().optional(),
    ativo: z.boolean().optional(),
});

export const addFazendaToGrupoSchema = z.object({
    fazenda_id: z.string().uuid("ID de fazenda inválido"),
});

export type CreateGrupoInput = z.infer<typeof createGrupoSchema>;
export type UpdateGrupoInput = z.infer<typeof updateGrupoSchema>;
export type AddFazendaToGrupoInput = z.infer<typeof addFazendaToGrupoSchema>;
