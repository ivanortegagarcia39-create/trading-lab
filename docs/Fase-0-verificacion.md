# Fase 0 — Verificacion y Configuracion
Estado: COMPLETADA CON ADVERTENCIAS DOCUMENTADAS
Fecha: 2026-04-20
Maquina: Alber

---

## 1. INSTRUMENTOS FTMO CONFIGURADOS EN SQ

### XAUUSD_ftmo
| Parametro | Valor |
|-----------|-------|
| Pip size | 0.01 |
| Tick size | 0.01 |
| Point Value | 100 |
| Spread | 30 pips |
| Slippage | 2 pips |
| Comision | $7/lote |
| Simbolo datos | XAUUSD_M1_dukas |

### EURUSD_ftmo
| Parametro | Valor |
|-----------|-------|
| Pip size | 0.0001 |
| Tick size | 0.0001 |
| Point Value | 100000 |
| Spread | 0.5 pips |
| Slippage | 0.5 pips |
| Comision | $7/lote |
| Simbolo datos | EURUSD_M1_dukas |

Ambos instrumentos asignados a sus simbolos _M1_dukas correspondientes en SQ.

---

## 2. CALIDAD DE DATOS M1

### XAUUSD_M1_dukas
- Gaps detectados: **2.615%**
- Causa: limitacion estructural de Dukascopy para datos M1 del Oro
- No es un error del proyecto ni de la descarga
- Decision: **ACEPTADO** para uso en H1
- Razon: los gaps M1 tienen impacto minimo en la construccion de velas H1
  (60 barras M1 por vela H1 — los gaps aislados no distorsionan el H1)

### EURUSD_M1_dukas
- Gaps detectados: **0.164%**
- Decision: **ACEPTADO** — dentro del rango normal

---

## 3. RANGO OOS VERIFICADO

| Parametro | Valor |
|-----------|-------|
| Simbolo | XAUUSD_M1_dukas |
| End day | 2026.04.20 |
| Estado | VERIFICADO |

OOS empieza en 2021.01.01. Los datos llegan hasta 2026-04-20.
El Builder usa solo el rango IS (2003.05.05 a 2020.12.31).
Los datos OOS nunca entran en el Builder.

---

## 4. SCRIPTS CREADOS Y PROBADOS

| Script | Estado | Resultado |
|--------|--------|-----------|
| scripts/validate-sqx-folder.py | CREADO Y PROBADO | PASS — divergencia 0.00% |
| scripts/validate-sqx-build.py | CREADO | Error de formato CSV resuelto |
| scripts/verify-symbol-specs.py | CREADO | Limitacion conocida de SQ documentada |

---

## 5. LIMITACION CONOCIDA — SQ BUILD 143

Los filtros siguientes **no estan disponibles** en los filtros
personalizados del Builder de SQ Build 143:

- Total Trades (numero total de trades)
- Win Rate (porcentaje de trades ganadores)
- Max Drawdown % (maximo drawdown porcentual)

**Solucion implementada:** estos filtros se aplican en Python
post-build a traves del evaluator-assistant, procesando los
CSVs exportados del databank de SQ.

**Filtros disponibles en SQ Build 143 (usados en el Builder):**
- Transacciones medias al mes > 6
- Factor de beneficio > 1.3
- Ratio Ret/DD > 0.8

**Filtros aplicados en Python post-build:**
- Total Trades >= 120
- Win Rate >= 38%
- Max DD <= 7%

---

## 6. BUILDER LIBRE — CONFIGURACION FINAL H1 XAUUSD

Esta es la configuracion validada y activa para Build 10.

### Condiciones de entrada/salida
| Parametro | Valor |
|-----------|-------|
| Conditions entry | Min 1, Max 3 |
| Conditions exit | Min 1, Max 2 |

### Stop Loss y Take Profit (ATR-based)
| Parametro | Valor |
|-----------|-------|
| SL multiplicador | 1.5 a 3.0 |
| SL periodo ATR | 14 |
| TP multiplicador | 3.0 a 6.0 |
| TP periodo ATR | 14 |
| Ratio TP/SL minimo | 200% |

### Algoritmo genetico
| Parametro | Valor |
|-----------|-------|
| Generaciones | 30 |
| Poblacion por isla | 100 |
| Islas | 4 |
| Modo | Continuo (Start again when finished) |

### Paleta de indicadores/señales
| Parametro | Valor |
|-----------|-------|
| Señales activadas | 340 (todas) |
| Indicadores activados | 106 (todos) |

### Gestion del dinero
| Parametro | Valor |
|-----------|-------|
| Capital | 25.000 USD |
| Riesgo por trade | 1% fijo |

### Comprobaciones cruzadas
| Parametro | Valor | Nota |
|-----------|-------|------|
| Monte Carlo | DESACTIVADO en Builder | Se aplica en Retester |
| Mayor precision | ACTIVADO | |

**Razon de Monte Carlo desactivado en Builder:**
Activarlo en el Builder ralentiza la generacion sin beneficio
adicional. El Retester aplica Monte Carlo sobre candidatas
ya pre-filtradas — es ahi donde tiene valor real.

### Filtros en SQ (Builder)
| Filtro | Valor |
|--------|-------|
| Trades/mes | > 6 |
| Profit Factor | > 1.3 |
| Ret/DD ratio | > 0.8 |

