# Seed de Homologação — Templates Agrícolas Realistas

```json
{
"cultures":[

{
"id":"CULT_CAFE",
"name":"Café",
"cycle":"PERENE"
},

{
"id":"CULT_FEIJAO",
"name":"Feijão",
"cycle":"ANUAL"
},

{
"id":"CULT_PIMENTA",
"name":"Pimenta do Reino",
"cycle":"PERENE"
},

{
"id":"CULT_CACAU",
"name":"Cacau",
"cycle":"PERENE"
}

],

"phase_templates":[

{

"id":"TPL_PLAN_CAFE",
"culture_id":"CULT_CAFE",
"phase":"PLANEJAMENTO",

"checklist":[

{"description":"Cultivo definido","required":true},
{"description":"Talhões vinculados","required":true},
{"description":"Área validada","required":true},
{"description":"Tipo de solo cadastrado","required":true},
{"description":"Irrigação avaliada","required":false},
{"description":"Análise de solo revisada","required":true},
{"description":"Necessidade de calagem avaliada","required":true},
{"description":"Necessidade de gessagem avaliada","required":false},
{"description":"Plano nutricional preliminar definido","required":true},
{"description":"Planejamento de insumos definido","required":true},
{"description":"Orçamento inicial validado","required":true},
{"description":"Cronograma preliminar definido","required":true}

],

"tasks":[

{"name":"Revisar calagem","criticality":"CRITICA"},
{"name":"Revisar gessagem","criticality":"NORMAL"},
{"name":"Planejar adubação inicial","criticality":"CRITICA"},
{"name":"Planejar irrigação","criticality":"NORMAL"},
{"name":"Validar disponibilidade de máquinas","criticality":"NORMAL"},
{"name":"Programar equipe operacional","criticality":"NORMAL"},
{"name":"Validar cronograma","criticality":"CRITICA"}

]

},

{

"id":"TPL_DEV_CAFE",
"phase":"DESENVOLVIMENTO",
"culture_id":"CULT_CAFE",

"tasks":[

{"name":"Monitorar ferrugem","criticality":"CRITICA"},
{"name":"Monitorar bicho mineiro","criticality":"CRITICA"},
{"name":"Aplicar adubação cobertura","criticality":"CRITICA"},
{"name":"Avaliar déficit hídrico","criticality":"CRITICA"},
{"name":"Revisar NDVI","criticality":"NORMAL"},
{"name":"Revisar necessidade de reanálise de solo","criticality":"NORMAL"}

]

},

{

"id":"TPL_PLAN_FEIJAO",
"phase":"PLANEJAMENTO",
"culture_id":"CULT_FEIJAO",

"checklist":[

{"description":"Cultivar definida","required":true},
{"description":"Sementes planejadas","required":true},
{"description":"Análise de solo revisada","required":true},
{"description":"Plano de inoculação definido","required":true},
{"description":"Adubação planejada","required":true},
{"description":"Orçamento definido","required":true}

],

"tasks":[

{"name":"Planejar inoculação","criticality":"CRITICA"},
{"name":"Planejar adubação base","criticality":"CRITICA"},
{"name":"Planejar fungicidas","criticality":"NORMAL"},
{"name":"Validar cronograma","criticality":"CRITICA"}

]

},

{

"id":"TPL_PLAN_PIMENTA",
"phase":"PLANEJAMENTO",
"culture_id":"CULT_PIMENTA",

"checklist":[

{"description":"Tutoramento avaliado","required":true},
{"description":"Irrigação validada","required":true},
{"description":"Análise de solo revisada","required":true},
{"description":"Plano nutricional definido","required":true}

],

"tasks":[

{"name":"Planejar tutoramento","criticality":"CRITICA"},
{"name":"Planejar irrigação","criticality":"CRITICA"},
{"name":"Planejar controle fitossanitário","criticality":"CRITICA"}

]

},

{

"id":"TPL_PLAN_CACAU",
"phase":"PLANEJAMENTO",
"culture_id":"CULT_CACAU",

"checklist":[

{"description":"Sombreamento avaliado","required":true},
{"description":"Análise de solo revisada","required":true},
{"description":"Plano nutricional definido","required":true},
{"description":"Orçamento validado","required":true}

],

"tasks":[

{"name":"Planejar manejo de sombra","criticality":"CRITICA"},
{"name":"Planejar adubação","criticality":"CRITICA"},
{"name":"Planejar controle de vassoura de bruxa","criticality":"CRITICA"}

]

}

],

"operation_templates":[

{

"id":"OP_PREP_CAFE",
"phase":"PREPARO_SOLO",
"culture_id":"CULT_CAFE",

"operations":[

{
"name":"Aplicação de Calcário",
"critical_operation":true,
"estimated_cost_default":1250,
"depends_on":[]
},

{
"name":"Aplicação de Gesso",
"critical_operation":false,
"estimated_cost_default":950,
"depends_on":["Aplicação de Calcário"]
},

{
"name":"Subsolagem",
"critical_operation":true,
"estimated_cost_default":1100,
"depends_on":[]
},

{
"name":"Gradagem",
"critical_operation":true,
"estimated_cost_default":850,
"depends_on":["Subsolagem"]
},

{
"name":"Incorporação de corretivos",
"critical_operation":true,
"estimated_cost_default":650,
"depends_on":["Aplicação de Calcário","Gradagem"]
}

]

},

{

"id":"OP_PLANTIO_CAFE",
"phase":"PLANTIO",
"culture_id":"CULT_CAFE",

"operations":[

{
"name":"Marcação de covas",
"critical_operation":true
},

{
"name":"Abertura de covas",
"critical_operation":true
},

{
"name":"Plantio de mudas",
"critical_operation":true
},

{
"name":"Adubação inicial",
"critical_operation":true
}

]

},

{

"id":"OP_DEV_CAFE",
"phase":"DESENVOLVIMENTO",
"culture_id":"CULT_CAFE",

"operations":[

{
"name":"Adubação cobertura",
"critical_operation":true
},

{
"name":"Pulverização ferrugem",
"critical_operation":true
},

{
"name":"Pulverização bicho mineiro",
"critical_operation":true
},

{
"name":"Manejo irrigação",
"critical_operation":false
}

]

},

{

"id":"OP_COL_CAFE",
"phase":"COLHEITA",
"culture_id":"CULT_CAFE",

"operations":[

{
"name":"Derriça",
"critical_operation":true
},

{
"name":"Transporte interno",
"critical_operation":true
},

{
"name":"Romaneio colheita",
"critical_operation":true
}

]

},

{

"id":"OP_PREP_FEIJAO",
"phase":"PREPARO_SOLO",
"culture_id":"CULT_FEIJAO",

"operations":[

{
"name":"Calagem",
"critical_operation":true
},

{
"name":"Gradagem",
"critical_operation":true
},

{
"name":"Nivelamento",
"critical_operation":true
}

]

},

{

"id":"OP_PLANTIO_FEIJAO",
"phase":"PLANTIO",
"culture_id":"CULT_FEIJAO",

"operations":[

{
"name":"Tratamento sementes",
"critical_operation":true
},

{
"name":"Inoculação",
"critical_operation":true
},

{
"name":"Semeadura",
"critical_operation":true
}

]

},

{

"id":"OP_DEV_FEIJAO",
"phase":"DESENVOLVIMENTO",
"culture_id":"CULT_FEIJAO",

"operations":[

{
"name":"Cobertura nitrogenada",
"critical_operation":true
},

{
"name":"Controle antracnose",
"critical_operation":true
},

{
"name":"Controle ferrugem",
"critical_operation":true
}

]

},

{

"id":"OP_PREP_PIMENTA",
"phase":"PREPARO_SOLO",
"culture_id":"CULT_PIMENTA",

"operations":[

{
"name":"Correção de solo",
"critical_operation":true
},

{
"name":"Instalação tutoramento",
"critical_operation":true
},

{
"name":"Preparação covas",
"critical_operation":true
}

]

},

{

"id":"OP_DEV_PIMENTA",
"phase":"DESENVOLVIMENTO",
"culture_id":"CULT_PIMENTA",

"operations":[

{
"name":"Manejo irrigação",
"critical_operation":true
},

{
"name":"Controle fusariose",
"critical_operation":true
},

{
"name":"Adubação cobertura",
"critical_operation":true
}

]

},

{

"id":"OP_PREP_CACAU",
"phase":"PREPARO_SOLO",
"culture_id":"CULT_CACAU",

"operations":[

{
"name":"Calagem",
"critical_operation":true
},

{
"name":"Correção orgânica",
"critical_operation":false
}

]

},

{

"id":"OP_DEV_CACAU",
"phase":"DESENVOLVIMENTO",
"culture_id":"CULT_CACAU",

"operations":[

{
"name":"Controle vassoura de bruxa",
"critical_operation":true
},

{
"name":"Poda sanitária",
"critical_operation":true
},

{
"name":"Adubação cobertura",
"critical_operation":true
}

]

}

],

"phenology_events":[

{
"culture":"Café",
"events":[
"Florada",
"Chumbinho",
"Granação",
"Maturação"
]
},

{
"culture":"Feijão",
"events":[
"Emergência",
"V3",
"Florescimento",
"Enchimento de grãos"
]
}

],

"monitoring_templates":[

{
"culture":"Café",
"occurrences":[
"Ferrugem",
"Bicho mineiro",
"Cercosporiose"
]
},

{
"culture":"Cacau",
"occurrences":[
"Vassoura de Bruxa",
"Podridão Parda"
]
}

]

}
```