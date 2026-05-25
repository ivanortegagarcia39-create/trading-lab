#!/usr/bin/env python3
"""
sq-exporter-pyautogui.py -- Exporta .mq5 desde SQ GUI automaticamente.

Flujo:
  1. Abre SQ GUI si no esta abierto
  2. Focaliza la ventana de SQ
  3. Navega a Custom Projects → Builder → Results
  4. Selecciona estrategias (Ctrl+A o por nombre)
  5. Clic derecho → "Source code" → guarda .mq5 en results/approved/
  6. Cierra el dialogo

COORDENADAS:
  Las marcadas con # REL son relativas a la esquina superior-izquierda
  de la ventana de SQ (se calculan dinamicamente).
  Las marcadas con # ABS son absolutas y dependen de la resolucion.
  Las marcadas con # CALIBRATE hay que ajustarlas con SQ abierto
  ejecutando: python scripts/sq-exporter-pyautogui.py --calibrate

Uso:
    python scripts/sq-exporter-pyautogui.py
    python scripts/sq-exporter-pyautogui.py --strategy "Strategy 0.1487"
    python scripts/sq-exporter-pyautogui.py --dry-run
    python scripts/sq-exporter-pyautogui.py --calibrate

Requiere:
    pip install pyautogui pygetwindow Pillow
"""

import argparse
import io
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

try:
    import pyautogui
    import pygetwindow as gw
except ImportError as e:
    print(f"ERROR: dependencia no instalada — {e}")
    print("Ejecuta: pip install pyautogui pygetwindow Pillow")
    sys.exit(1)

# ── Rutas ──────────────────────────────────────────────────────────────────────

ROOT        = Path(__file__).parent.parent
APPROVED    = ROOT / "results" / "approved"
DEBUG_DIR   = ROOT / "results" / "debug-screenshots"
SQ_EXE      = Path(r"C:\Program Files\StrategyQuant X\StrategyQuantX.exe")
SQ_EXE_ALT = Path(r"D:\StrategyQuantX\StrategyQuantX.exe")

# ── Seguridad pyautogui ────────────────────────────────────────────────────────

pyautogui.FAILSAFE  = True   # mover raton a esquina sup-izq aborta el script
pyautogui.PAUSE     = 0.3    # pausa entre acciones (segundos)

# ── Identificacion de la ventana de SQ ────────────────────────────────────────

# Fragmentos del titulo de ventana que identifican SQ.
# Si SQ tiene otro titulo en tu instalacion, ajusta esta lista.
SQ_TITLE_FRAGMENTS = ["strategyquant", "strategy quant", "sq x"]

# ── Tiempos de espera (segundos) ───────────────────────────────────────────────

WAIT_SQ_OPEN     = 20   # espera max al abrir SQ desde cero
WAIT_UI_RESPONSE = 3    # espera tras click hasta que la UI reaccione
WAIT_MENU        = 1.5  # espera tras abrir menu contextual
WAIT_DIALOG      = 2    # espera que aparezca dialogo de guardado
WAIT_SAVE        = 5    # espera max al guardar un archivo

# ── Layout de SQ (coordenadas relativas a ventana) ────────────────────────────
#
# IMPORTANTE: estas coordenadas asumen SQ maximizado en 3440x1440.
# Si tu resolucion o layout es diferente, usa --calibrate para ajustarlas.
#
# Estructura del panel izquierdo de SQ (Custom Projects):
#   - Panel lateral izquierdo: ~300px de ancho
#   - Arbol de proyectos: empieza ~70px desde arriba de la ventana

LAYOUT = {
    # ── Panel izquierdo — arbol de proyectos ──────────────────────────
    # Clic en "Custom Projects" para expandir el arbol
    "custom_projects":  (150, 130),   # REL — CALIBRATE

    # Clic en "Builder" dentro del arbol
    "builder_node":     (165, 160),   # REL — CALIBRATE

    # Clic en "Results" dentro de Builder
    "results_node":     (178, 185),   # REL — CALIBRATE

    # ── Panel central — tabla de estrategias ──────────────────────────
    # Primer click en la tabla de resultados para darle foco
    "results_table":    (900, 400),   # REL — CALIBRATE

    # ── Menu contextual → "Source code" ──────────────────────────────
    # Offset en Y dentro del menu contextual donde aparece "Source code"
    # Cuenta las opciones: tipicamente 4-6 items abajo del inicio del menu
    "menu_source_code_offset_y": 120, # px desde donde aparece el menu — CALIBRATE
}


