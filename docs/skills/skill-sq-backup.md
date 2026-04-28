# Skill: Backup de StrategyQuant

## Proposito
Protocolo para proteger los proyectos, settings y datos de SQ.
Los archivos .sqx son irremplazables sin backup.
Un apagon durante un build sin backup = estrategias perdidas.

---

## QUE HACER BACKUP

### 1. Carpeta user/projects/ — CRITICO
Contiene todos los proyectos de SQ y sus databanks.
Cada proyecto incluye las estrategias generadas (.sqx) y la configuracion del build.
**Sin backup de projects/ → las estrategias generadas se pierden para siempre.**

### 2. Carpeta user/settings/ — IMPORTANTE
Contiene la configuracion personalizada de SQ:
- Vistas y filtros guardados del databank
- Columnas personalizadas
- Preferencias de UI y atajos

### 3. Carpeta user/data/ — GRANDE (~20GB)
Contiene los datos M1 descargados de Dukascopy.
Son grandes pero se pueden re-descargar desde Dukascopy si se pierden.
Prioridad de backup: menor que projects/ y settings/.

---

## FRECUENCIA DE BACKUP

| Tipo | Frecuencia | Automatico |
|------|-----------|-----------|
| user/projects/ | Horario durante builds activos | sq-watchdog.py |
| user/settings/ | Horario durante builds activos | sq-watchdog.py |
| user/data/ | Semanal (datos estables, cambian poco) | Manual |
| Backup completo | Antes de cualquier update de SQ | Manual obligatorio |

**Regla critica:** Antes de actualizar SQ a una nueva version → backup completo manual.
Las actualizaciones de SQ pueden cambiar el formato de los proyectos y corromper databanks.

---

## DONDE GUARDAR

```
backups/
├── sq_configs/     ← projects/ y settings/ (en .gitignore — son binarios)
│   ├── 2026-04-27/
│   ├── 2026-04-28/
│   └── latest/     ← copia del backup mas reciente
└── sq_data/        ← datos M1 (NUNCA en git — demasiado grandes)
    └── dukascopy-m1/
```

**Recomendacion adicional:** disco externo o NAS para redundancia.
El repositorio git no es suficiente como unico backup de binarios grandes.

### sq-watchdog.py hace backup horario automatico

```bash
# Backup manual inmediato
python scripts/sq-watchdog.py --backup

# Monitoreo continuo con backup cada hora
python scripts/sq-watchdog.py --monitor --interval 3600
```

El watchdog verifica que SQ sigue corriendo Y hace backup en cada ciclo.
Si SQ se congela → alerta Telegram + backup de lo que hay hasta ese momento.

---

## RECUPERACION

### Si SQ se corrompe o hay apagon durante build

1. Anotar cuantas estrategias hay en el databank antes de cerrar
2. Anotar el PF maximo observado en ese momento
3. Copiar user/projects/[proyecto] desde el ultimo backup horario
4. Reinstalar SQ limpio si es necesario
5. Restaurar user/ desde backup
6. Retomar el build desde el databank existente — SQ no pierde lo generado antes del backup

**Perdida maxima:** 1 hora de generacion (backup horario).

### Si se pierden los datos M1 (user/data/)

Los datos M1 se pueden re-descargar desde Dukascopy:
- Dukascopy Historical Data Feed — formato Ticks o M1 OHLCV
- Periodo disponible: desde 2003 para Forex y Metales
- Tiempo de re-descarga: 2-4 horas para todos los activos principales

### Si se pierden los proyectos .sqx sin backup

**No hay recuperacion posible.** Los archivos .sqx son propietarios de SQ.
No se pueden regenerar — solo relanzar el build desde cero (24-48h de CPU).
Las mismas configuraciones generan estrategias DIFERENTES cada vez
por la naturaleza genetica del Builder.

---

## LECCION DEL PROYECTO

El apagon del 2026-04-22 durante el Build 10 demostro que los proyectos
SQ pueden corromperse sin previo aviso. El sq-watchdog.py hace backup
horario precisamente para este escenario.

**Consecuencia del apagon:** Build 10 tuvo que reiniciarse desde el
ultimo backup horario disponible. Las estrategias generadas en esa
ultima hora se perdieron pero el resto del databank se recupero.
Sin ese backup, habrian sido 20+ horas de CPU perdidas.

---

## CHECKLIST PRE-BUILD

Antes de lanzar cualquier build en alber:

- [ ] Backup manual de user/projects/ y user/settings/
- [ ] Verificar que sq-watchdog.py esta configurado con --monitor
- [ ] Verificar espacio en disco para backups/ (minimo 10GB libres)
- [ ] Verificar temperatura CPU antes de lanzar (< 70C ideal)
- [ ] Confirmar UPS o bateria disponible para evitar apagones

---

## RELACION CON OTROS SCRIPTS Y SKILLS

- `scripts/sq-watchdog.py` — automatiza backup horario durante builds
- `skill-compute-prioritization.md` — reglas de temperatura y prioridad CPU
- `skill-builder-libre.md` — configuracion del build que se va a hacer backup
- `skill-session-workflow.md` — protocolo de sincronizacion git entre dispositivos
