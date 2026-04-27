# skill-telegram-setup.md — Configuración del bot Telegram

## Propósito
Guía para crear el bot y conectarlo al sistema de notificaciones de TradingLab.

---

## 1. Crear el bot con BotFather

```
1. Abrir Telegram → buscar @BotFather
2. Enviar: /newbot
3. Nombre visible: TradingLab Monitor
4. Username: tradinglab_<tuusuario>_bot
5. BotFather devuelve el TOKEN:
   123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
6. Guardar el token — no compartir, no commitear
```

---

## 2. Obtener el CHAT_ID

### Opción A — getUpdates
```
1. Enviar cualquier mensaje al bot desde tu cuenta
2. Abrir en el navegador:
   https://api.telegram.org/bot<TOKEN>/getUpdates
3. Buscar: "chat":{"id": <NÚMERO>}
4. Ese número es tu CHAT_ID
```

### Opción B — grupo/canal
```
1. Crear grupo privado
2. Añadir el bot como administrador
3. Enviar mensaje al grupo
4. Repetir getUpdates → el CHAT_ID del grupo es negativo (-100...)
```

---

## 3. Archivo de configuración

**Ruta:** `config/telegram-config.json`
**Estado:** en `.gitignore` — nunca se commitea

```json
{
    "token": "123456789:ABCdefGHIjklMNOpqrSTUvwxYZ",
    "chat_id": "-1001234567890"
}
```

---

## 4. Tipos de alertas

| Nivel | Emoji | Cuándo usarlo |
|-------|-------|---------------|
| INFO | ✅ | Pipeline completado, estrategia aprobada |
| WARNING | ⚠️ | DD superando 5%, build sin resultados |
| CRITICAL | 🔴 | DD > 8%, EA desconectado, error grave |
| ACCIÓN HUMANA | 🎯 | Challenge request, inicio demo |

---

## 5. Función Python de envío

```python
import json, requests
from pathlib import Path

def notify(message, level="INFO"):
    config = json.loads(Path("config/telegram-config.json").read_text())
    url = f"https://api.telegram.org/bot{config['token']}/sendMessage"
    emoji = {"INFO": "✅", "WARNING": "⚠️", "CRITICAL": "🔴"}
    requests.post(url, json={
        "chat_id": config["chat_id"],
        "text": f"{emoji.get(level, '')} {message}"
    }, timeout=10)
```

**Script centralizado:** `scripts/telegram-notifier.py`

Uso desde línea de comandos:
```bash
python scripts/telegram-notifier.py --level INFO --message "Build 10 completado"
python scripts/telegram-notifier.py --level CRITICAL --message "DD > 8%"
python scripts/telegram-notifier.py --challenge strategy.json
python scripts/telegram-notifier.py --daily-report metrics.json
python scripts/telegram-notifier.py --dry-run --level WARNING --message "Test"
```

---

## 6. Kill switch — comando /STOP

El bot puede escuchar comandos para detener los EAs de emergencia.

### Flujo
```
Usuario envía /STOP al bot
  → bot recibe el mensaje via getUpdates (polling)
  → script ejecuta cierre de todos los EAs en MT5
  → notificación CRITICAL confirmando el cierre
```

### Implementación (polling básico)
```python
import time, json, requests
from pathlib import Path

def poll_commands():
    config = json.loads(Path("config/telegram-config.json").read_text())
    url = f"https://api.telegram.org/bot{config['token']}"
    offset = 0
    while True:
        resp = requests.get(f"{url}/getUpdates",
                            params={"offset": offset, "timeout": 30}, timeout=35)
        for update in resp.json().get("result", []):
            offset = update["update_id"] + 1
            text = update.get("message", {}).get("text", "")
            if text.strip().upper() == "/STOP":
                execute_kill_switch()
        time.sleep(1)

def execute_kill_switch():
    # Implementación: cerrar terminal64.exe o enviar señal a MT5
    import subprocess
    subprocess.run(["taskkill", "/F", "/IM", "terminal64.exe"])
    notify("🔴 KILL SWITCH activado — todos los EAs detenidos", level="CRITICAL")
```

> El kill switch se activa SOLO desde el chat_id autorizado.
> Verificar siempre `update["message"]["chat"]["id"] == config["chat_id"]`.

---

## 7. Checklist de configuración

- [ ] Bot creado en BotFather y token guardado
- [ ] `config/telegram-config.json` creado (no commitear)
- [ ] CHAT_ID obtenido y verificado
- [ ] Mensaje de prueba recibido en Telegram
- [ ] `scripts/telegram-notifier.py` funcionando con `--dry-run`
- [ ] Primera notificación real enviada (INFO)
- [ ] Kill switch probado en entorno de test
