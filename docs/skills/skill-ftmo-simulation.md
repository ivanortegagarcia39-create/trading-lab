# Skill: Simulacion de Challenge FTMO

## Proposito
Guia para el funding-specialist y el orchestrator.
Define como calcular si una estrategia aprobada
pasaria un challenge FTMO 2-Step real.

---

## POR QUE SIMULAR EL CHALLENGE

Los resultados del Builder y Retester muestran
metricas globales de años de datos.
El challenge FTMO dura hasta alcanzar el objetivo
con limites dinamicos diarios.
Una estrategia con buen PF global puede fallar
si tiene rachas malas en periodos cortos.

---

## DATOS NECESARIOS PARA LA SIMULACION

- PF out-of-sample del Retester
- Max Drawdown out-of-sample
- Trades por mes (promedio)
- Win Rate
- Ratio TP/SL
- Rendimiento mensual promedio
- Peor mes historico
- Mejor mes historico
- Max racha perdedora consecutiva

---

## CALCULO DE VIABILIDAD — CUENTA 25.000$

### Objetivo del Challenge
Ganar 2.500$ (10%) en plazo ilimitado.
Riesgo por trade: 250$ (1%).

### Formula de rendimiento por trade
Con ratio TP/SL 2:1 y win rate 45%:
Rendimiento = 250$ x (0.45 x 2 - 0.55) = 87.5$ por trade
Trades necesarios: 2.500$ / 87.5$ = 29 trades minimo

Con ratio TP/SL 3:1 y win rate 40%:
Rendimiento = 250$ x (0.40 x 3 - 0.60) = 150$ por trade
Trades necesarios: 2.500$ / 150$ = 17 trades minimo

### Tabla de referencia rapida

Ratio 2:1, WR 45%: ~29 trades para objetivo
Ratio 2:1, WR 50%: ~20 trades para objetivo
Ratio 2.5:1, WR 42%: ~22 trades para objetivo
Ratio 3:1, WR 40%: ~17 trades para objetivo

Con 2 trades por dia en H1 y sesion 08:00-20:00:
~40 trades al mes → cualquier ratio >= 2:1 viable

---

## VERIFICACION DE LIMITES DINAMICOS

### Daily Loss Limit (5% dinamico = 1.250$ inicial)
Margen operativo: 3% = 750$

Con 1% riesgo y max 2 trades/dia:
Peor caso (2 perdedores): 500$ = 2% → DENTRO del 3%
Margen de seguridad: 250$ adicionales

Señal de alerta:
Si el peor dia historico en Retester supera 750$
→ riesgo de violar Daily Loss en challenge real.

### Max Drawdown (10% dinamico = 2.500$ inicial)
Margen operativo: 7% = 1.750$

Max racha perdedora segura:
6 trades x 250$ = 1.500$ → DENTRO del 7%
7 trades x 250$ = 1.750$ → en el limite

Señal de alerta:
Si la max racha perdedora en Retester supera
6 trades consecutivos → riesgo alto en challenge.

---

## SIMULACION MANUAL DEL CHALLENGE

### Como simularla con datos del Retester

1. Dividir resultados del Retester en ventanas de 30 dias
2. Para cada ventana calcular:
   - Rendimiento total del periodo
   - DD maximo del periodo
   - Dia con mayor perdida

3. Clasificar cada ventana:
   PASA si:
   - Rendimiento >= +10%
   - DD maximo < 7%
   - Ningun dia con perdida > 3%

   FALLA si:
   - Rendimiento < +10% al final
   - DD supera el 7%
   - Algun dia con perdida > 3%

4. Calcular porcentaje de ventanas que PASAN
   > 60% → estrategia lista para challenge
   40-60% → revisar tamaño de posicion
   < 40% → no intentar el challenge todavia

---

## CHECKLIST PRE-CHALLENGE

[ ] PF out-of-sample >= 1.5 con comisiones reales
[ ] Rendimiento mensual promedio supera +10%
    en al menos 40% de los meses del Retester
[ ] Ningun mes con dia de perdida > 3%
[ ] DD maximo en cualquier ventana de 30 dias < 7%
[ ] Trades por mes >= 20
[ ] Ratio TP/SL >= 2:1
[ ] Max racha perdedora <= 6 trades consecutivos
[ ] WFE del Optimizer >= 50%
[ ] Decision humana final: SI

Si alguno no se cumple → no intentar el challenge.
Volver al pipeline y mejorar o generar nueva estrategia.

---

## NOTAS SOBRE EL CHALLENGE 2-STEP

### Fase 1 — Challenge
Objetivo: +10%
Daily Loss: 5% dinamico
Max DD: 10% dinamico
Dias minimos: 4 con posiciones iniciadas
Sin Regla del Mejor Dia

### Fase 2 — Verification
Objetivo: +5%
Mismos limites de riesgo
Mismos dias minimos
Misma estrategia — NO cambiar nada

### Cuenta Funded
Misma estrategia que en el challenge.
FTMO puede cancelar si se detecta cambio de logica.
Profit split: 80% base, escalable hasta 90%.