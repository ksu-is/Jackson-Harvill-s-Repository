#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ScoutSense: Practical Usage Examples
Real-world use cases for the prediction and comparison tools
"""

from pathlib import Path
from scoutsense.utils.data_loader import load_draft_data
from scoutsense.utils.feature_engineering import engineer_features
from scoutsense.utils.models import (
    DraftPositionPredictor,
    PlayerSuccessClassifier,
    PlayerComparison
)

# Data file path
DATA_FILE = Path(__file__).parent.parent / 'data' / 'nfl_draft_data.csv'

def example_1_predict_draft_position():
    """Example 1: Predict where a player will be drafted"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Draft Position Prediction")
    print("="*80)
    
    # Load data
    df = load_draft_data(str(DATA_FILE))
    df_engineered = engineer_features(df)
    
    # Train predictor
    predictor = DraftPositionPredictor()
    predictor.train(df_engineered)
    
    # Predict for top 3 overall picks
    print("\nPredicting draft position for top 3 prospects:")
    top_picks = df_engineered.nsmallest(3, 'draft_pick')
    
    for idx, player in top_picks.iterrows():
        predicted = predictor.predict(player)
        actual = int(player['draft_pick'])
        error = abs(predicted - actual)
        
        print(f"\n{player['name']}")
        print(f"  Position: {player['pos']}")
        print(f"  College: {player['college']}")
        print(f"  Actual Pick: {actual}")
        print(f"  Predicted Pick: {predicted}")
        print(f"  Error: {error} picks")


def example_2_success_probability():
    """Example 2: Assess probability of player success"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Player Success Classification")
    print("="*80)
    
    # Load data
    df = load_draft_data(str(DATA_FILE))
    df_engineered = engineer_features(df)
    
    # Train classifier
    classifier = PlayerSuccessClassifier(success_threshold=5)
    classifier.train(df_engineered)
    
    # Show success probability for various draft rounds
    print("\nAverage success probability by draft round:")
    print(f"{'Round':<10} {'Avg Success %':<15} {'Avg Pick':<10}")
    print("-" * 35)
    
    for round_num in range(1, 8):
        round_players = df_engineered[df_engineered['draft_round'] == round_num]
        if len(round_players) > 0:
            avg_success = round_players.apply(lambda p: classifier.predict_proba(p), axis=1).mean()
            avg_pick = round_players['draft_pick'].mean()
            print(f"{int(round_num):<10} {avg_success*100:>13.1f}% {int(avg_pick):>10}")


def example_3_find_player_comps():
    """Example 3: Find comparable players (player comps)"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Find Player Comps")
    print("="*80)
    
    # Load data
    df = load_draft_data(str(DATA_FILE))
    df_engineered = engineer_features(df)
    
    # Create comparison tool
    comparator = PlayerComparison(df_engineered)
    
    # Example: Find QBs similar to Matthew Stafford
    print("\n[CASE 1] QBs similar to Matthew Stafford")
    print("-" * 80)
    similar_qbs = comparator.find_similar_players("Matthew Stafford", n_similar=3, position_only=True)
    
    # Example: Find wide receivers similar to a late-round pick
    print("\n[CASE 2] WRs similar to Percy Harvin (2009 Round 1, Pick 22)")
    print("-" * 80)
    similar_wrs = comparator.find_similar_players("Percy Harvin", n_similar=5, position_only=True)


def example_4_overvalued_undervalued():
    """Example 4: Identify overvalued and undervalued picks"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Identify Overvalued & Undervalued Picks")
    print("="*80)
    
    # Load data
    df = load_draft_data(str(DATA_FILE))
    df_engineered = engineer_features(df)
    
    # Train predictor
    predictor = DraftPositionPredictor()
    predictor.train(df_engineered)
    
    # Predict for all players
    df_engineered['predicted_pick'] = df_engineered.apply(lambda p: predictor.predict(p), axis=1)
    df_engineered['pick_difference'] = df_engineered['predicted_pick'] - df_engineered['draft_pick']
    
    # Overvalued: picked earlier than predicted
    print("\nTOP 5 OVERVALUED PICKS (drafted earlier than model predicted)")
    print(f"{'Name':<20} {'Pos':<5} {'Actual':<8} {'Predicted':<10} {'Difference':<12}")
    print("-" * 60)
    overvalued = df_engineered.nlargest(5, 'pick_difference')
    for _, player in overvalued.iterrows():
        print(f"{player['name']:<20} {player['pos']:<5} "
              f"{int(player['draft_pick']):<8} {int(player['predicted_pick']):<10} "
              f"{int(player['pick_difference']):<12}")
    
    # Undervalued: picked later than predicted
    print("\nTOP 5 UNDERVALUED PICKS (drafted later than model predicted)")
    print(f"{'Name':<20} {'Pos':<5} {'Actual':<8} {'Predicted':<10} {'Difference':<12}")
    print("-" * 60)
    undervalued = df_engineered.nsmallest(5, 'pick_difference')
    for _, player in undervalued.iterrows():
        diff = int(player['pick_difference'])
        print(f"{player['name']:<20} {player['pos']:<5} "
              f"{int(player['draft_pick']):<8} {int(player['predicted_pick']):<10} "
              f"{diff:<12}")


def example_5_position_analysis():
    """Example 5: Compare similar players within position"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Compare Top 3 Players of Each Position")
    print("="*80)
    
    # Load data
    df = load_draft_data(str(DATA_FILE))
    df_engineered = engineer_features(df)
    
    comparator = PlayerComparison(df_engineered)
    
    # Get unique positions
    positions = df_engineered['pos'].unique()[:3]
    
    for pos in positions:
        pos_players = df_engineered[df_engineered['pos'] == pos].nsmallest(3, 'draft_pick')
        
        print(f"\n[{pos}] Top 3 Draft Picks")
        print("-" * 80)
        
        player_names = pos_players['name'].tolist()
        if len(player_names) > 0:
            comparator.compare_players(player_names)


def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("SCOUTSENSE: PRACTICAL USAGE EXAMPLES")
    print("="*80)
    
    try:
        example_1_predict_draft_position()
        example_2_success_probability()
        example_3_find_player_comps()
        example_4_overvalued_undervalued()
        example_5_position_analysis()
        
        print("\n" + "="*80)
        print("ALL EXAMPLES COMPLETED!")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
