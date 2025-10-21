#!/usr/bin/env python3
"""
fakedata.py — Generate synthetic datasets for ML:
- Regression
- Classification

Features:
- Optional categorical columns
- Optional missing values in features
- Reproducible seeds
- CSV/Parquet output + metadata JSON

Examples:
  python fakedata.py classification --samples 2000 --features 20 --informative 5 --classes 3 --weights 0.6,0.3,0.1 --categorical 3 --missing-rate 0.02 --out data_class.csv
  python fakedata.py regression --samples 5000 --features 30 --informative 8 --noise 4.0 --degree 2 --out data_reg.parquet --format parquet
"""

from __future__ import annotations

import argparse
import json
import math
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.datasets import make_classification, make_regression


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rng(seed: Optional[int]) -> np.random.Generator:
    return np.random.default_rng(seed)


def _parse_float_list(s: Optional[str]) -> Optional[List[float]]:
    if s is None or str(s).strip() == "":
        return None
    try:
        return [float(x.strip()) for x in str(s).split(",") if x.strip() != ""]
    except Exception as e:
        raise argparse.ArgumentTypeError(f"Invalid float list: {s!r}") from e


def _validate_sum_to_one(weights: List[float], tol: float = 1e-6) -> None:
    if not weights:
        return
    s = sum(weights)
    if not math.isclose(s, 1.0, rel_tol=tol, abs_tol=tol):
        raise ValueError(f"class weights must sum to 1.0, got {s:.6f} for {weights}")


def _introduce_missingness(df: pd.DataFrame, missing_rate: float, seed: Optional[int]) -> pd.DataFrame:
    if missing_rate <= 0:
        return df
    if not (0.0 < missing_rate < 1.0):
        raise ValueError("missing_rate must be in (0, 1).")
    rng = _rng(seed)
    arr = df.to_numpy(copy=True)
    n, m = arr.shape
    k = int(round(missing_rate * n * m))
    if k == 0:
        return df
    rows = rng.integers(low=0, high=n, size=k, endpoint=False)
    cols = rng.integers(low=0, high=m, size=k, endpoint=False)
    for i, j in zip(rows, cols):
        arr[i, j] = np.nan
    return pd.DataFrame(arr, columns=df.columns, index=df.index)


def _add_categorical_columns(
    df: pd.DataFrame,
    n_categorical: int,
    cardinality_range: Tuple[int, int],
    seed: Optional[int],
) -> pd.DataFrame:
    if n_categorical <= 0:
        return df
    low, high = cardinality_range
    if low < 2 or high < low:
        raise ValueError("cardinality range must satisfy 2 <= low <= high")
    rng = _rng(seed)
    cats = {}
    for i in range(n_categorical):
        card = int(rng.integers(low=low, high=high + 1))
        levels = [f"c{i}_L{j}" for j in range(card)]
        cats[f"cat{i}"] = rng.choice(levels, size=len(df))
    cat_df = pd.DataFrame(cats, index=df.index)
    for c in cat_df.columns:
        cat_df[c] = cat_df[c].astype("object")
    return pd.concat([df, cat_df], axis=1)


@dataclass
class Meta:
    task: str
    created_at: str
    n_samples: int
    n_features_numeric: int
    n_features_categorical: int
    params: dict
    target_name: str
    feature_names: List[str]
    notes: Optional[str] = None


