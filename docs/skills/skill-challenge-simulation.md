# Skill: Protocolo de Simulacion de Challenge en Demo

## Filosofia

> "No se compra un challenge hasta que no se ha pasado
> en simulacion demo identica."

Esto elimina el riesgo de perder el coste del challenge
por errores detectables en demo. Si el sistema no puede
pasar el challenge en simulacion, no pasara el real.
Los numeros deciden. No la esperanza.

---

## Flujo completo del AutoDemoPipeline v3.0

```
Forward Test (3 criterios automaticos)
        |
        v
challenge-demo-simulator.py
  Simula Fase 1 (Challenge)
  Si PASS → simula Fase 2 (Verification)
        |
        v
challenge-verdict-generator
  PASS / FAIL / REVIEW
        |
   PASS |                    FAIL |                REVIEW |
        v                         v                        v
Telegram autorizacion     Causa raiz al KG        +2 semanas demo
Humano responde SI        Restriccion al Builder  Si mejora → PASS
Sistema registra          Estrategia descartada   Si no → FAIL
Comprar challenge
```

---

## Criterios de simulacion (mas estrictos que el challenge real)

Se aplica un margen de seguridad del 20% sobre los limites reales.
Si el sistema pasa con margen, el challenge real tiene mucho menos
probabilidad de fallar por eventos inesperados.

| Criterio | Limite Real FTMO | Limite Simulacion |
|----------|-----------------|-------------------|
| DD diario max | 5% | 4% |
| DD total max | 10% | 8% |
| Profit objetivo | +10% (Fase 1) | +10% (identico) |
| Profit objetivo | +5% (Fase 2) | +5% (identico) |
| PF minimo del periodo | — | 1.2 (criterio adicional) |

El margen existe porque el challenge real tiene eventos que
la simulacion no captura perfectamente (slippage real,
noticias inesperadas, problemas tecnicos). El margen de
seguridad del 20% compensa esa incertidumbre.

---

## Fase 1 — Preparacion

### Requisitos previos para iniciar simulacion
- [ ] Forward test completado con los 3 criterios automaticos aprobados
- [ ] Cuenta demo disponible en results/demo-accounts-inventory.json
- [ ] CSV de trades del forward test disponible con formato correcto
- [ ] Capital objetivo definido (tipicamente 10.000 USD para primer challenge)

### Formato del CSV de trades requerido
```
timestamp,pnl,balance
2026-04-01T09:15:00,45.50,10045.50
2026-04-01T14:30:00,-22.00,10023.50
...
```
- timestamp: ISO-8601 con hora exacta del cierre del trade
- pnl: ganancia o perdida del trade en USD (negativo = perdida)
- balance: balance de la cuenta tras el trade

### Comando de ejecucion
```bash
python scripts/challenge-demo-simulator.py \
    --trades-csv results/forward-test-[ID]-trades.csv \
    --propfirm ftmo_2step \
    --strategy-id XAUUSD_B11_S001 \
    --capital 10000 \
    --output results/
```

---

## Fase 2 — Ejecucion de la simulacion

El simulador opera tick a tick sobre los trades historicos:

### En cada trade calcula:
1. DD diario desde balance de apertura a las 00:00 Prague
2. DD total dinamico desde el equity maximo historico (FTMO)
   o desde el capital inicial (E8, tipo fixed)
3. Profit acumulado desde el inicio de la fase
4. Dias de trading completados (dias con al menos 1 trade)

### Si viola cualquier regla:
- FAIL inmediato con causa exacta
- Registro del estado en el momento del fallo
- No continua la simulacion

### Si alcanza el objetivo:
- Verifica que se han cumplido los dias minimos de trading
- Si si → PASS con metricas completas
- Si no → continua hasta cumplir los dias minimos

---

## Fase 3 — Veredicto automatico

El challenge-verdict-generator analiza el resultado del simulador.

### Score Final (0-100)

