// packages/zod-schemas/src/fazenda-schemas.ts
// Schemas de validação para UnidadeProdutiva (ex-Fazenda)

import { z } from "zod";

export const createUnidadeProdutivaSchema = z.object({
    nome: z.string().min(2, "Nome deve ter pelo menos 2 caracteres").max(150, "Nome muito longo"),
    tipo_propriedade: z.enum(["fazenda", "sitio", "chacara", "arrendamento", "parceria"]).default("fazenda"),
    cpf_cnpj: z.string().max(20, "CPF/CNPJ inválido").optional().or(z.literal("")),
    inscricao_estadual: z.string().max(50, "Inscrição estadual muito longa").optional().or(z.literal("")),
    // Áreas
    area_total_ha: z.coerce.number().gt(0, "Área deve ser maior que zero").optional().or(z.literal(0)),
    area_app_ha: z.coerce.number().gte(0).optional().or(z.literal(0)),
    area_rl_ha: z.coerce.number().gte(0).optional().or(z.literal(0)),
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
    codigo_car: z.string().max(80).optional().or(z.literal("")),
    nirf: z.string().max(20).optional().or(z.literal("")),
    ccir: z.string().max(30).optional().or(z.literal("")),
    sigef_codigo: z.string().max(50).optional().or(z.literal("")),
});

export const updateUnidadeProdutivaSchema = createUnidadeProdutivaSchema.partial();

export type CreateUnidadeProdutivaInput = z.infer<typeof createUnidadeProdutivaSchema>;
export type UpdateUnidadeProdutivaInput = z.infer<typeof updateUnidadeProdutivaSchema>;

// Aliases para compatibilidade retroativa
export const createFazendaSchema = createUnidadeProdutivaSchema;
export const updateFazendaSchema = updateUnidadeProdutivaSchema;
export type CreateFazendaInput = CreateUnidadeProdutivaInput;
export type UpdateFazendaInput = UpdateUnidadeProdutivaInput;
