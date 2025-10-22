import os
import shutil
import tempfile

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def tmp_artifacts_dir():
    d = tempfile.mkdtemp(prefix="auto_model_artifacts_")
    try:
        yield d
    finally:
        shutil.rmtree(d, ignore_errors=True)


def df_basic_classification(n_rows=200, seed=0):
    rng = np.random.default_rng(seed)
    X = pd.DataFrame({
        "num_a": rng.normal(size=n_rows),
        "num_b": rng.uniform(-1, 1, size=n_rows),
        "cat_a": rng.choice(["x", "y", "z"], size=n_rows),
        "text_a": rng.choice(["foo", "bar baz", "quux"], size=n_rows),
    })
    y = (X["num_a"] + rng.normal(scale=0.5, size=n_rows) > 0).astype(int)
    X["target"] = y
    return X, "target"


def df_edge_cases(seed=0):
    rng = np.random.default_rng(seed)
    # Very small dataset
    X_small = pd.DataFrame({"a": [1.0], "b": [np.nan], "target": [1]})

    # Zero rows (schema-only)
    X_zero = pd.DataFrame({"a": pd.Series(dtype=float), "b": pd.Series(dtype=float), "target": pd.Series(dtype=int)})

    # Duplicate columns
    X_dup = pd.DataFrame(
        np.column_stack([rng.normal(size=10), rng.normal(size=10), rng.integers(0, 2, size=10)]),
        columns=["a", "a", "target"],  # duplicate "a"
    )

    # High cardinality categoricals
    X_high_card = pd.DataFrame({
        "id": [f"user_{i}" for i in range(2000)],
        "cat": [f"cat_{i}" for i in range(2000)],
        "num": rng.normal(size=2000),
        "target": rng.integers(0, 2, size=2000),
    })

    # All-null column and Inf
    X_null_inf = pd.DataFrame({
        "all_null": [np.nan]*100,
        "with_inf": [np.inf] + list(rng.normal(size=99)),
        "target": rng.integers(0, 2, size=100),
    })

    # Unicode/emoji column names and values
    X_unicode = pd.DataFrame({
        "café": rng.normal(size=50),
        "emoji🙂": rng.normal(size=50),
        "text": ["naïve café ☕"]*50,
        "target": rng.integers(0, 2, size=50),
    })

    # Time series with out-of-order timestamps and gaps
    ts = pd.date_range("2023-01-01", periods=100, freq="D").to_series(index=None)
    ts = ts.drop(index=[5, 6, 50])  # gaps
    X_ts = pd.DataFrame({
        "timestamp": ts.sample(frac=1.0, random_state=seed).values,  # shuffled
        "value": rng.normal(size=len(ts)),
        "target": rng.integers(0, 2, size=len(ts)),
    })

    return {
        "small": (X_small, "target"),
        "zero_rows": (X_zero, "target"),
        "duplicate_cols": (X_dup, "target"),
        "high_card": (X_high_card, "target"),
        "null_inf": (X_null_inf, "target"),
        "unicode": (X_unicode, "target"),
        "time_series": (X_ts, "target"),
    }
