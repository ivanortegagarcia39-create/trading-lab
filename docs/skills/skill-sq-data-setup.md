# skill-sq-data-setup.md — Configuración de Datos en SQ para TradingLab

## 1. Instrumentos FTMO a crear en SQ

Para cada activo, crear un instrumento personalizado con broker = FTMO y los siguientes valores:

| Activo   | Pip Size | Point Value | Spread BT (2x real) | Slippage | Comisión    |
|----------|----------|-------------|---------------------|----------|-------------|
| EURUSD   | 0.0001   | 10 USD/lot  | 1.0 pips            | 0.5 pip  | 7 USD/lote  |
| GBPUSD   | 0.0001   | 10 USD/lot  | 1.6 pips            | 0.5 pip  | 7 USD/lote  |
| USDJPY   | 0.01     | 9.1 USD/lot | 1.0 pips            | 0.5 pip  | 7 USD/lote  |
| USDCHF   | 0.0001   | 10 USD/lot  | 1.4 pips            | 0.5 pip  | 7 USD/lote  |
| AUDUSD   | 0.0001   | 10 USD/lot  | 1.2 pips            | 0.5 pip  | 7 USD/lote  |
| NZDUSD   | 0.0001   | 10 USD/lot  | 1.6 pips            | 0.5 pip  | 7 USD/lote  |
| USDCAD   | 0.0001   | 7.7 USD/lot | 1.4 pips            | 0.5 pip  | 7 USD/lote  |
| EURGBP   | 0.0001   | 12.5 USD/l  | 1.6 pips            | 0.8 pip  | 7 USD/lote  |
| EURJPY   | 0.01     | 9.1 USD/lot | 2.0 pips            | 0.8 pip  | 7 USD/lote  |
| GBPJPY   | 0.01     | 9.1 USD/lot | 2.4 pips            | 1.0 pip  | 7 USD/lote  |
| EURAUD   | 0.0001   | 6.7 USD/lot | 3.0 pips            | 0.8 pip  | 7 USD/lote  |
| EURCHF   | 0.0001   | 10 USD/lot  | 2.0 pips            | 0.8 pip  | 7 USD/lote  |
| AUDJPY   | 0.01     | 9.1 USD/lot | 2.0 pips            | 0.8 pip  | 7 USD/lote  |
| GBPAUD   | 0.0001   | 6.7 USD/lot | 3.0 pips            | 1.0 pip  | 7 USD/lote  |
| CADJPY   | 0.01     | 9.1 USD/lot | 2.0 pips            | 0.8 pip  | 7 USD/lote  |
| NZDJPY   | 0.01     | 9.1 USD/lot | 2.0 pips            | 0.8 pip  | 7 USD/lote  |
| XAUUSD   | 0.01     | 1 USD/lot   | 60 pips             | 2.0 pip  | 7 USD/lote  |
| XAGUSD   | 0.001    | 5 USD/lot   | 6 pips              | 1.0 pip  | 7 USD/lote  |
| US30     | 1.0      | 1 USD/lot   | 4.0 pts             | 2.0 pts  | 7 USD/lote  |
| US500    | 0.1      | 1 USD/lot   | 1.0 pts             | 1.0 pts  | 7 USD/lote  |
| NAS100   | 0.1      | 1 USD/lot   | 3.0 pts             | 2.0 pts  | 7 USD/lote  |
| DE40     | 0.1      | 1 USD/lot   | 6.0 pts             | 2.0 pts  | 7 USD/lote  |
| UK100    | 0.1      | 1 USD/lot   | 2.0 pts             | 2.0 pts  | 7 USD/lote  |
| JP225    | 1.0      | 0.91 USD/l  | 10.0 pts            | 2.0 pts  | 7 USD/lote  |

> Regla: spread backtest = spread real × 2 (conservador para backtests en SQ)

---

## 2. Descarga de datos (Dukascopy M1)

**Proveedor:** Dukascopy  
**Timeframe:** M1 (siempre — se puede agregar H1 después derivando de M1)  
**Período:** 2003-01-01 → hoy  
**Opción:** Fill gaps (NO reescribir datos existentes)

### Proceso en SQ Data Manager

1. SQ → Data → Data Manager → Download
2. Seleccionar símbolo
3. Provider: **Dukascopy**
4. Timeframe: **M1**
5. From: **2003-01-01** | To: **hoy**
6. Fill gaps: **ON** (no reescribir)
7. Click Download

### Orden de prioridad de descarga

```
1. EURUSD   — referencia, menor peso computacional
2. XAUUSD   — prioridad Build 11 (activo activo)
3. GBPUSD, USDJPY, USDCHF
4. AUDUSD, NZDUSD, USDCAD
5. Crosses: EURGBP, EURJPY, GBPJPY, EURAUD
6. XAGUSD, Indices: US500, NAS100, US30, DE40
7. Resto de crosses y exóticos
```

Estimación de tiempo: ~2-4 horas por activo en conexión estándar.  
Espacio total estimado: **20-30 GB** para todos los activos.

---

## 3. Asignación de instrumentos FTMO en SQ

Después de descargar cada símbolo:

1. SQ → Symbols → [buscar símbolo, ej: EURUSD]
2. Click **Edit**
3. En campo **Broker/Instrument**: seleccionar o crear instrumento FTMO
4. Verificar que los valores coinciden con la tabla de arriba
5. Guardar
6. Repetir para cada símbolo

### Verificación antes de buildear

```bash
python scripts/sq-data-validator.py --activo XAUUSD
```

Si resultado es LISTO → listo para buildear.  
Si resultado es WARN/FAIL → ver instrucciones manuales en el output.

---

## 4. Limitaciones conocidas

| Activo | Limitación | Causa | Impacto |
|--------|-----------|-------|---------|
| XAUUSD | ~2.6% gaps estructurales | Dukascopy no tiene datos de fines de semana y festivos en oro | Normal, no es error |
| XAGUSD | ~2.0% gaps | Ídem plata | Normal |
| US30/US500/NAS100 | ~1.2-1.5% gaps | Festivos USA en datos intradía | Normal |
| Todos  | Datos M1 2003+ | Dukascopy empieza 2003 para la mayoría | Usar IS hasta 2020-12, OOS desde 2021-01 |
| Crypto | Solo desde 2017-2018 | No hay datos anteriores | Menor período IS/OOS |
| Indices JP225 | Gaps mayores en noches | Mercado cerrado Tokio | Normal |

**Nota:** Los gaps estructurales de XAUUSD (2.6%) fueron la causa del WARN en health-check.  
Son normales. El umbral de alerta en sq-data-validator es 2.0% para distinguir estructurales de reales.

---

## 5. Checklist antes de lanzar Build 11 en ivano

- [ ] Descarga XAUUSD M1 completa (desde 2003)
- [ ] Instrumento FTMO asignado (spread 60 pips, slippage 2, comisión 7)
- [ ] `python scripts/sq-data-validator.py --activo XAUUSD` → LISTO
- [ ] `python scripts/build-launcher.py --build 11 --activo XAUUSD --spread-real 30`
