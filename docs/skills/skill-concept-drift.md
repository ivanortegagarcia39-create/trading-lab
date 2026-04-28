# Skill: Concept Drift Detection

## Propósito

Detectar automáticamente cuándo el mercado o las estrategias están cambiando
de comportamiento, antes de que ese cambio cause pérdidas reales.

Dos detectores trabajan en paralelo:
- **BOCPD**: para cambios abruptos de régimen de mercado
- **ADDM**: para degradación gradual de las predicciones del sistema

---

## BOCPD — Bayesian Online Change-Point Detection

### Qué detecta

Cambios abruptos en la distribución de los retornos del mercado.
Ejemplo: el mercado pasa de tendencial a lateral de forma brusca.

### Cómo funciona

1. Mantiene una ventana deslizante de los últimos 50 retornos
2. Divide la ventana en dos mitades y compara sus distribuciones
3. Calcula la probabilidad de que haya un cambio de punto
4. Umbral de alarma: probabilidad > 0.7 → `CHANGE_POINT`

### Niveles de alerta

| Probabilidad | Nivel | Acción |
|---|---|---|
| < 0.5 | NONE | Sin acción |
| 0.5 – 0.7 | WARNING | Monitorear |
| > 0.7 | CHANGE_POINT | Re-validar estrategias activas + notificar Telegram |

### Cuándo actuar ante CHANGE_POINT

- Re-ejecutar retester de estrategias activas con datos recientes
- Revisar si las métricas en demo siguen dentro de expectativas
- Considerar pausar nuevas entradas hasta que el régimen se estabilice
- **NO** descartar estrategias solo por un CHANGE_POINT — esperar confirmación

### Cuándo ignorar la señal

- Si el cambio de punto está en datos de baja liquidez (festivos, cierre de año)
- Si la ventana de retornos tiene menos de 20 datos reales
- Si hay un solo CHANGE_POINT aislado sin confirmación en días siguientes

---

## ADDM — Autoregressive Drift Detection Method

### Qué detecta

Degradación gradual de las predicciones del sistema:
si el sistema predice PF=2.0 pero consistentemente el activo da PF=1.4,
hay drift en las predicciones.

### Cómo funciona

1. Para cada estrategia, mantiene historial de `(PF_esperado, PF_real)`
2. Calcula residual = PF_esperado − PF_real
3. Si la media móvil del residual supera 2σ durante 3 periodos consecutivos → `DRIFT_DETECTED`

### Niveles de alerta

| Nivel | Condición | Acción |
|---|---|---|
| NONE | Residuales normales | Sin acción |
| WARNING | 2 de 3 periodos sobre 2σ | Monitorear más de cerca |
| CRITICAL / DRIFT_DETECTED | 3 periodos consecutivos sobre 2σ | Revisar estrategia + notificar |

### Cuándo actuar ante DRIFT_DETECTED

- Investigar si el drift es por cambio de mercado o por problema de datos
- Revisar las comisiones configuradas (pueden haber cambiado)
- Ejecutar retester con datos OOS actualizados
- Si el drift persiste >2 semanas: re-evaluar la estrategia desde el WFO

### Cuándo ignorar la señal

- Con menos de 10 observaciones (ADDM no tiene datos suficientes)
- Si la causa es conocida: evento macro puntual, spread ampliado temporalmente
- Si el PF real sigue por encima del mínimo del EvalGate (1.5)

---

## Comandos

```bash
# Verificar estabilidad actual (usado semanalmente por self-improvement-engine)
python scripts/concept-drift-detector.py --check

# Ver reporte completo
python scripts/concept-drift-detector.py --report

# Actualizar BOCPD con nuevos retornos (lista de floats)
python scripts/concept-drift-detector.py --update-bocpd 0.012 -0.005 0.008 0.003 ...

# Actualizar ADDM para una estrategia
python scripts/concept-drift-detector.py --update-addm STRAT001 1.8 1.4
```

---

## Integración con el ciclo semanal

El `self-improvement-engine.py` ejecuta automáticamente `--check` en el paso 2b
de cada ciclo semanal.

Si detecta `CHANGE_POINT` o `DRIFT_DETECTED`:
1. La alerta se añade al informe del ciclo
2. Se notifica via Telegram
3. Se incluye en el resumen enviado al usuario

---

## Estado y archivos

| Archivo | Contenido |
|---|---|
| `results/drift-detection.json` | Estado actual: ventana BOCPD, historial de change-points, residuales ADDM por estrategia |

El archivo de estado no se versiona en git (datos operativos del sistema).

---

## Guía rápida de decisión

```
BOCPD CHANGE_POINT detected?
  SÍ → ¿Es el segundo en 7 días?
         SÍ → Pausar nuevas entradas, re-validar todo
         NO → Monitorear, esperar confirmación

ADDM DRIFT_DETECTED en STRAT001?
  SÍ → PF_real aún > 1.5?
         SÍ → Warning, no actuar aún
         NO → Pausar estrategia, re-evaluar desde WFO
```
