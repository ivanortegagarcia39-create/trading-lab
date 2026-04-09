# Skill: Gestion de Datos Historicos

## Proposito
Guia para el data-manager y el sq-specialist.
Define como gestionar, verificar y actualizar
los datos historicos en StrategyQuant X.
Datos correctos = resultados fiables.
Datos incorrectos = decisiones equivocadas.

---

## PRINCIPIOS FUNDAMENTALES

1. Verificar datos ANTES de cada build
2. Datos desactualizados = resultados irreales
3. Gaps en datos = estrategias sobreajustadas
   a periodos sin datos
4. El periodo OOS (2021-2026) debe estar
   siempre actualizado hasta la fecha actual

---

## INVENTARIO DE DATOS DEL PROYECTO

### Datos activos
EUR/USD:
- Simbolo SQ: EURUSD_M1_dukas
- Fuente: Dukascopy
- Temporalidad base: M1
- Periodo requerido: 2003.05.05 a fecha actual
- Registros esperados: ~8-9 millones
- Uso: in-sample 2003-2020, OOS 2021-actual

XAU/USD:
- Simbolo SQ: XAUUSD_M1_dukas
- Fuente: Dukascopy
- Temporalidad base: M1
- Periodo requerido: 2003.05.05 a fecha actual
- Registros esperados: ~8-9 millones
- Uso: in-sample 2003-2020, OOS 2021-actual

### Datos pendientes Capa 1
GBP/USD:
- Simbolo SQ: GBPUSD_M1_dukas (cuando se descargue)
- Fuente: Dukascopy
- Estado: PENDIENTE

USD/JPY:
- Simbolo SQ: USDJPY_M1_dukas (cuando se descargue)
- Fuente: Dukascopy
- Estado: PENDIENTE

### Datos pendientes Capa 2
GC (Gold Futures CME):
- Fuente: necesita proveedor de datos CME
- Estado: PENDIENTE investigar fuente

NQ (Nasdaq Futures CME):
- Fuente: necesita proveedor de datos CME
- Estado: PENDIENTE investigar fuente

---

## VERIFICACION DE DATOS PRE-BUILD

### Paso 1: Abrir Gestor de datos en SQ
SQ → Gestor de datos (Data Manager)
Buscar el simbolo que se va a usar en el build.

### Paso 2: Verificar fechas
Campos a verificar:
- Fecha de: debe ser 2003.05.05 o anterior
- Fecha final: debe ser reciente (menos de 30 dias)

Si fecha final tiene mas de 30 dias → actualizar.
Si fecha de inicio es posterior a 2003 → datos
incompletos para el periodo in-sample completo.

### Paso 3: Verificar numero de registros
EUR/USD M1 completo (2003-2026):
- Esperado: ~8.6 millones de registros
- Minimo aceptable: 7 millones
- Si es muy inferior → datos incompletos

XAU/USD M1 completo (2003-2026):
- Esperado: ~8.5 millones de registros
- Minimo aceptable: 6.5 millones

### Paso 4: Verificar calidad visual
En Gestor de datos seleccionar el simbolo
y ver el grafico de datos disponibles.
Buscar visualmente:
- Gaps grandes (semanas o meses sin datos)
- Datos que terminan antes de lo esperado
- Periodos con muy poca actividad

### Paso 5: Decision
DATOS OK → proceder con el build
DATOS DESACTUALIZADOS → actualizar primero
DATOS INCOMPLETOS → descargar datos faltantes
DATOS NO DISPONIBLES → descargar desde Dukascopy

---

## COMO ACTUALIZAR DATOS EXISTENTES

Para actualizar EUR/USD o XAU/USD con
los ultimos dias/semanas de datos:

1. Abrir SQ → Gestor de datos
2. Seleccionar el simbolo (EURUSD_M1_dukas)
3. Clic en boton "Actualizar" o "Update"
4. SQ descargara automaticamente desde la
   ultima fecha disponible hasta hoy
