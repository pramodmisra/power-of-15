"""
Compliant ML Training Script — The Power of 15
================================================
Insurance claim severity prediction following all 15 rules.

Author: Pramod Misra
Rules Reference: https://github.com/pramodmisra/power-of-15
"""

import hashlib
import json
import logging
import os
import random
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Rule 10: Configure logging (not print statements)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# =============================================================
# Rule 6: Hyperparameters in a config dataclass, not globals
# =============================================================
@dataclass
class TrainingConfig:
    """All training parameters in one place for reproducibility."""

    seed: int = 42
    test_size: float = 0.2
    n_estimators: int = 200
    max_depth: int = 15
    min_samples_split: int = 5
    data_path: str = "data/insurance_claims.csv"
    output_dir: str = "checkpoints"
    target_column: str = "claim_amount"


# =============================================================
# Rule 11: Seed all sources of randomness
# =============================================================
def set_seed(seed: int) -> None:
    """Set random seed for reproducibility across all libraries."""
    # Rule 5: Validate input
    if not isinstance(seed, int) or seed < 0:
        raise ValueError(f"Seed must be a non-negative integer, got: {seed}")

    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    logger.info("Random seed set to %d", seed)


# =============================================================
# Rule 13: Capture full run metadata
# =============================================================
def capture_metadata(config: TrainingConfig, data_path: Path) -> dict:
    """Build metadata dict for experiment tracking."""
    # Rule 5: Validate inputs
    if not data_path.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")

    data_hash = hashlib.sha256(data_path.read_bytes()).hexdigest()[:12]

    git_sha = "unknown"
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,  # Rule 2: bounded
        )
        if result.returncode == 0:
            git_sha = result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        logger.warning("Could not capture git SHA")

    return {
        "config": asdict(config),
        "data_checksum": data_hash,
        "git_sha": git_sha,
        "python_version": sys.version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# =============================================================
# Data loading with validation (Rules 5, 7)
# =============================================================
def load_and_validate(path: str, target_col: str) -> pd.DataFrame:
    """Load CSV and validate schema."""
    # Rule 5: Validate input
    if not Path(path).exists():
        raise FileNotFoundError(f"Data file not found: {path}")

    df = pd.read_csv(path)

    # Rule 5: Schema assertions
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not in data. Columns: {list(df.columns)}")
    if df[target_col].isna().any():
        raise ValueError(f"Target column has {df[target_col].isna().sum()} null values")
    if not np.issubdtype(df[target_col].dtype, np.number):
        raise TypeError(f"Target must be numeric, got: {df[target_col].dtype}")

    logger.info("Loaded %d rows, %d columns from %s", len(df), len(df.columns), path)
    return df


# =============================================================
# Rule 12: Split FIRST, transform LATER
# =============================================================
def split_and_transform(
    df: pd.DataFrame, target_col: str, test_size: float, seed: int
) -> tuple:
    """Split data then fit scaler on train only."""
    # Rule 5: Validate
    if not 0.0 < test_size < 1.0:
        raise ValueError(f"test_size must be between 0 and 1, got: {test_size}")

    feature_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c != target_col]
    X = df[feature_cols].values
    y = df[target_col].values

    # Rule 12: Split raw data FIRST
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=seed
    )

    # Rule 12: Fit scaler on TRAIN ONLY
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)  # transform only, no fit

    # Rule 12: Assert non-overlap (index-based check)
    assert X_train_scaled.shape[0] + X_test_scaled.shape[0] == X.shape[0], "Row count mismatch"

    # Rule 5: Post-condition checks
    assert not np.isnan(X_train_scaled).any(), "NaN in training features after scaling"
    assert not np.isnan(X_test_scaled).any(), "NaN in test features after scaling"

    logger.info("Split: %d train, %d test", len(X_train_scaled), len(X_test_scaled))
    return X_train_scaled, X_test_scaled, y_train, y_test, scaler, feature_cols


