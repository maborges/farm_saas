// packages/zod-schemas/src/index.ts
// Barrel export de todos os schemas compartilhados

// Core — identidade, plataforma, time
export * from "./admin-schemas";
export * from "./team-schemas";
export * from "./role-schemas";
export * from "./grupo-schemas";
export * from "./fazenda-schemas";
export * from "./infraestrutura-schemas";
export * from "./arquivo-geo-schemas";
export * from "./plan-schemas";
export * from "./propriedade-schemas";

// Domínios de negócio
export * from "./agricola/index";

// Cadastros
export * from "./commodity-schemas";
