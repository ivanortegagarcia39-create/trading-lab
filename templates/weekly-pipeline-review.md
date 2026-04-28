---
semana: {{date:YYYY-[W]WW}}
fecha_inicio: {{date:YYYY-MM-DD}}
builds_activos: 0
estrategias_databank: 0
estrategias_en_evaluacion: 0
estrategias_aprobadas: 0
portfolio_size: 0
accounts_active: 0
---

# Revisión Semanal del Pipeline — {{date:YYYY-[W]WW}}

## Estado del Pipeline

| Métr ica | Esta semana | Semana anterior | Tendencia |
|---------|------------|-----------------|-----------|
| Builds activos | {{builds_activos}} | | |
| Estrategias en databank | {{estrategias_databank}} | | |
| En evaluación (EvalGate) | {{estrategias_en_evaluacion}} | | |
| Aprobadas acumuladas | {{estrategias_aprobadas}} | | |
| Portfolio activo | {{portfolio_size}} estrategias | | |
| Cuentas activas | {{accounts_active}} | | |

**Semáforo del pipeline:**
- [ ] 🟢 Normal — builds corriendo, métricas dentro de umbrales
- [ ] 🟡 Atención — sin nuevas aprobaciones en 2+ semanas
- [ ] 🔴 Alerta — sin databank en 72h o tasa de aprobación < 0.5/semana

---

## Builds Esta Semana

### Build activo
- Build ID: ___
- Activo: ___
- Estado: ___
- Horas corriendo: ___
- Candidatas en databank: ___

### Decisiones de build
_¿Se lanzó algún build nuevo? ¿Se detuvo alguno? ¿Por qué?_

---

## Estrategias en Proceso

### EvalGate
| ID | Activo | PF | DD% | Trades | Veredicto |
|----|--------|----|-----|--------|-----------|
| | | | | | |

### Retester / Paso 12b
| ID | Activo | PF OOS | Caída PF% | Veredicto |
|----|--------|--------|-----------|-----------|
| | | | | |

### WFO
| ID | Activo | WFE% | Ventanas OK | Veredicto |
|----|--------|------|-------------|-----------|
| | | | | |

### Forward Test en Demo
| ID | Activo | Días | Trades | PF demo | PF OOS ratio | Estado |
|----|--------|------|--------|---------|--------------|--------|
| | | | | | | |

---

## Portfolio Actual

| ID Estrategia | Activo | DD Diario | DD Total | PF 4 sem | Z-Score | Estado |
|---------------|--------|-----------|----------|----------|---------|--------|
| | | | | | | |

**Correlación media 30d:** ___  
**DD combinado actual:** ___%  
**Resultado `portfolio-monitor.py`:** ___

---

## Alertas de la Semana

| Tipo | Descripción | Acción tomada |
|------|-------------|---------------|
| | | |

_Si no hubo alertas: "Sin alertas esta semana"_

---

## Ajustes de Criterios Propuestos

_Solo completar si hay evidencia numérica que justifique un cambio en los umbrales del pipeline. Recordar: los cambios en criterios requieren consenso (CLAUDE.md regla 13)._

| Criterio actual | Valor actual | Valor propuesto | Justificación |
|----------------|-------------|----------------|---------------|
| | | | |

---

## Métricas del Sistema

- Tasa de aprobación esta semana: ___ / semana (mínimo 0.5)
- Semanas consecutivas sin nueva aprobación: ___
- Semanas desde último build iniciado: ___
- ¿Build sin databank > 72h?: Sí / No

---

## Próxima Semana

### Prioridades
1. ___
2. ___
3. ___

### Bloqueos pendientes
_Listar bloqueos que impiden avanzar (VPS, hardware, etc.)_

### Hito más cercano
_Describir el próximo hito crítico del roadmap_
