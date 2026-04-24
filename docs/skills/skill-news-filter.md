# Skill: Filtrado de Noticias y Eventos de Alto Impacto

## Proposito

Evitar que los EAs operen durante eventos de alta volatilidad
que pueden destruir el DD diario de un challenge en segundos.
El filtro de noticias es la ultima linea de defensa antes
de que el mercado cambie las reglas de golpe.

---

## EVENTOS A FILTRAR POR ACTIVO

### XAUUSD (Oro)
NFP (Non-Farm Payrolls), FOMC (decision de tipos Fed),
CPI (inflacion USA), PPI, GDP USA, ISM Manufacturing/Services.
El Oro reacciona con fuerza a cualquier dato macro de USA.

### EURUSD
ECB (decision de tipos BCE), IPC Eurozona,
GDP Eurozona, datos de empleo EU.

### Todos los activos
Eventos geopoliticos extremos (guerras, cierres de gobierno,
crisis bancarias sistemicas como SVB 2023).
Estos no aparecen en el calendario — se gestiona
via Dynamic Spread Protection (ver abajo).

---

## VENTANA DE PROTECCION

| Evento | Ventana antes | Ventana despues |
|--------|--------------|-----------------|
| Estandar (CPI, GDP, ISM) | -15 min | +15 min |
| NFP | -30 min | +30 min |
| FOMC | -30 min | +30 min |

Razon de la ventana previa:
El spread se amplifica antes del evento cuando los market makers
retiran liquidez anticipando el movimiento. Entrar antes del
evento es tan peligroso como durante el evento.

---

## DYNAMIC SPREAD PROTECTION

Proteccion independiente del calendario de noticias.
Cubre eventos no anunciados: flash crashes, eventos
geopoliticos repentinos, fallos de infraestructura.

Logica:
```
Si spread_actual > 3 * spread_promedio_activo:
  → Suspender nuevas entradas automaticamente
  → Mover stops de posiciones abiertas a break-even
  → Registrar el evento en results/production-logs/
```

El spread promedio de referencia es la media movil
del spread de las ultimas 100 velas H1 del activo.

Esta proteccion funciona 24/7 sin necesidad de API externa.
Es la proteccion mas robusta porque no depende de datos externos.

---

## CIERRE PREVENTIVO

Si hay posicion abierta y faltan 5 minutos para un evento
de alto impacto en el calendario:

Accion: cerrar la posicion al precio de mercado actual.
Razon: mejor perder el trade potencial que arriesgar
el DD de un challenge en un movimiento de 50-100 pips en segundos.

El cierre preventivo es automatico — no requiere intervencion humana.
El orchestrator registra el cierre en el audit trail como:
  "CIERRE PREVENTIVO — Evento: [nombre] a las [hora]"

---

## HORA BRUJA — ROLLOVER DIARIO

No abrir nuevos trades entre 22:55 y 00:05 CEST.
Cerrar trades abiertos a las 23:50 CEST si el EA
esta configurado sin holding overnight.

Razon: durante el rollover diario del broker los spreads
se multiplican por 3-5x durante 5-10 minutos.
El triple swap del miercoles amplifica este efecto.

La sincronizacion del rollover usa ftmo-timezone-sync.mq5
para el calculo correcto del horario Prague (CET/CEST).

---

## FIN DE SEMANA

Cerrar todas las posiciones el viernes a las 22:00 CEST.
No abrir nuevas posiciones despues de las 21:30 CEST del viernes.

Razon: los gaps del lunes al abrir el mercado pueden
superar el SL configurado. El broker puede ejecutar
el stop a un precio peor (slippage de gap).

Excepcion unica: estrategias Swing explicitamente validadas
para holding de fin de semana, con SL mas amplio configurado
y validado en el WFO con datos que incluyen gaps de lunes.

---

## FUENTE DE DATOS DEL CALENDARIO

Fuente primaria: ForexFactory API o Investing.com economic calendar.
Consultar via WebRequest desde el EA en MT5.
Frecuencia: al inicio de cada sesion de trading (08:00 CEST).

Si la API no esta disponible:
  Modo conservador automatico:
  No abrir trades en las horas de mayor riesgo estadistico:
  08:30 CEST (apertura Europa, datos UK/EU frecuentes)
  10:00 CEST (datos zona euro frecuentes)
  14:30 CEST (datos USA frecuentes — NFP, CPI, GDP)
  20:00 CEST (cierre de sesion — baja liquidez)

El modo conservador es menos preciso pero mas seguro que
operar sin informacion de noticias.

---

## INTEGRACION EN EL PIPELINE

El news-filter se integra como modulo del EA exportado.
El export-specialist verifica que el EA incluye:
  [ ] Ventana de proteccion configurable (default: 30 min)
  [ ] Dynamic Spread Protection (default: 3x spread medio)
  [ ] Cierre preventivo activo
  [ ] Bloqueo de rollover diario
  [ ] Bloqueo de fin de semana

Sin estos filtros el EA no se aprueba para challenge.

---

## LO QUE ESTA SKILL NUNCA HACE

NUNCA omite el filtro de NFP y FOMC.
NUNCA opera durante el rollover diario.
NUNCA mantiene posiciones abiertas el fin de semana
  sin validacion explicita de holding overnight.
NUNCA desactiva el Dynamic Spread Protection.
NUNCA depende exclusivamente del calendario externo —
  el Dynamic Spread Protection funciona sin API.
