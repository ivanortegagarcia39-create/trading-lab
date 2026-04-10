# Skill: Interpretacion del Walk-Forward Optimization

## Proposito
Guia para el sq-specialist y el orchestrator.
Permite interpretar correctamente los resultados
de una Walk-Forward Optimization (WFO) en SQ
y extraer conclusiones accionables.
Evita gastar horas de computo en estrategias
que no superaran la validacion final.

---

## CONCEPTOS CLAVE DEL WFO

### In-Sample (IS)
Periodo donde SQ optimiza los parametros.
El Builder busca los valores optimos dentro
del rango configurado para ese periodo.

### Out-of-Sample (OOS)
Periodo inmediatamente posterior al IS donde
se prueba la estrategia con los parametros
optimizados — datos que no vio durante la
optimizacion.
Este es el resultado que importa.

### Walk-Forward Efficiency (WFE)
Formula: (PF promedio OOS / PF promedio IS) x 100
Mide que porcentaje del rendimiento IS se mantiene
en datos no vistos.
Es la metrica mas importante del WFO.

---

## COMO LEER EL INFORME WFO DE SQ

SQ genera una tabla con filas para cada ventana.
Las columnas relevantes son:

| Ventana | IS PF | IS DD% | OOS PF | OOS DD% | Params optimos |
|---------|-------|--------|--------|---------|----------------|
| 1       | 1.85  | 4.2    | 1.62   | 5.1     | ATR=2.0 ADX=22 |
| 2       | 1.79  | 4.8    | 1.55   | 5.9     | ATR=2.1 ADX=20 |
| 3       | 1.91  | 3.8    | 1.48   | 6.2     | ATR=1.9 ADX=23 |
| 4       | 1.76  | 5.1    | 1.60   | 5.4     | ATR=2.0 ADX=21 |
| 5       | 1.82  | 4.5    | 1.55   | 5.7     | ATR=2.1 ADX=22 |
| MEDIA   | 1.83  | 4.5    | 1.56   | 5.7     | -              |

WFE = (1.56 / 1.83) x 100 = 85% → EXCELENTE

---

## CRITERIOS DE EVALUACION

### 1. Walk-Forward Efficiency (WFE)

WFE >= 70% → Excelente. Estrategia muy robusta.
WFE 50-70% → Buena. Aceptable para avanzar.
WFE 40-50% → Regular. Considerar simplificar.
WFE < 40% → Pobre. DESCARTAR o SIMPLIFICAR.

### 2. Estabilidad de parametros
Observar la columna de parametros optimos.
Si los valores oscilan ampliamente entre ventanas
el edge no es consistente.

Ejemplo estable (BUENO):
ATR mult: 2.0, 2.1, 1.9, 2.0, 2.1
Desviacion estandar: 0.08 → estable

Ejemplo inestable (MALO):
ATR mult: 1.5, 2.8, 1.6, 3.2, 1.4
Desviacion estandar: 0.82 → inestable

Regla practica: la desviacion estandar de cada
parametro optimizado debe ser menor al 20%
de su valor medio.

### 3. Rentabilidad OOS por ventana
Contar cuantas ventanas OOS tienen PF < 1.0:

0 ventanas negativas → OK
1 ventana negativa aislada → Precaucion
2 ventanas negativas consecutivas → DESCARTAR

Una ventana negativa aislada puede coincidir
con un cambio de regimen conocido (2008, 2020).
Dos consecutivas indican deterioro sistematico.

### 4. Drawdown OOS maximo
El DD OOS de CADA ventana debe ser <= 7%.
Si alguna ventana supera el 7% la estrategia
es demasiado arriesgada para FTMO.
Una sola ventana con DD OOS > 8% → DESCARTAR.

### 5. Ultima ventana OOS
La ultima ventana (la mas reciente) debe tener
rendimiento similar al promedio OOS.
Si es muy inferior al promedio → el edge podria
estar desapareciendo en datos recientes.
Accion: REVISAR con datos mas actualizados.

---

