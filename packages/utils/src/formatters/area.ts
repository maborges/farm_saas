/**
 * Formatadores de área para o domínio rural brasileiro.
 * Unidades: hectare (ha), alqueire (al), acre, m².
 */

const ALQUEIRE_PAULISTA_HA = 2.42; // 1 alqueire paulista = 2,42 ha
const ALQUEIRE_MINEIRO_HA = 4.84;  // 1 alqueire mineiro = 4,84 ha
const ACRE_HA = 0.404686;

const AREA_FORMATTER = new Intl.NumberFormat("pt-BR", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 4,
});

/**
 * Formata área em hectares.
 * @example formatHectares(125.5) → "125,5000 ha"
 */
export function formatHectares(value: number, decimals = 4): string {
  return `${new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value)} ha`;
}

/**
 * Formata área compacta para exibição em cards.
 * @example formatHectaresCompact(125.5) → "125,5 ha"
 */
export function formatHectaresCompact(value: number): string {
  return `${new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(value)} ha`;
}

export const formatArea = formatHectaresCompact;

/**
 * Converte hectares para alqueire paulista.
 * @example haToAlqueirePaulista(2.42) → 1
 */
export function haToAlqueirePaulista(ha: number): number {
  return ha / ALQUEIRE_PAULISTA_HA;
}

/**
 * Converte hectares para alqueire mineiro.
 */
export function haToAlqueireMineiro(ha: number): number {
  return ha / ALQUEIRE_MINEIRO_HA;
}

/**
 * Converte hectares para acres.
 */
export function haToAcre(ha: number): number {
  return ha / ACRE_HA;
}

/**
 * Formata m² como hectares automaticamente.
 * @example formatM2AsHa(24200) → "2,4200 ha"
 */
export function formatM2AsHa(m2: number): string {
  return formatHectares(m2 / 10000);
}

/**
 * Parseia string de hectares para number.
 * @example parseHectares("125,5000 ha") → 125.5
 */
export function parseHectares(value: string): number {
  const cleaned = value.replace(/\sha$/, "").replace(/\./g, "").replace(",", ".");
  return parseFloat(cleaned);
}
