# 🌱 context-cultivo-multiplas-culturas.md

## 🎯 Objetivo

Definir a modelagem e o fluxo correto para cenários onde um mesmo talhão possui múltiplos cultivos simultâneos, garantindo separação adequada de operações, cálculo preciso de custos por cultura, rastreabilidade de produção e suporte a cenários reais como consórcio, ILP e divisão de área.

## 🧠 Conceito Fundamental

Talhão representa o espaço físico. Cultivo representa a unidade de negócio.

Toda a lógica de operação, custo, produção e resultado deve estar centrada no cultivo, nunca no talhão.

## 🧱 Estrutura Base

Safra → Cultivo → Talhão (com área associada)

## 🌱 Cenário Real

Talhão 01 com 50 hectares na Safra 2025 pode conter dois cultivos simultâneos:

- Café ocupando 40 hectares  
- Milho ocupando 10 hectares  

Esses cultivos coexistem no mesmo talhão, porém devem ser tratados como entidades independentes dentro do sistema.

## ⚙️ Registro de Operações

Toda operação deve estar associada a um cultivo.

Operações específicas são registradas diretamente no cultivo correspondente:
- Plantio de milho → cultivo milho  
- Adubação de café → cultivo café  
- Poda de café → cultivo café  

Operações compartilhadas (que impactam todo o talhão) devem ser rateadas entre os cultivos.

Exemplo:
Aplicação de calcário no talhão inteiro.

Nesse caso:
- Café recebe 80%  
- Milho recebe 20%  

Para suportar isso, deve existir uma estrutura de rateio:

Operacao:
- id
- tipo
- data
- talhao_id

OperacaoRateio:
- operacao_id
- cultivo_id
- percentual
- area

## 💰 Cálculo de Custos

Todo custo deve ser atribuído ao cultivo, seja de forma direta ou via rateio.

Custos diretos:
- Semente de milho → 100% milho  
- Adubo de café → 100% café  

Custos compartilhados:
Exemplo de custo de R$ 10.000:
- Café → R$ 8.000  
- Milho → R$ 2.000  

Estrutura recomendada:

Custo:
- id
- safra_id
- valor_total
- tipo

CustoRateio:
- custo_id
- cultivo_id
- valor
- percentual

## 🌾 Colheita

A colheita deve ser sempre registrada por cultivo, nunca por talhão.

Exemplo:
- Milho: 600 sacas  
- Café: 300 sacas  

Modelagem:

Colheita:
- id
- cultivo_id
- data
- quantidade
- unidade

Regras importantes:
- produção nunca deve ser agregada por talhão  
- estoque deve ser separado por cultura  
- comercialização deve ser independente por cultivo  

## 🔄 Fluxo Completo do Processo

1. Criar a safra  
2. Criar os cultivos (ex: café e milho)  
3. Associar os cultivos ao talhão com suas respectivas áreas  
4. Registrar operações:
   - específicas diretamente no cultivo  
   - compartilhadas via rateio  
5. Registrar custos:
   - diretos no cultivo  
   - indiretos via rateio  
6. Registrar colheita por cultivo  
7. Apurar resultados por cultura:
   - custo total  
   - produção total  
   - rentabilidade  

## ⚠️ Erros Comuns

Misturar produção por talhão  
Atribuir custos diretamente ao talhão  
Duplicar operações para cada cultivo  
Ignorar rateio em operações compartilhadas  

## 🔥 Regra de Ouro

Tudo que gera valor ou custo pertence ao cultivo. O talhão é apenas o contexto físico.

## 🚀 Nível Avançado

Para aumentar precisão e reduzir dependência de rateios manuais, recomenda-se a subdivisão lógica do talhão em áreas de cultivo.

## 🌿 Subdivisão de Talhão

Criar subáreas dentro do talhão representando cada cultivo.

Modelagem:

CultivoArea:
- id
- cultivo_id
- talhao_id
- area (hectares)
- geometria (opcional)

Exemplo:

Talhão 01 com 50 hectares:
- CultivoArea 1 → Café com 40 hectares  
- CultivoArea 2 → Milho com 10 hectares  

## 🎯 Benefícios

Elimina necessidade de rateio manual em muitos casos  
Aumenta precisão dos dados  
Melhora rastreabilidade  
Permite análises espaciais  

## 🗺️ Georreferenciamento

A inclusão de geometria (polígono) permite:

- visualização em mapa  
- agricultura de precisão  
- aplicação localizada de insumos  

## ⚙️ Operações com Subárea

Operações podem ser vinculadas diretamente à área do cultivo:

Operacao:
- cultivo_area_id

Isso elimina a necessidade de rateio manual em diversas situações.

## 💰 Custos com Subárea

Custos também podem ser diretamente associados:

Custo:
- cultivo_area_id

## 🧠 Automação de Rateio

Quando não houver subdivisão de área, o sistema deve aplicar regras automáticas.

Regra padrão:
percentual = area_cultivo / area_total

Outras opções:
- rateio manual  
- rateio por intensidade de uso  
- rateio por tipo de operação  

## 🔮 Evoluções Futuras

Integração com satélite  
Sensores de campo  
Recomendação automática  
Inteligência de custo por cultura  

## 📌 Conclusão

Operações pertencem ao cultivo  
Custos pertencem ao cultivo  
Colheita pertence ao cultivo  
Talhão é apenas o contexto físico  
Rateio é utilizado quando necessário  

## 🧠 Insight Final

Cada cultura dentro de um talhão deve ser tratada como um negócio independente dentro do sistema.