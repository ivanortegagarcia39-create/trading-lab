# Skill: Gestión de Cambios de Reglas en Prop Firms

## Proposito
Protocolo para detectar, clasificar y responder a cambios
en las reglas de prop firms.
Un cambio de reglas puede invalidar una estrategia o una cuenta
de forma inmediata — el sistema debe detectarlo antes que el EA.

---

## RIESGO PRINCIPAL

Las prop firms pueden cambiar sus reglas sin previo aviso.
Casos históricos documentados:

- **MyForexFunds (agosto 2023):** CFTC emitió orden de cese.
  Fondos bloqueados sin previo aviso. Afectó a miles de traders.
- **FTMO (enero 2024):** Cambió definición de "group trading".
  Muchas cuentas canceladas retroactivamente.
- **Varios (2024-2025):** Prohibición progresiva de criptos
  y aumento de restricciones en noticias.

**Lección:** La diversificación entre firms es una protección real,
no una preferencia. Un sistema mono-firm tiene riesgo de ruina total.

---

## MONITOREO SEMANAL

El agente `propfirm-regulatory-watcher.md` ejecuta hash check
semanal de las páginas de T&C de cada prop firm activa.

### Proceso automático
1. Descargar HTML de página T&C de cada firm
2. Calcular SHA-256 del contenido relevante
3. Comparar con hash de la semana anterior
4. Si el hash cambia → clasificar cambio y notificar

### Clasificación del cambio

| Clasificación | Criterio | Tiempo de respuesta |
|--------------|----------|---------------------|
| CRÍTICO | Afecta cuentas activas o capital | Inmediato (< 2h) |
| IMPORTANTE | Afecta estrategia futura | Próxima sesión |
| INFORMATIVO | Cambio de UI, texto aclaratorio | Siguiente revisión semanal |

---

## CAMBIOS CRÍTICOS — acción inmediata

Actuar en menos de 2 horas al detectar cualquiera:

### Prohibición de EAs / trading algorítmico
→ Pausar todas las cuentas afectadas inmediatamente
→ Cerrar todas las posiciones abiertas manualmente
→ No abrir nuevas posiciones hasta aclarar
→ Contactar soporte de la firm para confirmar alcance

### Cambio en Daily Loss Limit o Max Drawdown
→ Actualizar Risk Manager EA en VPS con nuevos valores
→ Verificar que ninguna cuenta activa está cerca del nuevo límite
→ Recalcular `risk-calculator.py` con nuevos parámetros
→ Actualizar `config/pipeline-config.json` sección `risk_manager`

### Prohibición de activos
→ Retirar EAs de esos activos del VPS inmediatamente
→ Cerrar posiciones abiertas en esos activos
→ Actualizar `market-selector` para excluir el activo

### Cierre de la firma (regulatorio o voluntario)
→ Retirar capital inmediatamente si es posible
→ Documentar fondos en riesgo
→ Activar firm alternativa con estrategias equivalentes
→ No depositar nuevo capital en esa firm

---

## CAMBIOS IMPORTANTES — acción en próxima sesión

### Nuevas restricciones de horario de trading
→ Actualizar parámetros de sesión en EA (`sesion_inicio`, `sesion_fin`)
→ Recompilar EA con nuevos valores
→ Verificar que el cambio no invalida el backtest IS

### Cambios en profit split
→ Recalcular rentabilidad esperada del portfolio
→ Si split cae por debajo de 70% → evaluar migrar a firm alternativa
→ Actualizar proyecciones en `docs/project-status.md`

### Nuevos requisitos de días mínimos de trading
→ Ajustar frecuencia mínima de la estrategia
→ Verificar que el EA tiene suficientes señales para cumplir el nuevo mínimo
→ Si no cumple → buscar estrategia con mayor frecuencia en databank

### Cambios en el proceso de verificación / KYC
→ Completar el nuevo proceso antes del próximo retiro
→ No afecta cuentas activas — acción no urgente

---

## HISTORIAL DE CAMBIOS CONOCIDOS FTMO 2026

| Fecha | Cambio | Clasificación | Estado |
|-------|--------|--------------|--------|
| Hasta 2026-04-27 | Sin cambios críticos detectados | — | OK |
| 2026 T&C | Scaling plan: +25% cada 4 meses confirmado | INFORMATIVO | Documentado |
| 2026 T&C | Prohibición HFT reforzada con detección automática | INFORMATIVO | Documentado |
| 2026 T&C | Group trading detection mejorada | IMPORTANTE | Ver export-specialist.md |

**Próxima revisión programada:** primera sesión de cada semana.

---

## DIVERSIFICACIÓN COMO PROTECCIÓN

### Regla de concentración máxima
**Nunca más del 30% del capital total en una sola firma.**

Con 3 firms activas en Capa 3+:
- FTMO: 40% del capital (máximo permitido por excepción si es la única activa)
- E8 Funding: 30% del capital
- TFT o alternativa: 30% del capital

Si una firma cierra sin aviso → máximo 40% del capital en riesgo.
El sistema continúa operativo con las otras firms.

### Plan de activación de firm alternativa
Mantener siempre una estrategia aprobada lista para desplegarse
en una segunda firm. Tiempo de activación objetivo: < 48h.

1. Estrategia aprobada en databank con WFO aprobado
2. EA compilado y probado en demo
3. Cuenta de la firm alternativa creada (aunque no activa)
4. Proceso de challenge conocido y documentado

### Firms priorizadas por tipo de activo

| Firm | Activos principales | DD permitido | Estado |
|------|--------------------|--------------|----- --|
| FTMO 2-Step | Forex + Metales + Índices | 10% dinámico | PRINCIPAL |
| E8 Funding | Forex + Metales | 8% estático | ALTERNATIVA |
| TFT | Forex + Metales + Índices | 6% dinámico | ALTERNATIVA |
| Apex | Futuros CME | Variable | PENDIENTE datos |
| MFF | Futuros CME | Variable | PENDIENTE datos |

---

## CHECKLIST DE REVISIÓN SEMANAL

Ejecutar cada lunes al inicio de sesión:

- [ ] Hash check T&C FTMO — ¿hubo cambios?
- [ ] Hash check T&C E8/TFT — ¿hubo cambios?
- [ ] Verificar que ninguna cuenta está cerca del límite de DD
- [ ] Verificar que los EAs siguen activos en VPS
- [ ] Revisar noticias del sector (Twitter/X: @FTMO_com, foros prop trading)
- [ ] Si hay cambio detectado → clasificar y actuar según protocolo

---

## RELACIÓN CON OTROS AGENTES Y SKILLS

- `agents/propfirm-regulatory-watcher.md` — automatiza el hash check
- `agents/propfirm-compliance-officer.md` — verifica compliance continuo
- `agents/propfirm-analyst.md` — compara firms para nuevas estrategias
- `skill-ftmo-rules.md` — reglas FTMO vigentes documentadas
- `skill-propfirms-comparison.md` — comparativa detallada de firms
