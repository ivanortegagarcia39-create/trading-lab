# Skill: Gestion de Riesgo Completa — TradingLab

## Proposito
Define los 5 niveles de riesgo del sistema, el ajuste dinamico
por drawdown, el Kelly fraccionado y las protecciones automaticas.
Toda la logica de riesgo es numerica y automatica.
No hay decision subjetiva sobre el tamaño de posicion.

---

## LOS 5 NIVELES DE RIESGO

### Nivel 1 — Por trade
**Regla:** 1% del balance por cada trade individual.
**Calculo:** `lotes = (balance * 0.01) / (sl_pips * valor_pip)`
**Herramienta:** `scripts/risk-calculator.py`

### Nivel 2 — Por estrategia
**Regla:** maximo 2 trades abiertos simultaneamente por estrategia.
Esta regla esta hardcoded en el EA en MT5.
Razon: mas de 2 trades simultaneos en una estrategia H1 indica
acumulacion de riesgo que no esta modelada en el backtest.

### Nivel 3 — Por portfolio
**Regla:** riesgo total maximo del 5% en cualquier momento.
Con 3 estrategias: 1% x 2 trades x 3 = maximo 6% teorico.
En practica: el portfolio usa riesgo reducido por estrategia
cuando hay multiples activas (ver Ajuste Dinamico por Portfolio).

**Ajuste por numero de estrategias:**

| Estrategias activas | Riesgo por trade | Riesgo max simultaneo |
|--------------------|------------------|-----------------------|
| 1 | 1.0% | 2.0% |
| 2 | 0.9% | 3.6% |
| 3 | 0.8% | 4.8% |
| 4 | 0.7% | 5.6% |
| 5 | 0.6% | 6.0% |
| 6+ | 0.5% | ≤6.0% |

### Nivel 4 — Por dia (buffer FTMO)
**Regla:** DD diario maximo 4.8% antes del limite FTMO del 5%.
El Risk Manager EA cierra todas las posiciones cuando el DD
diario alcanza el 4.8%. Nunca se llega al limite del 5%.
Margen de seguridad: 0.2% = 50$ en cuenta 25k.

### Nivel 5 — Por challenge (buffer FTMO)
**Regla:** DD total maximo 9.5% antes del limite FTMO del 10%.
El Risk Manager EA cierra todo si el DD total alcanza el 9.5%.
Margen de seguridad: 0.5% = 125$ en cuenta 25k.

---

## AJUSTE DINAMICO POR DRAWDOWN

Los umbrales estan definidos en `config/pipeline-config.json`
seccion `risk_manager`.

| DD actual | Riesgo por trade | Accion adicional |
|-----------|-----------------|-----------------|
| 0 - 3% | 1.0% (normal) | Sin cambios |
| 3 - 4% | 0.75% (-25%) | Warning Telegram |
| 4 - 4.8% | 0.5% (reducido) | Warning Telegram |
| 4.8% | 0% — STOP | Risk Manager EA cierra todo |
| 4.8 - 6% | 0.25% (minimo) | Tras reactivar manual |
| > 6% | 0.25% (minimo) | account-recovery-manager activo |
| 9.5% | 0% — STOP TOTAL | Cierre total de posiciones |

**Herramienta:** `scripts/risk-calculator.py --dd-actual [valor]`

---

## KELLY FRACCIONADO

### Formula
```
Kelly = (p * b - q) / b
```
Donde:
- p = probabilidad de win (ej. 0.50 para WR 50%)
- q = probabilidad de loss = 1 - p
- b = ratio TP/SL (ej. 2.0 para ratio 2:1)

### Ejemplo con WR 50% y ratio 2:1
```
Kelly = (0.50 * 2 - 0.50) / 2 = 0.25 = 25%
Kelly fraccionado (25%) = 0.25 * 0.25 = 6.25%
```

**NUNCA usar el Kelly completo.** El Kelly completo asume
estimaciones perfectas de p y b — que en trading son
aproximaciones con error. El 25% del Kelly es la fraccion
estandar de la industria para sistemas automaticos.

