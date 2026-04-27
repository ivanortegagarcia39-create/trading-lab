# Skill: Challenge Tracker FTMO — Seguimiento Diario

## Proposito
Protocolo para trackear el progreso diario de un challenge
FTMO 2-Step. Semaforo visual, umbrales de alerta, y cuándo
parar voluntariamente para proteger el capital.

---

## METRICAS DIARIAS A REGISTRAR

Cada dia de trading registrar estos valores:

| Metrica | Descripcion |
|---------|-------------|
| Balance actual | Saldo de la cuenta al cierre del dia |
| Equity actual | Balance + P&L flotante al cierre |
| Profit acumulado (USD) | Balance actual - Capital inicial |
| Profit acumulado (%) | Profit / Capital inicial * 100 |
| Objetivo (USD) | 10% del capital inicial |
| Progreso objetivo (%) | Profit acumulado / Objetivo * 100 |
| DD diario maximo hoy | Mayor caida intraday desde balance de medianoche |
| DD total maximo | Mayor caida desde pico historico de equity |
| Dias trading completados | Dias con al menos 1 posicion iniciada |
| Trades hoy | Numero de trades abiertos hoy |

### Calculos exactos (zona horaria Europe/Prague)

**DD diario:**
```
limite_diario = balance_medianoche_prague * 0.95
margen_restante_dia = equity_actual - limite_diario
dd_diario_pct = (balance_medianoche - equity_minima_hoy) / balance_medianoche * 100
```

**DD total dinamico:**
```
limite_total = pico_equity_historico * 0.90
margen_restante_total = equity_actual - limite_total
dd_total_pct = (pico_equity - equity_actual) / pico_equity * 100
```

IMPORTANTE: usar siempre medianoche de Prague (CET/CEST),
no medianoche UTC. Ver skill-ftmo-rules.md seccion Midnight Reset Bug.

---

## SEMAFORO DE ESTADO

### VERDE — Dentro de limites seguros
Condiciones (todas deben cumplirse):
- DD diario actual < 3%
- DD total actual < 5%
- Profit acumulado progresando
- Dias de trading >= dias transcurridos * 0.3

Accion: continuar segun plan. EA operando normal.

### AMARILLO — Precaucion
Condiciones (cualquiera activa el amarillo):
- DD diario entre 3% y 4.5%
- DD total entre 5% y 7.5%
- Profit acumulado < 50% del objetivo a la mitad del tiempo previsto
- Sin trades en los ultimos 5 dias

Accion:
1. Verificar que el EA esta funcionando correctamente
2. Revisar si hay noticias o eventos que expliquen el DD
3. No intervenir en la logica del EA
4. Activar monitoreo mas frecuente (cada hora en lugar de diario)

### ROJO — Riesgo de violacion
Condiciones (cualquiera activa el rojo):
- DD diario >= 4.5%
- DD total >= 7.5%
- Equity se acerca a menos de 300$ del limite diario
- Equity se acerca a menos de 500$ del limite total

Accion INMEDIATA:
1. Evaluar si detener el EA manualmente
2. Si hay posiciones abiertas con perdida flotante alta: cerrar manualmente
3. No abrir nuevas posiciones ese dia
4. Registrar el incidente en Obsidian con detalle

---

## CUANDO PARAR VOLUNTARIAMENTE

### Parar porque el objetivo esta cumplido
Si se cumplen AMBAS condiciones:
- Profit acumulado >= 10% del capital inicial
- Dias de trading completados >= 4

→ Detener el EA. No arriesgar el beneficio ganado.
→ Notificar al orchestrator para avanzar a Fase 2 (Verification).
→ No continuar operando "para ganar mas" — el objetivo esta cumplido.

### Parar para proteger el capital
Si se cumple CUALQUIERA:
- DD total supera 8% (margen de seguridad de 2% antes del limite)
- DD diario supera 4% en 2 dias seguidos
- El EA genera 3 dias seguidos negativos con DD > 2% por dia

→ Detener el EA.
→ Analizar las ultimas operaciones con strategy-analyzer.py.
→ Si el patron es sistematico → escalar a orchestrator para revision WFO.
→ Si es ruido de mercado → aguardar y reactivar en la siguiente sesion.

---

## REGISTRO EN OBSIDIAN — TEMPLATE DIARIO

Crear nota diaria en Obsidian con este template:

```markdown
# Challenge FTMO — [FECHA]

## Estado del Dia
- Semaforo: [VERDE / AMARILLO / ROJO]
- Balance actual: $[VALOR]
- Equity actual: $[VALOR]
- Profit acumulado: $[VALOR] ([PCT]%)
- Progreso objetivo: [PCT]% de $[OBJETIVO]

## Drawdown
- DD diario maximo hoy: [PCT]% ($[USD])
- DD total actual: [PCT]% ($[USD])
- Limite diario restante: $[USD]
- Limite total restante: $[USD]

## Trading
- Dias completados: [N] / 4 minimos
- Trades hoy: [N]
- PnL hoy: $[VALOR]

## Notas
[Observaciones relevantes — eventos, noticias, comportamiento del EA]

## Acciones Tomadas
[Si las hubo — solo si el semaforo fue AMARILLO o ROJO]
```

### Donde guardar en Obsidian
Ruta recomendada: `Trading/Challenges/[PROP-FIRM]/[CUENTA]/[FECHA].md`
Ejemplo: `Trading/Challenges/FTMO/25k-2026-04/2026-04-27.md`

---

## TABLA DE SEGUIMIENTO SEMANAL

Mantener una tabla en Obsidian con resumen semanal:

| Semana | Profit % | DD Total Max | DD Diario Max | Dias Trading | Trades | Estado |
|--------|----------|-------------|---------------|--------------|--------|--------|
| S1     |          |             |               |              |        |        |
| S2     |          |             |               |              |        |        |
| S3     |          |             |               |              |        |        |
| S4     |          |             |               |              |        |        |

---

## CRITERIOS DE ESCALADO AL ORCHESTRATOR

El humano escala al orchestrator cuando:
1. Semaforo ROJO por 2 dias consecutivos
2. El EA genera trades en horarios inesperados
3. Slippage observado difiere del backtest > 30%
4. Challenge en riesgo de fallo con > 7 dias restantes

En ningun otro caso el humano interviene en la logica del EA.

---

## HERRAMIENTAS DE SOPORTE

- `scripts/ftmo-dd-calculator.py --mode verify`: verificacion rapida de DD actual
- `scripts/ftmo-dd-calculator.py --mode simulate`: simulacion completa con historico
- `scripts/portfolio-monitor.py --mode report`: estado del portfolio completo
- Agente `performance-monitor`: monitoreo automatico en produccion
