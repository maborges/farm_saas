---
modulo: Frota e Máquinas
submodulo: Telemetria
nivel: enterprise
core: false
dependencias_core: [Identidade e Acesso, Cadastro da Propriedade]
dependencias_modulos: [../essencial/cadastro-equipamentos.md, ../profissional/custo-hora-maquina.md]
standalone: false
complexidade: XL
assinante_alvo: [grande produtor, cooperativa, empresa agricola]
---

# Telemetria

## Descricao Funcional

Monitoramento em tempo real da frota via dispositivos GPS/telemetria instalados nos equipamentos. Rastreia posicao, velocidade, horas trabalhadas, horas ociosas, rotas percorridas e geofencing (cercas virtuais). Fornece dados automaticos de horimetro, eliminando registro manual e permitindo analise precisa de produtividade e uso da frota.

## Personas

- **Gestor de frota:** monitora frota em tempo real, analisa produtividade
- **Gestor agricola:** verifica se operacoes estao ocorrendo nos talhoes corretos
- **Seguranca:** monitora velocidade e uso fora do horario permitido
- **Proprietario:** visao executiva de utilizacao e ociosidade da frota

## Dores que resolve

- Desconhecimento de onde as maquinas estao em tempo real
- Impossibilidade de medir horas efetivas de trabalho vs. ociosidade
- Uso nao autorizado de equipamentos fora do horario ou area permitida
- Registro manual de horimetro impreciso e sujeito a fraude
- Falta de dados para otimizar rotas e alocacao de maquinas

## Regras de Negocio

1. Cada equipamento com telemetria deve ter um dispositivo vinculado (ID unico)
2. Dados recebidos via API de integracao com provedor de telemetria (MQTT/REST)
3. Posicao atualizada a cada 30 segundos (configuravel)
4. Estados do equipamento inferidos: `TRABALHANDO` (movendo + RPM alto), `OCIOSO` (parado + motor ligado), `DESLOCAMENTO` (movendo + RPM baixo), `DESLIGADO`
5. Geofencing: alertas quando equipamento entra/sai de area definida
6. Horimetro automatico: acumulado de horas com motor ligado, sincronizado com cadastro
7. Velocidade maxima configuravel por tipo de equipamento — alerta ao exceder
8. Horario de operacao permitido configuravel — alerta fora do horario
9. Dados historicos armazenados por no minimo 12 meses
10. Tolerancia de 5 minutos sem sinal antes de considerar dispositivo offline

## Entidades de Dados Principais

- **DispositivoTelemetria:** id, tenant_id, equipamento_id, numero_serie_dispositivo, provedor, modelo, status (ATIVO/INATIVO), data_instalacao
- **PosicaoTelemetria:** id, dispositivo_id, timestamp, latitude, longitude, velocidade_km_h, rpm, estado_equipamento, horimetro_acumulado
- **Geofence:** id, tenant_id, nome, tipo (TALHAO/SEDE/ZONA_RESTRITA), poligono_geojson, ativo
- **AlertaTelemetria:** id, tenant_id, dispositivo_id, tipo (GEOFENCE/VELOCIDADE/HORARIO/OFFLINE), timestamp, detalhes, lido
- **ResumoOperacaoDiaria:** id, dispositivo_id, data, horas_trabalhando, horas_ocioso, horas_deslocamento, km_percorridos, area_coberta_ha

## Integracoes Necessarias

- **Provedor de telemetria:** API MQTT/REST para recebimento de dados (ex: Trimble, Enalta, FieldView)
- **Cadastro de Equipamentos:** vinculo dispositivo-equipamento, sincronizacao de horimetro
- **Custo/Hora Maquina:** horas trabalhadas automaticas para calculo de custo
- **Agricola (Talhoes):** geofences baseadas nos talhoes cadastrados
- **Agricola (Operacoes):** vincular horas/area trabalhada automaticamente a operacoes

## Fluxo de Uso Principal

1. Tecnico instala dispositivo de telemetria no equipamento
2. Gestor vincula dispositivo ao equipamento no sistema
3. Configura geofences (talhoes, sede, zonas restritas)
4. Configura regras de alerta (velocidade, horario)
5. Mapa em tempo real exibe posicao de todos os equipamentos
6. Sistema coleta dados continuamente e classifica estados
7. Ao final do dia, gera resumo operacional por equipamento
8. Alertas sao exibidos em tempo real e armazenados no historico

## Casos Extremos e Excecoes

- Dispositivo sem sinal GPS (area com cobertura ruim): armazenar localmente no dispositivo e enviar ao reconectar
- Dispositivo offline por mais de 24h: gerar alerta critico de dispositivo
- Equipamento operando fora de qualquer geofence: classificar como "area nao mapeada"
- Dois dispositivos vinculados ao mesmo equipamento: aceitar apenas um ativo por vez
- Volume de dados massivo (frota grande): particionamento de tabela por mes, retencao configuravel
- Provedor de telemetria troca API: camada de abstracao para multiplos provedores
- Horimetro do dispositivo diverge do horimetro manual: priorizar telemetria, registrar divergencia

## Criterios de Aceite

- [ ] Vinculo dispositivo-equipamento com CRUD
- [ ] Recepcao de dados via API REST com autenticacao
- [ ] Mapa em tempo real com posicao dos equipamentos
- [ ] Classificacao automatica de estados (trabalhando/ocioso/deslocamento/desligado)
- [ ] Geofencing com alertas de entrada/saida
- [ ] Resumo operacional diario por equipamento
- [ ] Horimetro automatico sincronizado com cadastro
- [ ] Alertas de velocidade, horario e dispositivo offline
- [ ] Historico de posicoes consultavel por periodo
- [ ] Isolamento por tenant

## Sugestoes de Melhoria Futura

- Heatmap de atividade por talhao
- Replay de rota percorrida no mapa (animacao)
- Calculo automatico de area coberta (ha/dia)
- Integracao com CAN Bus para dados de motor (consumo, temperatura)
- Machine learning para deteccao de padroes de uso anomalo
