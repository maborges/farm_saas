/**
 * Constantes de culturas agrícolas para o domínio do AgroSaaS.
 * Sincronizado com os valores usados no backend Python.
 */

export const CULTURAS = [
  "SOJA",
  "MILHO",
  "MILHO_SAFRINHA",
  "TRIGO",
  "ALGODAO",
  "CAFE",
  "CANA_ACUCAR",
  "ARROZ",
  "FEIJAO",
  "SORGO",
  "GIRASSOL",
  "AMENDOIM",
  "MANDIOCA",
  "EUCALIPTO",
  "PASTAGEM",
  "OUTRO",
] as const;

export type Cultura = (typeof CULTURAS)[number];

export const CULTURA_LABEL: Record<Cultura, string> = {
  SOJA: "Soja",
  MILHO: "Milho (Verão)",
  MILHO_SAFRINHA: "Milho Safrinha",
  TRIGO: "Trigo",
  ALGODAO: "Algodão",
  CAFE: "Café",
  CANA_ACUCAR: "Cana-de-Açúcar",
  ARROZ: "Arroz",
  FEIJAO: "Feijão",
  SORGO: "Sorgo",
  GIRASSOL: "Girassol",
  AMENDOIM: "Amendoim",
  MANDIOCA: "Mandioca",
  EUCALIPTO: "Eucalipto",
  PASTAGEM: "Pastagem",
  OUTRO: "Outro",
};

export const SISTEMAS_PLANTIO = [
  "PLANTIO_DIRETO",
  "CONVENCIONAL",
  "MINIMO_CULTIVO",
  "ORGANICO",
] as const;

export type SistemaPlantio = (typeof SISTEMAS_PLANTIO)[number];

export const SISTEMA_PLANTIO_LABEL: Record<SistemaPlantio, string> = {
  PLANTIO_DIRETO: "Plantio Direto",
  CONVENCIONAL: "Convencional",
  MINIMO_CULTIVO: "Cultivo Mínimo",
  ORGANICO: "Orgânico",
};

export const SAFRA_STATUS = [
  "PLANEJADA",
  "PREPARO_SOLO",
  "PLANTIO",
  "DESENVOLVIMENTO",
  "COLHEITA",
  "POS_COLHEITA",
  "ENCERRADA",
  "CANCELADA",
] as const;

export type SafraStatus = (typeof SAFRA_STATUS)[number];

export const SAFRA_STATUS_LABEL: Record<SafraStatus, string> = {
  PLANEJADA: "Planejada",
  PREPARO_SOLO: "Preparo de Solo",
  PLANTIO: "Plantio",
  DESENVOLVIMENTO: "Desenvolvimento",
  COLHEITA: "Colheita",
  POS_COLHEITA: "Pós-Colheita",
  ENCERRADA: "Encerrada",
  CANCELADA: "Cancelada",
};

export const SAFRA_STATUS_COLOR: Record<SafraStatus, string> = {
  PLANEJADA: "bg-slate-100 text-slate-700",
  PREPARO_SOLO: "bg-amber-100 text-amber-700",
  PLANTIO: "bg-lime-100 text-lime-700",
  DESENVOLVIMENTO: "bg-green-100 text-green-700",
  COLHEITA: "bg-yellow-100 text-yellow-700",
  POS_COLHEITA: "bg-orange-100 text-orange-700",
  ENCERRADA: "bg-gray-100 text-gray-600",
  CANCELADA: "bg-red-100 text-red-600",
};
