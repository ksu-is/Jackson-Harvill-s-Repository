# ScoutSense - File Organization Checklist

## ✅ Completed

- [x] Created `scoutsense/scripts/` directory
- [x] Created `scoutsense/scripts/demo.py` (moved from root)
- [x] Created `scoutsense/scripts/examples.py` (moved from root)
- [x] Created `scoutsense/data/` directory
- [x] Created `scoutsense/tests/` directory
- [x] Created `scoutsense/__init__.py` (package initialization)
- [x] Created `scoutsense/utils/__init__.py`
- [x] Created `scoutsense/scripts/__init__.py`
- [x] Created `scoutsense/tests/__init__.py`
- [x] Created `PROJECT_STRUCTURE.md` (comprehensive guide)
- [x] Created `FILE_ORGANIZATION.md` (this file)

## 📋 Remaining Tasks

### Phase 1: Move Data Files
```bash
# Move CSV files to scoutsense/data/
mv nfl_draft_data.csv scoutsense/data/
mv nfl_draft_engineered.csv scoutsense/data/
```

### Phase 2: Update File Paths in Scripts
Update the hardcoded paths in:
- `scoutsense/scripts/demo.py` (line ~21)
- `scoutsense/scripts/examples.py` (line ~24)

**Old Path**:
```python
df = load_draft_data('C:\\Users\\jacks\\Downloads\\nfl_draft_data.csv')
```

**New Path** (relative):
```python
from pathlib import Path
data_path = Path(__file__).parent.parent / 'data' / 'nfl_draft_data.csv'
df = load_draft_data(str(data_path))
```

Or **New Path** (absolute):
```python
df = load_draft_data('scoutsense/data/nfl_draft_data.csv')
```

### Phase 3: Delete Legacy Files from Root
```bash
# Delete old files (now in organized structure)
rm demo_models.py          # → scoutsense/scripts/demo.py
rm examples.py             # → scoutsense/scripts/examples.py
rm test_features.py        # → (can delete, was for testing)
```

### Phase 4: Delete Empty Legacy Files in utils/
```bash
# These are empty and can be deleted
rm scoutsense/utils/interface.py   # Empty file
rm scoutsense/utils/model.py       # Empty file
rm scoutsense/utils/predict.py     # Empty file
```

### Phase 5: Verify Directory Structure
```bash
# Check the new structure
tree scoutsense/
# or
ls -R scoutsense/
```

---

## 📁 Final Directory Structure (After Organization)

```
ScoutSense/
├── README.md
├── BUILD_SUMMARY.md
├── MODELS_QUICKSTART.md
├── PROJECT_STRUCTURE.md
├── FILE_ORGANIZATION.md
├── LICENSE
├── .gitignore
├── .git/
│
├── scoutsense/
│   ├── __init__.py                      ✅ NEW
│   ├── README.md
│   │
│   ├── utils/
│   │   ├── __init__.py                  ✅ NEW
│   │   ├── data_loader.py              ✅ EXISTING
│   │   ├── feature_engineering.py      ✅ EXISTING
│   │   ├── models.py                   ✅ EXISTING
│   │   └── __pycache__/
│   │
│   ├── scripts/
│   │   ├── __init__.py                  ✅ NEW
│   │   ├── demo.py                      ✅ NEW (from root)
│   │   └── examples.py                  ✅ NEW (from root)
│   │
│   ├── data/                            ✅ NEW
│   │   ├── nfl_draft_data.csv           ⏳ TO MOVE
│   │   └── nfl_draft_engineered.csv     ⏳ TO MOVE
│   │
│   ├── notebooks/                       ✅ NEW (empty, ready for use)
│   ├── tests/                           ✅ NEW (empty, ready for tests)
│   │   └── __init__.py                  ✅ NEW
│   │
│   └── app/                             ✅ EXISTING (for web app)
│
└── [DELETE AFTER MOVING]
    ├── nfl_draft_data.csv               ❌ TO DELETE
    ├── nfl_draft_engineered.csv         ❌ TO DELETE  
    ├── demo_models.py                   ❌ TO DELETE
    ├── examples.py                      ❌ TO DELETE
    └── test_features.py                 ❌ TO DELETE
```

---

## 🔄 Running Scripts After Organization

### Option 1: From Project Root
```bash
cd ScoutSense
python -m scoutsense.scripts.demo
python -m scoutsense.scripts.examples
```

### Option 2: With Updated Relative Paths
After updating file paths in scripts:
```bash
python scoutsense/scripts/demo.py
python scoutsense/scripts/examples.py
```

### Option 3: Import and Use Directly
```python
from scoutsense.utils.data_loader import load_draft_data
from scoutsense.utils.feature_engineering import engineer_features
from scoutsense.utils.models import DraftPositionPredictor

# Code here...
```

---

## 📝 Notes

### Import Paths
- All modules can now be imported via `scoutsense.*`
- No need to add paths to `sys.path`
- Clean, professional package structure

### Data Location
- CSV files belong in `scoutsense/data/`
- Makes it easier to manage and version
- Scripts can find data relative to their location

### Backwards Compatibility
- Old import statements will break until paths are updated
- This is expected and necessary for clean organization
- Update takes ~5 minutes

### Git Considerations
- Add `scoutsense/data/*.csv` to `.gitignore` (optional, since CSVs are large)
- Keep documentation files (*.md) tracked in git
- Keep code files (*.py) tracked in git

---

## ✨ Benefits of This Organization

1. **Professional Structure**: Matches industry standard Python package layout
2. **Scalability**: Easy to add new modules, scripts, or notebooks
3. **Maintainability**: Clear separation of concerns
4. **Testability**: Dedicated `tests/` directory for unit tests
5. **Discoverability**: Clear directory names show purpose of each section
6. **Documentation**: Multiple levels of docs (package, project, structure)

---

## Quick Reference

| What | Where | Status |
|------|-------|--------|
| Core Models | `scoutsense/utils/models.py` | ✅ |
| Feature Engineering | `scoutsense/utils/feature_engineering.py` | ✅ |
| Data Loading | `scoutsense/utils/data_loader.py` | ✅ |
| Demo Script | `scoutsense/scripts/demo.py` | ✅ |
| Examples | `scoutsense/scripts/examples.py` | ✅ |
| Data Files | `scoutsense/data/` | ⏳ |
| Tests | `scoutsense/tests/` | 📋 |
| Notebooks | `scoutsense/notebooks/` | 📋 |

**Legend**: ✅ Ready | ⏳ To Move | 📋 To Create

---

**Created**: November 14, 2025
**Status**: Implementation Guide Ready