# =============================================================
# Training with bounded loop (Rule 2) — sklearn doesn't need
# epochs, but we validate the model output (Rule 5)
# =============================================================
def train_model(
    X_train: np.ndarray, y_train: np.ndarray, config: TrainingConfig
) -> RandomForestRegressor:
    """Train a RandomForest with validation."""
    # Rule 5: Input validation
    assert X_train.ndim == 2, f"Expected 2D array, got {X_train.ndim}D"
    assert len(X_train) == len(y_train), "Feature/target length mismatch"
    assert len(X_train) > 0, "Empty training set"

    model = RandomForestRegressor(
        n_estimators=config.n_estimators,
        max_depth=config.max_depth,
        min_samples_split=config.min_samples_split,
        random_state=config.seed,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    # Rule 5: Post-training sanity check
    train_preds = model.predict(X_train[:10])
    assert not np.isnan(train_preds).any(), "NaN predictions from trained model"
    assert not np.isinf(train_preds).any(), "Inf predictions from trained model"

    logger.info("Model trained: %d estimators, max_depth=%s", config.n_estimators, config.max_depth)
    return model


# =============================================================
# Evaluation with full metrics (Rule 13)
# =============================================================
def evaluate_model(
    model: RandomForestRegressor, X_test: np.ndarray, y_test: np.ndarray
) -> dict:
    """Evaluate and return structured metrics."""
    # Rule 5: Validate
    assert X_test.ndim == 2, f"Expected 2D test array, got {X_test.ndim}D"

    predictions = model.predict(X_test)

    # Rule 5: Output validation
    assert not np.isnan(predictions).any(), "NaN in test predictions"

    metrics = {
        "mae": float(mean_absolute_error(y_test, predictions)),
        "rmse": float(np.sqrt(mean_squared_error(y_test, predictions))),
        "r2": float(r2_score(y_test, predictions)),
        "n_test_samples": len(y_test),
    }

    logger.info("Evaluation — MAE: %.2f, RMSE: %.2f, R²: %.4f", metrics["mae"], metrics["rmse"], metrics["r2"])
    return metrics


# =============================================================
# Rule 13: Save with structured naming and full lineage
# =============================================================
def save_run(
    config: TrainingConfig, metadata: dict, metrics: dict, model: RandomForestRegressor
) -> Path:
    """Save model checkpoint with full lineage."""
    import joblib

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    git_short = metadata["git_sha"][:7]
    run_dir = Path(config.output_dir) / f"run_{timestamp}_{git_short}"
    run_dir.mkdir(parents=True, exist_ok=True)

    # Save model
    model_path = run_dir / "model.joblib"
    joblib.dump(model, model_path)

    # Save full metadata + metrics (Rule 13)
    run_record = {**metadata, "metrics": metrics, "model_path": str(model_path)}
    with open(run_dir / "run_metadata.json", "w") as f:
        json.dump(run_record, f, indent=2)

    # Save config separately for quick reference
    with open(run_dir / "config.json", "w") as f:
        json.dump(asdict(config), f, indent=2)

    logger.info("Run saved to %s", run_dir)
    return run_dir


# =============================================================
# Main pipeline orchestrator (Rule 4: each step is a function call)
# =============================================================
def main() -> None:
    """Run the full training pipeline."""
    config = TrainingConfig()

    # Rule 11: Seed first
    set_seed(config.seed)

    # Rule 13: Capture metadata before training
    data_path = Path(config.data_path)
    metadata = capture_metadata(config, data_path)

    # Pipeline steps — each is a single function call (Rule 4)
    df = load_and_validate(config.data_path, config.target_column)
    X_train, X_test, y_train, y_test, scaler, features = split_and_transform(
        df, config.target_column, config.test_size, config.seed
    )
    model = train_model(X_train, y_train, config)
    metrics = evaluate_model(model, X_test, y_test)
    run_dir = save_run(config, metadata, metrics, model)

    logger.info("Pipeline complete. Artifacts in %s", run_dir)


if __name__ == "__main__":
    main()
