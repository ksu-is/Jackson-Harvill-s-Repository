#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ScoutSense Demo: Prediction Models & Player Comparison
Demonstrates draft position prediction, success classification, and player similarity
"""

from pathlib import Path
from scoutsense.utils.data_loader import load_draft_data
from scoutsense.utils.feature_engineering import engineer_features
from scoutsense.utils.models import (
    DraftPositionPredictor, 
    PlayerSuccessClassifier, 
    PlayerComparison,
    demonstrate_models
)

def main():
    # Load and engineer data
    print("="*80)
    print("SCOUTSENSE: Loading Data")
    print("="*80)
    
    data_file = Path(__file__).parent.parent / 'data' / 'nfl_draft_data.csv'
    df = load_draft_data(str(data_file))
    print(f"[LOADED] {len(df)} players from CSV")
    
    print("\n[ENGINEERING] Creating 25+ features...")
    df_engineered = engineer_features(df)
    print(f"[COMPLETE] {df_engineered.shape[1]} total features")
    
    # Run demonstrations
    demonstrate_models(df_engineered)
    
    # Interactive examples
    print("\n" + "="*80)
    print("INTERACTIVE EXAMPLES")
    print("="*80)
    
    # Create models
    predictor = DraftPositionPredictor()
    predictor.train(df_engineered)
    
    classifier = PlayerSuccessClassifier(success_threshold=5)
    classifier.train(df_engineered)
    
    comparator = PlayerComparison(df_engineered)
    
    # Example 1: Predict draft position for a random player
    print("\n[EXAMPLE 1] Draft Position Prediction")
    print("-" * 80)
    sample_player = df_engineered.sample(1).iloc[0]
    predicted_pick = predictor.predict(sample_player)
    actual_pick = sample_player['draft_pick']
    error = abs(predicted_pick - actual_pick)
    print(f"Player: {sample_player['name']}")
    print(f"Position: {sample_player['pos']}")
    print(f"College: {sample_player['college']}")
    print(f"Actual Draft Pick: {int(actual_pick)}")
    print(f"Predicted Draft Pick: {predicted_pick}")
    print(f"Prediction Error: {error:.0f} picks")
    
    # Example 2: Success probability
    print("\n[EXAMPLE 2] Player Success Classification")
    print("-" * 80)
    sample_positions = df_engineered['pos'].unique()[:3]
    for pos in sample_positions:
        pos_players = df_engineered[df_engineered['pos'] == pos]
        if len(pos_players) > 0:
            p = pos_players.sample(1).iloc[0]
            success_prob = classifier.predict_proba(p)
            print(f"{p['name']:<20} ({pos}) Success Probability: {success_prob:.1%}")
    
    # Example 3: Find similar players
    print("\n[EXAMPLE 3] Player Similarity Matching")
    print("-" * 80)
    test_name = "Matthew Stafford"
    if test_name in df_engineered['name'].values:
        print(f"Finding 3 players most similar to {test_name}...")
        similar = comparator.find_similar_players(test_name, n_similar=3, position_only=True)
    
    # Example 4: Multi-player comparison
    print("\n[EXAMPLE 4] Side-by-Side Player Comparison")
    print("-" * 80)
    print("Comparing top 3 overall picks...")
    top_picks = df_engineered.nsmallest(3, 'draft_pick')['name'].tolist()
    if top_picks:
        comparator.compare_players(top_picks)
    
    print("\n" + "="*80)
    print("Demo Complete!")
    print("="*80)

if __name__ == "__main__":
    main()