# ── I/O ────────────────────────────────────────────────────────────────────────

def _screenshot(name: str) -> Path | None:
    """Captura la pantalla y guarda en debug-screenshots/."""
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)
    ts   = datetime.now().strftime("%H%M%S")
    path = DEBUG_DIR / f"{ts}_{name}.png"
    try:
        pyautogui.screenshot(str(path))
        print(f"  [debug] Screenshot: {path.name}")
        return path
    except Exception as e:
        print(f"  [debug] No se pudo capturar screenshot: {e}")
        return None


def _fail(reason: str, label: str = "error") -> None:
    """Captura screenshot de debug y lanza excepcion."""
    _screenshot(label)
    raise RuntimeError(f"[ABORT] {reason}")


# ── Gestion de SQ ──────────────────────────────────────────────────────────────

def _sq_process_running() -> bool:
    """True si StrategyQuantX.exe esta en el listado de procesos."""
    r = subprocess.run(
        ["tasklist", "/FI", "IMAGENAME eq StrategyQuantX.exe"],
        capture_output=True, text=True, shell=True
    )
    return "strategyquantx.exe" in r.stdout.lower()


def _find_sq_window() -> gw.Win32Window | None:
    """Devuelve la ventana de SQ o None si no se encuentra."""
    for title in gw.getAllTitles():
        title_l = title.lower()
        if any(f in title_l for f in SQ_TITLE_FRAGMENTS):
            wins = gw.getWindowsWithTitle(title)
            if wins:
                return wins[0]
    return None


def open_sq(dry_run: bool) -> gw.Win32Window:
    """Abre SQ si no esta abierto y devuelve su ventana."""
    win = _find_sq_window()
    if win:
        print(f"  SQ ya abierto: '{win.title}'")
        return win

    # Buscar ejecutable
    sq_exe = None
    for candidate in [SQ_EXE, SQ_EXE_ALT]:
        if candidate.exists():
            sq_exe = candidate
            break

    if sq_exe is None:
        if dry_run:
            print(f"  [DRY-RUN] SQ EXE no encontrado — simulando igualmente")
            return None
        _fail(
            f"StrategyQuantX.exe no encontrado.\n"
            f"  Rutas buscadas:\n"
            f"    {SQ_EXE}\n"
            f"    {SQ_EXE_ALT}\n"
            f"  Abre SQ manualmente y vuelve a ejecutar.",
            "sq_not_found"
        )

    if dry_run:
        print(f"  [DRY-RUN] Abriria: {sq_exe}")
        return None

    print(f"  Abriendo SQ: {sq_exe.name} ...")
    subprocess.Popen([str(sq_exe)])

    # Esperar hasta WAIT_SQ_OPEN segundos
    deadline = time.time() + WAIT_SQ_OPEN
    while time.time() < deadline:
        time.sleep(2)
        win = _find_sq_window()
        if win:
            print(f"  SQ detectado: '{win.title}'")
            time.sleep(3)   # esperar que termine de cargar la UI
            return win

    _fail(f"SQ no aparecio en {WAIT_SQ_OPEN}s", "sq_open_timeout")


def focus_sq(win: gw.Win32Window, dry_run: bool) -> None:
    """Maximiza y focaliza la ventana de SQ."""
    if dry_run:
        print("  [DRY-RUN] Focalizaria ventana SQ")
        return
    try:
        win.restore()
        win.maximize()
        win.activate()
        time.sleep(1)
    except Exception as e:
        print(f"  WARN focus: {e} — continuando")


# ── Navegacion UI ──────────────────────────────────────────────────────────────

def _win_abs(win: gw.Win32Window, rel_x: int, rel_y: int) -> tuple[int, int]:
    """Convierte coordenadas relativas a la ventana en absolutas de pantalla."""
    return win.left + rel_x, win.top + rel_y


def navigate_to_results(win: gw.Win32Window, dry_run: bool) -> None:
    """
    Expande Custom Projects → Builder → Results en el panel izquierdo.

    El panel izquierdo de SQ muestra un arbol de proyectos.
    Los nodos se expanden con doble-clic o clic simple en la flecha.
    Ajusta LAYOUT['custom_projects'], ['builder_node'], ['results_node']
    si el layout de tu instalacion es diferente.
    """
    steps = [
        ("custom_projects", "Custom Projects"),
        ("builder_node",    "Builder"),
        ("results_node",    "Results"),
    ]
    for key, label in steps:
        rel = LAYOUT[key]
        abs_x, abs_y = _win_abs(win, *rel)
        print(f"  Clic en '{label}' ({abs_x}, {abs_y})...")
        if not dry_run:
            pyautogui.doubleClick(abs_x, abs_y)
            time.sleep(WAIT_UI_RESPONSE)
        else:
            print(f"  [DRY-RUN] doubleClick({abs_x}, {abs_y})")

    _screenshot("after_navigate")


