# Skill: Protocolo de Recuperacion ante Fallos

## Proposito
Define que hacer cuando algo falla durante el
pipeline — especialmente durante builds de 48 horas
en modo continuo. Cada minuto de build perdido
es tiempo que no se recupera.
Las acciones de recuperacion son automaticas
y no requieren decision humana.

---

## FALLOS DURANTE EL BUILD LIBRE (48h)

### Fallo 1: SQ se cierra inesperadamente
Causa probable: memoria insuficiente o error interno.

Recuperacion:
1. Abrir SQ inmediatamente
2. Ir al databank del Builder
3. Verificar cuantas candidatas se guardaron
4. Si hay candidatas guardadas:
   - Exportar las candidatas del databank
   - Guardar en results\raw\build-results\
   - Las candidatas guardadas son VALIDAS
   - Relanzar el build desde donde se quedo
5. Si el databank esta vacio:
   - El build se perdio completamente
   - Relanzar desde cero con misma configuracion

Prevencion:
- Cerrar todos los programas innecesarios antes
  del build (navegador, Obsidian, Antigravity)
- Verificar que hay al menos 8 GB de RAM libre
- No usar el ordenador para otras tareas pesadas
  durante el build

### Fallo 2: El ordenador se reinicia
Causa probable: actualizacion de Windows,
corte de luz, reinicio programado.

Recuperacion:
1. Abrir SQ y verificar el databank
2. Las candidatas que entraron al databank antes
   del reinicio estan guardadas y son validas
3. Relanzar el build con la misma configuracion
4. El modo continuo empezara un ciclo nuevo

Prevencion:
- Desactivar actualizaciones automaticas de Windows
  durante el build:
  Configuracion → Windows Update → Pausar 7 dias
- Desactivar suspension automatica:
  Configuracion → Energia → Nunca suspender
- Si hay riesgo de corte de luz usar SAI (UPS)

### Fallo 3: Build corriendo pero 0 candidatas tras 12h
Causa probable: comisiones incorrectas o datos
insuficientes.

Recuperacion:
1. NO parar el build todavia — esperar 4 horas mas
2. Si a las 16 horas sigue en 0:
   - Parar el build
   - Verificar comisiones (error mas comun)
   - Verificar datos con data-manager
   - Si comisiones incorrectas → corregir y relanzar
   - Si datos incorrectos → descargar y relanzar
3. Si hay candidatas pero PF maximo < 1.0:
   - Las comisiones probablemente estan mal
   - Verificar spread y slippage del activo

CRITICO: La solucion NUNCA es desactivar bloques
de indicadores. Si el Builder libre no encuentra
nada con paleta completa el problema es la
configuracion tecnica, no la paleta.

### Fallo 4: SQ muestra error de datos
Causa probable: datos corruptos o incompletos.

Recuperacion:
1. Parar el build
2. Ir a Gestor de datos en SQ
3. Verificar el simbolo y las fechas
4. Si hay gaps → descargar datos faltantes
5. Si datos corruptos → borrar y redescargar
6. Relanzar el build

### Fallo 5: Disco duro lleno
Causa probable: 1000 estrategias en databank
ocupan espacio considerable.

Recuperacion:
1. Exportar las candidatas actuales del databank
2. Guardar en results\raw\build-results\
3. Limpiar espacio en disco
4. Relanzar el build

Prevencion:
- Verificar al menos 10 GB libres antes del build
- No acumular builds anteriores sin limpiar

---

## FALLOS DURANTE EL RETESTER

### Fallo 1: Retester no carga las estrategias
Causa probable: formato incorrecto o databank erroneo.

Recuperacion:
1. Verificar que las estrategias estan en
   results\reviewed\ en formato .sqx
2. Usar el boton Carga — no el databank
3. Si no carga → exportar del databank y reimportar

### Fallo 2: Resultados muy diferentes al Builder
Causa probable: comisiones diferentes.

Recuperacion:
1. Comparar comisiones del Builder vs Retester
2. Si son diferentes → el Retester esta MAL
3. Corregir comisiones y relanzar
4. NUNCA aceptar resultados con comisiones distintas

