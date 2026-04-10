# Skill: Evitar el Sobreajuste (Overfitting)

## Proposito
Proporcionar criterios para que market-analyst y sq-specialist
diseñen estrategias con menor riesgo de sobreajuste desde
el propio diseño de la hipotesis.
Una hipotesis bien diseñada desde el principio reduce
drasticamente la necesidad de filtros posteriores y
aumenta la tasa de exito en el pipeline.

---

## POR QUE ES CRITICO EVITAR EL SOBREAJUSTE

El sobreajuste ocurre cuando una estrategia aprende
el ruido historico en lugar del edge real del mercado.
Resultado: excelente en backtest, terrible en real.

Los Builds 1-6 de TradingLab mostraron este patron:
- Build 4: PF 1.53-1.70 sin comisiones → Retester negativo
- Build 5: PF 1.27 con comisiones → edge insuficiente
El problema no era la configuracion sino el diseño
de la hipotesis desde el origen.

---

## PRINCIPIOS FUNDAMENTALES

### 1. Pocos grados de libertad
Cada condicion de entrada añade un grado de libertad.
Maximo recomendado: 3 condiciones logicas incluyendo filtros.
Mas condiciones = mas posibilidades de ajustarse al ruido.

### 2. Parametros con sentido economico
Usar valores estandar justificados por la teoria:
- RSI periodo 14 (estandar de Wilder)
- ATR periodo 14 (estandar)
- EMA 50 o 200 (niveles psicologicos del mercado)
NO optimizar entre 10 y 20 sin justificacion economica.

### 3. Evitar la optimizacion del ruido
Si una hipotesis funciona solo con un conjunto muy
estrecho de valores (ej. EMA exactamente 47 periodos)
es casi seguro que esta capturando ruido historico.
Señal de alerta: el optimo esta en el extremo del rango.

### 4. Simetria logica
La logica de entrada para largos y cortos debe ser
simetrica salvo que haya una razon economica clara.
Una estrategia que solo funciona en largo suele
estar capturando un sesgo del periodo historico.

---

## CHECKLIST PARA EL MARKET-ANALYST
(completar antes de enviar hipotesis al sq-specialist)

[ ] El numero de indicadores distintos es <= 3
[ ] Cada indicador tiene una razon de mercado clara:
    tendencia (EMA, ADX), momentum (RSI), volatilidad (ATR)
[ ] La mayoria de los parametros estan fijados a valores
    estandar sin necesidad de optimizacion
[ ] La logica de entrada es simetrica para largos y cortos
    o la asimetria esta justificada por estructura del mercado
[ ] Los costes de transaccion estan considerados en el diseño
    (un TP muy ajustado puede ser anulado por spread)
[ ] La hipotesis funciona en lenguaje natural sin ambiguedades
[ ] El edge tiene una explicacion economica real:
    ¿por que deberia funcionar este patron en el mercado?

---

## CHECKLIST PARA EL SQ-SPECIALIST
(completar durante configuracion del Builder)

[ ] El rango de optimizacion de cada parametro es estrecho
    Ejemplo correcto: multiplicador SL entre 1.8 y 2.2
    Ejemplo incorrecto: multiplicador SL entre 1.0 y 5.0
[ ] El numero maximo de condiciones en Builder es <= 3
[ ] Los bloques de construccion activados corresponden
    exactamente a la hipotesis — sin bloques extra
[ ] Las opciones geneticas usan poblaciones moderadas:
    20 generaciones y 50 por isla (ni mas ni menos)
[ ] Se ha verificado contra skill-sq-builder.md que
    cada condicion es nativa en SQ Builder

---

## SEÑALES DE ALARMA DURANTE EVALUACION DE RESULTADOS

### Alta sensibilidad a parametros
Si un cambio de ±0.1 en un multiplicador hace que el PF
caiga de 1.8 a 0.9 la estrategia es fragil.
Accion: SIMPLIFICAR o DESCARTAR.

### Rendimiento concentrado en un año atipico
Excelente en 2008 (crisis) pero mediocre en el resto.
Excelente en 2020 (COVID) pero sin edge en periodos normales.
Accion: DESCARTAR — el edge es especifico del regimen.

### Pocas operaciones con alta rentabilidad
Menos de 100 operaciones en 10 años es insuficiente
para validar un edge estadisticamente.
Accion: DESCARTAR o ajustar para generar mas señales.

### Parametro optimo en extremo del rango
Si el Builder encuentra que el optimo es el valor
maximo o minimo del rango configurado significa que
la optimizacion no ha convergido — el edge podria
estar fuera del rango o no existir.
Accion: REVISAR el rango o SIMPLIFICAR la hipotesis.

### Curva de equity con tramos muy largos sin operaciones
Si la estrategia no opera durante meses el edge
puede ser muy especifico de un regimen de mercado.
Accion: Verificar consistencia por años en Evaluation Gate.

---

## REGLAS PARA REDUCIR SOBREAJUSTE EN EL BUILDER

### Regla 1 — Menos bloques es mejor
Activar solo los bloques de construccion que
corresponden exactamente a la hipotesis.
No dejar bloques extra activados por si acaso.
Cada bloque adicional es un grado de libertad extra.

### Regla 2 — Rangos de parametros estrechos
El rango de cada parametro debe centrarse en el
valor estandar con ±20% de variacion maxima.
Ejemplo para multiplicador ATR:
- Valor estandar: 2.0
- Rango correcto: 1.6 a 2.4
- Rango incorrecto: 1.0 a 5.0

### Regla 3 — Verificar consistencia por periodos
Una estrategia robusta funciona en la mayoria de
los años del periodo in-sample, no solo en algunos.
Umbral minimo: 70% de los años con PF positivo.

### Regla 4 — Comparar IS vs OOS como test de robustez
Si el PF cae mas del 20% entre IS y OOS la estrategia
probablemente esta sobreajustada al periodo IS.
Este es el test mas importante de todos.

---

## HIPOTESIS CON BAJO RIESGO DE SOBREAJUSTE

Estas estructuras tienen menor riesgo por naturaleza:

### Trend Following simple (RECOMENDADA)
- 1 indicador de tendencia (EMA o ADX)
- 1 indicador de confirmacion (RSI o precio)
- SL y TP basados en ATR
- Logica simetrica para largos y cortos
- Riesgo de sobreajuste: BAJO

### NBAR Breakout con filtro
- Ruptura de maximo o minimo de N velas
- 1 filtro de confirmacion (RSI o ADX)
- SL en minimo o maximo de N velas
- TP = ratio fijo sobre SL
- Riesgo de sobreajuste: BAJO-MEDIO

### Mean Reversion con RSI extremos
- RSI en zona extrema (<30 o >70)
- 1 filtro de tendencia (EMA larga)
- SL y TP basados en ATR
- Riesgo de sobreajuste: MEDIO
  (depende del regimen de mercado)

---

## CONFIRMACION FINAL

Al terminar de diseñar la hipotesis el market-analyst
debe confirmar expresamente:

"Verificado contra skill-avoiding-overfitting.md
— riesgo de sobreajuste: BAJO / MEDIO / ALTO"

Si el riesgo es ALTO → rediseñar la hipotesis
antes de pasarla al sq-specialist.