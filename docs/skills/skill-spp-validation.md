# Skill: System Parameter Permutation (SPP) — Puerta de Robustez

## Proposito
Detectar estrategias fragiles a pequeños cambios en sus
parametros antes de que lleguen al WFO.
Una estrategia que depende de valores exactos de parametros
para ser rentable es sospechosa de sobreajuste.
El SPP lo detecta sistematicamente antes de invertir
tiempo en el WFO.

---

## POSICION EN EL PIPELINE

```
Retester → [SPP Validation] → WFO → Portfolio
```

El SPP se ejecuta despues del Retester y antes del WFO.
Solo las estrategias que PASAN el SPP entran al WFO.
Esto ahorra tiempo de WFO en estrategias sobreajustadas.

---

## METODO DE PERMUTACION

### Que se permuta
Cada parametro numerico de la estrategia se modifica
individualmente mientras el resto permanece fijo.

### Cuanto se permuta
Cada parametro se prueba en 3 valores:
- Valor original - 10%
- Valor original (baseline)
- Valor original + 10%

Ejemplo para EMA period = 20:
  Permutaciones: 18, 20, 22

Ejemplo para ATR multiplier = 2.0:
  Permutaciones: 1.8, 2.0, 2.2

### Que se mide en cada permutacion
El Profit Factor de la estrategia con ese parametro modificado,
manteniendo el resto identico al baseline.

### Redondeo de parametros enteros
Si el parametro es entero, redondear al entero mas cercano.
Period 20 → 18, 20, 22 (ya son enteros)
Period 7 → round(6.3)=6, 7, round(7.7)=8

---

## CRITERIOS DE EVALUACION

### PASA SPP
El PF no cae mas del 30% en NINGUNA permutacion individual.
Formula:
  pf_permutacion >= pf_baseline * 0.70 en todas las permutaciones

Ejemplo PASS:
  Baseline PF = 1.60
  Umbral minimo = 1.60 * 0.70 = 1.12
  PF con EMA=18: 1.45 — PASS (>= 1.12)
  PF con EMA=22: 1.38 — PASS (>= 1.12)
  PF con ATR=1.8: 1.52 — PASS (>= 1.12)
  PF con ATR=2.2: 1.41 — PASS (>= 1.12)
  Resultado: PASA SPP

### DESCARTAR
El PF cae > 30% en CUALQUIER permutacion individual.
Formula:
  pf_permutacion < pf_baseline * 0.70 en alguna permutacion

Ejemplo DESCARTAR:
  Baseline PF = 1.60
  Umbral minimo = 1.60 * 0.70 = 1.12
  PF con EMA=18: 0.95 — FAIL (< 1.12)
  Resultado: DESCARTAR — sobreajuste probable

### Tratamiento de parametros multi-variable
Si la estrategia tiene 5 parametros, se generan 10
permutaciones (5 parametros x 2 modificaciones ±10%).
Un fallo en cualquiera de ellas es descarte.

---

## COMO SE CONFIGURA EN SQ X

### Via Custom Project (metodo preferido)
En la tarea de Retester, activar la opcion:
  "Parameter sensitivity analysis"
  Perturbation: 10%
  Fail if PF drops more than: 30%

SQ ejecuta las permutaciones automaticamente como
parte del batch del Retester y marca las estrategias
que fallan. El Custom Project las excluye de la TAREA 5 (WFO).

### Via script Python (metodo alternativo)
Si SQ Build 143 no soporta el SPP nativo:
  python scripts/spp-validation.py
    --strategies-folder results/retester/
    --perturbation 10
    --max-pf-drop 30
    --output results/spp-passed/

El script re-ejecuta cada permutacion usando los CSVs
del Retester y calcula el PF resultante.

---

## INTERPRETACION DE RESULTADOS

### Estrategia con PF estable bajo permutacion
- Indica que el edge es real y no depende de parametros exactos
- La estrategia captura un patron del mercado, no ruido
- Confianza alta para entrar al WFO

### Estrategia que falla una permutacion cercana (±10%)
- El edge es fragil — depende de un valor muy especifico
- Altamente probable que sea sobreajuste al periodo IS
- Descarte sin segunda oportunidad

### Estrategia con muchos parametros que pasan por poco
- Sospechosa aunque tecnicamente pasa el umbral del 30%
- Anotar en el log para seguimiento en produccion
- No bloquea el avance al WFO pero merece atencion

---

## LO QUE ESTA VALIDACION NO GARANTIZA

El SPP NO garantiza que la estrategia funcione en OOS.
Solo garantiza que no depende de valores exactos en IS.
Una estrategia puede pasar el SPP y fallar en el WFO
si hay sobreajuste al periodo temporal en lugar de
sobreajuste a los valores de parametros.

El SPP y el WFO son complementarios — no sustitutos.
El SPP filtra sobreajuste de parametros.
El WFO filtra sobreajuste temporal.

---

## REGISTRO DE DECISIONES

Cada decision SPP se registra en el log del orchestrator:

Estrategia: [ID]
Fecha: [fecha]
Fase: SPP
Baseline PF: [valor]
Umbral minimo (70%): [valor]
Permutaciones ejecutadas: [numero]
Permutacion que falla: [parametro] = [valor] → PF [valor]
Decision: PASA SPP / DESCARTAR
