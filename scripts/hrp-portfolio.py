"""
hrp-portfolio.py
Optimizacion de portfolio con Hierarchical Risk Parity (HRP).
Compara HRP vs Markowitz (maximo Sharpe) y elige automaticamente.

Uso:
    python hrp-portfolio.py \
        --returns-csv results/strategy-returns.csv \
        --output results/portfolio-weights.json

Criterio de seleccion automatica:
    HRP   cuando correlaciones son inestables O hay < 5 estrategias
    MVO   cuando hay >= 5 estrategias con correlaciones estables

Restricciones:
    Ninguna estrategia puede superar el 40% del portfolio.

Input CSV formato:
    Fecha,Estrategia_A,Estrategia_B,Estrategia_C,...
    2021-01-04,0.012,-0.003,0.007,...
    (returns diarios como decimales)

Output JSON:
    {
      "metodo": "HRP",
      "razon": "< 5 estrategias",
      "pesos": {"Estrategia_A": 0.35, "Estrategia_B": 0.40, ...},
      "sharpe_hrp": 1.23,
      "sharpe_mvo": 1.18,
      "correlacion_media": 0.21,
      "correlacion_estable": true,
      "fecha": "2026-04-21T09:00:00Z"
    }
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

import numpy as np

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    from scipy.cluster.hierarchy import dendrogram, linkage
    from scipy.spatial.distance import squareform
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

try:
    from pypfopt import EfficientFrontier, risk_models, expected_returns
    HAS_PYPFOPT = True
except ImportError:
    HAS_PYPFOPT = False


# ─── Utilidades ───────────────────────────────────────────────────────────────

def load_returns(csv_path: str) -> tuple[list[str], np.ndarray]:
    """Carga el CSV de returns. Devuelve (nombres, matriz NxT)."""
    if not HAS_PANDAS:
        raise ImportError("pandas no disponible. Instalar: pip install pandas")
    import pandas as pd
    df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    names = list(df.columns)
    returns = df.values.T  # shape: (N_estrategias, T_dias)
    return names, returns


def correlation_matrix(returns: np.ndarray) -> np.ndarray:
    """Calcula la matriz de correlacion (N x N)."""
    cov = np.cov(returns)
    std = np.sqrt(np.diag(cov))
    with np.errstate(divide="ignore", invalid="ignore"):
        corr = np.where(
            np.outer(std, std) > 0,
            cov / np.outer(std, std),
            0.0,
        )
    np.fill_diagonal(corr, 1.0)
    return corr


def is_correlation_stable(returns: np.ndarray, threshold: float = 0.15) -> bool:
    """
    Estima si las correlaciones son estables dividiendo la serie en dos mitades
    y comparando la correlacion media de cada mitad.
    Estable si la diferencia es < threshold.
    """
    T = returns.shape[1]
    if T < 40:
        return False  # muy pocas observaciones para estimar estabilidad
    mid = T // 2
    corr1 = correlation_matrix(returns[:, :mid])
    corr2 = correlation_matrix(returns[:, mid:])
    n = corr1.shape[0]
    # Media de correlaciones off-diagonal
    mask = ~np.eye(n, dtype=bool)
    mean1 = np.abs(corr1[mask]).mean()
    mean2 = np.abs(corr2[mask]).mean()
    return abs(mean1 - mean2) < threshold


def sharpe_ratio(weights: np.ndarray, returns: np.ndarray,
                 rf: float = 0.0) -> float:
    """Calcula el Sharpe ratio anualizado (252 dias) de un portfolio."""
    portfolio_returns = weights @ returns  # shape: (T,)
    mean_ret = portfolio_returns.mean() * 252
    std_ret = portfolio_returns.std() * np.sqrt(252)
    if std_ret == 0:
        return 0.0
    return (mean_ret - rf) / std_ret


def apply_max_weight_constraint(weights: dict[str, float],
                                max_w: float = 0.40) -> dict[str, float]:
    """
    Normaliza los pesos limitando el maximo a max_w.
    Redistribuye el exceso proporcionalmente entre los demas.
    """
    names = list(weights.keys())
    w = np.array([weights[n] for n in names])
    # Clipear y renormalizar iterativamente
    for _ in range(100):
        clipped = np.clip(w, 0, max_w)
        total = clipped.sum()
        if total == 0:
            clipped = np.ones(len(w)) / len(w)
            break
        clipped /= total
        if np.allclose(w, clipped, atol=1e-6):
            break
        w = clipped
    return {n: float(round(v, 6)) for n, v in zip(names, w)}


# ─── HRP ──────────────────────────────────────────────────────────────────────

def hrp_weights(returns: np.ndarray, names: list[str]) -> dict[str, float]:
    """
    Implementacion de Hierarchical Risk Parity (Lopez de Prado 2016).
    No requiere PyPortfolioOpt — implementacion manual.
    """
    if not HAS_SCIPY:
        raise ImportError("scipy no disponible. Instalar: pip install scipy")

    n = returns.shape[0]
    corr = correlation_matrix(returns)
    cov = np.cov(returns)

    # Convertir correlacion a distancia y construir dendrograma
    dist = np.sqrt(0.5 * (1 - corr))
    np.fill_diagonal(dist, 0.0)
    condensed = squareform(dist)
    link = linkage(condensed, method="single")

    # Orden de las hojas del dendrograma
    from scipy.cluster.hierarchy import leaves_list
    sorted_idx = leaves_list(link)

    # Recursive bisection con inverse-variance weighting
    def get_cluster_var(idx: list[int]) -> float:
        cov_sub = cov[np.ix_(idx, idx)]
        inv_diag = 1.0 / np.diag(cov_sub)
        w = inv_diag / inv_diag.sum()
        return float(w @ cov_sub @ w)

    def recursive_bisection(items: list[int]) -> np.ndarray:
        if len(items) == 1:
            return np.array([1.0])
        mid = len(items) // 2
        left, right = items[:mid], items[mid:]
        var_left = get_cluster_var(left)
        var_right = get_cluster_var(right)
        alpha = 1 - var_left / (var_left + var_right)
        w_left = recursive_bisection(left) * alpha
        w_right = recursive_bisection(right) * (1 - alpha)
        return np.concatenate([w_left, w_right])

    sorted_items = list(sorted_idx)
    w_sorted = recursive_bisection(sorted_items)

    # Reordenar pesos al orden original
    w = np.zeros(n)
    for i, orig_idx in enumerate(sorted_items):
        w[orig_idx] = w_sorted[i]

    return {name: float(round(float(wi), 6)) for name, wi in zip(names, w)}


# ─── Markowitz MVO ────────────────────────────────────────────────────────────

def mvo_weights(returns: np.ndarray, names: list[str]) -> dict[str, float] | None:
    """
    Maximo Sharpe ratio via PyPortfolioOpt.
    Devuelve None si PyPortfolioOpt no esta disponible.
    """
    if not HAS_PYPFOPT or not HAS_PANDAS:
        return None

    import pandas as pd
    df = pd.DataFrame(returns.T, columns=names)
    mu = expected_returns.mean_historical_return(df, frequency=252)
    S = risk_models.sample_cov(df, frequency=252)
    try:
        ef = EfficientFrontier(mu, S)
        ef.max_sharpe()
        cleaned = ef.clean_weights()
        return {k: float(v) for k, v in cleaned.items()}
    except Exception:
        return None


# ─── Logica principal ─────────────────────────────────────────────────────────

def select_method(n_strategies: int, corr_stable: bool) -> tuple[str, str]:
    """
    Devuelve (metodo, razon) segun los criterios del proyecto.
    HRP: < 5 estrategias O correlaciones inestables
    MVO: >= 5 estrategias Y correlaciones estables
    """
    if n_strategies < 5:
        return "HRP", f"< 5 estrategias ({n_strategies})"
    if not corr_stable:
        return "HRP", "correlaciones inestables entre los dos semestres"
    return "MVO", f">= 5 estrategias ({n_strategies}) con correlaciones estables"


def main():
    parser = argparse.ArgumentParser(
        description="Optimizacion HRP / MVO del portfolio TradingLab."
    )
    parser.add_argument(
        "--returns-csv", required=True,
        help="CSV con returns diarios por estrategia"
    )
    parser.add_argument(
        "--output", required=True,
        help="Archivo JSON de salida con los pesos"
    )
    parser.add_argument(
        "--max-weight", type=float, default=0.40,
        help="Peso maximo permitido por estrategia (default: 0.40)"
    )
    args = parser.parse_args()

    if not HAS_PANDAS:
        print("ERROR: pandas no disponible. pip install pandas")
        sys.exit(1)
    if not HAS_SCIPY:
        print("ERROR: scipy no disponible. pip install scipy")
        sys.exit(1)

    print(f"Cargando returns: {args.returns_csv}")
    names, returns = load_returns(args.returns_csv)
    n = len(names)
    T = returns.shape[1]
    print(f"  Estrategias: {n}")
    print(f"  Observaciones: {T} dias")

    # Calculo de correlacion y estabilidad
    corr = correlation_matrix(returns)
    n_corr = corr.shape[0]
    mask = ~np.eye(n_corr, dtype=bool)
    mean_corr = float(np.abs(corr[mask]).mean())
    corr_stable = is_correlation_stable(returns)

    print(f"  Correlacion media: {mean_corr:.3f}")
    print(f"  Correlaciones estables: {corr_stable}")

    # Seleccion del metodo
    method, reason = select_method(n, corr_stable)
    print(f"\nMetodo seleccionado: {method} — {reason}")

    # Calcular pesos HRP siempre
    hrp_w = hrp_weights(returns, names)
    hrp_w = apply_max_weight_constraint(hrp_w, args.max_weight)
    hrp_arr = np.array([hrp_w[nm] for nm in names])
    sharpe_hrp = sharpe_ratio(hrp_arr, returns)

    # Calcular pesos MVO si PyPortfolioOpt disponible
    mvo_w = mvo_weights(returns, names)
    sharpe_mvo = None
    if mvo_w is not None:
        mvo_w = apply_max_weight_constraint(mvo_w, args.max_weight)
        mvo_arr = np.array([mvo_w.get(nm, 0.0) for nm in names])
        sharpe_mvo = sharpe_ratio(mvo_arr, returns)

    # Elegir los pesos finales segun el metodo
    if method == "HRP":
        final_weights = hrp_w
    else:
        final_weights = mvo_w if mvo_w is not None else hrp_w
        if mvo_w is None:
            reason += " (PyPortfolioOpt no disponible — usando HRP como fallback)"
            method = "HRP"

    # Mostrar resultado
    print("\nPesos finales:")
    for name, w in sorted(final_weights.items(), key=lambda x: -x[1]):
        print(f"  {name}: {w:.2%}")
    print(f"\nSharpe HRP: {sharpe_hrp:.3f}")
    if sharpe_mvo is not None:
        print(f"Sharpe MVO: {sharpe_mvo:.3f}")

    # Guardar resultado
    output = {
        "metodo": method,
        "razon": reason,
        "pesos": final_weights,
        "sharpe_hrp": round(sharpe_hrp, 4),
        "sharpe_mvo": round(sharpe_mvo, 4) if sharpe_mvo is not None else None,
        "correlacion_media": round(mean_corr, 4),
        "correlacion_estable": corr_stable,
        "n_estrategias": n,
        "n_observaciones": T,
        "max_weight_constraint": args.max_weight,
        "fecha": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nResultado guardado en: {args.output}")


if __name__ == "__main__":
    main()
