/**
 * Formatadores de data para o domínio rural brasileiro.
 * Inclui formatos específicos como ano-safra (2024/2025) e períodos rurais.
 */

/**
 * Formata data como string brasileira (dd/MM/yyyy).
 * @example formatDateBR("2024-03-15") → "15/03/2024"
 */
export function formatDateBR(value: string | Date): string {
  const date = typeof value === "string" ? new Date(value + "T00:00:00") : value;
  return date.toLocaleDateString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

export const formatDateShort = formatDateBR;

/**
 * Formata data e hora como string brasileira.
 * @example formatDateTimeBR("2024-03-15T14:30:00") → "15/03/2024 14:30"
 */
export function formatDateTimeBR(value: string | Date): string {
  const date = typeof value === "string" ? new Date(value) : value;
  return date.toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/**
 * Formata mês e ano (ex: para período de competência).
 * @example formatMesAno("2024-03") → "Mar/2024"
 */
export function formatMesAno(value: string | Date): string {
  const date = typeof value === "string" ? new Date(value + "-01T00:00:00") : value;
  return date.toLocaleDateString("pt-BR", {
    month: "short",
    year: "numeric",
  });
}

/**
 * Formata ano-safra no padrão brasileiro.
 * @example formatAnoSafra("2024/2025") → "Safra 2024/2025"
 * @example formatAnoSafra("2024") → "Safra 2024"
 */
export function formatAnoSafra(anoSafra: string): string {
  return `Safra ${anoSafra}`;
}

/**
 * Calcula e formata dias entre duas datas.
 * @example formatDiasDecorridos("2024-01-01", "2024-03-31") → "90 dias"
 */
export function formatDiasDecorridos(inicio: string | Date, fim?: string | Date): string {
  const start = typeof inicio === "string" ? new Date(inicio) : inicio;
  const end = fim ? (typeof fim === "string" ? new Date(fim) : fim) : new Date();
  const diffMs = end.getTime() - start.getTime();
  const dias = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  return `${dias} dia${dias !== 1 ? "s" : ""}`;
}

/**
 * Retorna a diferença em dias entre duas datas como número.
 */
export function diffDias(inicio: string | Date, fim?: string | Date): number {
  const start = typeof inicio === "string" ? new Date(inicio) : inicio;
  const end = fim ? (typeof fim === "string" ? new Date(fim) : fim) : new Date();
  return Math.floor((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
}

/**
 * Formata período de safra com datas de plantio e colheita.
 * @example formatPeriodoSafra("2024-10-01", "2025-02-28") → "Out/2024 → Fev/2025"
 */
export function formatPeriodoSafra(
  dataInicio: string | null,
  dataFim: string | null
): string {
  if (!dataInicio) return "Período não definido";
  const inicio = formatMesAno(dataInicio);
  if (!dataFim) return `A partir de ${inicio}`;
  return `${inicio} → ${formatMesAno(dataFim)}`;
}

/**
 * Verifica se uma data está dentro de um período.
 */
export function isDateInRange(
  date: string | Date,
  inicio: string | Date,
  fim: string | Date
): boolean {
  const d = typeof date === "string" ? new Date(date) : date;
  const s = typeof inicio === "string" ? new Date(inicio) : inicio;
  const e = typeof fim === "string" ? new Date(fim) : fim;
  return d >= s && d <= e;
}
