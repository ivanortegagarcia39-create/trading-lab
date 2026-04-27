# Skill: Priorización de Recursos Computacionales

## Proposito
Define como distribuir la carga de CPU entre ivano y alber
para que los builds de SQ y los scripts de análisis no compitan
por recursos y no se degraden mutuamente.

---

## RECURSOS DISPONIBLES

| Dispositivo | Uso principal | Limitación |
|-------------|--------------|------------|
| ivano | Claude Code, scripts Python, documentación | No ejecutar SQ |
| alber | SQ builds (CPU intensivo), MT5, scripts de análisis | No ejecutar builds pesados durante SQ |

---

## REGLAS DE PRIORIZACIÓN EN ALBER

### Prioridad de procesos

1. **SQ build activo — prioridad máxima de CPU**
   No ejecutar ningún otro proceso pesado mientras SQ está generando.
   SQ usa todos los núcleos disponibles en modo continuo.
   Cualquier competencia por CPU alarga el build y puede causar
   que SQ se congele (ver sq-watchdog.py).

2. **No ejecutar procesos pesados durante builds**
   Prohibido durante build activo: compilaciones, instalaciones pip,
   actualizaciones de Windows, renderizado de video, Ollama con modelos grandes.

3. **Ollama puede correr en paralelo con SQ pero con prioridad baja**
   Si se usa Ollama (deepseek-r1:7b) durante un build:
   - Establecer prioridad de proceso a "Por debajo de lo normal" en Task Manager
   - Solo usar modelos <= 7B durante builds
   - Si temperatura > 75°C → detener Ollama inmediatamente

4. **MT5 puede correr siempre — consume muy poca CPU**
   MT5 en modo forward test demo es ligero.
   Compatible con builds activos sin restricción.

5. **Scripts Python de análisis solo cuando SQ está parado**
   Scripts que procesan muchos CSVs (evaluator-assistant, portfolio-builder,
   data-quality-checker) consumen CPU y disco.
   Ejecutarlos después de que SQ haya completado el build o en pausa.

---

## REGLAS DE PRIORIZACIÓN EN IVANO

1. **Claude Code tiene prioridad máxima**
   No ejecutar builds ni procesos intensivos mientras se trabaja con Claude Code.
   Claude Code + navegador + Obsidian es el perfil de uso normal de ivano.

2. **Obsidian puede correr siempre en paralelo**
   Obsidian es ligero. Compatible con cualquier otro proceso en ivano.

3. **Python scripts de documentación son ligeros — sin restricción**
   auto-reporter.py, session-starter.py, system-health-check.py:
   todos son operaciones de lectura/escritura de archivos.
   Sin impacto en rendimiento general.

---

## TEMPERATURA Y HARDWARE

### Umbrales críticos

| Temperatura CPU | Acción |
|----------------|--------|
| < 70°C | Normal — sin restricciones |
| 70-75°C | Advertencia — monitorear |
| 75-80°C | Detener Ollama si está corriendo |
| 80-85°C | Reducir carga — pausar scripts de análisis |
| > 85°C | **Pausar build SQ. Dejar enfriar 30 minutos** |

### Comportamiento durante builds largos (24-48h)

SQ en build continuo eleva la temperatura de forma sostenida.
Verificar temperatura cada 4-6 horas durante builds.

Herramientas de monitoreo en Windows:
- Task Manager → Performance → CPU
- HWiNFO64 (recomendado para monitoreo continuo)

**Regla crítica:** Nunca ejecutar SQ y Ollama simultáneamente
si la temperatura supera los 75°C.

---

## REGLA DE SINCRONIZACIÓN ENTRE DISPOSITIVOS

Protocolo obligatorio antes y después de cada sesión:

```bash
# Al INICIAR sesión en cualquier dispositivo
git pull origin main

# Al CERRAR sesión en cualquier dispositivo
git add .
git commit -m "descripción de lo trabajado"
git push origin main
```

**Nunca dejar cambios sin pushear al cerrar sesión.**
Si alber tiene resultados de build sin commitear y se apaga,
esos resultados se pierden o quedan inaccesibles desde ivano.

### División de trabajo por dispositivo

| Tipo de trabajo | Dispositivo |
|----------------|-------------|
| Claude Code, documentación, skills, agentes | ivano |
| SQ Builder, Retester, Optimizer | alber |
| Scripts de análisis post-build | alber (cuando SQ está parado) |
| git push de código Python | ivano |
| git push de resultados CSV | alber |
| MT5 forward test | alber |

---

## MONITOREO DEL BUILD (sq-watchdog.py)

Durante builds largos en alber, sq-watchdog.py verifica
que SQ no se haya congelado.

```bash
# Verificar que SQ sigue corriendo
python scripts/sq-watchdog.py --check

# Monitoreo continuo con alerta Telegram si SQ se detiene
python scripts/sq-watchdog.py --monitor --interval 1800
```

Si SQ se congela durante un build:
1. Anotar cuántas estrategias hay en el databank
2. Anotar el PF máximo observado
3. Reiniciar SQ
4. Retomar el build desde el databank existente (SQ no pierde lo generado)
