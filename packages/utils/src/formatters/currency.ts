/**
 * Formatadores de moeda para o domínio rural brasileiro.
 * Padrão: Real Brasileiro (BRL), localidade pt-BR.
 */

const BRL_FORMATTER = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const BRL_COMPACT_FORMATTER = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
  notation: "compact",
  maximumFractionDigits: 1,
});

const DECIMAL_FORMATTER = new Intl.NumberFormat("pt-BR", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

/**
 * Formata um valor numérico como moeda brasileira.
 * @example formatBRL(1250.5) → "R$ 1.250,50"
 */
export function formatBRL(value: number): string {
  return BRL_FORMATTER.format(value);
}

export const formatCurrency = formatBRL;

/**
 * Formata valor de forma compacta (útil para dashboards).
 * @example formatBRLCompact(1500000) → "R$ 1,5 mi"
 */
export function formatBRLCompact(value: number): string {
  return BRL_COMPACT_FORMATTER.format(value);
}

/**
 * Formata um número com separadores brasileiros sem símbolo de moeda.
 * @example formatDecimalBR(1250.5) → "1.250,50"
 */
export function formatDecimalBR(value: number, decimals = 2): string {
  return new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

/**
 * Formata custo por hectare.
 * @example formatCustoHa(350.75) → "R$ 350,75/ha"
 */
export function formatCustoHa(value: number): string {
  return `${formatBRL(value)}/ha`;
}

/**
 * Parseia uma string de moeda brasileira para number.
 * @example parseBRL("R$ 1.250,50") → 1250.5
 */
export function parseBRL(value: string): number {
  const cleaned = value
    .replace(/[R$\s]/g, "")
    .replace(/\./g, "")
    .replace(",", ".");
  return parseFloat(cleaned);
}