def select_strategies(win: gw.Win32Window, strategy: str | None, dry_run: bool) -> None:
    """
    Da foco a la tabla de resultados y selecciona estrategias.
    Si strategy es None → Ctrl+A (todas).
    Si strategy tiene nombre → busca con Ctrl+F o selecciona manualmente.

    LIMITACION: la busqueda por nombre con Ctrl+F depende de que SQ
    implemente ese atajo en el panel Results. Si no, hay que hacer
    scroll manual + clic en la fila correcta (requiere calibracion visual).
    """
    table_rel = LAYOUT["results_table"]
    abs_x, abs_y = _win_abs(win, *table_rel)

    print(f"  Clic en tabla Results ({abs_x}, {abs_y})...")
    if not dry_run:
        pyautogui.click(abs_x, abs_y)
        time.sleep(0.5)

    if strategy:
        # Buscar estrategia por nombre — requiere que SQ soporte Ctrl+F
        # o que el nombre sea visible en la primera fila
        print(f"  Buscando estrategia: '{strategy}'")
        print(f"  NOTA: la seleccion por nombre requiere scroll manual si Ctrl+F no funciona")
        if not dry_run:
            pyautogui.hotkey("ctrl", "f")
            time.sleep(WAIT_UI_RESPONSE)
            pyautogui.typewrite(strategy, interval=0.05)
            time.sleep(0.5)
            pyautogui.press("enter")
            time.sleep(WAIT_UI_RESPONSE)
        else:
            print(f"  [DRY-RUN] Ctrl+F → '{strategy}' → Enter")
    else:
        # Seleccionar todo con Ctrl+A
        print("  Ctrl+A — seleccionando todas las estrategias...")
        if not dry_run:
            pyautogui.hotkey("ctrl", "a")
            time.sleep(0.5)
        else:
            print("  [DRY-RUN] Ctrl+A")

    _screenshot("after_select")


def open_context_menu(win: gw.Win32Window, dry_run: bool) -> tuple[int, int]:
    """
    Clic derecho en la tabla para abrir el menu contextual.
    Devuelve las coordenadas absolutas donde aparecio el menu.
    """
    table_rel = LAYOUT["results_table"]
    abs_x, abs_y = _win_abs(win, *table_rel)

    print(f"  Clic derecho en tabla ({abs_x}, {abs_y})...")
    if not dry_run:
        pyautogui.rightClick(abs_x, abs_y)
        time.sleep(WAIT_MENU)
    else:
        print(f"  [DRY-RUN] rightClick({abs_x}, {abs_y})")

    _screenshot("context_menu")
    return abs_x, abs_y


def click_source_code(menu_x: int, menu_y: int, dry_run: bool) -> None:
    """
    Hace clic en la opcion 'Source code' del menu contextual.

    El menu aparece aproximadamente donde se hizo el clic derecho.
    'Source code' suele estar 4-6 opciones abajo del inicio del menu.
    Ajusta LAYOUT['menu_source_code_offset_y'] segun tu instalacion.

    Alternativa: usar pyautogui.locateOnScreen() con una imagen de referencia
    del texto 'Source code' si las coordenadas varían.
    """
    offset_y = LAYOUT["menu_source_code_offset_y"]
    target_x = menu_x + 80   # centrado en el menu (ABS — CALIBRATE)
    target_y = menu_y + offset_y

    print(f"  Buscando 'Source code' en menu ({target_x}, {target_y})...")

    # Intento por imagen si existe imagen de referencia
    ref_img = ROOT / "config" / "sq-menu-source-code.png"
    if ref_img.exists() and not dry_run:
        loc = pyautogui.locateCenterOnScreen(str(ref_img), confidence=0.8)
        if loc:
            print(f"  'Source code' encontrado por imagen en ({loc.x}, {loc.y})")
            pyautogui.click(loc.x, loc.y)
            time.sleep(WAIT_DIALOG)
            return
        else:
            print("  WARN: imagen de referencia no encontrada — usando coordenadas fijas")

    if not dry_run:
        pyautogui.click(target_x, target_y)
        time.sleep(WAIT_DIALOG)
    else:
        print(f"  [DRY-RUN] click({target_x}, {target_y})")

    _screenshot("after_source_code")


