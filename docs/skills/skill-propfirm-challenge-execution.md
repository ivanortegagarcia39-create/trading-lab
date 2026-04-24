# Skill: Ejecucion del Challenge en Prop Firm

## Proposito
Define el flujo completo de un challenge desde que el
pipeline genera la notificacion de autorizacion hasta
que la cuenta pasa a funded y entra en modo scaling.
Guia para el orchestrator, propfirm-analyst y export-specialist.
Evita errores criticos en el momento mas delicado del pipeline.

---

## FLUJO COMPLETO DE UN CHALLENGE

### PRE-CHALLENGE (automatico)

El orchestrator ejecuta estos pasos en orden antes de
solicitar autorizacion humana. Si cualquier paso falla
→ no enviar solicitud de autorizacion hasta resolver.

**Paso 1 — Forward Test pasa 3 criterios numericos**
- Minimo 20 trades ejecutados en demo.
- PF demo >= 70% del PF OOS backtest.
- DD demo <= DD OOS + 30%.
Los 3 criterios deben cumplirse simultaneamente.
Ver skill-forward-test-protocol.md para detalles.

**Paso 2 — propfirm-compliance-officer verifica reglas**
Checklist automatico:
  [ ] Ratio TP/SL efectivo >= 2:1 en forward test
  [ ] Max trades/dia respetado
  [ ] Horario de sesion respetado (08:00-20:00)
  [ ] Spread y comisiones dentro de los esperados
  [ ] Sin trades en fin de semana
  [ ] Holding time compatible con reglas de la firma
  [ ] Magic number unico — sin colision con otros EAs
Si cualquier check falla → no continuar.

**Paso 3 — propfirm-health-monitor verifica salud de la firma**
Score de la firma >= 60/100 (ver agents/propfirm-health-monitor.md).
Si score < 60 → pausar y notificar al humano antes de comprar.

**Paso 4 — propfirm-regulatory-watcher verifica T&C**
Sin cambios CRITICOS en T&C en las ultimas 2 semanas.
Si hay cambio CRITICO reciente → no comprar hasta clarificar.

**Paso 5 — coordination-detector verifica sin conflictos**
Verificar que no hay otro EA con el mismo activo corriendo
en otra cuenta de la misma firma en el mismo horario.

**Paso 6 — Sistema genera notificacion Telegram**
Formato exacto (ver orchestrator.md — protocolo de challenge):
```
SISTEMA LISTO PARA CHALLENGE

Estrategia: [ID-version] | [Activo] [TF]
Prop firm:  [nombre] | Cuenta: [tamaño] | Coste: [X] EUR

VALIDACIONES PASADAS:
  Spread 2x:          PF [X]
  Post-swaps:         PF [X]
  Stress test (5p):   DD max [X]%
  WFO Matrix:         [X]/5 configuraciones
  Forward Test:       [X] trades, PF [X]
  Compliance:         APROBADO
  Score total:        [X]/100

Autorizar compra? → SI para confirmar
```

---

### COMPRA DEL CHALLENGE (unico paso humano)

El humano recibe el mensaje de Telegram, revisa los datos
y responde SI para confirmar.

El sistema registra la autorizacion en el audit trail:
  hash-logger registra CHALLENGE-AUTORIZADO con timestamp y firma.

El humano accede a la web de la prop firm y compra el challenge.
El challenge ID (numero de cuenta) se comunica al orchestrator.

Timeout: si el humano no responde en 72 horas →
la estrategia pasa a cola de espera y se lanza nuevo ciclo.

---

### CHALLENGE FASE 1 (automatico tras compra)

**Configuracion inicial (export-specialist)**
- EA desplegado en VPS con los instrumentos exactos de la firma.
- Verificar que el simbolo del broker coincide exactamente.
- ftmo-timezone-sync.mq5 activo para calculo correcto del DD.
- ConnectionMonitor.mqh activo para deteccion de freeze.

**Parametros de riesgo (Risk Manager)**
El margen operativo para challenge de 10k FTMO:
  Daily Loss Limit FTMO: 5% = 500 USD
  Margen operativo: 4.8% = 480 USD por dia (buffer de 20 USD)
  Max DD FTMO: 10% = 1.000 USD total
  Margen operativo: 9.5% = 950 USD total
  Riesgo por trade: 1% del balance actual