def generate_regression(
    n_samples: int,
    n_features: int,
    n_informative: int,
    noise: float,
    bias: float,
    effective_rank: Optional[int],
    tail_strength: float,
    polynomial_degree: int,
    seed: Optional[int],
) -> tuple[pd.DataFrame, pd.Series, dict]:
    if n_informative > n_features:
        raise ValueError("n_informative cannot exceed n_features")
    X, y, coef = make_regression(
        n_samples=n_samples,
        n_features=n_features,
        n_informative=n_informative,
        noise=noise,
        bias=bias,
        effective_rank=effective_rank,
        tail_strength=tail_strength,
        coef=True,
        random_state=seed,
    )
    # Polynomial expansion (no interactions)
    if polynomial_degree and polynomial_degree > 1:
        cols = []
        for d in range(2, polynomial_degree + 1):
            cols.append(pd.DataFrame(np.power(X, d), columns=[f"num{j}^{d}" for j in range(n_features)]))
        X_df = pd.concat([pd.DataFrame(X, columns=[f"num{j}" for j in range(n_features)]), *cols], axis=1)
    else:
        X_df = pd.DataFrame(X, columns=[f"num{j}" for j in range(n_features)])
    y_s = pd.Series(y, name="target")
    params = dict(
        n_samples=n_samples,
        n_features=n_features,
        n_informative=n_informative,
        noise=noise,
        bias=bias,
        effective_rank=effective_rank,
        tail_strength=tail_strength,
        polynomial_degree=polynomial_degree,
        seed=seed,
        coef=coef.tolist(),
    )
    return X_df, y_s, params


def generate_classification(
    n_samples: int,
    n_features: int,
    n_informative: int,
    n_redundant: int,
    n_repeated: int,
    n_classes: int,
    n_clusters_per_class: int,
    weights: Optional[List[float]],
    class_sep: float,
    flip_y: float,
    seed: Optional[int],
) -> tuple[pd.DataFrame, pd.Series, dict]:
    if n_informative + n_redundant + n_repeated > n_features:
        raise ValueError("n_informative + n_redundant + n_repeated must be <= n_features")
    if weights:
        _validate_sum_to_one(weights)
    X, y = make_classification(
        n_samples=n_samples,
        n_features=n_features,
        n_informative=n_informative,
        n_redundant=n_redundant,
        n_repeated=n_repeated,
        n_classes=n_classes,
        n_clusters_per_class=n_clusters_per_class,
        weights=weights,
        class_sep=class_sep,
        flip_y=flip_y,
        random_state=seed,
    )
    X_df = pd.DataFrame(X, columns=[f"num{j}" for j in range(n_features)])
    y_s = pd.Series(y, name="label")
    params = dict(
        n_samples=n_samples,
        n_features=n_features,
        n_informative=n_informative,
        n_redundant=n_redundant,
        n_repeated=n_repeated,
        n_classes=n_classes,
        n_clusters_per_class=n_clusters_per_class,
        weights=weights,
        class_sep=class_sep,
        flip_y=flip_y,
        seed=seed,
    )
    return X_df, y_s, params


