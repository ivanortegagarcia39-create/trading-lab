# Skill: Checklist Pre-Build

## Proposito
Lista de verificacion obligatoria que el sq-specialist
debe completar ANTES de lanzar cualquier build en SQ.
Si algun punto falla — NO lanzar el build hasta corregirlo.

---

## BLOQUE 1 — VERIFICACION DE DATOS

[ ] Los datos del mercado estan importados en SQ
[ ] El simbolo correcto esta seleccionado en Builder
[ ] La fecha de inicio del build es correcta
[ ] La fecha de fin es 2020.12.31 o anterior
[ ] Los datos 2021-2026 NO estan incluidos en el build
[ ] El periodo cubre minimo 10 anos de datos
[ ] La temporalidad M1 disponible para conversion a H1

VERIFICACION EN SQ:
Gestor de datos → buscar simbolo → confirmar
que las fechas cubren el rango del build.

SEÑAL DE ALERTA:
Build termina en menos de 2 horas con mas de
200 estrategias → datos no cubren el periodo.
Detener y verificar.

---

## BLOQUE 2 — VERIFICACION DE HIPOTESIS

[ ] La hipotesis tiene todos los campos obligatorios
[ ] La logica se explica en una frase simple
[ ] Cada condicion verificada contra skill-sq-builder.md
[ ] No hay logica de rango de sesion asiatica
[ ] No hay logica de noticias economicas
[ ] No hay logica de dias de la semana en entradas
[ ] SL es ATR-based (no porcentaje fijo)
[ ] TP es ATR-based con ratio minimo 2:1 sobre el SL
[ ] Ventana de sesion minimo 6 horas
[ ] Temporalidad H1 confirmada — no M15
[ ] Funding-specialist ha confirmado compatibilidad FTMO

SEÑAL DE ALERTA:
Si la hipotesis menciona "rango asiatico",
"ruptura de apertura" o "nivel dinamico" →
revisar skill-sq-builder.md. Probablemente NO nativo.

---

## BLOQUE 3 — VERIFICACION DE CONFIGURACION EN SQ

### Tab Datos
[ ] Simbolo correcto segun hipotesis
[ ] Temporalidad: H1 (no M15)
[ ] Fecha inicio correcta
[ ] Fecha fin: 2020.12.31
[ ] Precision: 1 minute data tick simulation
[ ] Comisiones configuradas segun estandar FTMO:
    EUR/USD: 0.5 pips + 7 USD/lote + 0.5 pip slippage
    XAU/USD: 30 pips + 7 USD/lote + 2 pips slippage

### Tab Que construir
[ ] Tipo: Simple strategy (no Multi-TF)
[ ] Stop Loss required: ACTIVADO — ATR-based
[ ] Take Profit required: ACTIVADO — ATR-based ratio >= 2:1
[ ] Direcciones: Long y Short habilitados

### Tab Opciones geneticas
[ ] Max Generations: 20
[ ] Population Size: 50 por isla
[ ] Islands: 4
[ ] Start again when finished: DESACTIVADO
[ ] Filter initial population: sin filtro

### Tab Opciones de negociacion
[ ] Limitar intervalo de tiempo: ACTIVADO
[ ] Rango: 08:00 a 20:00 (minimo 6 horas)
[ ] Maximo trades por dia: 2
[ ] Salida al final del dia: ACTIVADO
[ ] No comercie fines de semana: ACTIVADO
[ ] Salida el viernes: ACTIVADO

### Tab Gestion del dinero
[ ] Metodo: Riesgo fijo en % de la cuenta
[ ] Riesgo por trade: 1%
[ ] Capital inicial: 25.000$

### Tab Clasificacion
[ ] Maximum strategies: 500
[ ] Filtro Factor de beneficio: > 0.8
[ ] Filtro Transacciones medias al mes: > 8
[ ] Filtro Ratio Ret/DD: > 0.5
[ ] Ranking: Aptitud ponderada
    PF: Maximice Peso 3
    Max Drawdown: Minimizar Peso 2
    Trades: Maximice Peso 1

### Tab Bloques de construccion
[ ] Signals: solo los de la hipotesis
[ ] Indicadores: solo los de la hipotesis
[ ] Operators: activados si hay indicadores
[ ] Tipos de salida: solo SL y TP requeridos
[ ] Tope dinamico: DESACTIVADO
[ ] Trailing: DESACTIVADO
[ ] Salida por barras: DESACTIVADO

### Tab Comprobaciones cruzadas
[ ] Mayor precision: ACTIVADO
[ ] Todo lo demas: DESACTIVADO

---

## BLOQUE 4 — VERIFICACION FINAL ANTES DE INICIO

[ ] Resumen en pestana Progreso muestra:
    - Simbolo correcto
    - Temporalidad H1
    - Fechas 2003-2020
    - Sesion 08:00-20:00
    - Risk 1% of account
    - Comisiones aplicadas
[ ] Commit de Git hecho antes de lanzar
[ ] Databank de resultados vacio antes de lanzar
[ ] Ordenador disponible durante el build
[ ] Build nocturno si dura mas de 4 horas

---

## BLOQUE 5 — MONITOREO DURANTE EL BUILD

### Primera revision a los 30 minutos
[ ] Estrategias generandose a ritmo normal
[ ] Tiempo estimado coherente (6-12h para 18 anos H1)
[ ] "En la base de datos" empieza a subir

SEÑAL DE ALERTA:
- 0 en databank con > 500 generadas → filtros estrictos
- Build termina en menos de 2 horas → datos insuficientes
- Error en pantalla → detener y revisar

### Si el build termina con malos resultados
1. Cuantas estrategias se generaron en total?
2. Cual es el PF maximo de las generadas?
3. Cual es el numero maximo de trades?

PF maximo < 1.2 → hipotesis no funciona
PF maximo 1.2-1.5 → filtros demasiado estrictos
Trades maximo < 30 → problema de datos o sesion corta

---

## TIEMPO ESTIMADO DE BUILD

5 anos M1 en H1: 1-2 horas
10 anos M1 en H1: 2-4 horas
15 anos M1 en H1: 4-8 horas
18 anos M1 en H1: 6-12 horas

Build termina mucho antes de lo estimado
→ datos no cubren el periodo completo.

---

## APRENDIZAJES CRITICOS

Build 1-2: logica asiatica no nativa en SQ
→ Verificar siempre contra skill-sq-builder.md

Build 3: filtros estrictos y 100 generaciones
→ Usar siempre 20 generaciones y 50 por isla

Build 4: sin comisiones reales
→ Comisiones FTMO obligatorias desde el Builder

Build 5-6: M15 con comisiones reales
→ H1 como temporalidad principal siempre

Build 7: primer build correcto con H1 y comisiones
→ Referencia para todos los builds futuros