| Componente | Peso |
|------------|------|
| Profit alcanzado (ambas fases) | 30 pts |
| DD diario maximo Fase 1 | 20 pts |
| DD diario maximo Fase 2 | 20 pts |
| PF del periodo completo | 20 pts |
| Eficiencia temporal | 10 pts |

Score >= 70 → PASS EXCELENTE
Score 50-69 → PASS ACEPTABLE
Score < 50 → REVIEW (aunque tecnicamente haya pasado)

### Accion por veredicto

**PASS:**
- Sistema genera notificacion Telegram con todos los datos
- Humano responde SI → sistema registra autorizacion con timestamp
- Humano compra el challenge manualmente

**FAIL:**
- Causa raiz registrada en Knowledge Graph
- Restriccion especifica anadida para el Builder del siguiente ciclo
- Estrategia marcada como DESCARTADA — sin segunda oportunidad

**REVIEW:**
- orchestrator extiende simulacion 2 semanas adicionales
- Se generan nuevos trades del forward test extendido
- Si tras la extension: PASS → proceder, FAIL → descartar definitivamente

---

## Fase 4 — Autorizacion humana (unico paso manual)

Cuando el veredicto es PASS, el sistema envia:

```
CHALLENGE SIMULADO SUPERADO

Estrategia: [ID]
Prop Firm:  [nombre] | Cuenta: [capital] USD

Fase 1 — Challenge:
  Duracion:      [X] dias de trading
  Profit:        +[X]%
  DD Diario Max: [X]%
  DD Total Max:  [X]%
  Resultado:     PASADA

Fase 2 — Verification:
  Duracion:      [X] dias de trading
  Profit:        +[X]%
  DD Diario Max: [X]%
  DD Total Max:  [X]%
  Resultado:     PASADA

PF del periodo: [X]
Score Final:    [X]/100

Autorizar compra del challenge?
Responder SI para confirmar.
```

El humano responde "SI" al bot de Telegram.
El sistema registra la autorizacion en el audit trail con timestamp y hash.

**Timeout:** si el humano no responde en 72 horas:
- Estrategia pasa a cola de espera
- Pipeline lanza nuevo ciclo automaticamente

---

## Restricciones al Builder segun causa de FAIL

El sistema aprende automaticamente de cada fallo:

| Causa de fallo | Restriccion anadida |
|----------------|---------------------|
| DD diario > 4% | Reducir riesgo por trade a 0.5% proxima iteracion |
| DD total > 8% | Exigir max_dd_oos < 5% en proximas candidatas |
| Profit no alcanzado | Exigir PF OOS >= 1.4 en proximas candidatas |
| PF < 1.0 | Exigir PF IS >= 1.8 en proximas candidatas |

Estas restricciones se guardan en results/builder-restrictions.json.

---

## Reglas inquebrantables

1. Sin simulacion aprobada → sin compra de challenge
2. La simulacion usa margenes de seguridad del 20% — no se reducen
3. FAIL en simulacion = DESCARTADA — sin segunda oportunidad en el mismo ciclo
4. REVIEW puede extenderse maximo UNA vez — si no mejora → FAIL definitivo
5. La autorizacion humana es solo para confirmar "SI" — no para opinar sobre los numeros
6. Si la cuenta demo expira durante la simulacion → la simulacion es invalida
7. Una cuenta demo = una estrategia — nunca dos simultaneas

---

## Referencias

- `scripts/challenge-demo-simulator.py` — motor de simulacion
- `config/propfirm-rules.json` — reglas exactas de cada prop firm
- `agents/challenge-verdict-generator.md` — emite el veredicto final
- `agents/demo-account-factory.md` — gestion de cuentas demo
- `agents/orchestrator.md` — coordina el pipeline completo
- `docs/skills/skill-forward-test-protocol.md` — protocolo previo (forward test)
- `results/demo-accounts-inventory.json` — inventario de cuentas demo
