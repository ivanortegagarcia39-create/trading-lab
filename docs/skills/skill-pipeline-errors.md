# Skill: Gestion de Errores del Pipeline

## Proposito
Guia para todos los agentes y para el usuario.
Define que hacer cuando algo falla de forma
inesperada en cualquier fase del pipeline.
Basada en los errores reales ocurridos durante
los Builds 1-7.

---

## ERRORES EN SQ BUILDER

### Error: Build termina en menos de 2 horas
Sintoma: build de 18 anos termina en 30-60 minutos
Causa: datos no cubren el periodo completo
Solucion:
1. Parar el build
2. Abrir SQ → Gestor de datos
3. Verificar fechas del simbolo
4. Si datos incompletos → descargar datos faltantes
5. Relanzar el build

### Error: 0 estrategias aceptadas con > 500 generadas
Sintoma: muchas estrategias generadas pero ninguna
pasa los filtros automaticos
Causa: filtros demasiado estrictos
Solucion:
1. Parar el build
2. Ir a Clasificacion → Filtros personalizados
3. Bajar Factor de beneficio de 0.8 a 0.7
4. Bajar Transacciones medias al mes de 8 a 5
5. Relanzar el build

### Error: PF maximo < 1.2 en todos los resultados
Sintoma: estrategias generadas pero PF muy bajo
Causa: hipotesis no tiene edge con comisiones reales
Solucion:
1. Parar el build
2. Invocar orchestrator para decision SIMPLIFICAR
3. Generar nueva hipotesis con market-analyst
4. NO bajar mas los filtros — el problema es la logica

### Error: SQ se cierra inesperadamente
Sintoma: SQ cierra solo durante el build
Causa: memoria insuficiente o error interno
Solucion:
1. Verificar que los resultados parciales
   se guardaron en Last Generation
2. Si hay resultados → guardarlos antes de relanzar
3. Reducir Population Size de 50 a 30
4. Reducir Islands de 4 a 2
5. Relanzar el build

### Error: Subfichas duplicadas
Sintoma: SQ da error al lanzar sobre subfichas
Causa: dos subfichas con la misma temporalidad
Solucion:
1. Ir a Tab Datos → Subfichas
2. Verificar que cada subficha tiene temporalidad
   diferente
3. Si son iguales → cambiar una a diferente periodo
4. O usar Simple strategy en vez de Multi-TF

### Error: Indicador sin operador de comparacion
Sintoma: SQ da error sobre bloques de construccion
Causa: indicador activado sin operador asociado
Solucion:
1. Ir a Bloques de construccion → Indicadores
2. Si hay indicador activado → activar tambien Operators
3. O desactivar el indicador si no es necesario

---

## ERRORES EN SQ RETESTER

### Error: Retester carga estrategias incorrectas
Sintoma: retester muestra estrategias de otros builds
Causa: databank incorrecto seleccionado
Solucion:
1. En Retester → Bancos de datos → Fuente
2. Seleccionar -currently selected-
3. Verificar manualmente que las estrategias
   correctas estan seleccionadas
4. O usar boton Carga para cargar desde
   results\reviewed\ directamente

### Error: Resultados muy diferentes entre builds
Sintoma: PF del Retester muy diferente al Builder
Causa: comisiones diferentes entre Builder y Retester
Solucion:
1. Verificar que las comisiones son identicas
   en Builder y Retester
2. EUR/USD: 0.5 pips + 7 USD + 0.5 pip slippage
3. XAU/USD: 30 pips + 7 USD + 2 pips slippage
4. Si son diferentes → ajustar y relanzar Retester

### Error: 0 trades en periodo OOS
Sintoma: Retester no genera ningun trade en 2021-2026
Causa: estrategia muy restrictiva o datos OOS vacios
Solucion:
1. Verificar que hay datos desde 2021 en SQ
2. Verificar que la sesion horaria cubre
   periodos con actividad real
3. Si datos OOS incompletos → descargar datos

---

## ERRORES EN CLAUDE CODE

### Error: Claude Code no reconoce el proyecto
Sintoma: Claude Code no lee CLAUDE.md ni los archivos
Causa: lanzado desde carpeta incorrecta
Solucion:
1. Cerrar Claude Code
2. cd C:\Users\ivano\trading-lab
3. Verificar que estais en la carpeta correcta
4. claude — relanzar desde la carpeta correcta

### Error: Agente propone logica no nativa en SQ
Sintoma: sq-specialist genera config con logica
que SQ no puede implementar
Causa: agente no leyo skill-sq-builder.md
Solucion:
1. Relanzar el agente con instruccion explicita:
   "Lee docs\skills\skill-sq-builder.md PRIMERO
   antes de generar ninguna configuracion"
2. Verificar cada condicion contra la skill

### Error: Claude Code pierde contexto en sesion larga
Sintoma: Claude Code repite preguntas ya respondidas
Causa: contexto de la sesion demasiado largo
Solucion:
1. Escribir en Claude Code:
   "Lee CLAUDE.md y docs\project-status.md
   para recuperar el contexto del proyecto"
2. Si persiste → abrir nueva sesion y pegar
   el contenido de docs\project-status.md

### Error: Commit falla por identidad no configurada
Sintoma: git commit da error sobre identidad
Causa: Git no tiene email y nombre configurados
Solucion:
git config --global user.email "tu@email.com"
git config --global user.name "Tu Nombre"
Luego repetir el commit.

---

## ERRORES EN ANTIGRAVITY

### Error: Archivo guardado en carpeta incorrecta
Sintoma: archivo creado en vault de Obsidian
  en vez de trading-lab
Causa: carpeta incorrecta abierta en Antigravity
Solucion:
1. File → Open Folder
2. Navegar a C:\Users\ivano\trading-lab
3. Select Folder
4. Verificar que el Explorer muestra trading-lab
5. Recrear el archivo en la ubicacion correcta

---

## ERRORES EN GIT

### Error: Nothing to commit
Sintoma: git commit dice nothing to commit
Causa: archivos ya commiteados anteriormente
Solucion: es normal — no hay nada que hacer

### Error: Merge conflict
Sintoma: git pull da error de conflicto
Causa: cambios en dos dispositivos diferentes
Solucion:
1. git status — ver archivos en conflicto
2. Abrir el archivo en conflicto en Antigravity
3. Resolver el conflicto manualmente
4. git add .
5. git commit -m "fix: merge conflict resuelto"

---

## PROTOCOLO GENERAL ANTE CUALQUIER ERROR

1. PARAR — no intentar solucionar sin entender
2. DOCUMENTAR — anotar el error exacto
3. DIAGNOSTICAR — identificar la causa raiz
4. CONSULTAR — buscar en esta skill la solucion
5. APLICAR — ejecutar la solucion paso a paso
6. VERIFICAR — confirmar que el error se resolvio
7. DOCUMENTAR — actualizar esta skill si el error
   no estaba documentado

---

## ERRORES CRITICOS — NUNCA IGNORAR

Estos errores requieren atencion inmediata:

1. Build usando datos OOS (2021-2026)
   → Parar inmediatamente — invalida los resultados

2. Comisiones incorrectas en Builder
   → Los resultados son irreales — relanzar con
   comisiones correctas

3. EA operando en cuenta real sin forward test
   → Pausar EA hasta completar forward test en demo

4. DD acercandose al limite de la prop firm
   → Activar protocolo de alerta roja del
   performance-monitor