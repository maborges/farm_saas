// packages/zod-schemas/src/role-schemas.ts
// Schemas de validação para Perfis e Permissões

import { z } from "zod";

export const permissionLevelValues = ["write", "read", "none"] as const;

export const createRoleSchema = z.object({
    nome: z.string().min(2, "Nome deve ter pelo menos 2 caracteres").max(50, "Nome muito longo"),
    descricao: z.string().max(200, "Descrição muito longa").nullable().optional(),
    permissoes: z.record(z.enum(permissionLevelValues)),
});

export const updateRoleSchema = z.object({
    nome: z.string().min(2, "Nome deve ter pelo menos 2 caracteres").max(50, "Nome muito longo").optional(),
    descricao: z.string().max(200, "Descrição muito longa").nullable().optional(),
    permissoes: z.record(z.enum(permissionLevelValues)).optional(),
});

export type CreateRoleInput = z.infer<typeof createRoleSchema>;
export type UpdateRoleInput = z.infer<typeof updateRoleSchema>;
