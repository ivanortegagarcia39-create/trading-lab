# Skill: Control de Sobreajuste en Builder Libre

## Proposito
Define como el pipeline de validacion detecta y
elimina automaticamente estrategias sobreajustadas
generadas por el Builder libre.
En el enfoque anterior el humano intentaba evitar
el sobreajuste diseñando hipotesis simples.
En el enfoque actual SQ genera libremente y el
pipeline filtra automaticamente.

---

## FILOSOFIA DEL CONTROL DE SOBREAJUSTE

El Builder libre con paleta completa genera
mas sobreajuste que un Builder restringido.
Esto es ESPERADO y CORRECTO.

La solucion NO es restringir el Builder.
La solucion es tener un pipeline de validacion
mas exigente que descarte automaticamente
todo lo que no sea robusto.

Analogia: es mejor pescar con red grande y
devolver al mar los peces pequeños que pescar
con anzuelo pequeño y esperar que pique el
pez correcto.

---

## SEÑALES DE SOBREAJUSTE QUE DETECTA EL PIPELINE

### En el Evaluation Gate (automatico)
- PF > 3.0 con trades < 100 → DESCARTAR
  Casi seguro curve-fitting
- Mas del 45% del beneficio en un solo mes → DESCARTAR
  Edge concentrado en periodo especifico
- Años con PF < 1.0 superan el 35% → DESCARTAR
  Inconsistencia entre periodos
- DD maximo en ultimos 3 meses del IS → DESCARTAR
  Estrategia deteriorandose
- Max racha perdedora > 8 trades → DESCARTAR
  Estructura de riesgo fragil

### En el paso 12b (automatico)
- Caida PF IS→OOS > 25% → DESCARTAR
  El edge no se mantiene fuera de muestra
- PF OOS < 1.2 → DESCARTAR
  Edge insuficiente en datos no vistos
- Frecuencia OOS cae > 50% respecto al IS → DESCARTAR
  La estrategia depende de condiciones del IS

### En el WFO (automatico)
- WFE < 40% → DESCARTAR
  La optimizacion no se traslada a datos nuevos
- Parametros con desviacion > 35% entre ventanas → DESCARTAR
  No hay parametros estables — el edge es ruido
- 2 ventanas OOS negativas consecutivas → DESCARTAR
  Deterioro sistematico no aislado
- PF OOS < 1.0 en la ultima ventana → DESCARTAR
  El edge ha desaparecido en datos recientes

### En Monte Carlo (automatico en Builder)
- Si Monte Carlo muestra degradacion significativa
  la estrategia depende del orden de las operaciones
  → descartada automaticamente por SQ

---

## POR QUE EL BUILDER LIBRE GENERA MAS CANDIDATAS VALIDAS

Con el enfoque anterior (Builds 1-8):
- 2-3 indicadores activados
- Espacio de busqueda: ~1.000 combinaciones
- Resultado: 0 estrategias aprobadas en 8 builds

Con el Builder libre:
- +100 indicadores activados
- Espacio de busqueda: ~10.000.000 combinaciones
- Resultado esperado: 5-15 aprobadas por ciclo de 48h

La diferencia es que con un espacio de busqueda
10.000x mayor SQ encuentra edges que un humano
nunca habria considerado. Muchos seran sobreajuste
pero el pipeline los descarta automaticamente.

---

## TASAS DE DESCARTE ESPERADAS POR FASE

Estas tasas son NORMALES y ESPERADAS:

| Fase | Entrada | Descartadas | Pasan |
|------|---------|-------------|-------|
| Builder filtros | 4000+ | ~75% | ~1000 |
| Evaluation Gate | ~1000 | ~70% | ~300 |
| Retester + 12b | ~300 | ~60% | ~120 |
| WFO | ~120 | ~70% | ~35 |
| Aprobacion final | ~35 | ~60% | ~5-15 |
| Portfolio | ~5-15 | ~30% | ~3-10 |

Un ratio del 0.1% de candidatas que llegan
a produccion es estandar en la industria
del trading algoritmico.

---

## REGLAS PARA EL SQ-SPECIALIST

### En el Retester
Retestear TODAS las candidatas que pasan el
Evaluation Gate en lote. No seleccionar manualmente.
El paso 12b descarta automaticamente.

### En el Optimizer
Lanzar WFO para TODAS las que pasan el 12b.
No seleccionar manualmente.
El dictamen WFO descarta automaticamente.

### En la configuracion
Maximo 3 parametros a optimizar en el WFO.
Rangos estrechos centrados en valores del Builder.
Si el Builder encontro ATR mult = 2.3 el rango
del WFO seria 2.0 a 2.6 — no 1.0 a 5.0.

---

## REGLA FUNDAMENTAL

El sobreajuste se combate con validacion exigente
no con restriccion del espacio de busqueda.

Builder libre + pipeline estricto = estrategias robustas.
Builder restringido + pipeline flexible = 8 builds fallidos.