#!/usr/bin/env python3
"""
sq-controller.py — Controla StrategyQuant X via Selenium.

Instalacion: pip install selenium webdriver-manager

Uso:
    python scripts/sq-controller.py --connect
    python scripts/sq-controller.py --configure --build 11 --activo XAUUSD
    python scripts/sq-controller.py --start
    python scripts/sq-controller.py --stop
    python scripts/sq-controller.py --status
    python scripts/sq-controller.py --export --output results/
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT    = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"

SQ_URL       = "http://localhost:8080"
RETRY_COUNT  = 3
RETRY_WAIT   = 10

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("sq-controller")


class SQNotRunningError(Exception):
    pass


class SQElementNotFoundError(Exception):
    pass


class SQController:
    def __init__(self):
        self.driver = None
        self.wait   = None

    def connect(self):
        """Inicializar Selenium WebDriver y verificar que SQ está corriendo."""
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.common.exceptions import WebDriverException
        from webdriver_manager.chrome import ChromeDriverManager

        for attempt in range(1, RETRY_COUNT + 1):
            try:
                options = webdriver.ChromeOptions()
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                self.driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=options,
                )
                self.driver.get(SQ_URL)
                self.wait = WebDriverWait(self.driver, 15)
                logger.info(f"Conectado a SQ en {SQ_URL}")
                return True
            except WebDriverException as e:
                logger.warning(f"Intento {attempt}/{RETRY_COUNT} fallido: {e}")
                if attempt < RETRY_COUNT:
                    time.sleep(RETRY_WAIT)
                else:
                    raise SQNotRunningError(
                        f"No se pudo conectar a SQ en {SQ_URL} tras {RETRY_COUNT} intentos. "
                        "Verificar que StrategyQuant X esta corriendo."
                    )

    def _find(self, by, locator, timeout=15):
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, locator))
            )
        except TimeoutException:
            raise SQElementNotFoundError(f"Elemento no encontrado: {by}={locator}")

    def _click(self, by, locator, timeout=15):
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException
        try:
            elem = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, locator))
            )
            elem.click()
            return elem
        except TimeoutException:
            raise SQElementNotFoundError(f"Elemento no clickable: {by}={locator}")

    def set_symbol(self, symbol_name: str):
        """Navegar a simbolos y seleccionar el especificado."""
        from selenium.webdriver.common.by import By
        logger.info(f"Configurando simbolo: {symbol_name}")
        self._click(By.XPATH, "//a[contains(text(),'Symbols') or contains(@href,'symbols')]")
        time.sleep(1)
        search = self._find(By.XPATH, "//input[@placeholder='Search' or @type='search']")
        search.clear()
        search.send_keys(symbol_name)
        time.sleep(0.5)
        self._click(By.XPATH, f"//td[contains(text(),'{symbol_name}')]")
        logger.info(f"Simbolo {symbol_name} seleccionado")

    def configure_builder(self, config: dict):
        """Configurar todos los parametros del Builder desde un dict."""
        from selenium.webdriver.common.by import By
        logger.info("Configurando Builder...")
        self._click(By.XPATH, "//a[contains(text(),'Builder') or contains(@href,'builder')]")
        time.sleep(1)

        field_map = {
            "symbol":         "//input[@id='symbol' or @name='symbol']",
            "timeframe":      "//select[@id='timeframe' or @name='timeframe']",
            "capital":        "//input[@id='capital' or @name='capital']",
            "risk":           "//input[@id='risk' or @name='risk']",
            "generations":    "//input[@id='generations' or @name='generations']",
            "population":     "//input[@id='population' or @name='population']",
            "islands":        "//input[@id='islands' or @name='islands']",
            "max_strategies": "//input[@id='maxStrategies' or @name='maxStrategies']",
            "trading_hours":  "//input[@id='tradingHours' or @name='tradingHours']",
            "sl_type":        "//select[@id='slType' or @name='slType']",
            "tp_type":        "//select[@id='tpType' or @name='tpType']",
            "atr_multiplier_sl": "//input[@id='atrSL' or @name='atrSL']",
            "atr_multiplier_tp": "//input[@id='atrTP' or @name='atrTP']",
        }

        for param, xpath in field_map.items():
            value = config.get(param)
            if value is None:
                continue
            try:
                elem = self._find(By.XPATH, xpath, timeout=5)
                elem.clear()
                elem.send_keys(str(value))
                logger.info(f"  {param} = {value}")
            except SQElementNotFoundError:
                logger.warning(f"  Campo no encontrado: {param}")

    def set_data_range(self, is_start: str, is_end: str, oos_start: str, oos_end: str):
        """Configurar fechas IS y OOS en el Builder."""
        from selenium.webdriver.common.by import By
        logger.info(f"Fechas IS: {is_start}->{is_end}  OOS: {oos_start}->{oos_end}")
        date_fields = {
            "is_start":  ("is_start",  "//input[@id='isStart' or @placeholder='IS Start']"),
            "is_end":    ("is_end",    "//input[@id='isEnd'   or @placeholder='IS End']"),
            "oos_start": ("oos_start", "//input[@id='oosStart' or @placeholder='OOS Start']"),
            "oos_end":   ("oos_end",   "//input[@id='oosEnd'   or @placeholder='OOS End']"),
        }
        values = {"is_start": is_start, "is_end": is_end,
                  "oos_start": oos_start, "oos_end": oos_end}
        for key, (_, xpath) in date_fields.items():
            try:
                elem = self._find(By.XPATH, xpath, timeout=5)
                elem.clear()
                elem.send_keys(values[key])
            except SQElementNotFoundError:
                logger.warning(f"  Campo fecha no encontrado: {key}")

    def activate_all_blocks(self):
        """Activar todos los grupos de indicadores (paleta completa)."""
        from selenium.webdriver.common.by import By
        logger.info("Activando todos los bloques de indicadores...")
        try:
            self._click(By.XPATH, "//a[contains(text(),'Blocks') or contains(text(),'Indicators')]")
            time.sleep(0.5)
            select_all = self.driver.find_elements(
                By.XPATH,
                "//input[@type='checkbox' and (@id='selectAll' or contains(@name,'all'))]",
            )
            if select_all:
                for cb in select_all:
                    if not cb.is_selected():
                        cb.click()
                logger.info("  Todos los bloques activados via 'Select All'")
            else:
                checkboxes = self.driver.find_elements(By.XPATH, "//input[@type='checkbox']")
                activated  = sum(1 for cb in checkboxes
                                 if not cb.is_selected() and (cb.click() or True))
                logger.info(f"  {activated} bloques activados individualmente")
        except SQElementNotFoundError:
            logger.warning("  Pestana de bloques no encontrada")

    def set_filters(self, min_pf: float, min_trades_month: int, max_dd: float):
        """Configurar filtros del Builder."""
        from selenium.webdriver.common.by import By
        logger.info(f"Filtros: PF>{min_pf}, trades/mes>{min_trades_month}, DD<{max_dd}")
        for value, xpath in [
            (str(min_pf),           "//input[@id='minPF' or @placeholder='Min PF']"),
            (str(min_trades_month), "//input[@id='minTrades' or @name='minTrades']"),
            (str(max_dd),           "//input[@id='maxDD'   or @name='maxDD']"),
        ]:
            try:
                elem = self._find(By.XPATH, xpath, timeout=5)
                elem.clear()
                elem.send_keys(value)
            except SQElementNotFoundError:
                logger.warning(f"  Filtro no encontrado para valor {value}")

    def start_builder(self) -> datetime:
        """Pulsar Start y verificar que el Builder arranca."""
        from selenium.webdriver.common.by import By
        logger.info("Iniciando Builder...")
        self._click(By.XPATH, "//button[contains(text(),'Start') or @id='btnStart']")
        time.sleep(2)
        ts     = datetime.now()
        status = self.get_builder_status()
        if status.get("state") != "RUNNING":
            raise RuntimeError(f"Builder no arranco. Estado: {status}")
        logger.info(f"  Builder iniciado a las {ts.strftime('%H:%M:%S')}")
        return ts

    def stop_builder(self):
        """Pulsar Stop y esperar confirmacion de parada."""
        from selenium.webdriver.common.by import By
        logger.info("Parando Builder...")
        self._click(By.XPATH, "//button[contains(text(),'Stop') or @id='btnStop']")
        for _ in range(12):
            time.sleep(5)
            if self.get_builder_status().get("state") != "RUNNING":
                logger.info("  Builder parado correctamente")
                return
        logger.warning("  Builder podria no haberse parado correctamente")

    def get_databank_count(self) -> int:
        """Leer numero de estrategias en el databank."""
        from selenium.webdriver.common.by import By
        try:
            elem = self._find(
                By.XPATH,
                "//span[contains(@id,'databankCount') or contains(@class,'databank-count')]",
                timeout=5,
            )
            return int(elem.text.strip().replace(",", ""))
        except (SQElementNotFoundError, ValueError):
            return 0

    def export_databank_csv(self, output_folder: str) -> list:
        """Exportar todas las estrategias del databank a CSV."""
        from selenium.webdriver.common.by import By
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Exportando databank a {output_folder}...")
        self._click(By.XPATH, "//a[contains(text(),'Databank') or contains(@href,'databank')]")
        time.sleep(0.5)
        self._click(By.XPATH, "//button[contains(text(),'Export') or @id='btnExport']")
        time.sleep(2)
        try:
            csv_opt = self.driver.find_element(
                By.XPATH, "//option[contains(text(),'CSV')] | //button[contains(text(),'CSV')]"
            )
            csv_opt.click()
            time.sleep(1)
        except Exception:
            pass
        try:
            confirm = self.driver.find_element(
                By.XPATH, "//button[contains(text(),'OK') or contains(text(),'Confirm')]"
            )
            confirm.click()
            time.sleep(3)
        except Exception:
            pass
        exported = list(output_path.glob("Strategy*.csv")) + list(output_path.glob("*.csv"))
        logger.info(f"  {len(exported)} archivos exportados")
        return [str(f) for f in exported]

    def get_builder_status(self) -> dict:
        """Leer estado del Builder: state, strategies, best_pf."""
        from selenium.webdriver.common.by import By
        result = {"state": "UNKNOWN", "strategies": 0, "best_pf": 0.0}
        try:
            elems = self.driver.find_elements(
                By.XPATH,
                "//span[contains(@id,'builderStatus') or contains(@class,'builder-status')]",
            )
            if elems:
                text = elems[0].text.upper()
                if "RUNNING" in text or "BUILDING" in text:
                    result["state"] = "RUNNING"
                elif "STOPPED" in text or "PAUSED" in text:
                    result["state"] = "STOPPED"
                elif "FINISHED" in text or "DONE" in text:
                    result["state"] = "FINISHED"
            result["strategies"] = self.get_databank_count()
            pf_elems = self.driver.find_elements(
                By.XPATH, "//span[contains(@id,'bestPF') or contains(@class,'best-pf')]"
            )
            if pf_elems:
                result["best_pf"] = float(pf_elems[0].text.strip() or 0)
        except Exception as e:
            logger.warning(f"Error leyendo estado: {e}")
        return result

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None


def _load_build_config(build_n: int, activo: str) -> dict:
    defaults_path = ROOT / "config" / "build-defaults.json"
    if defaults_path.exists():
        try:
            return json.loads(defaults_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "symbol": activo, "timeframe": "H1", "capital": 25000,
        "risk": 1.0, "generations": 30, "population": 100,
        "islands": 4, "max_strategies": 2000,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="SQ Controller — TradingLab")
    parser.add_argument("--connect",   action="store_true", help="Verificar conexion con SQ")
    parser.add_argument("--configure", action="store_true", help="Configurar Builder")
    parser.add_argument("--start",     action="store_true", help="Iniciar Builder")
    parser.add_argument("--stop",      action="store_true", help="Parar Builder")
    parser.add_argument("--status",    action="store_true", help="Ver estado actual")
    parser.add_argument("--export",    action="store_true", help="Exportar databank a CSV")
    parser.add_argument("--build",     type=int,            help="Numero del build")
    parser.add_argument("--activo",                         help="Activo (ej: XAUUSD)")
    parser.add_argument("--output",    default="results/",  help="Carpeta de exportacion")
    args = parser.parse_args()

    if not any([args.connect, args.configure, args.start,
                args.stop, args.status, args.export]):
        parser.print_help()
        return 0

    ctrl = SQController()
    try:
        ctrl.connect()
        print(f"  Conectado a SQ en {SQ_URL}")

        if args.configure:
            if not args.build or not args.activo:
                print("  ERROR: --configure requiere --build y --activo")
                return 1
            config = _load_build_config(args.build, args.activo.upper())
            ctrl.configure_builder(config)
            print(f"  Builder configurado para Build {args.build} — {args.activo.upper()}")

        if args.start:
            ts = ctrl.start_builder()
            print(f"  Builder iniciado: {ts.strftime('%Y-%m-%d %H:%M:%S')}")

        if args.stop:
            ctrl.stop_builder()
            print("  Builder parado")

        if args.status:
            status = ctrl.get_builder_status()
            print(f"  Estado    : {status['state']}")
            print(f"  Estrategias en databank: {status['strategies']}")
            print(f"  Mejor PF  : {status['best_pf']:.2f}")

        if args.export:
            files = ctrl.export_databank_csv(args.output)
            print(f"  Exportados {len(files)} archivos a {args.output}")
            for f in files:
                print(f"    {f}")

        return 0

    except SQNotRunningError as e:
        print(f"  ERROR: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error inesperado: {e}", exc_info=True)
        return 1
    finally:
        ctrl.close()


if __name__ == "__main__":
    sys.exit(main())
