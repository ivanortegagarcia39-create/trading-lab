# Skill: Seleccion de Broker para MT5

## Proposito
Criterios para elegir el broker de MT5 para el VPS de produccion.
El broker afecta directamente la calidad de ejecucion y la validez
del forward test respecto al backtest.

---

## REQUISITOS OBLIGATORIOS

| Requisito | Criterio | Por que |
|-----------|---------|---------|
| Compatible con FTMO | Broker partner oficial o en lista aceptada | FTMO requiere broker especifico para sus challenges |
| Servidor en LD4 o FR2 | Londres o Frankfurt | Latencia < 5ms a servidores FTMO |
| Spread XAUUSD ≤ 35 pips | Similar al configurado en backtest (30 pips) | Diferencia > 5 pips invalida el edge calculado |
| Sin restricciones en EAs | Permitido trading algoritmico 24/7 | Cuentas manuales o con limites bloquean el EA |
| Sin requoting | ECN o STP preferido | El requoting da precios distintos a los del backtest |
| Ejecucion en modo Market | Sin ejecucion diferida | Los EAs de SQ usan ordenes de mercado |

---

## BROKERS RECOMENDADOS PARA FTMO

### 1. Eightcap — PRIMERA OPCION

- **Estado:** broker partner oficial de FTMO
- **Servidores:** LD4 (Londres) — latencia ~0.3ms desde VPS EU
- **XAUUSD spread:** 20-25 pips en horario liquido
- **Comision:** variable por cuenta tipo
- **Cuenta RAW:** comision 3.5 USD/lote por lado = 7 USD round turn
- **Ventaja:** integrado directamente con el sistema de challenges FTMO

### 2. IC Markets — SEGUNDA OPCION

- **Estado:** aceptado por FTMO (no partner oficial)
- **Servidores:** LD4 (Londres) y NY4 (Nueva York)
- **XAUUSD spread:** 20-30 pips en horario liquido
- **Comision cuenta RAW:** 3.5 USD/lote por lado = 7 USD round turn
- **Ventaja:** muy alta liquidez, ejecucion rapida

### 3. Pepperstone — TERCERA OPCION

- **Estado:** aceptado por FTMO
- **Servidores:** LD4 (Londres)
- **XAUUSD spread:** 25-35 pips en horario liquido
- **Comision Razor:** 3.5 USD/lote por lado = 7 USD round turn
- **Ventaja:** regulado en multiple jurisdicciones, soporte 24/5

---

## VERIFICACION PRE-DEPLOY

Antes de desplegar en produccion, verificar:

### 1. Spread real en broker vs spread del backtest

```
Spread backtest (SQ)  : 60 pips (= 30 real × 2)
Spread real en broker : verificar en MT5 durante sesion liquida
Diferencia aceptable  : <= 5 pips del spread real configurado
Si diferencia > 5 pips → no deployer — buscar otro broker
```

En MT5: boton derecho en XAUUSD → Tick Chart o ver en pantalla de cotizaciones

### 2. Latencia VPS → servidor broker

```bash
# Desde el VPS Windows (CMD o PowerShell)
ping [servidor-broker-LD4]

# Criterio: ping < 5ms al servidor del broker
# Si > 10ms → buscar VPS mas cercano al servidor
```

### 3. EA funciona en cuenta demo del broker

1. Compilar el EA en MetaEditor (broker demo)
2. Cargar en MT5 demo del broker elegido
3. Verificar que:
   - No hay errores de importacion ni compilacion
   - El EA ejecuta ordenes correctamente
   - Los parametros se cargan sin error
   - El spread mostrado en MT5 es similar al configurado en SQ

---

## COMO ABRIR CUENTA DEMO EN EL BROKER

Para Eightcap:
1. Registrar cuenta en eightcap.com
2. Abrir cuenta demo MT5 RAW
3. Descargar MT5 con los servidores de Eightcap preconfigurados
4. Login con credenciales de la cuenta demo

Para IC Markets / Pepperstone: proceso similar desde sus webs.

---

## TABLA DE COMPARACION

| Broker | Partner FTMO | Spread XAU | Comision | Servidor | Recomendacion |
|--------|-------------|-----------|---------|---------|--------------|
| Eightcap | SI (oficial) | 20-25 pips | 7 USD/RT | LD4 | 1a opcion |
| IC Markets | Aceptado | 20-30 pips | 7 USD/RT | LD4, NY4 | 2a opcion |
| Pepperstone | Aceptado | 25-35 pips | 7 USD/RT | LD4 | 3a opcion |

RT = Round Turn (entrada + salida)

---

## CONFIGURACION DE MT5 EN VPS

Una vez elegido el broker:

1. Instalar MT5 en VPS Windows
2. Login con credenciales del challenge FTMO
3. Verificar que el simbolo del broker coincide con el del challenge
   - FTMO puede tener prefijos: XAUUSDm, XAUUSDpro, etc.
   - El EA debe usar el simbolo exacto de la cuenta
4. Ajustar parametros del EA si el spread real es diferente al del backtest

---

## REGLA CRITICA

**El broker no cambia el backtest — solo afecta la ejecucion real.**
Si el spread del broker en produccion es 10 pips mayor que el del backtest,
el EA puede seguir siendo rentable pero con menor margen.
Verificar que el edge sigue siendo positivo con el spread real del broker.

---

## Referencias

- `docs/skills/skill-data-sources.md` — fuentes de datos para backtesting
- `docs/skills/skill-vps-setup.md` — configuracion del VPS
- `docs/skills/skill-mt5-deployment.md` — deployment de EAs en MT5
- `config/build-defaults.json` — spreads y comisiones configurados en builds
