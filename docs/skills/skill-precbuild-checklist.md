# Skill: Checklist Pre-Build — Builder Libre

## Proposito
Lista de verificacion obligatoria que el sq-specialist
debe completar ANTES de lanzar cualquier build libre.
Si algun punto falla — NO lanzar hasta corregirlo.

NOTA: Este checklist es para el Builder libre.
No hay verificacion de hipotesis porque no hay
hipotesis. SQ decide la logica libremente.

---

## BLOQUE 1 — VERIFICACION DE DATOS

[ ] data-manager ha verificado los datos del activo
[ ] El simbolo correcto esta seleccionado en Builder
[ ] La fecha de inicio es 2003.05.05 o anterior
[ ] La fecha de fin es 2020.12.31
[ ] Los datos 2021-actual NO estan incluidos en el build
[ ] El periodo cubre minimo 17 anos de datos
[ ] La temporalidad M1 disponible para conversion a H1

VERIFICACION EN SQ:
Gestor de datos → buscar simbolo → confirmar
que las fechas cubren el rango completo.

SEÑAL DE ALERTA:
Build termina en menos de 2 horas con mas de
200 estrategias → datos no cubren el periodo.
Detener y verificar.

---

## BLOQUE 2 — VERIFICACION DE CONFIGURACION BUILDER LIBRE

### Tab Datos
[ ] Simbolo correcto segun market-selector
[ ] Temporalidad: H1
[ ] Fecha inicio: 2003.05.05
[ ] Fecha fin: 2020.12.31
[ ] Precision: 1 minute data tick simulation
[ ] Comisiones configuradas segun activo:
    Verificar en CLAUDE.md las comisiones exactas
    del activo seleccionado

### Tab Que construir
[ ] Tipo: Simple strategy
[ ] Condiciones de entrada: Min 1, Max 3
[ ] Stop Loss required: ACTIVADO — ATR-based
    Multiplicador: 1.5 a 3.0
[ ] Take Profit required: ACTIVADO — ATR-based
    Multiplicador: 3.0 a 6.0
    Ratio minimo sobre SL: 200%
[ ] Direcciones: Long y Short habilitados

### Tab Bloques de construccion
[ ] TODOS los indicadores de tendencia activados
[ ] TODOS los indicadores de momentum activados
[ ] TODOS los indicadores de volatilidad activados
[ ] TODOS los indicadores de precio puro activados
[ ] TODAS las señales predefinidas activadas
[ ] TODOS los operators activados
[ ] Ningun bloque desactivado manualmente
[ ] Tipos de salida: solo SL y TP requeridos
[ ] Tope dinamico: DESACTIVADO
[ ] Trailing: DESACTIVADO
[ ] Salida por barras: DESACTIVADO

CRITICO: Si algun indicador o señal esta
desactivado manualmente el build tiene sesgo
humano. Activar TODO sin excepcion.

### Tab Opciones geneticas
[ ] Max Generations: 30
[ ] Population Size: 100 por isla
[ ] Islands: 4
[ ] Start again when finished: ACTIVADO
[ ] Filter initial population: sin filtro

### Tab Opciones de negociacion
[ ] Limitar intervalo de tiempo: ACTIVADO
[ ] Rango: 08:00 a 20:00
[ ] Maximo trades por dia: 2
[ ] Salida al final del dia: ACTIVADO
[ ] No comercie fines de semana: ACTIVADO
[ ] Salida el viernes: ACTIVADO

### Tab Gestion del dinero
[ ] Metodo: Riesgo fijo en % de la cuenta
[ ] Riesgo por trade: 1%
[ ] Capital inicial: 25.000$

### Tab Clasificacion
[ ] Maximum strategies: 1000
[ ] Stop generation: Never
[ ] Factor de beneficio: > 1.3
[ ] Transacciones medias al mes: > 6
[ ] Ratio Ret/DD: > 0.8
[ ] Ranking: Aptitud ponderada
    PF: Maximice Peso 3
    Max Drawdown: Minimizar Peso 2
    Trades: Maximice Peso 1

### Tab Comprobaciones cruzadas
[ ] Mayor precision: ACTIVADO
[ ] Monte Carlo gestion de operaciones: ACTIVADO
[ ] Todo lo demas: DESACTIVADO

---

## BLOQUE 3 — VERIFICACION FINAL ANTES DE INICIO

[ ] Resumen en pestana Progreso muestra:
    - Simbolo correcto
    - Temporalidad H1
    - Fechas 2003-2020
    - Sesion 08:00-20:00
    - Risk 1% of account
    - Comisiones aplicadas
    - Start again: ACTIVADO
    - Stop generation: Never
    - Monte Carlo: ACTIVADO
    - Max strategies: 1000
[ ] Commit de Git hecho antes de lanzar
[ ] Ordenador disponible durante 24-48 horas
[ ] Paleta COMPLETA de bloques verificada

---

## BLOQUE 4 — MONITOREO DURANTE EL BUILD

### Primera revision a los 60 minutos
[ ] Estrategias generandose a ritmo normal
[ ] Candidatas empezando a aparecer en databank
[ ] PF maximo del databank subiendo

### Señales de que todo va bien
- Candidatas con PF > 1.3 aparecen en el databank
- El numero de candidatas crece cada hora
- PF maximo sigue subiendo periodicamente

### Señales de problema
- 0 candidatas en databank tras 4 horas
  → Verificar comisiones (error mas comun)
  → Verificar que los datos cubren el periodo
  → NO restringir bloques como solucion
- Build termina solo antes de 2 horas
  → Datos insuficientes — verificar con data-manager

---

## CUANDO PARAR EL BUILD

Señales de que es momento de parar:
1. PF maximo no mejora en 6+ horas consecutivas
2. Se han completado mas de 5 ciclos completos
3. Hay mas de 50 candidatas con PF > 1.5
4. Han pasado 72 horas

Señales de que hay que seguir:
1. PF maximo sigue subiendo cada hora
2. El databank se llena rapidamente
3. Menos de 20 candidatas con PF > 1.5
4. Menos de 24 horas de ejecucion

---

## TIEMPO ESTIMADO DE BUILD

Modo continuo por ciclo (30 gen x 100 x 4 islas):
- 1 ciclo: 6-12 horas segun activo
- 24 horas: 2-4 ciclos completos
- 48 horas: 4-8 ciclos completos
- 72 horas: 6-12 ciclos completos

Recomendacion minima: 48 horas.
El Builder libre necesita mas tiempo que el
Builder con hipotesis porque explora un espacio
de busqueda mucho mayor.

---

## DIFERENCIAS CON EL CHECKLIST ANTERIOR

| Aspecto | Antes | Ahora |
|---------|-------|-------|
| Verificacion hipotesis | Obligatoria | NO EXISTE |
| Bloques activados | Solo los de la hipotesis | TODOS |
| Generaciones | 20 | 30 por ciclo |
| Poblacion | 50 por isla | 100 por isla |
| Modo | Se para solo | Continuo |
| Max estrategias | 500 | 1000 |
| PF filtro | > 0.8 | > 1.3 |
| Monte Carlo | Desactivado | ACTIVADO |
| Stop generation | Databank full | Never |

---

## REGLA FUNDAMENTAL

El checklist verifica configuracion tecnica
y restricciones de riesgo.
NO verifica logica de entrada — no hay logica
predefinida. SQ decide libremente.
Si alguien pide verificar la hipotesis antes
del build → recordar que no hay hipotesis.
Builder libre. Sin sesgo humano.