5. Verificar que el numero de registros aumento
6. Tiempo estimado: 5-15 minutos

---

## COMO DESCARGAR DATOS NUEVOS

Para descargar un activo que no existe en SQ:

1. Abrir SQ → Gestor de datos
2. Clic en "Descargar datos" o "Download data"
3. Seleccionar proveedor: Dukascopy
4. Buscar el simbolo:
   - EUR/USD → EURUSD
   - GBP/USD → GBPUSD
   - XAU/USD → XAUUSD
   - USD/JPY → USDJPY
5. Seleccionar periodo:
   - Desde: 2003.01.01
   - Hasta: fecha actual
6. Seleccionar resolucion: M1 (1 minuto)
7. Iniciar descarga
8. Tiempo estimado: 30-60 minutos por simbolo

---

## CALIDAD DE DATOS DUKASCOPY

### Ventajas
- Datos M1 gratuitos desde 2003
- Alta calidad y completitud
- Actualizacion frecuente
- Compatible directamente con SQ

### Limitaciones
- Solo datos spot (no futuros CME)
- Algunos periodos muy antiguos pueden tener gaps
- Requiere conexion a internet para descargar

### Periodos con posibles gaps conocidos
- Crisis financiera 2008: algunos gaps en exoticos
- Fin de semana del 11-12 enero 2015 (CHF crisis)
- Marzo 2020 (COVID): volatilidad extrema pero
  datos completos generalmente

---

## CONVERSION DE TEMPORALIDADES EN SQ

SQ convierte automaticamente los datos M1 a
cualquier temporalidad superior:
M1 → M5, M15, M30, H1, H4, D1

Para usar H1 en el Builder:
- Seleccionar simbolo M1 (EURUSD_M1_dukas)
- En Tab Datos seleccionar temporalidad H1
- SQ convierte automaticamente en tiempo real
- NO es necesario descargar datos H1 por separado

---

## MANTENIMIENTO PERIODICO DE DATOS

### Antes de cada build
- Verificar que los datos estan actualizados
- Si han pasado mas de 30 dias → actualizar

### Mensualmente
- Actualizar todos los simbolos activos
- Verificar que el periodo OOS llega a fecha actual
- Documentar en strategyquant\databanks\

### Al añadir nuevo activo al universo
- Descargar datos completos desde 2003
- Verificar calidad y completitud
- Actualizar inventario en agents\data-manager.md
- Notificar al market-selector del nuevo activo

---

## SEÑALES DE PROBLEMAS EN LOS DATOS

### Build termina demasiado rapido
Sintoma: build de 18 anos termina en < 2 horas
Causa probable: datos no cubren el periodo completo
Accion: verificar fechas en Gestor de datos

### PF muy diferente entre builds del mismo activo
Sintoma: resultados inconsistentes entre builds
Causa probable: gaps en datos o datos corruptos
Accion: verificar calidad visual de los datos

### 0 trades en periodo especifico
Sintoma: Retester no genera trades en ciertos meses
Causa probable: gap en datos OOS
Accion: verificar datos del periodo 2021-2026

### Numero de registros muy bajo
Sintoma: menos de 5 millones de registros en M1
Causa probable: descarga incompleta
Accion: borrar y volver a descargar los datos

---

## ARCHIVO DE VERIFICACION

Antes de cada build crear archivo de verificacion:
strategyquant\databanks\data-check-[fecha]-[activo].md

Contenido minimo:
Fecha verificacion: [fecha]
Activo: [simbolo]
Simbolo en SQ: [nombre exacto]
Fecha inicio datos: [fecha]
Fecha fin datos: [fecha]
Numero de registros: [numero]
Gaps detectados: SI/NO — [detallar si SI]
Datos actualizados (< 30 dias): SI/NO
Decision: OK PARA BUILD / ACTUALIZAR PRIMERO