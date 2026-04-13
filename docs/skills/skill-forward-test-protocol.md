# Skill: Protocolo de Forward Test en Demo

## Proposito
Define el procedimiento objetivo para el forward test
en cuenta demo — la unica intervencion humana del
pipeline. Sin protocolo objetivo el humano decidira
con intuicion y eso es sesgo.
Este protocolo convierte el forward test en una
verificacion tecnica con criterios numericos
— no en una decision subjetiva.

---

## QUE VERIFICA EL FORWARD TEST

El forward test NO evalua si la estrategia es buena.
Eso ya lo decidieron los numeros en el pipeline.

El forward test verifica SOLO que:
1. El EA ejecuta las operaciones correctamente
2. Los SL y TP se activan en los niveles correctos
3. El tamaño de posicion es correcto
4. El EA respeta las restricciones operativas
5. No hay errores tecnicos de ejecucion

Si el EA funciona tecnicamente → LANZAR CHALLENGE.
Si el EA tiene errores tecnicos → CORREGIR Y REPETIR.
No hay decision subjetiva sobre "si la estrategia
es buena o no" — eso ya esta decidido.

---

## DURACION

Minimo: 2 semanas (10 dias habiles)
Maximo: 4 semanas

Si el EA no genera ningun trade en 2 semanas
→ extender 1 semana mas.
Si no genera trades en 3 semanas → revisar
configuracion tecnica (simbolo, horario, etc).

---

## CONFIGURACION DE LA CUENTA DEMO

### Paso 1: Obtener cuenta demo de la prop firm
- FTMO: crear cuenta demo gratuita en ftmo.com
- E8: cuenta demo desde su web
- Usar la cuenta demo de la MISMA prop firm
  donde se hara el challenge real

### Paso 2: Conectar MT5 al servidor demo
- Abrir MT5
- File → Open an Account
- Buscar el broker de la prop firm
- Usar credenciales de la cuenta demo

### Paso 3: Verificar simbolo
- Abrir Market Watch en MT5
- Buscar el activo exacto (puede tener sufijo)
- Anotar el nombre exacto del simbolo
- Comparar con el simbolo del backtest

### Paso 4: Activar EA
- Abrir grafico del activo en H1
- Arrastrar el EA al grafico
- Configurar parametros segun Version 3 (trazabilidad)
- Activar AutoTrading (boton verde)
- Verificar cara sonriente en esquina del grafico

---

## CHECKLIST DIARIO (objetivo — sin subjetividad)

Cada dia a las 21:00 (tras cierre de sesion)
completar este checklist:

### Verificaciones tecnicas
[ ] MT5 conectado al servidor: SI/NO
[ ] EA activo (cara sonriente): SI/NO
[ ] AutoTrading activado (boton verde): SI/NO
[ ] No hay errores en Journal de MT5: SI/NO

### Operaciones del dia
Trades abiertos hoy: [numero]
Trades cerrados hoy: [numero]
Resultado del dia: [+/- USD] ([+/- %])

### Verificacion de ejecucion
Para CADA trade cerrado verificar:
[ ] SL se activo en el nivel correcto: SI/NO
[ ] TP se activo en el nivel correcto: SI/NO
[ ] Tamaño de posicion correcto (1% riesgo): SI/NO
[ ] Horario dentro de 08:00-20:00: SI/NO
[ ] No opero fin de semana: SI/NO
[ ] Max 2 trades por dia respetado: SI/NO

### Registro
Guardar en:
results\approved\[ID]-forward-test-log.md

Formato por dia:
Dia [N] — [fecha]
MT5 conectado: SI
EA activo: SI
Trades: [N] abiertos, [N] cerrados
Resultado: [+/- USD]
SL/TP correctos: SI/NO
Tamaño posicion: SI/NO
Horario respetado: SI/NO
Errores: [ninguno / descripcion]

---

## CRITERIOS DE APROBACION (objetivos)

### El EA PASA el forward test si cumple TODOS:
[ ] Minimo 5 trades ejecutados en las 2 semanas
[ ] SL y TP se activaron correctamente en el 100%
    de los trades cerrados por SL o TP
[ ] Tamaño de posicion correcto en el 100% de trades
[ ] Horario 08:00-20:00 respetado en el 100% de trades
[ ] Max 2 trades/dia respetado en el 100% de dias
[ ] No opero fines de semana
[ ] 0 errores tecnicos en Journal de MT5
[ ] EA estuvo activo el 100% del tiempo (sin caidas)

