/**
 * EXEMPLO: Como ficaria o app-sidebar.tsx com a modularização completa
 *
 * Este é um EXEMPLO de como atualizar o menu. NÃO copie diretamente!
 * Use como referência e adapte conforme necessário.
 *
 * Arquivo original: apps/web/src/components/layout/app-sidebar.tsx
 */

import { Modulos } from "@/lib/constants/modulos";
import { ModuleGate } from "@/components/shared/module-gate";
import { useHasAnyModule } from "@/hooks/use-has-module";

// ... outros imports

export function AppSidebarModularizado() {
  const pathname = usePathname();
  const { tenant, user } = useAppStore();

  // Verificar se tem ALGUM módulo agrícola para mostrar o grupo
  const hasAgricolaModules = useHasAnyModule(
    Modulos.AGRICOLA_PLANEJAMENTO,
    Modulos.AGRICOLA_CAMPO,
    Modulos.AGRICOLA_DEFENSIVOS,
    Modulos.AGRICOLA_PRECISAO,
    Modulos.AGRICOLA_COLHEITA
  );

  const hasPecuariaModules = useHasAnyModule(
    Modulos.PECUARIA_REBANHO,
    Modulos.PECUARIA_GENETICA,
    Modulos.PECUARIA_CONFINAMENTO,
    Modulos.PECUARIA_LEITE
  );

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader>{/* ... logo ... */}</SidebarHeader>

      <SidebarContent>
        {/* BLOCO AGRÍCOLA */}
        {hasAgricolaModules && (
          <SidebarGroup>
            <SidebarGroupLabel>Agrícola</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                <Collapsible>
                  <CollapsibleTrigger>
                    <SidebarMenuButton>
                      <Sprout className="h-4 w-4" />
                      <span>Agricultura</span>
                      <ChevronRight className="ml-auto" />
                    </SidebarMenuButton>
                  </CollapsibleTrigger>

                  <CollapsibleContent>
                    <SidebarMenuSub>
                      {/* A1 - Planejamento */}
                      <ModuleGate moduleId={Modulos.AGRICOLA_PLANEJAMENTO}>
                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton
                            isActive={pathname === "/agricola/planejamento"}
                          >
                            <Link
                              href="/agricola/planejamento"
                              className="flex items-center gap-2 w-full"
                            >
                              <BarChart3 className="h-3.5 w-3.5" />
                              📊 Planejamento de Safra
                            </Link>
                          </SidebarMenuSubButton>
                        </SidebarMenuSubItem>

                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton
                            isActive={pathname === "/agricola/safras"}
                          >
                            <Link
                              href="/agricola/safras"
                              className="flex items-center gap-2 w-full"
                            >
                              <Calendar className="h-3.5 w-3.5" />
                              Gestão de Safras
                            </Link>
                          </SidebarMenuSubButton>
                        </SidebarMenuSubItem>
                      </ModuleGate>

                      {/* A2 - Caderno de Campo */}
                      <ModuleGate moduleId={Modulos.AGRICOLA_CAMPO}>
                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton
                            isActive={pathname === "/agricola/operacoes"}
                          >
                            <Link
                              href="/agricola/operacoes"
                              className="flex items-center gap-2 w-full"
                            >
                              <Tractor className="h-3.5 w-3.5" />
                              📝 Caderno de Campo
                            </Link>
                          </SidebarMenuSubButton>
                        </SidebarMenuSubItem>

                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton
                            isActive={pathname === "/agricola/apontamentos"}
                          >
                            <Link
                              href="/agricola/apontamentos"
                              className="flex items-center gap-2 w-full"
                            >
                              <ClipboardCheck className="h-3.5 w-3.5" />
                              Apontamentos de Campo
                            </Link>
                          </SidebarMenuSubButton>
                        </SidebarMenuSubItem>
                      </ModuleGate>

                      {/* A3 - Defensivos */}
                      <ModuleGate moduleId={Modulos.AGRICOLA_DEFENSIVOS}>
                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton
                            isActive={pathname === "/agricola/defensivos"}
                          >
                            <Link
                              href="/agricola/defensivos"
                              className="flex items-center gap-2 w-full"
                            >
                              <ShieldAlert className="h-3.5 w-3.5" />
                              🛡️ Fitossanitário
                            </Link>
                          </SidebarMenuSubButton>
                        </SidebarMenuSubItem>

                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton
                            isActive={pathname === "/agricola/monitoramento"}
                          >
                            <Link
                              href="/agricola/monitoramento"
                              className="flex items-center gap-2 w-full"
                            >
                              <Bug className="h-3.5 w-3.5" />
                              Pragas & Doenças
                            </Link>
                          </SidebarMenuSubButton>
                        </SidebarMenuSubItem>
                      </ModuleGate>

                      {/* A4 - Agricultura de Precisão */}
                      <ModuleGate moduleId={Modulos.AGRICOLA_PRECISAO}>
                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton
                            isActive={pathname === "/agricola/ndvi"}
                          >
                            <Link
                              href="/agricola/ndvi"
                              className="flex items-center gap-2 w-full"
                            >
                              <Satellite className="h-3.5 w-3.5" />
                              🛰️ NDVI & Satélite
                            </Link>
                          </SidebarMenuSubButton>
                        </SidebarMenuSubItem>

                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton
                            isActive={pathname === "/agricola/prescricoes"}
                          >
                            <Link
                              href="/agricola/prescricoes"
                              className="flex items-center gap-2 w-full"
                            >
                              <Layers className="h-3.5 w-3.5" />
                              Mapas VRA
                            </Link>
                          </SidebarMenuSubButton>
                        </SidebarMenuSubItem>

                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton
                            isActive={pathname === "/agricola/analises_solo"}
                          >
                            <Link
                              href="/agricola/analises_solo"
                              className="flex items-center gap-2 w-full"
                            >
                              <Beaker className="h-3.5 w-3.5" />
                              Análises de Solo
                            </Link>
                          </SidebarMenuSubButton>
                        </SidebarMenuSubItem>
                      </ModuleGate>

                      {/* A5 - Colheita */}
                      <ModuleGate moduleId={Modulos.AGRICOLA_COLHEITA}>
                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton
                            isActive={pathname === "/agricola/colheita"}
                          >
                            <Link
                              href="/agricola/colheita"
                              className="flex items-center gap-2 w-full"
                            >
                              <Truck className="h-3.5 w-3.5" />
                              🚜 Colheita & Romaneio
                            </Link>
                          </SidebarMenuSubButton>
                        </SidebarMenuSubItem>
                      </ModuleGate>

                      {/* Itens comuns (aparecem se tiver QUALQUER módulo agrícola) */}
                      <SidebarMenuSubItem>
                        <SidebarMenuSubButton
                          isActive={pathname === "/agricola/mapa"}
                        >
                          <Link
                            href="/agricola/mapa"
                            className="flex items-center gap-2 w-full"
                          >
                            <MapPin className="h-3.5 w-3.5" />
                            Meus Talhões
                          </Link>
                        </SidebarMenuSubButton>
                      </SidebarMenuSubItem>

                      <SidebarMenuSubItem>
                        <SidebarMenuSubButton
                          isActive={pathname === "/agricola/climatico"}
                        >
                          <Link
                            href="/agricola/climatico"
                            className="flex items-center gap-2 w-full"
                          >
                            <CloudSun className="h-3.5 w-3.5" />
                            Clima & Previsão
                          </Link>
                        </SidebarMenuSubButton>
                      </SidebarMenuSubItem>
                    </SidebarMenuSub>
                  </CollapsibleContent>
                </Collapsible>
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        )}

        {/* BLOCO PECUÁRIA */}
        {hasPecuariaModules && (
          <SidebarGroup>
            <SidebarGroupLabel>Pecuária</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                <Collapsible>
                  <CollapsibleTrigger>
                    <SidebarMenuButton>
                      <Beef className="h-4 w-4" />
                      <span>Pecuária</span>
                      <ChevronRight className="ml-auto" />
                    </SidebarMenuButton>
                  </CollapsibleTrigger>

                  <CollapsibleContent>
                    <SidebarMenuSub>
                      {/* P1 - Controle de Rebanho */}
                      <ModuleGate moduleId={Modulos.PECUARIA_REBANHO}>
                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton
                            isActive={pathname === "/pecuaria/lotes"}
                          >
                            <Link
                              href="/pecuaria/lotes"
                              className="flex items-center gap-2 w-full"
                            >
                              <Beef className="h-3.5 w-3.5" />
                              🐄 Controle de Lotes
                            </Link>
                          </SidebarMenuSubButton>
                        </SidebarMenuSubItem>

                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton
                            isActive={pathname === "/pecuaria/piquetes"}
                          >
                            <Link
                              href="/pecuaria/piquetes"
                              className="flex items-center gap-2 w-full"
                            >
                              <MapPin className="h-3.5 w-3.5" />
                              Piquetes e Pastos
                            </Link>
                          </SidebarMenuSubButton>
                        </SidebarMenuSubItem>

                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton
                            isActive={pathname === "/pecuaria/manejo"}
                          >
                            <Link
                              href="/pecuaria/manejo"
                              className="flex items-center gap-2 w-full"
                            >
                              <Syringe className="h-3.5 w-3.5" />
                              Manejo e Sanidade
                            </Link>
                          </SidebarMenuSubButton>
                        </SidebarMenuSubItem>
                      </ModuleGate>

                      {/* P2 - Genética */}
                      <ModuleGate moduleId={Modulos.PECUARIA_GENETICA}>
                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton
                            isActive={pathname === "/pecuaria/genetica"}
                          >
                            <Link
                              href="/pecuaria/genetica"
                              className="flex items-center gap-2 w-full"
                            >
                              <Dna className="h-3.5 w-3.5" />
                              🧬 Genética & Reprodução
                            </Link>
                          </SidebarMenuSubButton>
                        </SidebarMenuSubItem>

                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton
                            isActive={pathname === "/pecuaria/iatf"}
                          >
                            <Link
                              href="/pecuaria/iatf"
                              className="flex items-center gap-2 w-full"
                            >
                              <Syringe className="h-3.5 w-3.5" />
                              IATF e Diagnósticos
                            </Link>
                          </SidebarMenuSubButton>
                        </SidebarMenuSubItem>
                      </ModuleGate>

                      {/* P3 - Confinamento */}
                      <ModuleGate moduleId={Modulos.PECUARIA_CONFINAMENTO}>
                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton
                            isActive={pathname === "/pecuaria/confinamento"}
                          >
                            <Link
                              href="/pecuaria/confinamento"
                              className="flex items-center gap-2 w-full"
                            >
                              <Factory className="h-3.5 w-3.5" />
                              🏭 Feedlot Control
                            </Link>
                          </SidebarMenuSubButton>
                        </SidebarMenuSubItem>

                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton
                            isActive={pathname === "/pecuaria/racao"}
                          >
                            <Link
                              href="/pecuaria/racao"
                              className="flex items-center gap-2 w-full"
                            >
                              <Wheat className="h-3.5 w-3.5" />
                              Fábrica de Ração
                            </Link>
                          </SidebarMenuSubButton>
                        </SidebarMenuSubItem>
                      </ModuleGate>

                      {/* P4 - Leite */}
                      <ModuleGate moduleId={Modulos.PECUARIA_LEITE}>
                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton
                            isActive={pathname === "/pecuaria/leite"}
                          >
                            <Link
                              href="/pecuaria/leite"
                              className="flex items-center gap-2 w-full"
                            >
                              <Milk className="h-3.5 w-3.5" />
                              🥛 Controle Leiteiro
                            </Link>
                          </SidebarMenuSubButton>
                        </SidebarMenuSubItem>
                      </ModuleGate>
                    </SidebarMenuSub>
                  </CollapsibleContent>
                </Collapsible>
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        )}

        {/* BLOCOS FINANCEIRO, OPERACIONAL, etc... seguem o mesmo padrão */}
      </SidebarContent>
    </Sidebar>
  );
}

/**
 * OBSERVAÇÕES IMPORTANTES:
 *
 * 1. SEMPRE use Modulos.XXX ao invés de strings hardcoded
 * 2. Use ModuleGate para proteger menu items
 * 3. Use useHasAnyModule para verificar se mostra o grupo inteiro
 * 4. Itens comuns (Mapa, Clima) aparecem se tiver QUALQUER módulo do grupo
 * 5. Adicione emojis/ícones para identificação visual rápida
 * 6. Mantenha hierarquia: Grupo > Módulo > Funcionalidades
 */
