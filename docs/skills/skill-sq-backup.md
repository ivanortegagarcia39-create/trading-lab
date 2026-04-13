# Skill: Backup de Datos y Estrategias de SQ

## Proposito
Define como proteger los datos historicos de SQ,
las estrategias generadas y las configuraciones
contra perdida por fallo de hardware, corrupcion
de datos o formateo del dispositivo.
Un build de 48 horas perdido por falta de backup
es inaceptable.

---

## QUE HAY QUE PROTEGER

### Datos historicos (Dukascopy M1)
Ubicacion en SQ: carpeta de datos de SQ
Tamaño: ~1-2 GB por activo
Tiempo de descarga: 30-60 minutos por activo
Riesgo de perdida: MEDIO — se pueden redescargar
pero tarda horas si son muchos activos.

### Estrategias del databank
Ubicacion: databank interno de SQ
Tamaño: variable segun numero de candidatas
Riesgo de perdida: ALTO — un build de 48 horas
no se puede reproducir exactamente. Las mismas
configuraciones generan estrategias diferentes
cada vez por la naturaleza genetica del Builder.

### Estrategias aprobadas (.sqx)
Ubicacion: results\approved\ en el repositorio
Riesgo de perdida: BAJO — estan en Git y GitHub.
Pero solo si se hizo commit y push.

### Configuraciones del Builder
Ubicacion: strategyquant\builder\ en el repositorio
Riesgo de perdida: BAJO — estan en Git y GitHub.

### Archivos .mq5 exportados
Ubicacion: results\approved\ en el repositorio
Riesgo de perdida: BAJO — estan en Git y GitHub.

---

## PROTOCOLO DE BACKUP

### Backup 1 — Despues de cada build (OBLIGATORIO)

Cuando el Builder libre termina o se para:

1. Exportar TODAS las candidatas del databank
   SQ → Databank → Seleccionar todo → Exportar
   Guardar en: results\raw\build-results\
   Formato: .sqx

2. Hacer commit y push inmediatamente:
   git add .
   git commit -m "backup: Build [N] - [X] candidatas"
   git push origin main

3. Copiar el databank completo a carpeta de backup:
   Crear carpeta: C:\Users\alber\trading-lab-backups\
   Copiar: build-[N]-databank-[fecha]\

Tiempo: 5-10 minutos. No es opcional.

### Backup 2 — Despues del Retester (OBLIGATORIO)

1. Exportar resultados del Retester
   Guardar en: results\reviewed\
   
2. Commit y push:
   git add .
   git commit -m "backup: Retester Build [N] completado"
   git push origin main

### Backup 3 — Despues del WFO (OBLIGATORIO)

1. Exportar estrategias optimizadas
   Guardar en: results\approved\ con sufijo -v2
   
2. Commit y push:
   git add .
   git commit -m "backup: WFO Build [N] completado"
   git push origin main

### Backup 4 — Datos historicos (SEMANAL)

Una vez por semana verificar que los datos
historicos de SQ estan respaldados:

Opcion A — Carpeta de backup local:
Copiar la carpeta de datos de SQ a:
C:\Users\alber\trading-lab-backups\sq-data\

Opcion B — Disco externo:
Si hay disco externo disponible copiar ahi.

Opcion C — No hacer backup de datos:
Los datos de Dukascopy se pueden redescargar.
Es la opcion menos segura pero aceptable si
no hay espacio o disco externo.
Tiempo de redescargar todo: 4-8 horas.

---

## ESTRUCTURA DE CARPETA DE BACKUPS

C:\Users\alber\trading-lab-backups\
│
├── build-9-databank-2026-04-12\
│   └── [archivos .sqx del databank]
│
├── build-10-databank-2026-04-15\
│   └── [archivos .sqx del databank]
│
├── sq-data\
│   └── [copia de datos historicos de SQ]
│
└── exports\
    └── [copias de .mq5 exportados]

NOTA: Esta carpeta NO esta en el repositorio Git.
Es un backup local adicional para proteger contra
perdida del databank de SQ que no se puede
reproducir exactamente.

---

## CUANDO HACER BACKUP

| Momento | Que respaldar | Donde | Obligatorio |
|---------|--------------|-------|-------------|
| Fin de build | Databank completo + commit | backup local + GitHub | SI |
| Fin de Retester | Resultados + commit | GitHub | SI |
| Fin de WFO | Estrategias optimizadas + commit | GitHub | SI |
| Exportacion MT5 | Archivos .mq5 + commit | GitHub + backup local | SI |
| Semanal | Datos historicos SQ | backup local | RECOMENDADO |
| Antes de formatear PC | TODO | disco externo | SI |

---

## RECUPERACION ANTE PERDIDA

### Si se pierde el databank de SQ
Las candidatas exactas NO se pueden recuperar.
El algoritmo genetico genera resultados diferentes
cada vez incluso con la misma configuracion.

Recuperacion:
1. Si hay backup local → importar desde backup
2. Si no hay backup → relanzar el build
   Se generaran candidatas DIFERENTES pero
   de calidad similar si la configuracion es igual

### Si se pierden los datos historicos
Recuperacion:
1. Abrir SQ → Gestor de datos → Descargar
2. Redescargar de Dukascopy
3. Tiempo: 30-60 minutos por activo

### Si se pierde el repositorio local
Recuperacion:
1. git clone desde GitHub
2. Todo el proyecto se recupera en 2 minutos
3. Solo se pierden archivos no commiteados

### Si se pierde el PC completo
Recuperacion:
1. Instalar herramientas (Git, Node, Claude Code, SQ)
2. git clone desde GitHub
3. Redescargar datos de Dukascopy (4-8 horas)
4. Importar backups de databank si hay disco externo
5. Tiempo total de recuperacion: 1 dia

---

## ARCHIVOS QUE GIT NO DEBE TRACKEAR

Crear o actualizar .gitignore en la raiz del
proyecto con estas exclusiones:

*.sqx.bak
*.tmp
*.log
__pycache__/
.DS_Store
Thumbs.db

NOTA: Los archivos .sqx SI se trackean en Git
porque son las estrategias del proyecto.
Solo excluir los temporales y backups.

---

## VERIFICACION DE INTEGRIDAD

Cada lunes verificar:

[ ] GitHub tiene el ultimo commit del proyecto
[ ] Carpeta de backups tiene el ultimo databank
[ ] Datos historicos de SQ estan completos
[ ] No hay archivos huerfanos sin commit
[ ] El repositorio no tiene conflictos pendientes

Comando rapido de verificacion:
git status
git log --oneline -5

Si git status muestra archivos sin commit
→ hacer commit inmediatamente.

---

## REGLA FUNDAMENTAL

Un build de 48 horas no se puede reproducir.
Un commit tarda 30 segundos.
Un backup del databank tarda 5 minutos.
No hacer backup despues de cada build es
arriesgar 48 horas de computo por ahorrarse
5 minutos. No hay excusa.