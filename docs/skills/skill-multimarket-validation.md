# Skill: Validacion Multi-Mercado — Robustez Cross-Asset

## Proposito
Verificar que una estrategia aprobada por WFO captura
un patron real del mercado y no es especifica de un
solo activo o un artefacto de los datos de ese activo.
Si el patron es real, deberia funcionar (no necesariamente
bien, pero al menos no perder) en activos correlacionados.

---

## POSICION EN EL PIPELINE

```
WFO → [Multimarket Validation] → Portfolio Filter → Portfolio
```

Se ejecuta despues del WFO y antes de la seleccion de portfolio.
No es una puerta de descarte automatico — es una penalizacion
en el score del portfolio.

---

## MERCADOS DE VALIDACION POR ACTIVO PRINCIPAL

| Activo principal | Mercado validacion 1 | Mercado validacion 2 |
|-----------------|---------------------|---------------------|
| EURUSD | GBPUSD | AUDUSD |
| XAUUSD | XAGUSD | US500 |
| GBPUSD | EURUSD | AUDUSD |
| USDJPY | EURJPY | GBPJPY |
| AUDUSD | NZDUSD | EURUSD |
| EURJPY | GBPJPY | USDJPY |
| XAGUSD | XAUUSD | US500 |
| US500 | US30 | NAS100 |
| EURUSD (EUR crosses) | EURJPY | EURGBP |

La lista se actualiza cuando se añaden nuevos activos
al universo del proyecto. market-selector gestiona
los pares de correlacion.

---

## METODOLOGIA DE VALIDACION

### Que se hace
Ejecutar la estrategia con sus parametros exactos
(sin modificacion) en los mercados de validacion.
Mismo periodo OOS: 2021.01.01 a fecha actual.
Mismas comisiones del activo de validacion.

### Que se mide
Solo el Profit Factor del periodo OOS en cada mercado
de validacion.

### Criterio de validacion

**PASA validacion multi-mercado:**
PF > 1.0 en AL MENOS 1 de los 2 mercados correlacionados.
No necesita ser rentable — solo no perder dinero.
PF = 1.0 significa beneficio neto cero despues de comisiones.

**PENALIZACION (no descarte):**
PF < 1.0 en AMBOS mercados correlacionados.
Accion: penalizacion de -10 puntos en el score del portfolio.
La estrategia NO se descarta automaticamente.
Razon: puede ser que el activo principal tenga caracteristicas
unicas legitimas (volatilidad del oro vs forex, por ejemplo).

**Ejemplo score con penalizacion:**
  Score base de la estrategia: 72/100
  PF XAGUSD = 0.91 (< 1.0)
  PF US500 = 0.88 (< 1.0)
  Penalizacion: -10 puntos
  Score final: 62/100
  Resultado: la estrategia puede entrar al portfolio con
  score mas bajo, compitiendo en desventaja con las que
  validaron correctamente

---

## INTERPRETACION DE RESULTADOS

### PF > 1.0 en los dos mercados de validacion
- Señal fuerte: el patron existe en activos correlacionados
- El sistema captura algo real en los precios
- Confianza alta para el portfolio

### PF > 1.0 en uno, < 1.0 en el otro
- Señal mixta: el patron parcialmente generaliza
- Normal y aceptable — no todos los correlados son identicos
- Sin penalizacion

### PF < 1.0 en ambos mercados
- Señal de alarma: la estrategia puede ser especifica del activo
- Puede ser un artefacto de los datos Dukascopy del activo
- Puede ser sobreajuste temporal muy especifico
- Penalizacion -10 en el score — no descarte
- El WFO ya filtro el sobreajuste temporal; esto es adicional

### PF muy bajo en validacion (< 0.80) en ambos
- Señal de alerta fuerte
- Penalizacion aumenta a -20 puntos en el score
- Anotar como "estrategia activo-especifica" en el informe

---

## COMO SE EJECUTA

### Opcion A: dentro del Custom Project (preferida)
Añadir tarea "Cross-Asset Validation" despues del WFO:
  Input: estrategias aprobadas por WFO
  Simbolos adicionales: segun tabla de correlacion
  Periodo: OOS de cada activo de validacion
  Output: score ajustado por penalizacion

### Opcion B: script Python manual
  python scripts/multimarket-validation.py
    --strategy-folder results/wfo-approved/
    --asset-map docs/skills/skill-multimarket-validation.md
    --oos-start 2021-01-01
    --output results/multimarket/

El script genera un CSV con:
  estrategia_id, pf_validacion1, pf_validacion2, penalizacion, score_ajustado

---

## LO QUE ESTA VALIDACION NUNCA HACE

NUNCA descarta automaticamente por PF < 1.0 en correlados
  (eso es decision del portfolio filter por score, no descarte)
NUNCA modifica los parametros de la estrategia para
  "mejorar" su comportamiento en otros activos
NUNCA genera una estrategia diferente por activo
NUNCA cambia el activo principal de la estrategia
NUNCA sustituye al WFO — es complementaria
NUNCA se ejecuta en el mercado principal
  (ese ya fue validado por todo el pipeline anterior)

---

## REGISTRO EN EL INFORME DE EVALUACION

Añadir al informe del orchestrator:

Validacion multi-mercado:
  Activo principal: [simbolo]
  Validacion 1: [simbolo] — PF OOS: [valor] — PASS/FAIL
  Validacion 2: [simbolo] — PF OOS: [valor] — PASS/FAIL
  Penalizacion aplicada: 0 / -10 / -20 puntos
  Score base: [valor]
  Score final: [valor ajustado]
