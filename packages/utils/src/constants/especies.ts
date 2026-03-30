/**
 * Constantes de espécies e categorias animais para o domínio pecuário do AgroSaaS.
 * Sincronizado com os valores do backend Python.
 */

export const ESPECIES_ANIMAIS = [
  "BOVINO_CORTE",
  "BOVINO_LEITE",
  "SUINO",
  "OVINO",
  "CAPRINO",
  "EQUINO",
  "ASININO",
  "BUBALINO",
  "AVES_CORTE",
  "AVES_POSTURA",
  "OUTRO",
] as const;

export type EspecieAnimal = (typeof ESPECIES_ANIMAIS)[number];

export const ESPECIE_LABEL: Record<EspecieAnimal, string> = {
  BOVINO_CORTE: "Bovino de Corte",
  BOVINO_LEITE: "Bovino de Leite",
  SUINO: "Suíno",
  OVINO: "Ovino",
  CAPRINO: "Caprino",
  EQUINO: "Equino",
  ASININO: "Asinino",
  BUBALINO: "Bubalino",
  AVES_CORTE: "Aves de Corte",
  AVES_POSTURA: "Aves de Postura",
  OUTRO: "Outro",
};

export const CATEGORIAS_BOVINO = [
  "BEZERRO",
  "BEZERRA",
  "GARROTE",
  "NOVILHA",
  "BOI",
  "VACA",
  "TOURO",
  "VACA_SECA",
] as const;

export type CategoriaBovino = (typeof CATEGORIAS_BOVINO)[number];

export const CATEGORIA_BOVINO_LABEL: Record<CategoriaBovino, string> = {
  BEZERRO: "Bezerro",
  BEZERRA: "Bezerra",
  GARROTE: "Garrote",
  NOVILHA: "Novilha",
  BOI: "Boi",
  VACA: "Vaca",
  TOURO: "Touro",
  VACA_SECA: "Vaca Seca",
};

export const FINALIDADES_LOTE = [
  "CRIA",
  "RECRIA",
  "ENGORDA",
  "REPRODUCAO",
  "LEITE",
  "MISTO",
] as const;

export type FinalidadeLote = (typeof FINALIDADES_LOTE)[number];

export const FINALIDADE_LOTE_LABEL: Record<FinalidadeLote, string> = {
  CRIA: "Cria",
  RECRIA: "Recria",
  ENGORDA: "Engorda",
  REPRODUCAO: "Reprodução",
  LEITE: "Leite",
  MISTO: "Misto",
};
