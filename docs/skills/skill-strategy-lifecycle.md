# Skill: Strategy Lifecycle

## Propósito

Documenta el ciclo de vida completo de una estrategia desde que SQ la genera
hasta que se retira del portfolio. Cada transición de estado es automática,
registrada y auditada.

---

## Estados y transiciones

```
SQ genera estrategia
        ↓
   [standby]  ←── 0-2 días (evaluación automática)
        ↓ pasa EvalGate automático
  [candidate]  ←── 1-3 días (Retester + WFO + Stress Test)
        ↓ pasa WFO y Forward Test
    [shadow]  ←── 4 semanas (Champion-Challenger paper trading)
        ↓ supera al champion en 2/3 métricas
    [active]  ←── meses / años (producción con capital real)
        ↓ ADDM detecta drift CRITICAL
   [decaying]  ←── máximo 4 semanas antes de decisión
        ↓                        ↓
   [retired]              [active] (recuperación)

Camino alternativo:
  [candidate] o [shadow] → [failed_challenge]
```

---

## Tiempo típico en cada estado

| Estado | Tiempo típico | Trigger de salida |
|---|---|---|
| standby | 0–2 días | EvalGate automático (PF > 1.5, DD < 7%) |
| candidate | 1–3 días | WFO OOS aprobado + Forward Test |
| shadow | 4 semanas | Champion-Challenger: win en 2/3 métricas |
| active | meses–años | ADDM CRITICAL o decay trimestral |
| decaying | max 4 semanas | Recuperación o retiro definitivo |
| retired | permanente | Registro histórico |

---

## Transiciones automáticas

El `strategy-retirement-manager.py --check` verifica diariamente:

| Condición | Transición |
|---|---|
| Timeout en standby (> 2 días) | standby → candidate (forzar evaluación) |
| Timeout en decaying (> 30 días) | decaying → retired |
| ADDM CRITICAL en estrategia active | active → decaying |
| ADDM vuelve a NONE en decaying | decaying → active |
| Champion-Challenger PROMOTE | shadow → active |

---

## Comandos

```bash
# Ver ciclo de vida de todas las estrategias
python scripts/strategy-retirement-manager.py --report

# Verificar y ejecutar transiciones pendientes
python scripts/strategy-retirement-manager.py --check

# Simular sin aplicar
python scripts/strategy-retirement-manager.py --check --dry-run

# Transición manual
python scripts/strategy-retirement-manager.py --transition STRAT001 active "Promovida manualmente tras revisión"
```

---

## Métricas de calidad del ciclo

### Tasa de conversión

El objetivo es > 5% de estrategias generadas por SQ lleguen a `active`.
Con el Builder libre generando 500-2000 estrategias por build, se esperan
25-100 candidatos por ciclo de builds.

**Embudos típicos:**
- standby → candidate: ~30% (EvalGate)
- candidate → shadow: ~20% (WFO)
- shadow → active: ~50% (Champion-Challenger)
- **Total: ~3-6% de standby a active**

### Duración media en producción

Objetivo: estrategias activas durante > 6 meses antes de decay.
Si la duración media baja de 3 meses → revisar criterios del WFO.

### Causas más frecuentes de retiro

Registradas en `config/retirement-audit.jsonl`. Causas esperadas:
1. ADDM CRITICAL (drift de mercado)
2. Timeout en decaying (no se recuperó)
3. Failed challenge (fallo en cuenta real)

Si la causa más frecuente es "timeout en standby" → pipeline demasiado lento.
Si es "failed challenge" → criterios de forward test demasiado permisivos.

---

## Integración con otros sistemas

| Sistema | Interacción |
|---|---|
| `concept-drift-detector.py` | ADDM CRITICAL → activa transición active → decaying |
| `champion-challenger.py` | PROMOTE → activa transición shadow → active |
| `quarterly-reoptimizer.py` | Detecta decay → marca para reoptimización antes de retirar |
| `self-improvement-engine.py` | Ejecuta `--check` en el paso 2h del ciclo semanal |
| `bayesian-criteria-updater.py` | false_negative en EvalGate → estrategia promovida que falló → criteria update |

---

## Garantías

- Toda transición queda en `config/retirement-audit.jsonl`
- Las transiciones a `active`, `retired` y `failed_challenge` se notifican por Telegram
- El estado `retired` es permanente — no hay rollback (el historial sí se conserva)
- Un humano puede hacer cualquier transición manualmente con `--transition`
- La lógica de entrada de una estrategia retirada puede usarse como referencia
  para futuros builds, pero no se reutiliza directamente (viola Builder libre)