def handle_save_dialog(activo_prefix: str, dry_run: bool) -> list[Path]:
    """
    Maneja el dialogo de guardado que abre SQ.

    SQ puede mostrar:
      a) Un dialogo de carpeta (seleccionar directorio de destino)
      b) Un dialogo de archivo por cada .mq5 (poco frecuente)
      c) Guardar directamente sin dialogo

    Estrategia: escribir la ruta de APPROVED y confirmar con Enter.
    Si SQ no muestra dialogo, los archivos quedan en el directorio
    predeterminado de SQ (normalmente Documents/StrategyQuant/strategies/).
    """
    APPROVED.mkdir(parents=True, exist_ok=True)
    approved_str = str(APPROVED)

    print(f"  Dialogo de guardado → escribiendo ruta: {approved_str}")

    if dry_run:
        print(f"  [DRY-RUN] typewrite('{approved_str}') → Enter")
        return []

    # Limpiar campo y escribir ruta destino
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.2)
    pyautogui.typewrite(approved_str, interval=0.04)
    time.sleep(0.3)
    pyautogui.press("enter")
    time.sleep(WAIT_SAVE)

    # Recopilar archivos guardados
    mq5_files = sorted(APPROVED.glob("*.mq5"))
    print(f"  Archivos .mq5 en approved/: {len(mq5_files)}")
    for f in mq5_files:
        print(f"    {f.name}")

    _screenshot("after_save")
    return mq5_files


def close_dialog(dry_run: bool) -> None:
    """Cierra cualquier dialogo abierto con Escape."""
    if dry_run:
        print("  [DRY-RUN] Escape para cerrar dialogo")
        return
    pyautogui.press("escape")
    time.sleep(0.5)


# ── Modo calibracion ──────────────────────────────────────────────────────────

