# Skill: Capacidades Tecnicas de SQ Builder

## Proposito
Referencia tecnica de lo que SQ Builder puede
y no puede hacer nativamente. Esta skill la usa
el sq-specialist para verificar que la configuracion
del Builder libre es correcta.

NOTA: En el enfoque Builder libre esta skill
NO se usa para restringir indicadores.
Se usa unicamente para verificar que SQ puede
ejecutar correctamente la configuracion.

---

## LO QUE SQ BUILDER PUEDE HACER

### Indicadores nativos disponibles (paleta completa)

Grupo tendencia:
- EMA, SMA, WMA, DEMA, TEMA, HMA
- ADX, DMI, Aroon
- Parabolic SAR
- Ichimoku (parcial)
- MACD (como indicador de tendencia)

Grupo momentum:
- RSI, Stochastic, CCI
- Williams %R, DeMarker
- Momentum, ROC
- MACD (como oscilador)

Grupo volatilidad:
- ATR
- Bollinger Bands
- Keltner Channel
- Donchian Channel
- Standard Deviation

Grupo precio puro:
- High, Low, Close, Open
- HL2, HLC3
- Highest (maximo de N velas)
- Lowest (minimo de N velas)
- Range (rango de la vela)

### Señales que SQ puede construir
- Cruce de indicadores entre si
- Indicador por encima o por debajo de nivel
- Indicador subiendo o bajando
- Precio por encima o por debajo de indicador
- Comparacion entre dos indicadores
- Condiciones basadas en velas anteriores
- Precio rompe maximo o minimo de N velas
- Precio rompe bandas de Bollinger/Keltner/Donchian

### Condiciones de tiempo nativas
- Filtro de hora de inicio y fin de sesion
- No operar fines de semana
- Salida al final del dia
- Salida el viernes
- Maximo de trades por dia

### Gestion del dinero nativa
- Lote fijo
- Riesgo fijo en % de la cuenta
- SL fijo en pips o ATR-based
- TP fijo en pips o ATR-based
- Trailing Stop

---

## LO QUE SQ BUILDER NO PUEDE HACER

Estas limitaciones afectan al Builder libre
igual que al Builder con hipotesis:

1. RANGO DE SESION ESPECIFICA
   SQ no puede calcular max/min de un rango
   de horas especifico (ej: rango asiatico)

2. INDICADORES DE SESION ESPECIFICA
   SQ no puede calcular indicadores solo sobre
   velas de una sesion concreta

3. CALENDARIO ECONOMICO
   SQ no tiene filtro nativo de noticias

4. DIAS DE LA SEMANA EN ENTRADAS
   SQ no puede diferenciar lunes de viernes
   para logicas de entrada

5. CONDICIONES DEPENDIENTES EN TIEMPO REAL
   SQ no puede encadenar condiciones donde
   el resultado de una afecta a la siguiente

Estas limitaciones NO son un problema porque
el Builder libre busca entre lo que SQ SI puede
hacer — que son millones de combinaciones.

---

## CONFIGURACION TECNICA DEL BUILDER LIBRE

### Multi-activo
El Builder libre se lanza por activo individual.
No se mezclan activos en el mismo build.
Cada activo tiene su propio ciclo de 24-48 horas.

### Comisiones por activo
Definidas en CLAUDE.md y skill-builder-libre.md.
Cada activo tiene sus comisiones especificas.
Verificar siempre antes de lanzar.

### Comprobaciones cruzadas
Mayor precision: ACTIVADO siempre
Monte Carlo gestion operaciones: ACTIVADO siempre

---

## USO DE ESTA SKILL

Esta skill se usa SOLO para:
1. Verificar que SQ puede ejecutar la configuracion
2. Diagnosticar errores tecnicos durante el build
3. Confirmar que las comisiones son correctas

Esta skill NO se usa para:
1. Decidir que indicadores activar (todos activados)
2. Restringir el espacio de busqueda
3. Proponer logicas de entrada
4. Limitar las señales disponibles