### Fallo 3: 0 trades en periodo OOS
Causa probable: datos OOS no descargados o
estrategia muy restrictiva.

Recuperacion:
1. Verificar datos 2021-actual en Gestor de datos
2. Si no hay datos OOS → descargar
3. Si hay datos pero 0 trades → la estrategia
   no genera señales en el periodo reciente
4. Documentar y dejar que el paso 12b descarte
   automaticamente

---

## FALLOS DURANTE EL WFO

### Fallo 1: WFO tarda mas de 12 horas
Causa probable: demasiados parametros o
rangos demasiado amplios.

Recuperacion:
1. Si lleva mas de 12 horas → parar
2. Reducir rangos de parametros (centrar mas
   en los valores del Builder)
3. Reducir de 3 parametros a 2 si es necesario
4. Relanzar

### Fallo 2: SQ se cierra durante el WFO
Recuperacion:
1. El WFO parcial NO se puede recuperar
2. Hay que relanzar desde cero
3. Verificar RAM disponible antes de relanzar

---

## FALLOS EN CLAUDE CODE

### Fallo 1: Claude Code no lee el proyecto
Causa probable: lanzado desde carpeta incorrecta.

Recuperacion:
1. Cerrar Claude Code
2. cd C:\Users\[usuario]\trading-lab
3. claude
4. Verificar que lee CLAUDE.md correctamente

### Fallo 2: Claude Code pierde contexto
Causa probable: sesion demasiado larga.

Recuperacion:
1. Pegar: "Lee CLAUDE.md y docs\project-status.md
   para recuperar el contexto completo"
2. Si persiste → cerrar sesion, hacer commit,
   abrir nueva sesion

### Fallo 3: Claude Code propone hipotesis manual
Causa probable: no leyo CLAUDE.md correctamente.

Recuperacion:
1. Rechazar la propuesta inmediatamente
2. Recordar: "Este proyecto usa Builder libre.
   No hay hipotesis manuales. Lee CLAUDE.md."
3. Si persiste → cerrar y abrir nueva sesion

---

## FALLOS EN GIT

### Fallo 1: Push rechazado
Causa probable: el otro dispositivo hizo push
antes y hay conflictos.

Recuperacion:
1. git pull origin main
2. Si hay conflictos → resolver en Antigravity
3. git add .
4. git commit -m "fix: merge conflict resuelto"
5. git push origin main

### Fallo 2: Commit accidental de archivos grandes
Causa probable: archivos .sqx en el repositorio.

Recuperacion:
1. Crear .gitignore si no existe
2. Añadir: *.sqx
3. git rm --cached [archivo]
4. git commit -m "fix: eliminar archivo grande"
5. git push origin main

---

## PROTOCOLO GENERAL ANTE CUALQUIER FALLO

1. PARAR — no intentar solucionar sin entender
2. VERIFICAR — que se perdio y que se conservo
3. DOCUMENTAR — anotar el error en el ticket
4. CONSULTAR — buscar en esta skill la solucion
5. APLICAR — ejecutar la recuperacion paso a paso
6. VERIFICAR — confirmar que se resolvio
7. CONTINUAR — retomar el pipeline donde se quedo

---

## PREVENCION ANTES DE CADA BUILD DE 48h

Checklist de prevencion:

[ ] Windows Update pausado 7 dias
[ ] Suspension automatica desactivada
[ ] Protector de pantalla desactivado
[ ] Al menos 10 GB libres en disco
[ ] Al menos 8 GB RAM disponibles
[ ] Programas innecesarios cerrados
[ ] SQ actualizado a ultima version
[ ] Datos verificados por data-manager
[ ] Commit de Git hecho antes de lanzar
[ ] Ordenador conectado a corriente (no bateria)

---

## REGLA FUNDAMENTAL

Los fallos tecnicos se resuelven con procedimientos.
No con decisiones emocionales.
Si se pierde un build → se relanza con la misma
configuracion. No se cambia nada.
Si SQ no encuentra candidatas → se verifica la
configuracion tecnica. No se restringe la paleta.
Los numeros deciden. Los fallos se documentan.