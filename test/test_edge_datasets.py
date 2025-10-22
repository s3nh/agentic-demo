import os
import hashlib
import json
import pandas as pd
import numpy as np
import pytest

# Replace 'automod' import with your actual module
# from your_package import automod


def _hash_path_tree(path):
    sha = hashlib.sha256()
    for root, dirs, files in os.walk(path):
        for f in sorted(files):
            with open(os.path.join(root, f), "rb") as fh:
                sha.update(fh.read())
    return sha.hexdigest()


def _run_module(df, target_col, out_dir, seed=42, time_budget_s=15):
    """
    Replace this with the canonical way to call your module, e.g.:
    result = automod.run(
        data=df, target=target_col,
        output_dir=out_dir,
        random_state=seed,
        time_budget_seconds=time_budget_s,
        generate_docs=True,
    )
    return result
    """
    # Placeholder for demonstration purposes
    class Result:
        model = object()
        metrics = {"accuracy": 0.5}
        docs_path = out_dir
        artifacts_path = out_dir
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "metrics.json"), "w") as f:
        json.dump({"accuracy": 0.5}, f)
    with open(os.path.join(out_dir, "report.md"), "w") as f:
        f.write("# Report\n\n- Dataset summary\n- Features\n- Metrics\n")
    return Result()


def test_basic_classification(tmp_artifacts_dir, df_basic_classification):
    df, target = df_basic_classification()
    res = _run_module(df, target, tmp_artifacts_dir)
    # Basic assertions
    assert os.path.exists(os.path.join(tmp_artifacts_dir, "metrics.json"))
    assert os.path.exists(os.path.join(tmp_artifacts_dir, "report.md"))
    with open(os.path.join(tmp_artifacts_dir, "metrics.json")) as f:
        metrics = json.load(f)
    assert "accuracy" in metrics


def test_edge_cases_handle_gracefully(tmp_artifacts_dir, df_edge_cases):
    cases = df_edge_cases()
    for name, (df, target) in cases.items():
        case_dir = os.path.join(tmp_artifacts_dir, name)
        if name in ("zero_rows",):
            with pytest.raises(Exception):
                _run_module(df, target, case_dir)
            continue
        # Expect either a successful run or a clear, specific exception
        try:
            res = _run_module(df, target, case_dir)
            assert os.path.exists(os.path.join(case_dir, "report.md"))
        except Exception as e:
            # Check exception message is actionable
            msg = str(e).lower()
            assert any(s in msg for s in [
                "empty", "nan", "duplicate", "unsupported", "invalid", "insufficient", "time series"
            ]), f"Non-actionable error for {name}: {e}"


def test_leakage_detection(tmp_artifacts_dir, df_basic_classification):
    df, target = df_basic_classification()
    # Simulate leakage by duplicating target as a feature
    df["leaky_feature"] = df[target]
    out = os.path.join(tmp_artifacts_dir, "leakage")
    try:
        res = _run_module(df, target, out)
        # If training succeeds, ensure a warning or doc note exists about perfect predictors/leakage
        with open(os.path.join(out, "report.md")) as f:
            content = f.read().lower()
        assert any(s in content for s in ["leakage", "perfect predictor", "data leak"]), \
            "Report should mention potential leakage"
    except Exception as e:
        # Also acceptable: module explicitly blocks and explains the leakage
        assert "leak" in str(e).lower()


def test_deterministic_outputs_with_fixed_seed(tmp_artifacts_dir, df_basic_classification):
    df, target = df_basic_classification()
    out1 = os.path.join(tmp_artifacts_dir, "run1")
    out2 = os.path.join(tmp_artifacts_dir, "run2")
    res1 = _run_module(df, target, out1, seed=123)
    res2 = _run_module(df, target, out2, seed=123)
    # Hash artifact trees to check determinism in docs/artifacts
    h1 = _hash_path_tree(out1)
    h2 = _hash_path_tree(out2)
    assert h1 == h2, "Artifacts should be identical with fixed seed"
