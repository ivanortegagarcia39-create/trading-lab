# Skill: Analisis de Correlacion del Portfolio

## Proposito

Define como medir, interpretar y gestionar la correlacion
entre estrategias del portfolio. Una correlacion alta entre
estrategias destruye la diversificacion y puede hacer que
el DD combinado sea tan alto como la peor estrategia individual.

---

## CORRELACION DE PEARSON

Mide la correlacion lineal entre los retornos de dos estrategias.
Rango: -1 (perfectamente opuestas) a +1 (identicas).

```
r = Σ((x_i - x̄)(y_i - ȳ)) / (n * σ_x * σ_y)
```

**Umbral del proyecto: correlacion < 0.5 para incluir en portfolio.**

| Correlacion | Interpretacion | Decision |
|-------------|----------------|----------|
| < 0.3 | Descorrelacionadas | Incluir — excelente diversificacion |
| 0.3 - 0.5 | Correlacion baja | Incluir — diversificacion aceptable |
| 0.5 - 0.7 | Correlacion moderada | EXCLUIR — poco valor de diversificacion |
| > 0.7 | Correlacion alta | EXCLUIR — son esencialmente la misma estrategia |
| > 0.85 | Correlacion muy alta | ALERTA CRITICA — Modo Panico |

---

## LIMITACIONES DE PEARSON

### No captura correlaciones no lineales

Dos estrategias pueden tener r = 0.1 en condiciones normales
pero r = 0.9 durante un crash. Pearson con datos historicos
no captura esta asimetria.

### Inestabilidad temporal

La correlacion calculada con datos 2003-2020 puede ser
completamente diferente a la correlacion en produccion 2026.
El mercado cambia — las correlaciones tambien.

### Factor Dolar (correlacion oculta)

EUR/USD, GBP/USD, AUD/USD, XAU/USD pueden tener
correlacion directa baja entre si en datos historicos.
Pero todos responden al mismo factor subyacente: debilidad del USD.
En eventos de fortaleza del dolar se mueven juntos.
Pearson no capta esto — requiere PCA (ver skill-pca-portfolio.md).

**Regla practica:** maximo 2 activos del Factor Dolar simultaneos.

---

## HRP — HIERARCHICAL RISK PARITY

Alternativa a la correlacion simple para asignar pesos.
Usa clustering jerarquico en lugar de correlacion directa.

**Ventajas sobre Markowitz clasico:**
- No requiere invertir la matriz de covarianza (numericamente inestable)
- Mas robusto cuando las correlaciones son inestables
- No sufre del problema de concentracion de Markowitz

**Implementacion:** scripts/hrp-portfolio.py

Usar HRP por defecto hasta tener 5+ estrategias con
historial estable de produccion. Es mas conservador que
Markowitz y mas adecuado para portfolios pequenos.

---

## CORRELACION DINAMICA EN PRODUCCION

La correlacion del backtest es historica — un promedio fijo.
En produccion la correlacion cambia semana a semana.

### Monitoreo mensual

Calcular correlacion con ventana rolling de 30 dias de retornos reales.
Si correlacion entre dos estrategias activas supera 0.6:
  → Alerta al orchestrator.
  → Investigar si el regimen de mercado ha cambiado.
  → No desactivar automaticamente — solo alertar.

### Modo Panico (correlacion media > 0.85)

Si la correlacion media del portfolio completo supera 0.85
durante mas de 5 dias consecutivos:

Accion automatica:
  1. Reducir riesgo de todas las estrategias a 0.5%
  2. Notificacion CRITICA al humano (CASO 2)
  3. No abrir nuevas posiciones hasta que la correlacion baje

Razon: correlacion > 0.85 en el portfolio significa que
todas las estrategias estan respondiendo al mismo factor.
El DD combinado puede ser catastrofico si ese factor
se mueve en contra del portfolio.

---

## CORRELACION POR SESION DE MERCADO

Las correlaciones varian segun la sesion de trading.

| Sesion | Correlaciones | Implicacion |
|--------|--------------|-------------|
| Asiatica (00:00-08:00 CEST) | Mas bajas | Mayor beneficio de diversificacion |
| Londres (08:00-17:00 CEST) | Moderadas | Diversificacion parcial |
| Overlap Londres-NY (14:00-17:00) | Mas altas | Menor beneficio de diversificacion |

Una estrategia que opera en sesion asiatica puede
coexistir con una estrategia que opera en overlap sin
conflicto de correlacion — operan en mercados distintos.

Para analisis granular por sesion: ver skill-pca-portfolio.md (Capa 3+).

---

## CALCULO EN EL PIPELINE

### Pre-produccion (backtest)

La correlacion se calcula con los retornos IS del backtest.
Usar los mismos datos IS que uso el Builder (2003-2020).
Implementado en scripts/portfolio-builder.py como
correlacion simplificada por factor de riesgo.

Limitacion conocida: sin datos de produccion real,
la correlacion se estima por factor (Factor Dolar: 0.6,
mismo activo: 0.9, diferente factor: 0.2).
Es una aproximacion conservadora.

### En produccion

Con datos reales de retorno diario por estrategia:
  Calcular matriz de correlacion mensualmente.
  Usar ventana rolling de 30 dias.
  El correlation-analyst actualiza la matriz en el registro.

---

## REGISTRO DE CORRELACION

Guardar en: results/portfolio-selected.json (campo correlaciones)

```json
{
  "correlaciones": {
    "XAUUSD-B10-1024-v1_vs_EURUSD-B11-2048-v1": 0.18,
    "XAUUSD-B10-1024-v1_vs_GBPJPY-B12-3072-v1": 0.22
  },
  "correlacion_media": 0.20,
  "modo_panico_activo": false,
  "fecha_calculo": "ISO-8601",
  "metodo": "pearson_backtest_is"
}
```

---

## LO QUE ESTA SKILL NUNCA HACE

NUNCA incluye dos estrategias con correlacion >= 0.5.
NUNCA ignora el Factor Dolar como fuente de correlacion oculta.
NUNCA usa correlacion de backtest como verdad absoluta en produccion.
NUNCA desactiva el monitoreo mensual de correlacion en produccion.
NUNCA permite mas de 2 activos del Factor Dolar simultaneamente.
NUNCA ignora una correlacion media > 0.85 en produccion.
