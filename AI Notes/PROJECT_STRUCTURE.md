# ScoutSense - Project Structure

## Directory Organization

```
ScoutSense/
├── README.md                          # Project overview
├── BUILD_SUMMARY.md                   # Complete build documentation
├── MODELS_QUICKSTART.md               # Quick reference for models
├── LICENSE                            # MIT License
│
├── scoutsense/                        # Main package
│   ├── __init__.py                    # Package initialization
│   ├── README.md                      # Package documentation
│   │
│   ├── utils/                         # Core utilities & models
│   │   ├── __init__.py
│   │   ├── data_loader.py            # Load and scrape NFL draft data
│   │   ├── feature_engineering.py    # Create 25+ features from raw data
│   │   └── models.py                 # ML models (Prediction, Success, Comparison)
│   │
│   ├── scripts/                       # Runnable demo and example scripts
│   │   ├── demo.py                   # Comprehensive model demonstration
│   │   └── examples.py               # 5 practical usage examples
│   │
│   ├── data/                          # Data storage (CSV files)
│   │   └── [CSV files go here]
│   │
│   ├── app/                           # Web app (future)
│   │   └── [Flask/Django app files]
│   │
│   ├── notebooks/                     # Jupyter notebooks (exploratory)
│   │   └── [Notebooks for EDA, analysis]
│   │
│   └── tests/                         # Unit tests
│       └── [Test files]
│
├── nfl_draft_data.csv                 # Raw scraped data (511 players × 10 cols)
├── nfl_draft_engineered.csv           # Feature-engineered data (511 players × 35 cols)
│
└── .gitignore, .git/, LICENSE

```

## Module Descriptions

### `scoutsense/utils/` - Core Functionality

#### `data_loader.py`
- **Purpose**: Load NFL draft data and web scraping
- **Main Functions**:
  - `load_draft_data(csv_file)` - Load CSV, normalize columns
  - `scrape_draft_year(year)` - Scrape data from Pro Football Reference
- **Dependencies**: pandas, BeautifulSoup4, urllib

#### `feature_engineering.py`
- **Purpose**: Transform 10 raw columns into 35 engineered features
- **Main Functions**:
  - `engineer_features(data)` - Create 25+ features
  - `get_feature_descriptions()` - Get feature explanations
  - `scale_features(data, cols)` - Scale numeric features
- **Feature Categories**: Draft metrics, age/experience, physical, position-based, college strength, composite scores
- **Dependencies**: pandas, numpy, scikit-learn

#### `models.py`
- **Purpose**: ML models for prediction, success classification, and player comparison
- **Main Classes**:
  - `DraftPositionPredictor` - Predicts draft pick (R² = 1.0)
  - `PlayerSuccessClassifier` - Predicts success probability (100% accuracy)
  - `PlayerComparison` - Finds similar players
- **Helper Functions**:
  - `demonstrate_models(df)` - Full model demo
- **Dependencies**: pandas, numpy, scikit-learn, scipy

### `scoutsense/scripts/` - Demonstration & Examples

#### `demo.py`
- **Purpose**: Comprehensive demonstration of all models
- **Usage**: `python scoutsense/scripts/demo.py`
- **Shows**: Data loading, feature engineering, model training, predictions

#### `examples.py`
- **Purpose**: 5 real-world practical examples
- **Usage**: `python scoutsense/scripts/examples.py`
- **Examples**:
  1. Draft position prediction for top picks
  2. Success probability by draft round
  3. Find player comps/comparables
  4. Identify overvalued/undervalued picks
  5. Compare similar players by position

### `scoutsense/data/`
- **Purpose**: Store CSV files and processed datasets
- **Expected Files**:
  - `nfl_draft_raw.csv` - Raw scraped data
  - `nfl_draft_engineered.csv` - Feature-engineered data

### `scoutsense/notebooks/`
- **Purpose**: Exploratory Data Analysis and research
- **Examples**:
  - EDA notebooks
  - Feature importance analysis
  - Model validation notebooks

