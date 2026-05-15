# Añadir LECCION-005 al lessons-learned sobre XAUUSD inviable

$leccion = @"

---

### LECCION-005: XAUUSD H1 inviable con spread 60 pips y reglas FTMO

Fecha: 2026-05-15
Build(s): 9, 10, 11
Decision: DESCARTAR activo permanentemente
Criterio que activo la decision: Coste por trade supera el riesgo permitido
Resultado observado: Con spread 60 pips (30 real x2), SL 50 pips y capital
  25000 USD al 1% de riesgo, el coste por trade es 317 USD vs riesgo de 250 USD.
  El coste supera el riesgo en un 26.8%. Con ratio 2:1 el ratio efectivo real
  es 1.6:1, por debajo del minimo del sistema. 3 builds consecutivos con 0
  estrategias en Results confirman la inviabilidad.
Leccion aplicable: XAUUSD descartado permanentemente con las reglas actuales.
  Activos viables: EURUSD (5.8%), USDJPY (6%), AUDUSD (6.5%), GBPUSD (7.2%).
  Ver results/asset-viability-ranking.json para ranking completo.
Ocurrencias confirmadas: 3 — ESTRUCTURAL
Estado: ESTRUCTURAL

CONTEXTO:
  Regimen de mercado: mixto (3 builds en periodos diferentes)
  Epoca del año: Q1-Q2 2026
  Volumen relativo: normal
  Prop firm activa: FTMO (objetivo)
  Activo principal: XAUUSD
  Fase del proyecto: Capa 0
"@

Add-Content "docs\lessons-learned.md" -Value $leccion -Encoding UTF8
Write-Host "LECCION-005 añadida"

git add -A && git commit -m "docs: LECCION-005 XAUUSD inviable - estructural confirmada" && git push origin main