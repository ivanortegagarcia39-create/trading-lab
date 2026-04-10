# Skill: Parametros de Busqueda para Builder Libre

## Proposito anterior (OBSOLETO)
Guia para diseñar hipotesis manuales de estrategias
con indicadores especificos. Este enfoque causo
los 8 builds fallidos por sesgo humano.

## Proposito actual
Define los parametros de busqueda que el market-analyst
(configurador) debe establecer antes de lanzar el
Builder libre. NO define logica de entrada.
NO restringe indicadores. Solo define el marco
de riesgo dentro del cual SQ busca libremente.

---

## PARAMETROS QUE SE DEFINEN

### 1. Activo
Confirmado por market-selector.
Opciones actuales: EUR/USD o XAU/USD
No se elige por preferencia — se elige por
scoring de compatibilidad con prop firms.

### 2. Temporalidad
H1 unicamente.
M15 descartado tras Builds 1-6 con comisiones reales.

### 3. Periodo in-sample
2003.05.05 a 2020.12.31
Nunca modificar sin consenso.
Minimo 17 años de datos para robustez estadistica.

### 4. Periodo out-of-sample
2021.01.01 a fecha actual
Reservado exclusivamente para el Retester.
NUNCA incluir en el Builder.

### 5. Comisiones
Segun el activo — definidas en CLAUDE.md:
EUR/USD: 0.5 pips + 7 USD/lote + 0.5 pip slippage
XAU/USD: 30 pips + 7 USD/lote + 2 pips slippage

### 6. Restricciones de riesgo
- Riesgo por trade: 1% del balance
- Max trades por dia: 2
- Sesion: 08:00 a 20:00
- Capital: 25.000 USD
- SL: ATR-based, rango 1.5x a 3.0x
- TP: ATR-based, rango 3.0x a 6.0x
- Ratio TP/SL minimo: 200% del SL
- Salida al final del dia: ACTIVADO
- No fines de semana: ACTIVADO
- Salida viernes: ACTIVADO

### 7. Paleta de bloques
COMPLETA — todos los indicadores y señales
activados segun skill-builder-libre.md.
Sin restriccion. Sin seleccion manual.

### 8. Opciones geneticas
- Generaciones: 30 por ciclo
- Poblacion: 100 por isla
- Islas: 4
- Modo continuo: ACTIVADO
- Monte Carlo: ACTIVADO

### 9. Clasificacion
- Max estrategias: 1000
- Stop generation: Never
- PF minimo: 1.3
- Trades/mes minimo: 6
- Ratio Ret/DD minimo: 0.8

---

## PARAMETROS QUE NO SE DEFINEN

El market-analyst NO define ni sugiere:

- Que indicadores usar
- Que señales activar
- Que condiciones de entrada configurar
- Que tipo de estrategia buscar
  (trend-following o mean-reversion)
- Que patrones de mercado explorar
- Que combinaciones de indicadores probar

TODO esto lo decide SQ libremente.

---

## CUANDO MODIFICAR PARAMETROS DE BUSQUEDA

Los parametros solo se modifican en estos casos:

### Cambio de activo
Si el market-selector recomienda un activo
diferente → ajustar comisiones y simbolo.
Paleta de bloques sigue completa.

### Cambio de prop firm
Si el propfirm-analyst recomienda una prop firm
con reglas diferentes → ajustar restricciones
de riesgo (DD, dias minimos, etc).
Paleta de bloques sigue completa.

### Resultados insuficientes tras 72 horas
Si el Builder libre no genera suficientes
candidatas con PF > 1.3 tras 72 horas:
- Verificar datos con data-manager
- Verificar comisiones (error comun)
- Considerar ampliar rango de SL/TP
- NO restringir indicadores como solucion

### Expansion a nuevo activo
Cuando se añada GBP/USD, USD/JPY o futuros:
- Configurar comisiones especificas del activo
- Verificar datos con data-manager
- Paleta de bloques sigue completa
- Lanzar ciclo de Builder independiente

---

## FORMATO DE ARCHIVO DE CONFIGURACION

Cada ciclo de Builder genera un archivo en:
strategyquant\builder\build-[N]-config.md

El archivo contiene SOLO parametros de busqueda
y restricciones de riesgo. NUNCA contiene
indicadores sugeridos ni logica de entrada.

Si el archivo contiene frases como:
"Probar con EMA y ADX"
"Usar RSI como filtro"
"Hipotesis de trend following"
→ el archivo esta MAL y debe corregirse.

El archivo correcto dice:
"Builder libre con paleta completa.
Sin hipotesis. Sin restriccion de logica.
SQ decide la estrategia."

---

## VERIFICACION ANTES DE LANZAR

Antes de lanzar cada ciclo verificar:

[ ] Activo confirmado por market-selector
[ ] Datos verificados por data-manager
[ ] Comisiones correctas segun activo
[ ] Paleta COMPLETA de bloques activada
[ ] Ningun indicador desactivado manualmente
[ ] Modo continuo ACTIVADO
[ ] Monte Carlo ACTIVADO
[ ] Max estrategias: 1000
[ ] Stop generation: Never
[ ] Restricciones de riesgo correctas

Si alguno falla → corregir antes de lanzar.

---

## REGLA FUNDAMENTAL

Este archivo define el MARCO de busqueda.
SQ encuentra las ESTRATEGIAS.
El pipeline de validacion filtra el SOBREAJUSTE.
Ningun humano decide la logica de entrada.