**Monitoreo continuo (performance-monitor)**
- Verificar EA activo cada 10 minutos.
- Si sin datos 10 minutos → CASO 2 al humano.
- Alertas Telegram automaticas:
  DD > 3% del dia: "[WARNING] DD diario: [X]%"
  DD > 4.5% del dia: "[CRITICAL] DD diario: [X]% — acercandose al limite"

**account-recovery-manager en standby**
  Activacion automatica si DD > 6% (ver agents/account-recovery-manager.md).

**Criterios de exito Fase 1**
- Profit: >= +10% del capital inicial.
- DD diario: siempre < 5%.
- DD total: siempre < 10%.
- Dias operados: >= 4 dias minimos.
- Ningun trade fuera de horario ni en fin de semana.

---

### CHALLENGE FASE 2 (automatico tras pasar Fase 1)

Mismo EA, mismos parametros, mismo VPS.
FTMO mueve automaticamente el challenge a Fase 2.

El objetivo es mas reducido (+5%) con los mismos limites de DD.
El performance-monitor detecta el cambio de fase y lo registra.
No hay intervencion humana entre Fase 1 y Fase 2.

**Criterios de exito Fase 2**
- Profit: >= +5% del capital.
- DD diario: siempre < 5%.
- DD total: siempre < 10%.
- Dias operados: >= 4 dias minimos.

---

### CUENTA FUNDED (automatico tras pasar Fase 2)

**Transicion**
FTMO notifica por email que la cuenta paso a funded.
El orchestrator registra el cambio de estado del ticket:
  challenge → funded.
El mismo EA sigue corriendo en el mismo VPS sin cambios.

**Periodo de observacion (4 semanas)**
No escalar durante las primeras 4 semanas.
El performance-monitor monitorea en tiempo real.
El scaling-manager inicia el conteo del periodo de 4 meses.

**Distribucion del profit**
FTMO: 80% al trader, 20% a la firma.
Los retiros se pueden solicitar una vez al mes.

**Monitoreo de decay**
performance-monitor evalua cada semana:
  Si PF produccion < 85% del PF OOS backtest durante 4 semanas:
  → activar protocolo de reoptimizacion (ver account-recovery-manager.md).

**Scaling automatico (cada 4 meses)**
scaling-manager evalua criterios y notifica al humano
si se cumplen todos para solicitar el scaling de +25%.
Ver agents/scaling-manager.md para criterios exactos.

---

## CRITERIOS DE EXITO RESUMIDOS

| Fase | Objetivo profit | DD diario max | DD total max |
|------|----------------|---------------|--------------|
| Challenge Fase 1 | +10% | 5% | 10% |
| Challenge Fase 2 | +5% | 5% | 10% |
| Funded — operativo | — | 5% | 10% |

---

## ACCIONES ANTE FALLO DEL CHALLENGE

### Si el challenge falla (DD maxima violada)

1. orchestrator registra el fallo en el audit trail.
2. La estrategia pasa a estado "challenge-fallado" en el registry.
3. El capital usado se descuenta del presupuesto de reintentos.
4. lessons-analyzer.py analiza las condiciones del fallo.
5. Si la causa es tecnica (configuracion) → corregir y reintentar.
6. Si la causa es la estrategia → descarte definitivo.
   No hay segunda oportunidad para estrategias con fallo de mercado.

### Si el EA tiene un problema tecnico durante el challenge

El performance-monitor detecta el problema y notifica CASO 2.
El humano interviene para resolver el problema tecnico.
El pipeline no descarta la estrategia por fallo tecnico del VPS.

---

## SELECCION DEL TAMANIO DE CUENTA

Para el primer challenge de cada estrategia:
- FTMO: cuenta 10k USD (minimo riesgo de capital).
- E8: cuenta 25k USD (el tamanio mas pequeno disponible).
- TFT: cuenta 25k USD.

Si la estrategia pasa el challenge en la cuenta pequena:
el scaling-manager gestiona el escalado gradual.
No empezar con cuentas grandes hasta tener historial en produccion.

---

## LO QUE ESTA SKILL NUNCA HACE

NUNCA salta el pre-challenge automatico para "ahorrar tiempo".
NUNCA compra el challenge sin autorizacion humana explicita.
NUNCA lanza Fase 2 con parametros diferentes a Fase 1.
NUNCA descarta la estrategia por un fallo tecnico del VPS.
NUNCA escala antes de 4 semanas de observacion en funded.
NUNCA acepta un challenge fallado como "normal" sin analisis.
