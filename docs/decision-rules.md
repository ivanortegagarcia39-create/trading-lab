# Decision Rules — Criterios Automaticos de Evaluacion

## Principio fundamental
Una estrategia no avanza por intuicion ni por
"parece prometedora". Solo avanza si cumple
criterios numericos medibles en cada puerta.

Las decisiones las toman los numeros.
No las personas. Sin excepciones.

Las 3 unicas decisiones posibles son:
PASA / DESCARTAR / ESPERA

Las decisiones REVISAR y SIMPLIFICAR del enfoque
anterior ya no existen. Una estrategia cumple
los numeros o se descarta. No hay segunda oportunidad.

---

## Umbrales del pipeline

### Evaluation Gate (Fase D)

| Metrica | Descarte auto | Aprobacion auto |
|---------|---------------|-----------------|
| PF in-sample | < 1.4 | >= 1.5 |
| Max Drawdown IS | > 7% | <= 6% |
| Trades totales | < 80 | >= 120 |
| Trades por mes | < 8 | >= 10 |
| Win Rate | < 30% | >= 38% |
| Ratio TP/SL | < 1.8:1 | >= 2:1 |
| Años positivos | < 65% | >= 75% |
| Beneficio en 1 mes | > 45% | <= 40% |
| DD en ultimos 3 meses | SI | NO |
| Max racha perdedora | > 8 | <= 6 |

Si cumple CUALQUIER criterio de descarte → DESCARTAR
Si cumple TODOS los criterios de aprobacion → PASA
Sin consultar al humano en ningun caso.

### Zona entre descarte y aprobacion
Reglas automaticas sin consulta humana:

PF entre 1.4 y 1.5:
- Trades > 150 → PASA (mayor muestra compensa)
- Trades <= 150 → DESCARTAR

DD entre 6% y 7%:
- PF > 1.6 → PASA (alto PF compensa DD marginal)
- PF <= 1.6 → DESCARTAR

Años negativos entre 25% y 35%:
- Coinciden con crisis (2008, 2015, 2020) → PASA
- No coinciden con crisis → DESCARTAR

---

### Retester — Paso 12b (Fase E)

| Metrica | Descarte auto | Aprobacion auto |
|---------|---------------|-----------------|
| PF out-of-sample | < 1.2 | >= 1.3 |
| Caida PF IS→OOS | > 25% | <= 20% |
| DD out-of-sample | > 7% | <= 6.5% |
| Trades/mes OOS | < 5 | >= 6 |
| Caida frecuencia | > 50% | <= 40% |

En el paso 12b NO hay zona intermedia.
O cumple aprobacion → PASA al WFO
O no cumple → DESCARTAR
El WFO es demasiado costoso para lanzarlo con dudas.

---

### Walk-Forward Optimization (Fase F)

| Metrica | Descarte auto | Aprobacion auto |
|---------|---------------|-----------------|
| WFE | < 40% | >= 50% |
| Ventanas OOS negativas | 2 consecutivas | Max 1 aislada |
| DD OOS por ventana | > 7.5% | <= 7% |
| PF OOS ultima ventana | < 1.0 | >= 1.1 |
| Desviacion parametros | > 35% | < 25% |
| PF OOS promedio | < 1.1 | >= 1.25 |

WFE entre 40% y 50% → DESCARTAR
(robustez insuficiente para produccion)

1 ventana negativa aislada con WFE > 50%:
- PF OOS promedio >= 1.3 → PASA
- PF OOS promedio < 1.3 → DESCARTAR

---

### Portfolio (Fase G)

| Metrica | Descarte | Incluir | Espera |
|---------|----------|---------|--------|
| Score individual | < 55 | >= 55 | - |
| Correlacion max | > 0.7 con 2+ | < 0.5 | 0.5-0.7 |
| DD combinado | > 15% | < 12% | 12-15% |
| Estrategias mismo activo | > 2 | <= 2 | - |
| Estrategias mismo estilo | > 3 | <= 3 | - |

ESPERA: estrategia valida pero no compatible
con el portfolio actual. Queda en cola hasta
que haya espacio.

---

## Señales de alerta automaticas

Estas situaciones activan DESCARTAR
independientemente de las metricas individuales:

- La estrategia solo funciona en 2 años o menos
- Mas del 60% del beneficio viene de menos
  del 10% de las operaciones
- PF muy alto (> 3.0) con pocos trades (< 100)
- El resultado mejora drasticamente al ampliar el SL
- Comportamiento completamente distinto IS vs OOS
- Monte Carlo muestra degradacion significativa

---

## Tasas de descarte esperadas

| Fase | Entrada | Descartadas | Pasan |
|------|---------|-------------|-------|
| Builder → Eval Gate | ~1000 | ~70% | ~300 |
| Eval Gate → Retester | ~300 | ~50% | ~150 |
| Retester → 12b → WFO | ~150 | ~60% | ~60 |
| WFO → Aprobacion | ~60 | ~75% | ~15 |
| Portfolio → Inclusion | ~15 | ~30% | ~10 |

Ratio final: ~1% de candidatas llegan a produccion.
Esto es NORMAL en la industria.

---

## Lo que ya no existe en este proyecto

### REVISAR — ELIMINADO
En el enfoque anterior una estrategia podia
volver atras para ajustes hasta 2 veces.
Esto no existe. Si no pasa → se descarta.

### SIMPLIFICAR — ELIMINADO
En el enfoque anterior se reducia complejidad
manualmente. Esto no existe. SQ genera la
complejidad que necesite y el pipeline filtra.

### FIRMA HUMANA — ELIMINADA
En el enfoque anterior el humano firmaba cada
decision del Evaluation Gate. Esto no existe.
Los numeros deciden automaticamente.

### SEGUNDA OPORTUNIDAD — ELIMINADA
Una estrategia descartada no vuelve al pipeline.
Es mas eficiente generar 1000 nuevas candidatas
que intentar arreglar una que no cumple los numeros.

---

## Regla de oro

Si hay duda sobre si un numero cumple o no
→ DESCARTAR. Siempre a favor de descartar.
Es mas barato generar otra candidata que
arriesgar dinero con una estrategia dudosa.