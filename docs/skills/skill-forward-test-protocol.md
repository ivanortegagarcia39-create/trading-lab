# Skill: Protocolo de Forward Test en MT5 Demo

## Propósito
Define el proceso completo del forward test en cuenta demo de MT5.
El forward test es la ÚNICA intervención humana en el pipeline.
Dura mínimo 2 semanas. Los criterios de aprobación son automáticos y numéricos.
El humano no opina sobre si la estrategia es buena o mala — eso ya lo decidieron
los números del pipeline. Solo verifica ejecución técnica y rendimiento mínimo.

---

## FASE 1 — CONFIGURACIÓN INICIAL

### 1. Abrir cuenta demo FTMO

1. Registrarse en dashboard.ftmo.com → "Free Trial" → cuenta demo MT5
2. Capital demo = capital del challenge objetivo (10k, 25k, 100k)
3. La cuenta demo FTMO tiene plazo de 45 días
4. Anotar credenciales en config/ (no en git)

### 2. Desplegar EA en VPS

1. Transferir el archivo `.ex5` al VPS via RDP
2. Copiar a: `MQL5\Experts\` dentro del directorio de datos de MT5
3. Abrir MT5 y verificar que el EA aparece en el Navigator
4. Adjuntar el EA al gráfico H1 del símbolo correcto (con sufijo si aplica)
5. Activar AutoTrading (botón verde)

### 3. Parámetros de producción obligatorios

```
Risk                       = 1.0%  (o ajustado por portfolio — ver skill-ea-parameters.md)
MagicNumber                = (único, asignado por export-specialist)
MaxSlippagePips            = (según activo)
UseNewsFilter              = true
NewsFilterMinutes          = 15
UseDynamicSpreadProtection = true
MaxSpreadMultiplier        = 3.0
CloseOnFriday              = true
FridayCloseHour            = 20
UseHeartbeat               = true
HeartbeatFile              = C:\TradingLab\heartbeat\EA_[SIMBOLO]_B[N].txt
```

### 4. Verificación de arranque (primeras 24h)

- [ ] EA adjuntado sin errores en el log de MT5 (Journal)
- [ ] EA muestra "smiley face" (activo) en la esquina del gráfico
- [ ] Archivo de heartbeat se actualiza periódicamente
- [ ] EA recibe ticks (verificar en el log)
- [ ] Si hay señal en las primeras 24h: verificar que la orden se ejecuta

Si 24h sin trades: es normal — el EA espera sus condiciones exactas.

---

## FASE 2 — MONITOREO DIARIO

### Tareas diarias (5 minutos)

1. Verificar heartbeat activo:
   ```bash
   python scripts/vps-health-monitor.py --check
   ```

2. Registrar balance del día:
   ```bash
   python scripts/ftmo-account-tracker.py \
       --account-id FTMO-25K-FT01 \
       --current-balance [balance] \
       --mode update
   ```

3. Ver estado del forward test:
   ```bash
   python scripts/ftmo-account-tracker.py \
       --account-id FTMO-25K-FT01 --mode report
   ```

### Alertas automáticas del sistema

| Condición | Alerta | Acción |
|-----------|--------|--------|
| DD diario > 3% | WARNING Telegram | Revisar logs MT5 — ¿trade anómalo? |
| DD diario > 4.5% | CRITICAL Telegram | Revisar urgente — posible error técnico |
| DD total > 7% | WARNING Telegram | Revisar configuración |
| DD total > 7.5% | CRITICAL Telegram | Detener si hay error técnico |
| Heartbeat > 15 min sin actualizar | CRITICAL | Verificar VPS y MT5 |
| 5 días sin trades | WARNING manual | Verificar configuración del EA |

### Lo que NO es motivo de intervención

- El EA tiene una racha perdedora de 3-5 trades → normal estadísticamente
- El EA no opera 2-3 días seguidos → normal si el mercado no da señales
- El balance está en negativo → el forward test no evalúa rendimiento en 2 semanas

---

## FASE 3 — CRITERIOS DE EVALUACIÓN AUTOMÁTICA

Al completar el periodo mínimo, el orchestrator evalúa automáticamente los datos.

### Criterios de APROBACIÓN (los 3 deben cumplirse simultáneamente)

| # | Criterio | Umbral |
|---|----------|--------|
| 1 | Trades ejecutados | ≥ 20 |
| 2 | PF producción | ≥ 70% del PF OOS del backtest |
| 3 | DD máximo | ≤ DD OOS del backtest × 1.30 |

**Ejemplo de cálculo:**
```
PF OOS backtest = 1.45
PF producción mínimo = 1.45 × 0.70 = 1.015

