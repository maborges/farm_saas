// packages/zod-schemas/src/team-schemas.ts
// Schemas de validação para Gestão de Equipe do Tenant

import { z } from "zod";

export const teamInviteSchema = z.object({
    email: z.string().email("E-mail inválido"),
    perfil_id: z.string().uuid("Perfil inválido"),
    fazenda_ids: z.array(z.string().uuid()).min(1, "Selecione pelo menos uma fazenda"),
    data_validade_acesso: z.string().nullable().optional(),
});

export const updateMemberRoleSchema = z.object({
    perfil_id: z.string().uuid("Perfil inválido"),
});

export type TeamInviteInput = z.infer<typeof teamInviteSchema>;
export type UpdateMemberRoleInput = z.infer<typeof updateMemberRoleSchema>;
