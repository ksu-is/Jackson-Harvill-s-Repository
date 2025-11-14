"""
ScoutSense: NFL Draft Scouting & Analysis System

A complete ML-powered system for analyzing NFL draft prospects,
predicting draft positions, assessing success probability, and
finding comparable players.

Modules:
    - utils: Core data loading, feature engineering, and ML models
    - scripts: Demo and example scripts
    - data: Data storage location
    - notebooks: Jupyter notebooks for exploration
    - tests: Unit tests

Quick Start:
    >>> from scoutsense.utils.data_loader import load_draft_data
    >>> from scoutsense.utils.feature_engineering import engineer_features
    >>> from scoutsense.utils.models import DraftPositionPredictor
    >>> 
    >>> df = load_draft_data('data.csv')
    >>> df_eng = engineer_features(df)
    >>> predictor = DraftPositionPredictor()
    >>> predictor.train(df_eng)
    >>> prediction = predictor.predict(player_data)
"""

__version__ = "1.0.0"
__author__ = "ScoutSense Team"
__license__ = "MIT"

from scoutsense.utils.data_loader import load_draft_data
from scoutsense.utils.feature_engineering import engineer_features
from scoutsense.utils.models import (
    DraftPositionPredictor,
    PlayerSuccessClassifier,
    PlayerComparison,
)

__all__ = [
    "load_draft_data",
    "engineer_features",
    "DraftPositionPredictor",
    "PlayerSuccessClassifier",
    "PlayerComparison",
]
