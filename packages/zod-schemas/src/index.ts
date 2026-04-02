// packages/zod-schemas/src/index.ts
// Barrel export de todos os schemas compartilhados

// Core — identidade, plataforma, time
export * from "./admin-schemas";
export * from "./team-schemas";
export * from "./role-schemas";
export * from "./grupo-schemas";
export * from "./fazenda-schemas";
export * from "./plan-schemas";

// Domínios de negócio
export * from "./agricola/index";