def calibrate_mode() -> None:
    """
    Modo interactivo para obtener coordenadas exactas con SQ abierto.
    Mueve el raton a cada elemento y pulsa Enter para registrar la posicion.
    """
    print("\n" + "=" * 60)
    print("  MODO CALIBRACION — sq-exporter-pyautogui")
    print("=" * 60)
    print("  Asegurate de que SQ esta abierto y visible.")
    print("  Mueve el raton al elemento indicado y pulsa ENTER.")
    print("  Pulsa Ctrl+C para cancelar en cualquier momento.")
    print("=" * 60)

    win = _find_sq_window()
    if not win:
        print("  ERROR: no se encuentra ventana de SQ.")
        print("  Abre SQ manualmente y vuelve a ejecutar --calibrate")
        return

    print(f"\n  Ventana SQ: '{win.title}'")
    print(f"  Posicion : ({win.left}, {win.top}) | Tamano: {win.width}x{win.height}")

    elements = [
        ("custom_projects", "el nodo 'Custom Projects' en el panel izquierdo"),
        ("builder_node",    "el nodo 'Builder' dentro de Custom Projects"),
        ("results_node",    "el nodo 'Results' dentro de Builder"),
        ("results_table",   "el centro de la tabla de resultados (panel central)"),
    ]

    calibrated = {}
    for key, desc in elements:
        input(f"\n  -> Mueve el raton a: {desc}\n     Pulsa ENTER cuando este posicionado...")
        abs_x, abs_y = pyautogui.position()
        rel_x = abs_x - win.left
        rel_y = abs_y - win.top
        calibrated[key] = (rel_x, rel_y)
        print(f"     ABS=({abs_x},{abs_y})  REL=({rel_x},{rel_y}) ← copia en LAYOUT['{key}']")

    print("\n  Ahora haremos un clic derecho sobre una estrategia para medir el menu.")
    input("  -> Mueve el raton a una estrategia en Results y pulsa ENTER...")
    abs_x, abs_y = pyautogui.position()
    pyautogui.rightClick(abs_x, abs_y)
    time.sleep(WAIT_MENU)
    _screenshot("calibrate_menu")

    input("  -> Mueve el raton a la opcion 'Source code' del menu y pulsa ENTER...")
    menu_x, menu_y = pyautogui.position()
    offset_y = menu_y - abs_y
    calibrated["menu_source_code_offset_y"] = offset_y
    print(f"     menu_source_code_offset_y = {offset_y} ← copia en LAYOUT")

    pyautogui.press("escape")

    print("\n" + "=" * 60)
    print("  RESUMEN — pega estos valores en LAYOUT:")
    print("=" * 60)
    for k, v in calibrated.items():
        print(f"    \"{k}\": {v},")
    print("=" * 60)


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="sq-exporter-pyautogui -- Exporta .mq5 desde SQ GUI"
    )
    parser.add_argument("--strategy",  help="Nombre exacto de la estrategia a exportar (sin arg → todas)")
    parser.add_argument("--dry-run",   action="store_true", help="Simula sin tocar nada")
    parser.add_argument("--calibrate", action="store_true", help="Modo calibracion de coordenadas")
    parser.add_argument("--no-open",   action="store_true", help="No intenta abrir SQ si no esta corriendo")
    args = parser.parse_args()

    if args.calibrate:
        calibrate_mode()
        return 0

    print(f"\n{'='*60}")
    print(f"  SQ EXPORTER — PyAutoGUI")
    print(f"{'='*60}")
    print(f"  Estrategia : {args.strategy or 'TODAS (Ctrl+A)'}")
    print(f"  Destino    : {APPROVED}")
    print(f"  Dry-run    : {args.dry_run}")
    print(f"  FAILSAFE   : mover raton a esquina superior-izquierda aborta")
    print(f"{'='*60}\n")

    try:
        # ── 1. Abrir / encontrar SQ ──
        print("[1] Buscando ventana de SQ...")
        if args.no_open and not _find_sq_window():
            print("  ERROR: SQ no esta abierto y --no-open activo")
            return 1
        win = open_sq(args.dry_run)

        if args.dry_run and win is None:
            # En dry-run sin SQ abierto simulamos con una ventana ficticia
            print("  [DRY-RUN] Simulando ventana SQ en (0, 0) 1920x1080")
            class _FakeWin:
                left = 0; top = 0; width = 1920; height = 1080
                title = "FakeWindow"
                def restore(self): pass
                def maximize(self): pass
                def activate(self): pass
            win = _FakeWin()

        # ── 2. Focalizar ventana ──
        print("[2] Focalizando ventana SQ...")
        focus_sq(win, args.dry_run)

        # ── 3. Navegar a Results ──
        print("[3] Navegando a Custom Projects → Builder → Results...")
        navigate_to_results(win, args.dry_run)

        # ── 4. Seleccionar estrategias ──
        print("[4] Seleccionando estrategias...")
        select_strategies(win, args.strategy, args.dry_run)

        # ── 5. Menu contextual → Source code ──
        print("[5] Abriendo menu contextual...")
        menu_x, menu_y = open_context_menu(win, args.dry_run)

        print("[5b] Haciendo clic en 'Source code'...")
        click_source_code(menu_x, menu_y, args.dry_run)

        # ── 6. Dialogo de guardado ──
        print("[6] Manejando dialogo de guardado...")
        mq5_files = handle_save_dialog(args.strategy or "all", args.dry_run)

        # ── 7. Cerrar dialogo ──
        print("[7] Cerrando dialogo...")
        close_dialog(args.dry_run)

        # ── Informe ──
        print(f"\n{'='*60}")
        print(f"  EXPORTACION COMPLETADA")
        print(f"{'='*60}")
        if mq5_files:
            print(f"  {len(mq5_files)} archivo(s) .mq5 en {APPROVED}:")
            for f in mq5_files:
                print(f"    {f.name}")
        elif args.dry_run:
            print("  [DRY-RUN] Sin archivos reales generados")
        else:
            print("  AVISO: no se encontraron .mq5 en results/approved/")
            print("  Posibles causas:")
            print("    - SQ guardo los archivos en otro directorio")
            print("    - El dialogo de guardado no aparecio")
            print("    - Las coordenadas del menu necesitan calibracion")
            print(f"  Revisa screenshots en: {DEBUG_DIR}")
        print(f"{'='*60}")

        if not args.dry_run and mq5_files:
            print(f"\n  Siguiente paso:")
            print(f"  python scripts/export-specialist.py --build N --activo ACTIVO --strategy 'nombre'")

        return 0

    except RuntimeError as e:
        print(f"\n{e}")
        print(f"  Screenshots de debug en: {DEBUG_DIR}")
        return 1
    except KeyboardInterrupt:
        print("\n  Abortado por usuario (Ctrl+C o FAILSAFE)")
        _screenshot("aborted")
        return 1


if __name__ == "__main__":
    sys.exit(main())
