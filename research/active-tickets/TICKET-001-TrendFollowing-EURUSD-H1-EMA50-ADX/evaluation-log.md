# Evaluation Log — TrendFollowing-EURUSD-H1-EMA50-ADX

## 2026-04-10 — market-selector
Activo seleccionado: EUR/USD. Score 8.70/10 frente a XAU/USD 7.80/10.
Justificacion: maxima compatibilidad FTMO, spread minimo (0.5 pips),
datos completos 2003-2026, liquidez maxima del mercado Forex.
Informe completo: research/market-notes/market-selection-2026-04-10.md
---

## 2026-04-10 — market-analyst
Hipotesis generada: TrendFollowing-EURUSD-H1-EMA50-ADX.
Estilo: Trend Following. Logica: precio vs EMA(50) + filtro ADX(14) > 20.
Edge economico: inercia institucional en sesiones de alta liquidez Londres/NY.
Riesgo de sobreajuste evaluado: BAJO.
2 indicadores (EMA50 + ADX14), parametros estandar, logica simetrica, 100% nativo SQ.
Se elige esta logica para no duplicar con Build 7 (NBARBreakout-RSI, resultado desconocido).
Archivo: research/strategy-hypotheses/TrendFollowing-EURUSD-H1-EMA50-ADX.md
---

## 2026-04-10 — propfirm-analyst
Prop firms evaluadas: FTMO, E8, TFT (unicas compatibles con EUR/USD spot).
MFF, TopStep y Apex descartadas — solo futuros CME.
Recomendacion principal: FTMO 2-Step 25.000 USD.
Justificacion: DD dinamico favorable para trend following, sin regla del mejor dia,
calculo de viabilidad cuadra (33 trades para 2.500 USD objetivo a ritmo 12/mes).
Alternativa: E8 si DD IS backtest <= 5%.
TFT no recomendada — trailing DD peligroso + regla de consistencia diaria conflictiva.
Alerta: si DD IS supera 7% en backtest revisar antes de comprar challenge FTMO.
Informe completo: results/reviewed/TrendFollowing-EURUSD-H1-EMA50-ADX-propfirm-eval.md
---

## 2026-04-10 — funding-specialist
Evaluacion teorica pre-build completada. Momento 1 del pipeline.
Reglas basicas FTMO: TODAS CUMPLEN. Tipo de estrategia permitido.
Decision: COMPATIBLE CON FTMO — puede avanzar al Builder.
Alertas registradas (verificar en Evaluation Gate):
  ALERTA 1: Frecuencia baja (6-12 t/mes) — verificar gaps > 14 dias sin trades
  ALERTA 2: DD IS esperado 4-8% deja margen ajustado — filtrar candidatas DD IS > 6.5%
  ALERTA 3: Contar meses con < 4 dias de trading — si > 20% de meses → ajustar hipotesis
EV teorico: 75-116 USD/trade segun WR. Objetivo 2.500 USD alcanzable en 2-6 meses.
Informe completo: results/reviewed/TrendFollowing-EURUSD-H1-EMA50-ADX-funding-eval.md
---

## 2026-04-10 — sq-specialist
Configuracion de Builder completada para Build 8.
Hipotesis verificada: 2 condiciones nativas SQ, parametros estandar, riesgo sobreajuste BAJO.
Bloques activados: Close above/below EMA(50) + ADX(14) above level 20.
Rangos de parametros: EMA periodo 40-60, ADX nivel 18-25, SL x1.8-2.2, TP x4.0-5.0.
Max condiciones fijado en 2 para forzar logica simple.
Duracion estimada del build: 6-12 horas.
Checklist pre-build: COMPLETO — listo para lanzar.
Configuracion guardada: strategyquant/builder/TrendFollowing-EURUSD-H1-EMA50-ADX-config.md
---
