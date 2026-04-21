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

## 7. ESTADO FINAL

**FASE 0: COMPLETADA** con las siguientes advertencias documentadas:

1. Gaps XAUUSD 2.615% — aceptado, limitacion estructural de Dukascopy
2. SQ Build 143 sin filtros Total Trades/Win Rate/Max DD — compensado con Python
3. verify-symbol-specs.py tiene limitacion con SQ Build 143 — verificacion manual en SQ

**Siguiente fase:** Fase 1 — Build 10 en curso desde 2026-04-20
