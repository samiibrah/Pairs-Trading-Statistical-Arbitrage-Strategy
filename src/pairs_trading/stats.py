from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint, adfuller

def engle_granger_coint_pvalue(y: pd.Series, x: pd.Series) -> float:
    """
    Engle-Granger cointegration test p-value between y and x.
    """
    y2, x2 = y.align(x, join="inner")
    y2, x2 = y2.dropna(), x2.dropna()
    y2, x2 = y2.align(x2, join="inner")
    if len(y2) < 50:
        return np.nan
    _score, pvalue, _ = coint(y2.values, x2.values)
    return float(pvalue)

def adf_pvalue(series: pd.Series) -> float:
    s = series.dropna()
    if len(s) < 50:
        return np.nan
    res = adfuller(s.values, autolag="AIC")
    return float(res[1])

def rolling_ols_beta(y: pd.Series, x: pd.Series, lookback: int) -> pd.Series:
    """
    Rolling hedge ratio beta from OLS: y ~ beta*x (+ intercept).
    Returns beta aligned to y/x index with NaNs for warmup.
    """
    y2, x2 = y.align(x, join="inner")
    df = pd.DataFrame({"y": y2, "x": x2}).dropna()
    idx = df.index

    betas = np.full(len(df), np.nan, dtype=float)
    X = df["x"].values
    Y = df["y"].values

    for i in range(lookback - 1, len(df)):
        xs = X[i - lookback + 1 : i + 1]
        ys = Y[i - lookback + 1 : i + 1]
        X_ = sm.add_constant(xs)
        model = sm.OLS(ys, X_).fit()
        betas[i] = model.params[1]  # coefficient on x

    out = pd.Series(betas, index=idx, name="beta")
    return out.reindex(y2.index)
