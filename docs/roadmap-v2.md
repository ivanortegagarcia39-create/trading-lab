# Roadmap V2 — Vision Completa TradingLab

## Objetivo final
Automatizacion total del pipeline de trading algoritmico:
desde el analisis de mercados hasta la operacion autonoma
en cuentas de fondeo de multiples prop firms.

---

## ESTADO ACTUAL
- 6 agentes operativos
- 11 skills especializadas
- Pipeline manual funcionando
- Objetivo inmediato: 3 estrategias aprobadas

---

## CAPA 0 — Ahora (pipeline manual)

### Objetivo
Conseguir las primeras estrategias aprobadas
con el pipeline manual actual.

### Proceso
market-selector → market-analyst → propfirm-analyst
→ funding-specialist → sq-specialist → Builder
→ Evaluation Gate → Retester → Optimizer
→ Aprobacion final

### Mercados activos
- EUR/USD H1
- XAU/USD H1

### Prop firms objetivo
- FTMO 2-Step como principal
- E8 y TFT como alternativas Forex

### Criterio de salida de Capa 0
3 estrategias aprobadas con PF >= 1.5 OOS

---

## CAPA 1 — Expansion (tras 3 estrategias aprobadas)

### Nuevos agentes

#### technical-analyst
Analisis tecnico avanzado — patrones, soportes,
resistencias, zonas de valor.
Archivo: agents\technical-analyst.md

#### correlation-analyst
Correlaciones entre activos del portfolio.
Evita estrategias correlacionadas.
Archivo: agents\correlation-analyst.md

#### risk-manager
Gestion de riesgo de portfolio completo.
Verifica exposicion total antes de aprobar.
Archivo: agents\risk-manager.md

#### news-researcher
Contexto macro y noticias.
Identifica periodos anomalos en datos historicos.
Archivo: agents\news-researcher.md

### Expansion de mercados
- GBP/USD (datos disponibles en Dukascopy)
- USD/JPY (datos disponibles en Dukascopy)
- NQ cuando tengamos datos de futuros CME
- GC cuando tengamos datos de futuros CME

### Expansion de prop firms
Analizar y documentar en skill-propfirms-comparison.md:
- MyFundedFutures para futuros NQ y GC
- Apex Trader Funding para maxima flexibilidad EAs
- TopStep para futuros CME

### Skills nuevas Capa 1
- skill-parallel-hypotheses.md
- skill-portfolio-correlation.md
- skill-pipeline-errors.md
- skill-sq-export-mt5.md

---

## CAPA 2 — Orquestador autonomo (tras 5+ estrategias)

### Objetivo
El orquestador deja de ser reactivo y pasa a ser
completamente autonomo — decide y ejecuta sin
que el usuario tenga que escribir prompts.

### Tecnologia
N8N como plataforma de automatizacion central:
- Instalacion local en Windows
- Interfaz visual para workflows
- Conexion con API de Anthropic (requiere API Key)
- Conexion con SQ Remote Control API
- Conexion con Telegram/Discord para notificaciones
- Conexion con Google Sheets para reporting

### Flujo automatizado Capa 2

Usuario envia mensaje en Telegram:
"Genera una hipotesis para GBP/USD"
        ↓
N8N recibe el mensaje
        ↓
N8N llama a Claude API con prompt de market-selector
        ↓
Claude analiza mercados y selecciona activo
        ↓
N8N llama a Claude API con prompt de market-analyst
        ↓
Claude genera hipotesis
        ↓
N8N llama a Claude API con prompt de propfirm-analyst
        ↓
Claude recomienda prop firm optima
        ↓
N8N llama a Claude API con prompt de funding-specialist
        ↓
Claude valida compatibilidad
        ↓
N8N llama a Claude API con prompt de sq-specialist
        ↓
Claude genera configuracion del Builder
        ↓
N8N notifica al usuario via Telegram:
"Configuracion lista para GBP/USD — lanza el build"
        ↓
Usuario lanza el build en SQ manualmente
        ↓
