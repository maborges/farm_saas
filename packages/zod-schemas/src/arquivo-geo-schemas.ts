import { z } from "zod";

export const FORMATOS_ARQUIVO_GEO = ["shp", "kml", "kmz", "geojson"] as const;
export const STATUS_ARQUIVO_GEO = ["PENDENTE", "PROCESSADO", "ERRO"] as const;

export type FormatoArquivoGeo = (typeof FORMATOS_ARQUIVO_GEO)[number];
export type StatusArquivoGeo = (typeof STATUS_ARQUIVO_GEO)[number];

export const arquivoGeoResponseSchema = z.object({
  id: z.string().uuid(),
  tenant_id: z.string().uuid(),
  area_rural_id: z.string().uuid(),
  uploaded_by: z.string().uuid().nullable(),
  nome_arquivo: z.string(),
  formato: z.string(),
  tamanho_bytes: z.number(),
  storage_backend: z.string(),
  storage_path: z.string(),
  status: z.enum(STATUS_ARQUIVO_GEO),
  poligonos_extraidos: z.number().nullable(),
  area_ha_extraida: z.number().nullable(),
  erro_msg: z.string().nullable(),
  created_at: z.string(),
});

export const arquivoGeoProcessadoResponseSchema = z.object({
  arquivo: arquivoGeoResponseSchema,
  poligonos: z.any().nullable(),
});

export type ArquivoGeoResponse = z.infer<typeof arquivoGeoResponseSchema>;
export type ArquivoGeoProcessadoResponse = z.infer<typeof arquivoGeoProcessadoResponseSchema>;
