# Claude Project Setup — TradingLab

## ¿Qué es un Claude Project y por qué elimina la fricción?

Un **Claude Project** es un espacio persistente en claude.ai donde se cargan documentos de referencia
que el modelo lee automáticamente al inicio de cada conversación. Sin Project, cada sesión empieza
de cero y el usuario debe re-explicar el contexto del proyecto, las reglas del pipeline y el estado
actual. Con Project, ese contexto ya está cargado — el agente arranca como si llevara semanas trabajando en el proyecto.

Beneficios concretos para TradingLab:
- Cero repetición de contexto en cada sesión
- Los agentes aplican las reglas de CLAUDE.md desde el primer mensaje
- El estado del build activo está siempre visible
- Las lecciones aprendidas influyen en cada decisión sin adjuntarlas manualmente

---

## Archivos a cargar en el Project

Cargar en este orden de prioridad:

| Archivo | Propósito |
|---------|-----------|
| `CLAUDE.md` | Constitución del proyecto — reglas, filosofía, pipeline |
| `docs/lessons-learned.md` | Lecciones estructurales y permanentes del pipeline |
| `docs/propfirm-rules.md` | Reglas FTMO/E8/TFT — límites de DD, horarios, compliance |
| `docs/project-status.md` | Estado actual: builds, portfolio, tickets activos |
| `docs/skills/skill-evaluation-auto.md` | Criterios numéricos exactos del Evaluation Gate |
| `docs/skills/skill-builder-libre.md` | Configuración del Builder libre sin hipótesis |
| `docs/skills/skill-portfolio-selection.md` | Criterios de correlación y selección de portfolio |

Tamaño típico: < 200 KB en total — bien dentro del límite del Project.

---

## Instrucciones a pegar en el Project

Pegar esto exactamente en el campo "Project instructions" de claude.ai:

```
Eres el orchestrator de TradingLab, un sistema 100% automático de generación y
validación de estrategias de trading algorítmico para prop firms.

Reglas fundamentales:
1. Los números deciden — nunca la intuición ni el criterio humano
2. Si una estrategia no cumple TODOS los criterios numéricos → DESCARTAR
3. No hay segunda oportunidad para estrategias descartadas
4. Temporalidad única: H1 para todos los activos
5. Sin hipótesis humana en la lógica de entrada — SQ decide

En cada sesión:
- Lee CLAUDE.md y los archivos del Project antes de responder
- Aplica los criterios exactos de skill-evaluation-auto.md
- Responde en español
- Sé directo: ejecutivo, sin rodeos, sin preguntas innecesarias al humano

El humano solo interviene en 2 casos:
1. Autorizar compra de challenge (tras forward test OK)
2. Alertas críticas de infraestructura
En ningún otro momento el humano decide nada.
```

---

## Cómo mantener los archivos actualizados

Sincronizar el Project tras cada sesión importante:

### Cuándo actualizar
- Después de cada build completado → actualizar `project-status.md`
- Cuando se aprueba o descarta una estrategia → actualizar `project-status.md`
- Cuando se añade una lección nueva → actualizar `lessons-learned.md`
- Cuando cambia algún criterio numérico del pipeline → actualizar `skill-evaluation-auto.md`

### Proceso de sincronización
1. Descargar el archivo actualizado del repo local
2. En el Project de claude.ai → Files → eliminar versión anterior
3. Subir el archivo nuevo
4. No es necesario reiniciar el Project — el cambio es inmediato

### Frecuencia recomendada
- `project-status.md`: después de cada build o sesión de evaluación
- `lessons-learned.md`: mensual o cuando se promueva una lección a ESTRUCTURAL
- Resto de archivos: solo cuando cambien los criterios (poco frecuente)

---

## Qué NO cargar en el Project

| Archivo/carpeta | Razón |
|-----------------|-------|
| `config/api-keys.json` | Contiene credenciales — nunca a servicios externos |
| `.chromadb/` | Base de datos binaria — no útil como texto |
| `.kuzu/` | Base de datos del Knowledge Graph — no útil como texto |
| `results/raw/` | Datos crudos voluminosos — sobrecargarían el contexto |
| `config/internal-critic-log.jsonl` | Log interno — no relevante para agentes |
| Cualquier archivo con claves, tokens o passwords | Seguridad básica |

**Regla general:** si el archivo contiene credenciales o es una base de datos binaria, no lo cargas.

---

## Verificación post-setup

Para confirmar que el Project funciona correctamente, iniciar una sesión nueva y escribir:

```
¿Cuál es el build activo y qué activo está en cola?
```

Si el agente responde con el estado correcto del build sin que el usuario haya dado contexto,
el Project está configurado correctamente.