DD OOS backtest = 5.2%
DD máximo producción = 5.2% × 1.30 = 6.76%
```

### Criterios de FALLA AUTOMÁTICA (cualquiera falla → estrategia descartada)

| Criterio | Falla si |
|----------|----------|
| PF producción | < 70% del PF OOS del backtest |
| DD máximo real | > DD OOS backtest × 1.30 |
| Ejecución técnica | Errores de SL/TP, horario, o position sizing |

### Criterios de ejecución técnica (complementarios)

Para cada trade ejecutado, verificar:
- SL y TP se activaron en el nivel correcto
- Tamaño de posición correcto (1% riesgo)
- Trade dentro del horario 06:00-18:00 UTC
- Máximo 2 trades por día respetado
- Sin operativa en fin de semana

---

## FASE 4 — DECISIÓN FINAL

### Si APRUEBA

El orchestrator envía notificación Telegram:
```
[INFO] Forward test APROBADO — XAUUSD_B11_S001
Trades: 27 en 15 días
PF producción: 1.38 (96% del PF OOS 1.44) ✓
DD máximo: 4.1% (79% del DD OOS 5.2%) ✓
Ejecución técnica: sin errores ✓

¿Autorizar compra del challenge? Responder SI
```

Humano responde "SI" al bot de Telegram.
El sistema registra la autorización en el audit trail con timestamp.
Humano compra el challenge en FTMO.

### Si FALLA

El orchestrator envía notificación Telegram con el motivo exacto.
La estrategia se marca como DESCARTADA en el registry.
Pipeline activa la siguiente candidata del ranking de portfolio.

**Regla inquebrantable:** sin segunda oportunidad en el mismo ciclo.

---

## DURACIÓN DEL FORWARD TEST

| Condición | Duración |
|-----------|----------|
| Normal (≥ 20 trades en 10 días) | Mínimo 10 días hábiles |
| Pocos trades (< 20 en 10 días) | Hasta 20 trades o 21 días |
| Máximo absoluto | 30 días (evaluar con lo disponible) |

---

## MÚLTIPLES ESTRATEGIAS EN SIMULTÁNEO

Si el portfolio tiene 3+ candidatas aprobadas por WFO, testear en paralelo
en la misma cuenta demo con distintos MagicNumbers.

Criterio adicional para portfolio combinado:
- DD combinado real ≤ DD combinado modelado × 1.20

---

## ERRORES TÉCNICOS COMUNES Y SOLUCIÓN

| Error | Causa probable | Solución |
|-------|---------------|----------|
| Sin trades en 2 semanas | Símbolo incorrecto o EA no activo | Verificar nombre exacto y cara sonriente |
| SL/TP no en nivel correcto | Diferencia pip size backtest vs broker | Ajustar parámetros del EA |
| Posición incorrecta | Money management en lote fijo | Cambiar a riesgo % |
| Opera fuera de horario | Diferencia zona horaria SQ vs MT5 | Ajustar horario en parámetros |
| EA se desactiva solo | Memoria insuficiente o crash MT5 | Configurar reinicio automático VPS |

Si se corrige un error técnico → reiniciar el forward test desde cero (las 2 semanas empiezan de nuevo).

---

## REGLA FUNDAMENTAL

El forward test verifica dos cosas:
1. Que el EA ejecuta correctamente (técnico)
2. Que el rendimiento real no diverge demasiado del backtest (numérico)

Si ambas se cumplen → el challenge se compra.
Sin opinión. Sin intuición. Sin sesgo.

---

## Referencias

- `scripts/ftmo-account-tracker.py` — registro diario de balance
- `scripts/vps-health-monitor.py` — monitoreo de heartbeat
- `scripts/telegram-notifier.py` — notificaciones de aprobación/fallo
- `docs/skills/skill-ea-parameters.md` — parámetros del EA en producción
- `docs/skills/skill-mt5-deployment.md` — despliegue del EA en VPS
- `docs/skills/skill-broker-selection.md` — selección del broker
- `agents/performance-monitor.md` — agente de monitoreo continuo
- `agents/orchestrator.md` — decisión automática de aprobación/fallo
