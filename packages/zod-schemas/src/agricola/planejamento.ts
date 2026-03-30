import { z } from "zod";

export const CategoriaOrcamentoSchema = z.enum([
  "SEMENTE", "FERTILIZANTE", "DEFENSIVO",
  "COMBUSTIVEL", "MAO_DE_OBRA", "SERVICO", "SEGURO", "OUTROS"
], { message: "Categoria de orçamento inválida" });

export type CategoriaOrcamento = z.infer<typeof CategoriaOrcamentoSchema>;

export const ItemOrcamentoCreateSchema = z.object({
  categoria: CategoriaOrcamentoSchema,
  descricao: z.string().min(2, "A descrição deve ter pelo menos 2 caracteres").max(200, "A descrição suporta até 200 caracteres"),
  quantidade: z.number().positive("A quantidade deve ser maior que 0"),
  unidade: z.string().min(1, "A unidade é obrigatória").max(20),
  custo_unitario: z.number().positive("O custo unitário deve ser maior que 0"),
  ordem: z.number().int().nonnegative().optional().default(0),
  observacoes: z.string().nullable().optional(),
});

export type ItemOrcamentoCreate = z.infer<typeof ItemOrcamentoCreateSchema>;

export const ItemOrcamentoUpdateSchema = z.object({
  categoria: CategoriaOrcamentoSchema.nullable().optional(),
  descricao: z.string().min(2, "A descrição deve ter pelo menos 2 caracteres").max(200).nullable().optional(),
  quantidade: z.number().positive("A quantidade deve ser maior que 0").nullable().optional(),
  unidade: z.string().min(1).max(20).nullable().optional(),
  custo_unitario: z.number().positive("O custo unitário deve ser maior que 0").nullable().optional(),
  ordem: z.number().int().nonnegative().nullable().optional(),
  observacoes: z.string().nullable().optional(),
});

export type ItemOrcamentoUpdate = z.infer<typeof ItemOrcamentoUpdateSchema>;