### El EA NO PASA si cumple CUALQUIERA:
[ ] SL o TP no se activo correctamente en algun trade
[ ] Tamaño de posicion incorrecto en algun trade
[ ] Opero fuera de horario
[ ] Opero mas de 2 trades en un dia
[ ] Opero en fin de semana
[ ] Errores tecnicos en Journal de MT5
[ ] EA se desactivo solo durante el periodo

---

## LO QUE NO SE EVALUA EN EL FORWARD TEST

El forward test NO evalua:
- Si la estrategia gana o pierde dinero
- Si el PF del periodo es bueno o malo
- Si el DD es aceptable
- Si el win rate es suficiente

TODO eso ya lo evaluaron los numeros del pipeline.
2 semanas de forward test NO son estadisticamente
significativas para evaluar rendimiento.

Un EA que pierde dinero en las 2 semanas de demo
pero funciona tecnicamente → PASA.

Un EA que gana dinero pero tiene errores tecnicos
→ NO PASA hasta corregir los errores.

---

## QUE HACER SI NO HAY TRADES EN 2 SEMANAS

Posibles causas:
1. Simbolo incorrecto en MT5
   → verificar nombre exacto del activo
2. Temporalidad incorrecta (no H1)
   → verificar que el grafico es H1
3. EA no activado correctamente
   → verificar cara sonriente y AutoTrading
4. Horario de trading muy restrictivo
   → verificar configuracion 08:00-20:00
5. Mercado en periodo de baja volatilidad
   → esperar 1 semana mas (total 3 semanas)

Si tras 3 semanas sigue sin trades:
→ revisar la exportacion con export-specialist
→ comparar parametros del EA con Version 2

---

## QUE HACER SI EL EA FALLA

### Error de ejecucion de SL/TP
Causa probable: diferencia entre simbolo del
backtest y simbolo del broker.
Solucion: verificar pip size y ajustar parametros.

### Tamaño de posicion incorrecto
Causa probable: money management configurado
como lote fijo en vez de riesgo porcentual.
Solucion: cambiar a riesgo % en parametros EA.

### Opera fuera de horario
Causa probable: diferencia de zona horaria entre
SQ (UTC) y MT5 (hora del broker).
Solucion: ajustar horario en parametros EA
considerando la diferencia horaria.

### Opera en fin de semana
Causa probable: parametro de fin de semana
no configurado correctamente en el EA.
Solucion: verificar parametro en codigo MQL5.

### Correccion y repeticion
1. Identificar el error exacto
2. Corregir en el codigo MQL5 o parametros
3. Recompilar si se cambio el codigo
4. REINICIAR el forward test desde cero
   (las 2 semanas empiezan de nuevo)
5. No continuar con un test parcial corregido

---

## RESULTADO FINAL DEL FORWARD TEST

Guardar en:
results\approved\[ID]-forward-test-resultado.md

Formato:
Estrategia: [ID]
Activo: [simbolo]
Prop firm: [nombre]
Periodo test: [fecha inicio] a [fecha fin]
Dias habiles: [numero]

TRADES EJECUTADOS:
- Total: [numero]
- Cerrados por TP: [numero]
- Cerrados por SL: [numero]
- Abiertos al final: [numero]

VERIFICACIONES TECNICAS:
- SL/TP correctos: [100% / porcentaje]
- Tamaño posicion correcto: [100% / porcentaje]
- Horario respetado: [100% / porcentaje]
- Max trades/dia respetado: [100% / porcentaje]
- No fines de semana: SI/NO
- Errores tecnicos: [0 / numero]
- EA activo continuamente: SI/NO

RENDIMIENTO (solo informativo — no decisivo):
- PF del periodo: [valor]
- DD del periodo: [valor]%
- Resultado neto: [+/- USD]

RESULTADO:
[ ] PASA — EA funciona correctamente
    Accion: LANZAR CHALLENGE
[ ] NO PASA — errores detectados
    Accion: corregir y repetir test desde cero

Verificado por: humano (unica intervencion del pipeline)

---

## REGLA FUNDAMENTAL

El forward test verifica funcionamiento tecnico.
No evalua si la estrategia es buena o mala.
Los numeros del pipeline ya decidieron que es buena.
El humano solo confirma que el EA ejecuta
correctamente lo que los numeros aprobaron.
Si funciona tecnicamente → se lanza.
Si no funciona → se corrige y se repite.
Sin opinion. Sin intuicion. Sin sesgo.