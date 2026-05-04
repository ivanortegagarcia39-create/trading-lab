Revisa el archivo scripts/sq-project-generator.py y añade una 
función verify_cfx() que se ejecute SIEMPRE al final de la 
generación y verifique que:

1. El CFX no contiene NINGUNA referencia a activos distintos 
   al activo del build (ej: si es XAUUSD, no debe haber EURUSD)
2. El Chart symbol apunta al activo correcto
3. El spread es el esperado (spread_real × 2)
4. No hay InstrumentInfo residuales de otros activos

Si cualquier verificación falla: abortar con error claro y 
restaurar el backup automáticamente.

También añade esta entrada al archivo lessons-learned 
(docs/lessons-learned.md o donde esté en el repo):

### LECCION-005: CFX residual apunta a activo incorrecto

Fecha: 2026-05-04
Build(s): 11 (detectado pre-launch)
Decision: ALERTA -> CORREGIDO
Criterio: nodos EURUSD_dukascopy residuales en CFX de XAUUSD
Resultado observado: CFX tenía instrument=XAUUSD_ftmo correcto
  pero Chart symbol=EURUSD_M1_dukas incorrecto. SQ habría 
  backtestado lógica XAUUSD con datos EURUSD.
Leccion aplicable: verificar TODOS los nodos del CFX antes 
  de lanzar, no solo spread e instrumento FTMO.
  verify_cfx() obligatorio en sq-project-generator.py.
Ocurrencias confirmadas: 1 — TENTATIVA

CONTEXTO:
  Regimen de mercado: N/A
  Epoca del año: Q2 2026
  Volumen relativo: N/A
  Prop firm activa: ninguna
  Activo principal: XAUUSD
  Fase del proyecto: Capa 0

Cuando termines:
git add -A && git commit -m "fix: verify_cfx() en sq-project-generator + LECCION-005" && git push origin main