### Limites
El Kelly fraccionado es una referencia, no una orden.
El riesgo por trade NUNCA supera el 1% por la restriccion FTMO.
Si el Kelly fraccionado > 1%: usar 1%.
Si el Kelly fraccionado < 0.25%: usar 0.25% (riesgo minimo).

---

## GESTION DE CORRELACION

### Correlacion alta entre dos estrategias
Si correlacion entre dos estrategias del portfolio > 0.6:
- Reducir riesgo de AMBAS estrategias a 0.7%
- Notificar via Telegram: "Correlacion elevada [A]/[B]: [valor]"
- Razon: correlacion > 0.6 implica que en un dia malo
  ambas perderan casi simultaneamente, duplicando el DD efectivo

### Modo Panico — correlacion media del portfolio > 0.85
Cuando todas las estrategias del portfolio se mueven juntas:
- Reducir riesgo de TODAS a 0.1% por trade
- Notificar CRITICAL via Telegram: "MODO PANICO activado"
- Razon: correlacion > 0.85 = el portfolio se comporta
  como si fuera una sola estrategia — riesgo concentrado
- Desactivacion: cuando correlacion media baja a < 0.70
  en una ventana de 5 dias consecutivos

**Herramienta:** `scripts/portfolio-monitor.py`
Umbral configurable en `config/pipeline-config.json`

---

## PROTECCIONES AUTOMATICAS

### 1. Risk Manager EA (MT5)
Nivel: codigo MQL5 en el EA desplegado en VPS.
Acciones automaticas:
- DD diario >= 4.8%: cerrar todas las posiciones del EA
- DD total >= 9.5%: cerrar todas las posiciones y desactivar
Prerequisito: EA compilado con la libreria Risk Manager.

### 2. account-recovery-manager
Nivel: agente Python + logica en EA.
Se activa cuando: DD > 6%.
Acciones:
- Reducir lote a 0.25% por trade
- Aumentar ratio TP/SL requerido a 2.5:1
- Notificar Telegram cada 24h con estado de recuperacion
- Desactivacion automatica cuando equity recupera al 97% del pico
Ver: `agents/account-recovery-manager.md`

### 3. Kill Switch Telegram /STOP
Nivel: comando manual via bot Telegram.
Accion: cierra TODAS las posiciones abiertas en MT5 via API.
Uso: cuando el humano detecta un evento extremo no modelado
(noticia de cisne negro, fallo de infraestructura, etc.)
Este es el UNICO caso de intervencion humana autorizada
en la gestion de riesgo de una posicion abierta.

### 4. portfolio-monitor.py
Nivel: script Python con alertas proactivas.
Monitoreo continuo cada 300 segundos (configurable).
Alertas automaticas:
- DD > 3%: WARNING Telegram
- DD > 4.5%: CRITICAL Telegram
- Correlacion > 0.85: CRITICAL Modo Panico
- Z-Score PF <= -2.0 por 4 semanas: WARNING Decay
- Sin trades 15 dias: WARNING Inactividad

---

## CALCULO PRACTICO — USO DIARIO

```bash
# Calcular lotes para XAUUSD con 150 pips de SL
python scripts/risk-calculator.py \
    --balance 25000 \
    --sl-pips 150 \
    --activo XAUUSD

# Ajuste cuando hay 3 estrategias activas y DD del 3.5%
python scripts/risk-calculator.py \
    --balance 25000 \
    --sl-pips 150 \
    --activo XAUUSD \
    --dd-actual 3.5 \
    --num-estrategias 3
```

---

## RELACION CON OTROS SKILLS

- `skill-ftmo-rules.md` — limites exactos de FTMO que motivan los buffers
- `skill-challenge-tracker.md` — seguimiento del DD durante el challenge
- `skill-portfolio-selection.md` — correlacion maxima 0.5 entre pares
- `skill-monte-carlo.md` — estimacion de probabilidad de exito por cuenta
- `agents/account-recovery-manager.md` — protocolo de recuperacion en DD
