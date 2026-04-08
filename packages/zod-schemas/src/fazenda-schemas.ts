// packages/zod-schemas/src/fazenda-schemas.ts
// Schemas de validação para Fazendas

import { z } from "zod";

export const createFazendaSchema = z.object({
    grupo_id: z.string().uuid("Selecione um grupo de fazendas"),
    nome: z.string().min(2, "Nome deve ter pelo menos 2 caracteres").max(150, "Nome muito longo"),
    tipo_propriedade: z.enum(["fazenda", "sitio", "chacara", "arrendamento", "parceria"]).default("fazenda"),
    cnpj: z.string().max(20, "CNPJ inválido").optional().or(z.literal("")),
    inscricao_estadual: z.string().max(50, "Inscrição estadual muito longa").optional().or(z.literal("")),
    area_total_ha: z.coerce.number().gt(0, "Área deve ser maior que zero").optional().or(z.literal(0)),
    coordenadas_sede: z.string().max(100, "Coordenadas inválidas").optional().or(z.literal("")),
    geometria: z.any().optional().nullable(),
    ativo: z.boolean().default(true),
    // Localização
    cep: z.string().max(9).optional().or(z.literal("")),
    logradouro: z.string().max(255).optional().or(z.literal("")),
    bairro: z.string().max(100).optional().or(z.literal("")),
    municipio: z.string().max(100).optional().or(z.literal("")),
    uf: z.string().length(2).optional().or(z.literal("")),
    ibge_municipio_codigo: z.string().max(7).optional().or(z.literal("")),
    // Regulatório
    car: z.string().max(80).optional().or(z.literal("")),
    ccir: z.string().max(30).optional().or(z.literal("")),
    sigef_codigo: z.string().max(50).optional().or(z.literal("")),
});

export const updateFazendaSchema = createFazendaSchema.partial().extend({
    grupo_id: z.string().uuid().optional(),
});

export type CreateFazendaInput = z.infer<typeof createFazendaSchema>;
export type UpdateFazendaInput = z.infer<typeof updateFazendaSchema>;
