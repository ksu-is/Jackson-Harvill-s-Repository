import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

def engineer_features(data):
    """
    Engineer meaningful features from NFL draft data for scouting analysis.
    
    Input columns expected:
    - Draft Pick: int
    - Team: str
    - Name: str
    - Pos: str (Position)
    - Age: int
    - Ht: str (Height - may be corrupted, handle gracefully)
    - Wt: str (Weight - may be corrupted, handle gracefully)
    - College: str
    - College/Yrs: int
    - Meets: int
    
    Returns DataFrame with original + engineered features
    """
    
    engineered_data = data.copy()
    
    # ============= DRAFT METRICS =============
    
    # 1. Draft Pick Value (earlier pick = higher value)
    # Normalize to 0-1 scale (lower pick # = higher value)
    engineered_data['draft_value_score'] = 1 - (engineered_data['draft_pick'] / engineered_data['draft_pick'].max())
    
    # 2. Round (approximate from draft pick)
    # Roughly: Round 1 = picks 1-32, Round 2 = 33-64, etc.
    engineered_data['draft_round'] = pd.cut(engineered_data['draft_pick'], 
                                            bins=[0, 32, 64, 96, 128, 192, 224, 256],
                                            labels=[1, 2, 3, 4, 5, 6, 7])
    engineered_data['draft_round'] = pd.to_numeric(engineered_data['draft_round'], errors='coerce')
    
    # 3. Early Pick Indicator (first 2 rounds = high priority)
    engineered_data['is_early_pick'] = (engineered_data['draft_pick'] <= 64).astype(int)
    
    # ============= AGE & EXPERIENCE METRICS =============
    
    # 4. Age normalized (college players typically 20-25)
    engineered_data['age_normalized'] = (engineered_data['age'] - engineered_data['age'].min()) / (engineered_data['age'].max() - engineered_data['age'].min())
    
    # 5. College years/experience
    engineered_data['college_years_numeric'] = pd.to_numeric(engineered_data['college/yrs'], errors='coerce')
    engineered_data['college_years_normalized'] = (engineered_data['college_years_numeric'] - engineered_data['college_years_numeric'].min()) / (engineered_data['college_years_numeric'].max() - engineered_data['college_years_numeric'].min())
    
    # 6. Age-to-experience ratio (younger with more years = good development)
    engineered_data['age_experience_ratio'] = engineered_data['age'] / engineered_data['college_years_numeric'].replace(0, 1)
    
    # ============= PHYSICAL ATTRIBUTES =============
    
    # Note: Height and Weight in CSV appear corrupted from scraping
    # These features will be NA if data can't be parsed
    engineered_data['height_numeric'] = pd.to_numeric(engineered_data['ht'], errors='coerce')
    engineered_data['weight_numeric'] = pd.to_numeric(engineered_data['wt'], errors='coerce')
    
    # BMI calculation (only where we have valid height/weight)
    # BMI = weight (lbs) / (height (inches) ^ 2) * 703
    engineered_data['bmi'] = (engineered_data['weight_numeric'] / 
                              (engineered_data['height_numeric'] ** 2)) * 703
    engineered_data['bmi'] = engineered_data['bmi'].replace([np.inf, -np.inf], np.nan)
    
    # ============= POSITION-BASED FEATURES =============
    
    # 7. Position categories
    engineered_data['position'] = engineered_data['pos'].str.upper().str.strip()
    
    # Position tiers (for scouting analysis)
    skill_positions = ['WR', 'RB', 'TE', 'QB']
    line_positions = ['OT', 'OG', 'C', 'DT', 'DE']
    secondary_positions = ['CB', 'S', 'FS', 'SS']
    
    engineered_data['position_tier'] = engineered_data['position'].apply(
        lambda x: 'SKILL' if x in skill_positions else 
                 'LINE' if x in line_positions else 
                 'SECONDARY' if x in secondary_positions else 'OTHER'
    )
    
    # QB flag (quarterbacks are unique in scouting)
    engineered_data['is_qb'] = (engineered_data['position'] == 'QB').astype(int)
    
    # Defensive position flag
    engineered_data['is_defensive'] = engineered_data['position'].str.contains('D|CB|S', regex=True, case=False, na=False).astype(int)
    
    # ============= COLLEGE STRENGTH METRICS =============
    
    # 8. Number of "Meets" (likely combine meets/benchmarks)
    engineered_data['meets_numeric'] = pd.to_numeric(engineered_data['meets'], errors='coerce')
    
    # Normalize meets score
    engineered_data['meets_normalized'] = (engineered_data['meets_numeric'] - engineered_data['meets_numeric'].min()) / \
                                          (engineered_data['meets_numeric'].max() - engineered_data['meets_numeric'].min())
    
    # 9. College school strength (frequency analysis - most players from strong programs)
    college_counts = engineered_data['college'].value_counts()
    engineered_data['college_frequency'] = engineered_data['college'].map(college_counts)
    engineered_data['college_frequency_normalized'] = (engineered_data['college_frequency'] - engineered_data['college_frequency'].min()) / \
                                                       (engineered_data['college_frequency'].max() - engineered_data['college_frequency'].min())
    
    # ============= COMPOSITE SCOUTING SCORES =============
    
    # 10. Overall Scout Grade (0-100 scale)
    # Combine: draft pick value (40%), age fitness (20%), college strength (20%), athletic profile (20%)
    engineered_data['scout_grade'] = (
        engineered_data['draft_value_score'] * 40 +
        (1 - engineered_data['age_normalized']) * 20 +  # Younger is better
        engineered_data['college_frequency_normalized'] * 20 +
        engineered_data['meets_normalized'] * 20
    )
    
    # 11. Draft Predictability Score (how predictable their draft position was)
    # Position-specific average draft picks
    position_avg_pick = engineered_data.groupby('position')['draft_pick'].transform('mean')
    engineered_data['position_avg_pick'] = position_avg_pick
    engineered_data['pick_vs_position_avg'] = engineered_data['draft_pick'] - engineered_data['position_avg_pick']
    engineered_data['draft_predictability'] = (engineered_data['pick_vs_position_avg'].abs() / engineered_data['position_avg_pick']).replace([np.inf, -np.inf], 0)
    
    # ============= ENCODE CATEGORICAL VARIABLES =============
    
    # One-hot encode position tier
    position_dummies = pd.get_dummies(engineered_data['position_tier'], prefix='pos_tier')
    engineered_data = pd.concat([engineered_data, position_dummies], axis=1)
    
    # ============= CLEANUP & VALIDATION =============
    
    # Fill NaN values in numeric features with median
    numeric_cols = engineered_data.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if engineered_data[col].isna().any():
            engineered_data[col] = engineered_data[col].fillna(engineered_data[col].median())
    
    return engineered_data