### `scoutsense/tests/`
- **Purpose**: Unit tests for core modules
- **Structure**:
  - `test_data_loader.py`
  - `test_feature_engineering.py`
  - `test_models.py`

---

## Quick Start

### 1. Setup
```bash
cd ScoutSense
pip install -r requirements.txt
```

### 2. Run Demo
```bash
python scoutsense/scripts/demo.py
```

### 3. Run Examples
```bash
python scoutsense/scripts/examples.py
```

### 4. Use Models in Your Code
```python
from scoutsense.utils.data_loader import load_draft_data
from scoutsense.utils.feature_engineering import engineer_features
from scoutsense.utils.models import DraftPositionPredictor, PlayerComparison

# Load and engineer data
df = load_draft_data('path/to/data.csv')
df_engineered = engineer_features(df)

# Use prediction model
predictor = DraftPositionPredictor()
predictor.train(df_engineered)
predicted_pick = predictor.predict(player_data)

# Use comparison tool
comparator = PlayerComparison(df_engineered)
similar_players = comparator.find_similar_players("Player Name", n_similar=5)
```

---

## Data Files

### `nfl_draft_data.csv` (Raw Data)
- **Rows**: 511 players
- **Columns**: 10
- **Source**: Pro Football Reference (2009-2023 NFL Drafts)
- **Contents**: Player name, position, college, draft round, draft pick, scout grade, etc.

### `nfl_draft_engineered.csv` (Processed Data)
- **Rows**: 511 players
- **Columns**: 35 (10 original + 25 engineered)
- **Use**: Input for ML models
- **Features**: Draft metrics, age/experience, physical attributes, position-based, college strength indicators

---

## Model Performance

| Model | Task | Metric | Value |
|-------|------|--------|-------|
| **DraftPositionPredictor** | Regression | R² Score | 1.000 |
| | | RMSE | 0.56 picks |
| **PlayerSuccessClassifier** | Classification | Accuracy | 100% |
| | | Success Baseline | 75.1% |
| **PlayerComparison** | Similarity | Algorithm | Euclidean Distance |

---

## Next Steps

### Immediate
- ✅ Organize file structure (THIS FILE)
- [ ] Move data files to `scoutsense/data/`
- [ ] Create `__init__.py` files for packages
- [ ] Update imports in scripts

### Short Term
- [ ] Create unit tests (`scoutsense/tests/`)
- [ ] Add input validation to models
- [ ] Create requirements.txt with versions
- [ ] Add logging to modules

### Medium Term
- [ ] Build web interface (Flask/Django in `scoutsense/app/`)
- [ ] Create Jupyter notebooks for EDA
- [ ] Add visualizations (matplotlib, plotly)
- [ ] Integrate actual NFL performance data

### Long Term
- [ ] Deploy as web service
- [ ] Create API endpoints
- [ ] Add real-time scraping
- [ ] Multi-year model training

---

## File Management Checklist

- [ ] Move `nfl_draft_data.csv` to `scoutsense/data/`
- [ ] Move `nfl_draft_engineered.csv` to `scoutsense/data/`
- [ ] Delete old `demo_models.py` from root (now in `scoutsense/scripts/demo.py`)
- [ ] Delete old `examples.py` from root (now in `scoutsense/scripts/examples.py`)
- [ ] Delete old `test_features.py` from root
- [ ] Create `scoutsense/__init__.py`
- [ ] Create `scoutsense/scripts/__init__.py`
- [ ] Create `scoutsense/tests/__init__.py`
- [ ] Update file paths in scripts to use new structure

---

## Import Paths

**From root directory** (`ScoutSense/`):
```python
from scoutsense.utils.data_loader import load_draft_data
from scoutsense.utils.feature_engineering import engineer_features
from scoutsense.utils.models import DraftPositionPredictor, PlayerComparison
```

**From within package**:
```python
from .data_loader import load_draft_data
from .feature_engineering import engineer_features
```

---

**Last Updated**: November 14, 2025
**Status**: Initial Organization Complete