## PROTOCOLO DE ANALISIS PASO A PASO

### Paso 1: Calcular WFE
Sumar todos los PF OOS y dividir entre el numero
de ventanas → PF OOS promedio.
Sumar todos los PF IS y dividir → PF IS promedio.
WFE = (PF OOS promedio / PF IS promedio) x 100.

### Paso 2: Verificar estabilidad de parametros
Para cada parametro optimizado calcular la
desviacion entre ventanas.
Si alguno varia mas del 20% → señal de alerta.

### Paso 3: Contar ventanas OOS negativas
Identificar cuantas ventanas tienen PF < 1.0.
Verificar si son consecutivas o aisladas.

### Paso 4: Verificar DD OOS por ventana
Buscar si alguna ventana supera el 7% de DD.

### Paso 5: Analizar la ultima ventana
Comparar el PF de la ultima ventana con el promedio.
Si es inferior al 80% del promedio → alerta.

### Paso 6: Emitir dictamen

---

## DICTAMENES POSIBLES

### ROBUSTA → PASA
Criterios:
- WFE >= 50%
- 0 ventanas OOS negativas
- DD OOS < 7% en todas las ventanas
- Parametros estables (desv < 20%)
- Ultima ventana similar al promedio

### ACEPTABLE CON RESERVAS → REVISAR
Criterios:
- WFE entre 40% y 50%
- Maximo 1 ventana negativa aislada
- DD OOS < 7% en todas las ventanas
- Algunos parametros ligeramente inestables

Accion: reducir numero de parametros optimizados
y repetir el WFO con rango mas estrecho.

### INESTABLE → SIMPLIFICAR
Criterios:
- WFE < 40%
- 2 o mas ventanas negativas
- O alguna ventana con DD > 7%
- O parametros muy erraticos

Accion: volver al Builder con hipotesis simplificada
(menos condiciones o menos parametros).

### DESCARTAR
Criterios:
- WFE < 30%
- 2 ventanas negativas consecutivas
- DD OOS > 8% en alguna ventana
- Ultima ventana con PF < 1.0

Esta decision es definitiva para esta hipotesis.

---

## EJEMPLOS DE DICTAMENES

### Ejemplo 1 — ROBUSTA

Estrategia: TrendFollowing-EURUSD-H1-EMA50-ADX

| Metrica WFO         | Valor         |
|---------------------|---------------|
| WFE                 | 85%           |
| Ventanas negativas  | 0             |
| DD OOS maximo       | 5.9%          |
| Estabilidad params  | ATR: 2.0±0.1  |
| Ultima ventana PF   | 1.58 (prom 1.56) |

Dictamen: ROBUSTA. WFE excelente, sin ventanas
negativas, DD controlado. PASA a aprobacion.

### Ejemplo 2 — INESTABLE

Estrategia: NBARBreakout-EURUSD-H1-RSI

| Metrica WFO         | Valor         |
|---------------------|---------------|
| WFE                 | 38%           |
| Ventanas negativas  | 2 consecutivas|
| DD OOS maximo       | 8.2%          |
| Estabilidad params  | RSI: 7 a 21   |
| Ultima ventana PF   | 0.89          |

Dictamen: INESTABLE. WFE bajo, DD excesivo,
parametros erraticos. DESCARTAR.

---

## INTEGRACION CON EL PIPELINE

El sq-specialist genera el dictamen WFO y lo
guarda en:
strategyquant\optimizer\[nombre]-wfo-analysis.md

El orchestrator lee el dictamen y toma la decision:
- ROBUSTA → avanzar a aprobacion final
- ACEPTABLE → REVISAR y repetir WFO simplificado
- INESTABLE → SIMPLIFICAR y volver al Builder
- DESCARTAR → cerrar ticket y archivar

---

## REGLA DE ORO DEL WFO

La robustez no se puede crear con optimizacion.
O esta en la logica desde el principio o no esta.

Si el WFO falla → la solucion no es optimizar mas.
La solucion es simplificar la hipotesis y volver
al Builder con menos condiciones y parametros.