def _save_outputs(
    X: pd.DataFrame,
    y: pd.Series,
    out_path: str,
    fmt: str,
    meta: Meta,
) -> None:
    df = X.copy()
    df[meta.target_name] = y.values

    ext = fmt.lower()
    if ext == "csv":
        df.to_csv(out_path, index=False)
    elif ext == "parquet":
        df.to_parquet(out_path, index=False)
    else:
        raise ValueError("Unsupported format, use 'csv' or 'parquet'")

    meta_path = os.path.splitext(out_path)[0] + ".meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(asdict(meta), f, indent=2)
    print(f"Wrote dataset: {out_path}")
    print(f"Wrote metadata: {meta_path}")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Generate synthetic datasets for ML.")
    subparsers = parser.add_subparsers(dest="task", required=True)

    # Common args
    def add_common(p: argparse.ArgumentParser):
        p.add_argument("--samples", type=int, default=1000, help="Number of samples (rows)")
        p.add_argument("--features", type=int, default=20, help="Number of numeric features (columns)")
        p.add_argument("--categorical", type=int, default=0, help="Number of categorical feature columns to add")
        p.add_argument("--cat-card-min", type=int, default=3, help="Min cardinality for each categorical feature")
        p.add_argument("--cat-card-max", type=int, default=10, help="Max cardinality for each categorical feature")
        p.add_argument("--missing-rate", type=float, default=0.0, help="Fraction of missing values to inject into features (0..1)")
        p.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
        p.add_argument("--out", type=str, required=True, help="Output file path (csv or parquet)")
        p.add_argument("--format", type=str, choices=["csv", "parquet"], default=None, help="Output format")
        return p

    # Regression
    preg = add_common(subparsers.add_parser("regression", help="Generate regression dataset"))
    preg.add_argument("--informative", type=int, default=10, help="Number of informative features")
    preg.add_argument("--noise", type=float, default=1.0, help="Gaussian noise std deviation")
    preg.add_argument("--bias", type=float, default=0.0, help="Bias term")
    preg.add_argument("--effective-rank", type=int, default=None, help="Approximate matrix rank (low-rank X)")
    preg.add_argument("--tail-strength", type=float, default=0.5, help="Relative importance of the fat noisy tail of singular values")
    preg.add_argument("--degree", type=int, default=1, help="Polynomial degree for numeric features (>=1)")

    # Classification
    pclf = add_common(subparsers.add_parser("classification", help="Generate classification dataset"))
    pclf.add_argument("--informative", type=int, default=10, help="Number of informative features")
    pclf.add_argument("--redundant", type=int, default=2, help="Number of redundant features")
    pclf.add_argument("--repeated", type=int, default=0, help="Number of repeated features")
    pclf.add_argument("--classes", type=int, default=2, help="Number of classes")
    pclf.add_argument("--clusters-per-class", type=int, default=2, help="Clusters per class")
    pclf.add_argument("--weights", type=_parse_float_list, default=None, help="Comma-separated class weights summing to 1.0, e.g. 0.9,0.1")
    pclf.add_argument("--class-sep", type=float, default=1.0, help="Class separation")
    pclf.add_argument("--flip-y", type=float, default=0.01, help="Fraction of labels to randomly flip")

    args = parser.parse_args(argv)

    if args.task == "regression":
        fmt = (args.format or os.path.splitext(args.out)[1].lstrip(".") or "csv").lower()
        X, y, params = generate_regression(
            n_samples=args.samples,
            n_features=args.features,
            n_informative=args.informative,
            noise=args.noise,
            bias=args.bias,
            effective_rank=args.effective_rank,
            tail_strength=args.tail_strength,
            polynomial_degree=args.degree,
            seed=args.seed,
        )
        X = _add_categorical_columns(X, args.categorical, (args.cat_card_min, args.cat_card_max), args.seed)
        X = _introduce_missingness(X, args.missing_rate, args.seed)
        meta = Meta(
            task="regression",
            created_at=_now_iso(),
            n_samples=args.samples,
            n_features_numeric=sum(c.startswith("num") for c in X.columns),
            n_features_categorical=sum(c.startswith("cat") for c in X.columns),
            params=params,
            target_name="target",
            feature_names=list(X.columns),
        )
        _save_outputs(X, y, args.out, fmt, meta)
        return 0

    if args.task == "classification":
        fmt = (args.format or os.path.splitext(args.out)[1].lstrip(".") or "csv").lower()
        X, y, params = generate_classification(
            n_samples=args.samples,
            n_features=args.features,
            n_informative=args.informative,
            n_redundant=args.redundant,
            n_repeated=args.repeated,
            n_classes=args.classes,
            n_clusters_per_class=args.clusters_per_class,
            weights=args.weights,
            class_sep=args.class_sep,
            flip_y=args.flip_y,
            seed=args.seed,
        )
        X = _add_categorical_columns(X, args.categorical, (args.cat_card_min, args.cat_card_max), args.seed)
        X = _introduce_missingness(X, args.missing_rate, args.seed)
        meta = Meta(
            task="classification",
            created_at=_now_iso(),
            n_samples=args.samples,
            n_features_numeric=sum(c.startswith("num") for c in X.columns),
            n_features_categorical=sum(c.startswith("cat") for c in X.columns),
            params=params,
            target_name="label",
            feature_names=list(X.columns),
        )
        _save_outputs(X, y, args.out, fmt, meta)
        return 0

    parser.error("Unknown task")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
