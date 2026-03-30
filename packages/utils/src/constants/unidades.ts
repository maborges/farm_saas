/**
 * Unidades de medida para o domínio rural do AgroSaaS.
 * Cobre: área, peso, volume, concentração e contagem.
 */

export const UNIDADES_AREA = ["ha", "alq", "m2", "acre"] as const;
export type UnidadeArea = (typeof UNIDADES_AREA)[number];

export const UNIDADES_PESO = ["kg", "t", "sc", "@", "g"] as const;
export type UnidadePeso = (typeof UNIDADES_PESO)[number];

export const UNIDADES_VOLUME = ["L", "mL", "m3", "cc"] as const;
export type UnidadeVolume = (typeof UNIDADES_VOLUME)[number];

export const UNIDADES_CONCENTRACAO = [
  "kg/ha",
  "L/ha",
  "sc/ha",
  "g/ha",
  "mL/ha",
  "t/ha",
  "%",
  "ppm",
] as const;
export type UnidadeConcentracao = (typeof UNIDADES_CONCENTRACAO)[number];

export const UNIDADES_INSUMO = [
  "kg",
  "t",
  "L",
  "mL",
  "sc",
  "un",
  "cx",
  "g",
] as const;
export type UnidadeInsumo = (typeof UNIDADES_INSUMO)[number];

export const UNIDADE_LABEL: Record<string, string> = {
  ha: "Hectare (ha)",
  alq: "Alqueire",
  m2: "Metro quadrado (m²)",
  acre: "Acre",
  kg: "Quilograma (kg)",
  t: "Tonelada (t)",
  sc: "Saca (sc)",
  "@": "Arroba (@)",
  g: "Grama (g)",
  L: "Litro (L)",
  mL: "Mililitro (mL)",
  m3: "Metro cúbico (m³)",
  cc: "Centímetro cúbico (cc)",
  "kg/ha": "kg por hectare",
  "L/ha": "L por hectare",
  "sc/ha": "Sacas por hectare",
  "g/ha": "g por hectare",
  "mL/ha": "mL por hectare",
  "t/ha": "Toneladas por hectare",
  "%": "Porcentagem (%)",
  ppm: "Partes por milhão (ppm)",
  un: "Unidade (un)",
  cx: "Caixa (cx)",
};

/** Tipos de operação agrícola */
export const TIPOS_OPERACAO_AGRICOLA = [
  "PREPARO_SOLO",
  "PLANTIO",
  "ADUBACAO",
  "PULVERIZACAO",
  "IRRIGACAO",
  "COLHEITA",
  "TRANSPORTE",
  "MANUTENCAO",
  "MONITORAMENTO",
  "OUTRO",
] as const;

export type TipoOperacaoAgricola = (typeof TIPOS_OPERACAO_AGRICOLA)[number];

export const TIPO_OPERACAO_LABEL: Record<TipoOperacaoAgricola, string> = {
  PREPARO_SOLO: "Preparo de Solo",
  PLANTIO: "Plantio",
  ADUBACAO: "Adubação",
  PULVERIZACAO: "Pulverização",
  IRRIGACAO: "Irrigação",
  COLHEITA: "Colheita",
  TRANSPORTE: "Transporte",
  MANUTENCAO: "Manutenção",
  MONITORAMENTO: "Monitoramento",
  OUTRO: "Outro",
};
