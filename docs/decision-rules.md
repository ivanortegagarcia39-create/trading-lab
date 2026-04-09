# Decision Rules — Criterios de Aprobacion de Estrategias

## Principio fundamental
Una estrategia no avanza por intuicion ni por
"parece prometedora". Solo avanza si cumple
criterios medibles en cada puerta del pipeline.

Las 4 decisiones posibles son siempre:
PASA / REVISAR / SIMPLIFICAR / DESCARTAR

---

## Umbrales minimos para FTMO 2-Step

| Metrica              | Minimo exigido     | Optimo            |
|----------------------|--------------------|-------------------|
| Profit Factor        | mayor de 1.5       | mayor de 2.0      |
| Max Drawdown         | menor del 7%       | menor del 5%      |
| Daily Drawdown       | menor del 3%       | menor del 2%      |
| Numero de trades     | minimo 100         | mas de 200        |
| Win Rate             | mayor del 40%      | mayor del 50%     |
| Ratio TP/SL          | minimo 2:1         | minimo 2.5:1      |
| Dias operando        | minimo 4 dias      | mas de 10 dias    |
| Trades por mes       | minimo 20          | mas de 30         |
| WFE Optimizer        | mayor del 50%      | mayor del 70%     |

---

## Criterios por fase del pipeline

### Fase Builder — Evaluation Gate

PASA si cumple TODOS:
- PF >= 1.5 con comisiones reales FTMO
- Max Drawdown < 7%
- Mas de 100 trades en el periodo de build
- Consistencia por anos > 70%
- La logica refleja la hipotesis original
- Ratio TP/SL >= 2:1

REVISAR si:
- PF entre 1.3 y 1.5 pero la logica es solida
- Drawdown ligeramente por encima pero corregible
- Pocos trades — se puede ampliar el periodo

SIMPLIFICAR si:
- Demasiados indicadores o condiciones (mas de 3)
- Resultado bueno pero estructura demasiado compleja
- Sospecha de curve-fitting

DESCARTAR si:
- PF menor de 1.3 con comisiones reales
- Drawdown supera el 7%
- Menos de 50 trades en el periodo completo
- La logica no tiene sentido economico
- Solo funciona en un periodo historico muy concreto

---

### Fase Retester — Out of Sample

PASA si cumple TODOS:
- PF out-of-sample >= 1.3
- PF no cae mas del 30% respecto al in-sample
- DD out-of-sample <= 7%
- Comportamiento consistente por trimestres

REVISAR si:
- PF cae entre 20% y 30%
- Un trimestre especifico da resultados muy malos
  pero el resto son consistentes

DESCARTAR si:
- PF out-of-sample cae mas del 30%
- DD out-of-sample supera el 7%
- Comportamiento completamente distinto
  entre in-sample y out-of-sample

---

### Fase Optimizer — Walk Forward

PASA si cumple TODOS:
- WFE mayor del 50%
- Ventanas out-of-sample consistentes
- Parametros optimos no estan en extremos del rango

DESCARTAR si:
- WFE menor del 40%
- Parametros optimos en extremos del rango
- Resultado bueno solo con una combinacion
  muy especifica de parametros

---

### Aprobacion final

PASA si cumple TODO:
- Ha superado Builder, Retester y Optimizer
- Cumple TODOS los umbrales de la tabla
- Funding-specialist confirma compatibilidad FTMO
- Decision humana final: SI

---

## Senales de alerta generales

Estas situaciones activan DESCARTAR
independientemente de las metricas:

- La estrategia solo funciona en 2 anos o menos
- El drawdown maximo ocurre en los ultimos meses
- Mas del 60% del beneficio viene de menos
  del 10% de las operaciones
- PF muy alto (>3) con pocos trades (<100)
- El resultado mejora drasticamente al ampliar el SL

---

## Regla de oro

Si hay duda entre PASA y REVISAR → siempre REVISAR.
Si hay duda entre REVISAR y DESCARTAR → siempre DESCARTAR.
Es mas facil generar una estrategia nueva que
arreglar una estrategia rota.

---

## Limite de revisiones

Una estrategia puede pasar por REVISAR maximo 2 veces.
A la tercera, DESCARTAR automaticamente.