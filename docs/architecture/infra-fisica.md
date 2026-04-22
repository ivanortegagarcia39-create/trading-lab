# Infraestructura Fisica del Proyecto

## Dispositivos del proyecto

### ivano
Rol: documentacion, Claude Code, git, scripts Python
Software: Git, Python 3.13, Claude Code, Obsidian
Cuando esta activo: siempre que se trabaja en el repo
Sistema: Windows 10 Pro

### alber
Rol: SQ builds, data management, MT5 local
Software: SQ X Pro Build 143, Git, Python 3.13,
  MT5, Claude Code
Cuando esta activo: durante builds y verificaciones
Sistema: Windows (verificar version)

---

## Estandar de terminal

PowerShell o CMD: comandos de sistema, git, instalar software
Python directo: manipulacion de datos SQ

Razon critica: PowerShell corrompe CSVs con separador
europeo (;) de SQ al usar Import-Csv sin especificar
delimitador. Siempre usar Python para datos SQ.

Separador CSV de SQ: punto y coma (;)
Formato decimal de SQ: coma (,) en algunos exports

REGLA: cualquier script que lea exports de SQ
debe abrir con:
  pandas.read_csv(file, sep=';', decimal=',')

---

## Consideraciones de hardware para builds SQ

Para builds largos de 24-48h en SQ:
- Mantener temperatura CPU < 80 grados C
  (SQ es extremadamente intensivo en CPU)
- Deshabilitar actualizaciones automaticas de Windows
  durante builds activos
- No ejecutar otros procesos pesados durante builds
- UPS recomendado para evitar apagones
  El apagon del 2026-04-22 interrumpio Build 10

Alternativa futura: instancia cloud para SQ cuando
el proyecto llegue a Capa 2 del roadmap.

---

## Sincronizacion entre dispositivos

Protocolo obligatorio:
1. git pull antes de empezar cualquier sesion
2. Trabajar normalmente
3. git push al finalizar la sesion

Frecuencia: al inicio Y al final de cada sesion.
Nunca trabajar en los dos dispositivos sin
sincronizar primero — los conflictos de git
en archivos binarios de SQ no se pueden resolver.

Dispositivo principal del repo: ivano
Dispositivo de builds: alber

Si hay conflicto: la version de ivano prevalece
para documentacion, la version de alber prevalece
para exports y resultados de SQ.

---

## Archivos criticos por dispositivo

Solo en alber (no commitear):
- strategyquant/databanks/*.sdf (bases de datos SQ)
- strategyquant/strategies/*.xml (estrategias SQ)
- MT5/Experts/*.ex5 (EAs compilados)

En ambos (repo git):
- Toda la carpeta docs/
- Toda la carpeta agents/
- Scripts Python en scripts/
- Resultados en results/

---

## Incidentes de hardware registrados

2026-04-22: apagon durante Build 10 en alber
  → Build interrumpido, datos no corrompidos
  → Reanudar desde el inicio del build
  → Pendiente: UPS para alber