### Filtros en Python post-build
| Filtro | Valor |
|--------|-------|
| Total Trades | >= 120 |
| Win Rate | >= 38% |
| Max DD | <= 7% |

---

## 7. STRESS TEST HISTORICO — PENDIENTE FASE 1 SQ

Las estrategias aprobadas por el Evaluation Gate y el WFO
deben validarse adicionalmente contra 5 periodos historicos
criticos. Este test verifica que la estrategia no solo funciona
en condiciones normales sino que sobrevive los eventos
de cola extrema del mercado.

**Criterio de aprobacion:** DD < 8% en cada periodo critico.
Si una estrategia supera el 8% en cualquier periodo → DESCARTAR.

### Periodos criticos obligatorios

| # | Evento | Periodo | Razon de inclusion |
|---|--------|---------|-------------------|
| 1 | Crisis financiera global | 2008-09-01 a 2008-10-31 | Mayor crash del SXX en Forex y Metales |
| 2 | Flash crash CHF | 2015-08-01 a 2015-09-30 | Ruptura de paridad SNB — movimientos extremos en pares CHF |
| 3 | COVID crash | 2020-02-01 a 2020-03-31 | Volatilidad record — ATR multiplicado x5 en muchos activos |
| 4 | Inflacion y subida de tipos | 2022-01-01 a 2022-06-30 | Tendencias sostenidas inusuales — EUR/USD -12% en 6 meses |
| 5 | Crisis SVB | 2023-03-01 a 2023-03-31 | Volatilidad bancaria — spike de incertidumbre intraday |

### Como ejecutar el stress test en SQ

1. En SQ: Abrir estrategia aprobada → Retester → Configurar periodo
2. Usar simbolo _ftmo con las comisiones reales (NO backtest sucio para stress test)
3. Ejecutar cada periodo por separado
4. Registrar DD maximo de cada periodo en el informe de evaluacion
5. Si cualquier DD > 8% → la estrategia no pasa el stress test → DESCARTAR

### Registro en el informe de evaluacion

Cada estrategia aprobada debe incluir en su informe:
```
STRESS TEST HISTORICO:
  2008 Crisis: DD maximo [valor]% → [PASS/FAIL]
  2015 Flash CHF: DD maximo [valor]% → [PASS/FAIL]
  2020 COVID: DD maximo [valor]% → [PASS/FAIL]
  2022 Inflacion: DD maximo [valor]% → [PASS/FAIL]
  2023 SVB: DD maximo [valor]% → [PASS/FAIL]
  Resultado final: [PASS/FAIL]
```

**Estado actual:** Pendiente de implementar en el pipeline de evaluacion.
La primera estrategia de Build 10 que pase el Evaluation Gate
debe pasar por este test antes del WFO.

---

## 8. PENDIENTES PARA VERIFICAR EN MAQUINA ALBER

Estas verificaciones requieren acceso directo a SQ y MT5.
El humano las realiza durante la proxima sesion de revision.

### P1 — Point Value de todos los activos del universo

Verificar en SQ Data Manager el Point Value de cada activo
antes de lanzar builds sobre ellos. Prestar especial atencion a:

| Activo | Point Value esperado | Estado |
|--------|---------------------|--------|
| XAUUSD | 100 (USD/lote/punto) | Verificado en Fase 0 |
| EURUSD | 100000 | Verificado en Fase 0 |
| USDJPY | 1000 | PENDIENTE verificar |
| GBPUSD | 100000 | PENDIENTE verificar |
| Indices (US30, US500) | Variable segun broker | PENDIENTE verificar |
| Cripto (BTC, ETH) | Variable | PENDIENTE verificar |

Errores en el Point Value generan calculos de tamaño de lote
incorrectos en el backtest — estrategias descartadas o aprobadas
por razones equivocadas.

### P2 — Gaps en datos GBPUSD y USDJPY

Verificar en SQ → Data Manager → Quality Report:
- GBPUSD_M1_dukas: porcentaje de gaps
- USDJPY_M1_dukas: porcentaje de gaps

Umbral: < 5% aceptable. Si > 5% → usar datos alternativos
o documentar como advertencia antes de lanzar build.

### P3 — Confirmar spread Build 10 = 60 pips XAUUSD

Verificar en SQ → Tab Datos → engranaje → Spread
que el valor activo del Build 10 para XAUUSD es 60 pips
(backtest sucio = doble del real FTMO de 30 pips).

Si el Build 10 se lanzo con 30 pips (spread real), documentar
en el historial del build. Las estrategias aprobadas
del Build 10 pasaran por un re-test con 60 pips
antes del WFO si la diferencia es significativa.

---

## 9. ESTADO FINAL

**FASE 0: COMPLETADA** con las siguientes advertencias documentadas:

1. Gaps XAUUSD 2.615% — aceptado, limitacion estructural de Dukascopy
2. SQ Build 143 sin filtros Total Trades/Win Rate/Max DD — compensado con Python
3. verify-symbol-specs.py tiene limitacion con SQ Build 143 — verificacion manual en SQ
4. Stress Test Historico definido — pendiente de ejecucion con estrategias de Build 10
5. Point Value USDJPY/GBPUSD/Indices/Cripto — pendiente verificacion manual en Alber
6. Spread Build 10 XAUUSD — confirmar si es 30 o 60 pips (backtest sucio)

**Siguiente fase:** Fase 1 — Build 10 en curso desde 2026-04-20
