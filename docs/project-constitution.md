# Project Constitution — TradingLab

## Que es este proyecto
Sistema de desarrollo de estrategias de trading
algoritmico orientado a superar evaluaciones y
operar cuentas de prop firms (fondeo).

Usamos StrategyQuant para generar y validar
estrategias, y Claude Code con agentes especializados
para organizar, filtrar y documentar el proceso.

---

## Quienes somos
Traders en formacion. No somos programadores
profesionales ni traders institucionales.
El sistema esta disenado para ser operado
por personas sin experiencia tecnica avanzada.

---

## Objetivo principal
Tener un pipeline repetible que produzca
estrategias algoritmicas robustas, compatibles
con FTMO 2-Step, y documentadas correctamente.

No el objetivo: tener muchas estrategias.
Si el objetivo: tener pocas estrategias buenas
y un proceso solido para encontrarlas.

---

## Stack de herramientas

| Herramienta      | Rol en el proyecto                        |
|------------------|-------------------------------------------|
| StrategyQuant X  | Generar, testar y optimizar estrategias   |
| Claude Code      | Agentes, organizacion y documentacion     |
| Antigravity      | Editor de archivos del proyecto           |
| Obsidian         | Base de conocimiento y journal            |
| Git              | Control de versiones del proyecto         |
| Windows CMD      | Terminal para comandos y Claude Code      |

---

## Estructura del proyecto

C:\Users\ivano\trading-lab\
│
├── CLAUDE.md                → Constitucion para Claude Code
├── docs\                    → Reglas y workflows del sistema
│   ├── funding-rules.md     → Reglas FTMO 2-Step
│   ├── sq-workflow.md       → Pipeline completo de SQ
│   ├── decision-rules.md    → Criterios PASA/REVISAR/DESCARTAR
│   ├── project-constitution.md → Este archivo
│   ├── roadmap-v2.md        → Arquitectura de expansion
│   ├── project-status.md    → Estado actual del proyecto
│   └── skills\              → Conocimiento especializado
│
├── agents\                  → Instrucciones de los 4 agentes
│   ├── market-analyst.md
│   ├── funding-specialist.md
│   ├── sq-specialist.md
│   └── orchestrator.md
│
├── research\                → Ideas e hipotesis de estrategias
│   ├── market-notes\
│   └── strategy-hypotheses\
│
├── strategyquant\           → Configuraciones de SQ
│   ├── builder\
│   ├── retester\
│   ├── optimizer\
│   └── databanks\
│
├── results\                 → Outputs del pipeline
│   ├── raw\                 → Output directo del Builder
│   │   ├── build-results\
│   │   └── last-generation\
│   ├── reviewed\            → Pasan el Evaluation Gate
│   ├── approved\            → Estrategias validadas
│   └── rejected\            → Descartadas con documentacion
│
└── automation\              → Scripts y hooks (fase futura)
    ├── scripts\
    ├── hooks\
    └── mcp\

---

## Los 4 agentes del sistema

### market-analyst
Investiga mercados y genera hipotesis.
Escribe en research\
No aprueba estrategias.

### funding-specialist
Evalua compatibilidad con FTMO 2-Step.
Lee docs\funding-rules.md
No aprueba estrategias por su cuenta.

### sq-specialist
Convierte hipotesis en configuraciones de SQ.
Gestiona Builder, Retester y Optimizer.
No ejecuta SQ — lo hacemos nosotros.

### orchestrator
Decide que avanza y que se descarta.
Mantiene documentacion actualizada.
Sintetiza — no genera ideas.

---

## Mercados y temporalidades

Mercados activos:
- EUR/USD (Forex spot)
- XAU/USD (Oro spot)

Mercados pendientes de datos:
- GC (Gold Futures CME)
- NQ (Nasdaq Futures CME)

Temporalidad principal: H1
M15 descartado tras Builds 1-6 con comisiones reales.

---

## Foco actual vs futuro

### Foco actual
- Conseguir las primeras estrategias aprobadas
- Aprender el pipeline completo
- H1 como temporalidad principal
- EUR/USD y XAU/USD como mercados principales

### Futuro (no antes de 3+ estrategias aprobadas)
- Automatizacion con N8N
- Agentes adicionales
- Expansion a GC, NQ, GBP/USD
- Control remoto Discord/Telegram

---

## Reglas de comportamiento

1. Ningun agente aprueba estrategias solo.
   Siempre hay decision humana final.

2. Ningun build se lanza sin hipotesis previa
   documentada en research\strategy-hypotheses\

3. Comisiones reales FTMO obligatorias en todos
   los builds desde el principio.

4. Toda decision importante se documenta
   en results\ y en Obsidian.

5. El CLAUDE.md no se modifica sin consenso.

6. Si hay duda entre avanzar y revisar,
   siempre se revisa.

7. Los datos 2021-2026 son INTOCABLES hasta
   el Retester. Nunca usarlos en el Builder.

---

## Estado actual del proyecto

Fase completada:
- Instalacion de herramientas
- Estructura de carpetas creada
- Documentos base redactados
- 4 agentes creados
- 10 skills creadas

Fase en curso:
- Generar primera hipotesis con agentes
- Lanzar primer build con comisiones reales

Pendiente:
- Primera estrategia aprobada
- Retester y Optimizer
- Challenge FTMO

---

## Ultima actualizacion
Fecha: Abril 2026
Estado: Reconstruccion en nuevo dispositivo