def get_feature_descriptions():
    """Return descriptions of all engineered features"""
    features = {
        'draft_value_score': 'Normalized draft pick value (0-1, higher is better)',
        'draft_round': 'Approximate round from draft pick',
        'is_early_pick': 'Binary: 1 if picked in first 2 rounds',
        'age_normalized': 'Age normalized to 0-1 scale',
        'college_years_numeric': 'Years spent in college',
        'college_years_normalized': 'College years normalized to 0-1',
        'age_experience_ratio': 'Age divided by college years (development indicator)',
        'height_numeric': 'Height (parsed from raw data)',
        'weight_numeric': 'Weight (parsed from raw data)',
        'bmi': 'Body Mass Index calculated from height/weight',
        'is_qb': 'Binary: 1 if position is QB',
        'is_defensive': 'Binary: 1 if defensive position',
        'meets_numeric': 'Combine meets/benchmarks count',
        'meets_normalized': 'Meets score normalized to 0-1',
        'college_frequency': 'Number of players from same college in dataset',
        'college_frequency_normalized': 'College frequency normalized to 0-1',
        'scout_grade': 'Overall scouting grade (0-100 scale)',
        'draft_predictability': 'How close to position average pick (lower = more predictable)',
    }
    return features


def scale_features(data, feature_cols=None):
    """
    Scale numeric features to 0-1 range for ML models.
    
    Args:
        data: DataFrame with engineered features
        feature_cols: List of columns to scale (if None, scales all numeric)
    
    Returns:
        Scaled DataFrame
    """
    data_scaled = data.copy()
    
    if feature_cols is None:
        feature_cols = data_scaled.select_dtypes(include=[np.number]).columns.tolist()
    
    scaler = StandardScaler()
    data_scaled[feature_cols] = scaler.fit_transform(data_scaled[feature_cols])
    
    return data_scaled
