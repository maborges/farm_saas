/**
 * Formatadores de peso e volume para o domínio rural brasileiro.
 * Unidades: arroba (@), saca (sc), kg, tonelada (t), litro (L).
 */

const KG_POR_ARROBA = 15;
const KG_POR_SACA_SOJA = 60;
const KG_POR_SACA_MILHO = 60;
const KG_POR_SACA_TRIGO = 60;
const KG_POR_SACA_CAFE = 60;
const KG_POR_SACA_ALGODAO = 15; // pluma

export type CulturaWeight = "soja" | "milho" | "trigo" | "cafe" | "algodao";

const SACA_KG_MAP: Record<CulturaWeight, number> = {
  soja: KG_POR_SACA_SOJA,
  milho: KG_POR_SACA_MILHO,
  trigo: KG_POR_SACA_TRIGO,
  cafe: KG_POR_SACA_CAFE,
  algodao: KG_POR_SACA_ALGODAO,
};

/**
 * Formata peso em kg.
 * @example formatKg(1500) → "1.500 kg"
 */
export function formatKg(value: number): string {
  return `${new Intl.NumberFormat("pt-BR").format(value)} kg`;
}

/**
 * Formata peso em toneladas.
 * @example formatTonelada(1.5) → "1,500 t"
 */
export function formatTonelada(value: number): string {
  return `${new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: 3,
    maximumFractionDigits: 3,
  }).format(value)} t`;
}

/**
 * Formata peso em arrobas (@).
 * @example formatArroba(15) → "15,00 @"
 */
export function formatArroba(value: number): string {
  return `${new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)} @`;
}

/**
 * Formata sacas com cultura específica.
 * @example formatSacas(100, "soja") → "100,00 sc/60kg"
 */
export function formatSacas(value: number, cultura?: CulturaWeight): string {
  const kg = cultura ? SACA_KG_MAP[cultura] : 60;
  return `${new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)} sc/${kg}kg`;
}

/**
 * Converte kg para arrobas.
 */
export function kgToArroba(kg: number): number {
  return kg / KG_POR_ARROBA;
}

/**
 * Converte kg para sacas de uma cultura.
 */
export function kgToSacas(kg: number, cultura: CulturaWeight = "soja"): number {
  return kg / SACA_KG_MAP[cultura];
}

/**
 * Converte sacas para kg.
 */
export function sacasToKg(sacas: number, cultura: CulturaWeight = "soja"): number {
  return sacas * SACA_KG_MAP[cultura];
}

/**
 * Formata produtividade por hectare.
 * @example formatProdutividadeHa(60.5, "soja") → "60,50 sc/ha"
 */
export function formatProdutividadeHa(scHa: number): string {
  return `${new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(scHa)} sc/ha`;
}

/**
 * Formata volume em litros.
 * @example formatLitros(500) → "500 L"
 */
export function formatLitros(value: number): string {
  return `${new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(value)} L`;
}
