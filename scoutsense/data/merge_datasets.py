#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Merge engineered and raw NFL draft datasets into a comprehensive CSV
"""

import pandas as pd
from pathlib import Path

# Load both files
data_dir = Path(__file__).parent
engineered = pd.read_csv(data_dir / 'nfl_draft_engineered.csv')
raw = pd.read_csv(data_dir / 'nfl_draft_data.csv')

print("Loaded datasets:")
print(f"  Engineered: {engineered.shape}")
print(f"  Raw: {raw.shape}")

# Standardize column names in raw data
raw = raw.rename(columns={
    'Draft Pick': 'draft_pick',
    'Team': 'team',
    'Name': 'name',
    'Pos': 'pos',
    'Age': 'age',
    'Ht': 'ht',
    'Wt': 'wt',
    'College': 'college',
    'College/Yrs': 'college/yrs',
    'Meets': 'meets'
})

# Assign draft year
# Matthew Stafford was drafted in 2009, so engineered data is 2009
engineered['draft_year'] = 2009

# For raw data, estimate draft years
# There are 3835 total picks, with ~224 picks per draft year (32 teams × 7 rounds)
raw['draft_year'] = (raw.index // 224) + 2000

print("\nDraft years in datasets:")
print(f"  Engineered: {engineered['draft_year'].unique()}")
print(f"  Raw: {sorted(raw['draft_year'].unique())}")

# Combine: use engineered data for 2009 (more features), and raw data for other years
combined = pd.concat([engineered, raw[raw['draft_year'] != 2009]], ignore_index=True)

# Fill missing engineered columns in raw data rows with 0
engineered_cols = [col for col in engineered.columns if col not in raw.columns]
for col in engineered_cols:
    if col not in combined.columns:
        combined[col] = 0
    else:
        combined[col] = combined[col].fillna(0)

# Sort by year and pick
combined = combined.sort_values(['draft_year', 'draft_pick']).reset_index(drop=True)

# Fix data types: convert object columns that should be numeric
for col in ['pos_tier_LINE', 'pos_tier_OTHER', 'pos_tier_SKILL']:
    if col in combined.columns:
        combined[col] = pd.to_numeric(combined[col], errors='coerce').fillna(0).astype(int)

print(f"\nCombined dataset:")
print(f"  Shape: {combined.shape}")
print(f"  Years: {sorted(combined['draft_year'].unique())}")
print(f"  Rows per year:\n{combined['draft_year'].value_counts().sort_index()}")

# Save combined data
output_path = data_dir / 'nfl_draft_combined.csv'
combined.to_csv(output_path, index=False)

print(f"\nSaved to: {output_path}")
print(f"Columns: {list(combined.columns)}")
