# Skill: WFO Matrix — Walk-Forward Optimization Matrix

## Proposito

La WFO Matrix prueba la estrategia con multiples configuraciones
diferentes del Walk-Forward simultaneamente. Una estrategia que
pasa solo con una configuracion especifica esta sobreajustada
a esa particion temporal — no es robusta.

---

## QUE ES LA WFO MATRIX

SQ prueba automaticamente 5 configuraciones de WFO con:
- Diferentes tamaños de ventana IS/OOS
- Diferentes puntos de inicio temporal
- Diferentes ratios IS/OOS (70/30, 75/25, 80/20, etc.)

Cada configuracion genera un conjunto de ventanas deslizantes
y calcula el PF OOS en cada una.

El resultado es una matriz: 5 configuraciones × N ventanas.
Una estrategia robusta debe mostrar PF > 1.0 en la mayoria
de celdas de esa matriz — no solo en una fila o columna.

**Diferencia WFO Estandar vs Matrix:**

| | WFO Estandar | WFO Matrix |
|-|--------------|------------|
| Configuraciones | 1 | 5 simultaneas |
| Particiones | Una configuracion de IS/OOS | Multiples |
| Robustez | Moderada | Alta |
| Riesgo de sesgo | Medio | Bajo |

La Matrix es mas conservadora y por tanto mas robusta.
Una estrategia que solo pasa con una sola particion IS/OOS
no deberia llegar al portfolio.

---

## CRITERIO DE APROBACION

### Aprobacion

Minimo 3 de 5 configuraciones cumplen:
- PF OOS >= 1.2 en esa configuracion
- DD OOS <= 7% en esa configuracion

### Catastrophic Veto (descarte inmediato)

Si CUALQUIER configuracion de las 5 muestra:
- PF OOS < 0.8 (la estrategia pierde dinero en ese periodo)
- DD OOS > 10%

→ DESCARTE aunque las otras 4 configuren sean perfectas.

Razon: una ventana temporal con PF < 0.8 indica que
la estrategia fue destruida por ese regimen de mercado.
Ese regimen puede volver. No podemos ignorarlo.

### Zona gris

Si pasa 3-4 configuraciones pero ninguna con Catastrophic Veto:
→ Continuar con stress test. La zona gris no es descarte.
→ Registrar en el informe que paso con zona gris.

---

## WFE — WALK-FORWARD EFFICIENCY

Mide cuanto del edge del IS se preserva en OOS.
Es el indicador mas importante de robustez temporal.

```
WFE = (PF_OOS_promedio / PF_IS_promedio) * 100
```

| WFE | Clasificacion | Accion |
|-----|--------------|--------|
| >= 50% | Robusto | Continuar al stress test |
| 40-49% | Zona gris | Revision manual — puede continuar |
| < 40% | Descarte | Descarte automatico |

Ejemplo:
  PF IS promedio: 1.80
  PF OOS promedio: 0.95 → WFE = (0.95/1.80)*100 = 52.8% → ROBUSTO

Nota: el PF OOS puede ser menor que el IS — eso es normal.
Lo que no es aceptable es que sea < 40% del IS (demasiada degradacion).

---

## COMO CONFIGURAR EN SQ

```
SQ → abrir estrategia → Retester → WFO → seleccionar "Matrix"

Tab Datos:
  Simbolo: mismo activo que en el Builder
  Periodo: 2003-01-01 a fecha actual (IS + OOS juntos)
  Comisiones: identicas al Builder

Tab WFO:
  Tipo: Matrix
  IS ratio: 70-80%
  OOS ratio: 20-30%
  Numero de ventanas: 5-10
  Dejar que SQ genere las combinaciones automaticamente

Tab Opciones de negociacion:
  Mismos ajustes que en el Builder (sesion, max trades)

Ejecutar → esperar resultados de las 5 configuraciones
```

---

## INTERPRETACION DE RESULTADOS

### Señales positivas (estrategia robusta)

- Todas las configuraciones muestran PF OOS > 1.0
- La caida PF IS→OOS es similar en todas las configuraciones
- No hay ninguna ventana temporal con perdidas sostenidas
- WFE estable entre configuraciones (sin varianza extrema)

### Señales de sobreajuste

- Solo 1-2 configuraciones pasan — las otras fallan
- WFE varia mucho entre configuraciones (ej: 65% vs 25%)
- Una configuracion especifica domina todos los resultados
- Hay periodos temporales sistematicamente malos

### Señales de sobreajuste extremo

- PF IS muy alto (> 2.5) pero PF OOS < 1.0 en la mayoria
- WFE < 30% en todas las configuraciones
- Catastrophic Veto activado

---

## REGISTRO DEL WFO MATRIX

Guardar en: results/approved/[ID]-wfo-matrix.json

```json
{
  "estrategia_id": "XAUUSD-B10-1024-v1",
  "timestamp": "ISO-8601",
  "configuraciones_probadas": 5,
  "configuraciones_aprobadas": 4,
  "wfe_promedio": 58.3,
  "catastrophic_veto": false,
  "resultado": "APROBADO",
  "detalle": [
    {"config": 1, "is_ratio": 0.70, "pf_is": 1.82, "pf_oos": 1.12, "dd_oos": 4.1, "pasa": true},
    {"config": 2, "is_ratio": 0.75, "pf_is": 1.78, "pf_oos": 1.08, "dd_oos": 5.3, "pasa": true},
    {"config": 3, "is_ratio": 0.80, "pf_is": 1.85, "pf_oos": 0.98, "dd_oos": 6.8, "pasa": false},
    {"config": 4, "is_ratio": 0.70, "pf_is": 1.79, "pf_oos": 1.15, "dd_oos": 3.9, "pasa": true},
    {"config": 5, "is_ratio": 0.75, "pf_is": 1.81, "pf_oos": 1.19, "dd_oos": 4.5, "pasa": true}
  ]
}
```

---

## LO QUE ESTA SKILL NUNCA HACE

NUNCA acepta una estrategia que dispara el Catastrophic Veto.
NUNCA acepta una estrategia con WFE < 40%.
NUNCA usa solo una configuracion WFO — siempre la Matrix.
NUNCA omite el registro del detalle por configuracion.
NUNCA ajusta el umbral de WFE sin instruccion explicita.
