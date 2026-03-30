import { z } from "zod";

export const LoteBeneficiamentoCreateSchema = z.object({
  safra_id: z.string().uuid("ID de safra inválido"),
  talhao_id: z.string().uuid("ID de talhão inválido").nullable().optional(),
  numero_lote: z.string().min(1, "O número do lote é obrigatório"),
  metodo: z.enum(["NATURAL", "LAVADO", "HONEY", "DESCASCADO"], {
    message: "O método deve ser NATURAL, LAVADO, HONEY ou DESCASCADO",
  }),
  data_entrada: z.string().date("Data de entrada inválida"),
  peso_entrada_kg: z.number().positive("O peso de entrada deve ser maior que 0"),
  umidade_entrada_pct: z.number().min(0, "A umidade não pode ser negativa").max(100, "A umidade máxima é 100").nullable().optional(),
  local_secagem: z.string().nullable().optional(),
  observacoes: z.string().nullable().optional(),
});

export type LoteBeneficiamentoCreate = z.infer<typeof LoteBeneficiamentoCreateSchema>;

export const LoteBeneficiamentoUpdateSchema = z.object({
  status: z.string().nullable().optional(),
  local_secagem: z.string().nullable().optional(),
  data_inicio_secagem: z.string().date("Data de início de secagem inválida").nullable().optional(),
  data_fim_secagem: z.string().date("Data de fim de secagem inválida").nullable().optional(),
  data_saida: z.string().date("Data de saída inválida").nullable().optional(),
  peso_saida_kg: z.number().positive("O peso de saída deve ser maior que 0").nullable().optional(),
  umidade_saida_pct: z.number().min(0).max(100).nullable().optional(),
  peneira_principal: z.string().nullable().optional(),
  bebida: z.string().nullable().optional(),
  pontuacao_scaa: z.number().min(0).max(100).nullable().optional(),
  defeitos_intrinsecos: z.number().int().nonnegative().nullable().optional(),
  defeitos_extrinsecos: z.number().int().nonnegative().nullable().optional(),
  armazem_id: z.string().uuid("ID do armazém inválido").nullable().optional(),
  saca_inicio: z.number().int().positive().nullable().optional(),
  saca_fim: z.number().int().positive().nullable().optional(),
  observacoes: z.string().nullable().optional(),
});

export type LoteBeneficiamentoUpdate = z.infer<typeof LoteBeneficiamentoUpdateSchema>;
