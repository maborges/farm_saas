// packages/zod-schemas/src/plan-schemas.ts
// Schemas de validação para Gestão de Planos do Backoffice

import { z } from "zod";

export const billingPeriodValues = ["monthly", "annually"] as const;

export const createPlanSchema = z.object({
  name: z.string().min(3, "Nome deve ter pelo menos 3 caracteres").max(100, "Nome muito longo"),
  description: z.string().min(10, "Descrição deve ter pelo menos 10 caracteres").max(500, "Descrição muito longa"),
  price: z.number().min(0, "Preço deve ser maior ou igual a 0"),
  billing_period: z.enum(billingPeriodValues, { required_error: "Selecione um período de cobrança" }),
  features: z.array(z.string()).min(1, "Adicione pelo menos uma funcionalidade"),
  is_active: z.boolean().default(true),
  is_default: z.boolean().default(false),
});

export const updatePlanSchema = createPlanSchema.partial();

export type CreatePlanInput = z.infer<typeof createPlanSchema>;
export type UpdatePlanInput = z.infer<typeof updatePlanSchema>;
