# Roadmap V2 — Sistema Automatico TradingLab

## Objetivo final
Sistema 100% automatico multi-activo multi-prop firm
que genera, valida, despliega y monitorea portfolios
de estrategias de trading algoritmico sin intervencion
humana en las decisiones.

---

## ESTADO ACTUAL
- 11 agentes operativos
- 22 skills especializadas
- Builder libre sin sesgo humano
- Evaluation Gate 100% automatico
- correlation-analyst activo
- 30+ activos disponibles
- Pipeline de validacion completo

---

## CAPA 0 — Ahora (pipeline automatico multi-activo)

### Objetivo
Generar el primer portfolio de 3-5 estrategias
no correlacionadas en activos diferentes.

### Proceso
market-selector prioriza activos por scoring →
market-analyst configura Builder libre →
SQ genera candidatas 24-48h →
Evaluation Gate automatico →
Retester → paso 12b automatico →
WFO → dictamen automatico →
correlation-analyst construye portfolio →
export-specialist → forward test demo (unico humano)

### Mercados disponibles
30+ activos priorizados por scoring numerico:
Forex Majors, Forex Crosses, Metales, Indices, Cripto
El market-selector decide el orden — no el humano.

### Prop firms objetivo
- FTMO: Forex + Metales + Indices + Cripto
- E8: Forex + Metales + Indices
- TFT: Forex + Metales + Indices
- Apex: Futuros CME (cuando haya datos)
- MFF: Futuros CME (cuando haya datos)

El propfirm-analyst decide automaticamente
cual es la optima para cada estrategia y activo.

### Criterio de salida de Capa 0
Portfolio de 3 estrategias no correlacionadas
operando en cuentas de prop firms.

---

## CAPA 1 — Expansion (tras portfolio de 3 estrategias)

### Nuevos agentes

#### risk-manager
Gestion de riesgo de portfolio en tiempo real.
Calcula exposicion total considerando todas
las estrategias y cuentas activas.
Archivo: agents\risk-manager.md

#### news-researcher
Contexto macro automatico.
Identifica periodos anomalos en los datos.
Ajusta el riesgo del portfolio en eventos macro.
Archivo: agents\news-researcher.md

### Expansion de mercados
Descargar datos de todos los activos pendientes
priorizados por el market-selector.
Lanzar ciclos de Builder libre para cada activo.

### Expansion de portfolio
- Ampliar de 3 a 5 estrategias activas
- Maximizar diversificacion entre activos y estilos
- Reducir riesgo por estrategia segun tamaño

### Skills nuevas Capa 1
- skill-risk-realtime.md
- skill-news-impact.md
- skill-multi-account.md

---

## CAPA 2 — Ciclos autonomos (tras 5+ estrategias)

### Objetivo
El sistema lanza ciclos de Builder, evalua y
despliega estrategias sin que el humano tenga
que iniciar cada paso manualmente.

### Tecnologia
N8N como plataforma de automatizacion:
- Instalacion local o servidor
- Conexion con Claude API (requiere API Key)
- Conexion con SQ Remote Control API
- Conexion con Telegram/Discord para alertas
- Conexion con Google Sheets para reporting

### Flujo automatizado Capa 2

N8N detecta que el portfolio necesita mas estrategias
        ↓
N8N llama a Claude API → market-selector
        ↓
Prioriza siguiente activo por scoring
        ↓
N8N llama a Claude API → market-analyst
        ↓
Configura Builder libre para ese activo
        ↓
N8N lanza SQ Builder via Remote Control
        ↓
Builder corre 48 horas automaticamente
        ↓
N8N para el Builder y lee resultados
        ↓
N8N llama a Claude API → orchestrator
        ↓
Evaluation Gate automatico
        ↓
N8N lanza Retester via Remote Control
        ↓
Paso 12b automatico
        ↓
N8N lanza WFO via Remote Control
        ↓
Dictamen WFO automatico
        ↓
correlation-analyst decide inclusion en portfolio
        ↓
Si incluida → N8N notifica por Telegram:
"Nueva estrategia aprobada para [activo].
Activar forward test en demo."
        ↓
Humano hace forward test (unica intervencion)
        ↓
Humano confirma → N8N despliega EA en MT5

### Intervencion humana en Capa 2
- Forward test en demo (2 semanas)
- Comprar challenge en prop firm
- Revision semanal del sistema
- Ajustar umbrales si necesario

### Requisitos tecnicos
- API Key de Anthropic
- N8N instalado
- SQ Remote Control activado
- Telegram o Discord
- Costo estimado: 0.10-0.50$ por ciclo completo

---

## CAPA 3 — Automatizacion total (sistema maduro)

### Objetivo
Todo automatico excepto la compra del challenge
y el forward test en demo.

### Componentes

#### SQ Remote Control completo
N8N controla SQ directamente:
- Lanza builds para multiples activos en paralelo
- Lee resultados automaticamente
- Ejecuta Retester y WFO sin intervencion
- Aplica pipeline completo sin humano

#### MT5 EA Deployment automatico
- Estrategias aprobadas se exportan automaticamente
- EA se activa en cuenta demo automaticamente
- Tras 2 semanas exitosas notifica al humano
- Humano solo compra challenge y confirma

#### Multi-prop firm management
- Portfolio distribuido en multiples prop firms
- EUR/USD en FTMO + E8
- XAU/USD en FTMO
- NAS100 en FTMO + TFT
- Futuros en Apex + MFF
- Reporting consolidado automatico

#### Reemplazo automatico de estrategias
- performance-monitor detecta deterioro
- correlation-analyst busca reemplazo en cola
- Si no hay reemplazo → lanza nuevo ciclo Builder
- Todo sin intervencion humana

### Intervencion humana en Capa 3
- Comprar challenge en prop firm
- Revision semanal del sistema
- Ajustar umbrales si necesario

---

## CAPA 4 — Escalado (vision largo plazo)

### Objetivo
Escalar el sistema a maxima capacidad.

### Componentes
- Portfolio de 8+ estrategias activas
- 3+ prop firms operando simultaneamente
- Cuentas en multiples tamaños (10k, 25k, 50k, 100k)
- Rebalanceo automatico mensual
- Expansion continua a nuevos activos
- Risk manager en tiempo real
- Reporting automatico diario por Telegram

---

## ORDEN DE IMPLEMENTACION

AHORA (Capa 0):
→ Descargar datos de activos prioritarios
→ Lanzar Builder libre multi-activo
→ Pipeline automatico completo
→ Primer portfolio de 3 estrategias

CAPA 1 (tras portfolio de 3):
→ risk-manager y news-researcher
→ Expansion a 5 estrategias
→ Todos los activos descargados

CAPA 2 (tras 5 estrategias):
→ N8N instalado
→ API Key Anthropic
→ SQ Remote Control
→ Ciclos autonomos

CAPA 3 (sistema estable):
→ MT5 deployment automatico
→ Multi-prop firm
→ Reemplazo automatico

CAPA 4 (escalado):
→ 8+ estrategias
→ 3+ prop firms
→ Cuentas grandes

---

## REGLA FUNDAMENTAL

Nunca expandir antes de estabilizar la capa anterior.
Automatizar sin estrategias validadas = automatizar perdidas.
Pero ahora las estrategias las encuentra SQ libremente
y los numeros deciden — no el humano.