Cuando termina el build, usuario notifica a N8N
        ↓
N8N invoca orchestrator para Evaluation Gate
        ↓
... continua el pipeline automaticamente

### Decisiones que SIEMPRE requieren humano
- Evaluation Gate — decision final
- Aprobacion final de estrategia
- Lanzar builds en SQ (hasta tener SQ Remote Control)
- Intentar un challenge en prop firm

### Requisitos tecnicos Capa 2
- API Key de Anthropic (no plan Pro)
- N8N instalado localmente o en servidor
- SQ Remote Control activado
- Cuenta de Telegram o Discord
- Costo estimado por ciclo: 0.10-0.30$ en API

---

## CAPA 3 — Automatizacion total (sistema maduro)

### Objetivo
Automatizacion completa de principio a fin:
desde el analisis de mercados hasta la operacion
autonoma en cuentas de fondeo.

### Componentes

#### SQ Remote Control
- N8N controla SQ directamente via API REST
- Lanza builds automaticamente
- Lee resultados sin intervencion humana
- Aplica Evaluation Gate automaticamente

#### MT5 EA Deployment
- Estrategias aprobadas se exportan de SQ a MT5
- EA opera autonomamente en cuenta de fondeo
- N8N monitorea rendimiento en tiempo real
- Alertas automaticas si DD se acerca a limites

#### Multi-prop firm management
- Sistema gestiona multiples cuentas en paralelo
- EUR/USD en FTMO
- NQ en Apex o MFF
- GC en MFF
- Reporting consolidado en Google Sheets

#### Decision autonoma de challenges
- Sistema analiza cuando una estrategia esta lista
- Recomienda prop firm y tamaño de cuenta
- Notifica al usuario para decision final de compra
- El usuario solo aprueba o rechaza el challenge

### Flujo completamente automatizado Capa 3

N8N detecta que hay slots disponibles para nuevas estrategias
        ↓
Lanza ciclo completo automaticamente:
market-selector → hipotesis → validacion →
configuracion → build en SQ → evaluation →
retester → optimizer → aprobacion
        ↓
Si estrategia aprobada → exportar EA a MT5
        ↓
EA opera autonomamente en cuenta de fondeo
        ↓
N8N monitorea DD y rendimiento 24/5
        ↓
Si DD se acerca al limite → alerta a usuario
        ↓
Reporting diario automatico via Telegram

### Decisiones que siempre requieren humano en Capa 3
- Comprar challenge en prop firm
- Aprobar estrategia para produccion
- Responder alertas criticas de DD
- Cambios en reglas de prop firms

---

## CAPA 4 — Escalado (vision a largo plazo)

### Objetivo
Escalar el sistema a multiples prop firms,
multiples activos y multiples traders.

### Componentes
- Portfolio de 10+ estrategias aprobadas
- 3+ prop firms activas simultaneamente
- Cuentas en multiples tamaños (10k, 25k, 50k, 100k)
- Sistema de correlacion de portfolio automatico
- Risk manager de portfolio en tiempo real

---

## ORDEN DE IMPLEMENTACION GLOBAL

AHORA (Capa 0):
→ Primer build H1 con comisiones reales
→ Evaluation Gate y Retester
→ 3 estrategias aprobadas

CAPA 1 (tras 3 estrategias):
→ 4 agentes nuevos
→ GBP/USD y USD/JPY
→ Skills adicionales

CAPA 2 (tras 5+ estrategias):
→ N8N instalado y configurado
→ API Key de Anthropic activada
→ Orquestador semi-autonomo

CAPA 3 (tras sistema estable):
→ SQ Remote Control
→ MT5 EA deployment
→ Multi-prop firm management

CAPA 4 (vision largo plazo):
→ Portfolio completo
→ Escalado a multiples cuentas

---

## REGLA FUNDAMENTAL QUE NO CAMBIA

Nunca expandir antes de tener el proceso anterior estable.
La automatizacion sin estrategias validadas = automatizar perdidas.
Primero estrategias robustas, luego automatizacion.