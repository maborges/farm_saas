// packages/zod-schemas/src/admin-schemas.ts
// Schemas de validação para Gestão de Admins do Backoffice

import { z } from "zod";

export const backofficeRoleValues = [
    "super_admin", "admin", "suporte", "financeiro", "comercial",
] as const;

export const createAdminSchema = z.object({
    email: z.string().email("E-mail inválido"),
    nome: z.string().min(3, "Nome deve ter pelo menos 3 caracteres").max(100, "Nome muito longo"),
    password: z.string().min(8, "Senha deve ter pelo menos 8 caracteres"),
    role: z.enum(backofficeRoleValues, { required_error: "Selecione uma role" }),
});

export const updateAdminSchema = z.object({
    nome: z.string().min(3, "Nome deve ter pelo menos 3 caracteres").max(100, "Nome muito longo").optional(),
    role: z.enum(backofficeRoleValues).optional(),
    ativo: z.boolean().optional(),
});

export const resetPasswordSchema = z.object({
    nova_senha: z.string().min(8, "Senha deve ter pelo menos 8 caracteres"),
});

export type CreateAdminInput = z.infer<typeof createAdminSchema>;
export type UpdateAdminInput = z.infer<typeof updateAdminSchema>;
export type ResetPasswordInput = z.infer<typeof resetPasswordSchema>;
