#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NFL Draft Prediction & Comparison Models
Includes draft position prediction, player success classification, and similarity analysis
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
from scipy.spatial.distance import euclidean, cosine
import warnings
warnings.filterwarnings('ignore')


class DraftPositionPredictor:
    """Predict a player's draft position based on college stats and attributes"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_cols = None
        self.trained = False
        
    def train(self, df):
        """
        Train model to predict draft pick number
        
        Args:
            df: DataFrame with engineered features including 'draft_pick'
        """
        print("Training Draft Position Predictor...")
        
        # Select features for prediction (exclude target and identifiers)
        exclude_cols = ['draft_pick', 'name', 'team', 'college', 'pos', 'position', 
                       'position_tier', 'ht', 'wt', 'age', 'meets']
        self.feature_cols = [c for c in df.columns if c not in exclude_cols]
        
        X = df[self.feature_cols].fillna(df[self.feature_cols].median())
        y = df['draft_pick']
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data (80/20)
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
        
        # Train Gradient Boosting model (better for regression)
        self.model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, 
                                               max_depth=5, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        print(f"  Train/Test split: {len(X_train)}/{len(X_test)}")
        print(f"  RMSE: {rmse:.2f} picks")
        print(f"  R² Score: {r2:.3f}")
        
        self.trained = True
        return self
    
    def predict(self, player_data):
        """
        Predict draft position for a player
        
        Args:
            player_data: DataFrame row or dict with player features
            
        Returns:
            Predicted draft pick number
        """
        if not self.trained:
            raise ValueError("Model must be trained first")
        
        if isinstance(player_data, pd.Series):
            player_data = player_data.to_frame().T
        elif isinstance(player_data, dict):
            player_data = pd.DataFrame([player_data])
        
        X = player_data[self.feature_cols].fillna(0)
        X_scaled = self.scaler.transform(X)
        prediction = self.model.predict(X_scaled)[0]
        
        return max(1, int(prediction))  # Ensure positive pick number
    
    def feature_importance(self, top_n=10):
        """Get most important features for draft prediction"""
        if not self.trained:
            return None
        
        importances = self.model.feature_importances_
        indices = np.argsort(importances)[-top_n:][::-1]
        
        result = {}
        for idx in indices:
            result[self.feature_cols[idx]] = float(importances[idx])
        
        return result


class PlayerSuccessClassifier:
    """Predict if a player will have a successful NFL career"""
    
    def __init__(self, success_threshold=5):
        """
        Args:
            success_threshold: Players drafted in rounds <= threshold are "successful"
                             (Round 1-5 typically means more NFL success)
        """
        self.model = None
        self.scaler = StandardScaler()
        self.feature_cols = None
        self.success_threshold = success_threshold
        self.trained = False
        
    def train(self, df):
        """
        Train model to classify successful vs unsuccessful players
        Using draft round as proxy for success (early picks = more successful)
        
        Args:
            df: DataFrame with engineered features
        """
        print(f"\nTraining Player Success Classifier (success = round <= {self.success_threshold})...")
        
        # Define success: early draft picks have higher NFL success rate
        df['success'] = (df['draft_round'] <= self.success_threshold).astype(int)
        
        # Select features
        exclude_cols = ['draft_pick', 'draft_round', 'success', 'name', 'team', 'college', 
                       'pos', 'position', 'position_tier', 'ht', 'wt', 'age', 'meets']
        self.feature_cols = [c for c in df.columns if c not in exclude_cols]
        
        X = df[self.feature_cols].fillna(df[self.feature_cols].median())
        y = df['success']
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
        
        # Train Random Forest classifier
        self.model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"  Train/Test split: {len(X_train)}/{len(X_test)}")
        print(f"  Success rate in dataset: {y.sum()}/{len(y)} ({y.mean()*100:.1f}%)")
        print(f"  Model Accuracy: {accuracy:.3f}")
        
        self.trained = True
        return self
    
    def predict_proba(self, player_data):
        """
        Predict success probability for a player
        
        Args:
            player_data: DataFrame row or dict with player features
            
        Returns:
            Probability of success (0-1)
        """
        if not self.trained:
            raise ValueError("Model must be trained first")
        
        if isinstance(player_data, pd.Series):
            player_data = player_data.to_frame().T
        elif isinstance(player_data, dict):
            player_data = pd.DataFrame([player_data])
        
        X = player_data[self.feature_cols].fillna(0)
        X_scaled = self.scaler.transform(X)
        proba = self.model.predict_proba(X_scaled)[0][1]
        
        return float(proba)


class PlayerComparison:
    """Find and compare similar players in the draft"""
    
    def __init__(self, df):
        """
        Args:
            df: DataFrame with engineered features for all players
        """
        self.df = df.copy()
        self.feature_cols = None
        self._prepare_features()
    
    def _prepare_features(self):
        """Prepare and scale features for comparison"""
        exclude_cols = ['draft_pick', 'draft_round', 'name', 'team', 'college', 
                       'pos', 'position', 'position_tier', 'ht', 'wt', 'age', 'meets']
        self.feature_cols = [c for c in self.df.columns if c not in exclude_cols and 
                            pd.api.types.is_numeric_dtype(self.df[c])]
        
        # Scale features for fair comparison
        scaler = StandardScaler()
        self.df_scaled = self.df.copy()
        self.df_scaled[self.feature_cols] = scaler.fit_transform(self.df[self.feature_cols].fillna(0))
    
    def find_similar_players(self, player_name_or_idx, n_similar=5, position_only=False):
        """
        Find players most similar to a given player
        
        Args:
            player_name_or_idx: Player name (str) or index (int)
            n_similar: Number of similar players to return
            position_only: If True, only compare within same position
            
        Returns:
            DataFrame of similar players with similarity scores
        """
        # Find player index
        if isinstance(player_name_or_idx, str):
            matches = self.df[self.df['name'].str.contains(player_name_or_idx, case=False, na=False)]
            if matches.empty:
                return pd.DataFrame()
            player_idx = matches.index[0]
            player_name = matches['name'].iloc[0]
        else:
            player_idx = player_name_or_idx
            player_name = self.df.loc[player_idx, 'name']
        
        player_data = self.df_scaled.loc[player_idx, self.feature_cols].values
        player_position = self.df.loc[player_idx, 'pos']
        
        # Calculate distances to all other players
        distances = []
        for idx in self.df.index:
            if idx == player_idx:
                continue
            
            # Filter by position if requested
            if position_only and self.df.loc[idx, 'pos'] != player_position:
                continue
            
            other_data = self.df_scaled.loc[idx, self.feature_cols].values
            dist = euclidean(player_data, other_data)
            distances.append((idx, dist))
        
        # Sort by distance and get top N
        distances.sort(key=lambda x: x[1])
        similar_indices = [d[0] for d in distances[:n_similar]]
        similar_distances = [d[1] for d in distances[:n_similar]]
        
        # Build result DataFrame
        result = self.df.loc[similar_indices].copy()
        result['similarity_score'] = 1 / (1 + np.array(similar_distances))  # Convert distance to similarity
        result = result.sort_values('similarity_score', ascending=False)
        
        print(f"\nPlayers similar to {player_name} ({player_position}):")
        print(f"{'Rank':<5} {'Name':<20} {'Pos':<5} {'Pick':<5} {'College':<20} {'Similarity':<10}")
        print("-" * 75)
        for i, (idx, row) in enumerate(result.iterrows(), 1):
            print(f"{i:<5} {row['name']:<20} {row['pos']:<5} {int(row['draft_pick']):<5} {row['college']:<20} {row['similarity_score']:.3f}")
        
        return result
    
    def compare_players(self, player_names):
        """
        Compare multiple players side-by-side
        
        Args:
            player_names: List of player names to compare
            
        Returns:
            DataFrame with comparison data
        """
        players = []
        for name in player_names:
            match = self.df[self.df['name'].str.contains(name, case=False, na=False)]
            if not match.empty:
                players.append(match.iloc[0])
        
        if not players:
            return pd.DataFrame()
        
        result = pd.DataFrame(players)
        
        # Show key comparison metrics
        print(f"\nComparing {len(players)} players:")
        print(f"{'Name':<20} {'Pos':<5} {'Pick':<5} {'Age':<5} {'College':<20} {'Scout Grade':<12}")
        print("-" * 75)
        for _, row in result.iterrows():
            print(f"{row['name']:<20} {row['pos']:<5} {int(row['draft_pick']):<5} "
                  f"{int(row['age']):<5} {row['college']:<20} {row['scout_grade']:.2f}")
        
        return result


def demonstrate_models(df):
    """Demonstrate all models on sample data"""
    print("\n" + "="*80)
    print("SCOUTSENSE: NFL DRAFT PREDICTION & COMPARISON DEMO")
    print("="*80)
    
    # Train Draft Position Predictor
    predictor = DraftPositionPredictor()
    predictor.train(df)
    
    # Train Success Classifier
    classifier = PlayerSuccessClassifier(success_threshold=5)
    classifier.train(df)
    
    # Feature importance
    print("\n[FEATURE IMPORTANCE] Top factors for draft position:")
    importances = predictor.feature_importance(top_n=10)
    for i, (feat, imp) in enumerate(importances.items(), 1):
        print(f"  {i}. {feat}: {imp:.4f}")
    
    # Player Comparison
    comparator = PlayerComparison(df)
    
    # Demo: Find similar QBs to Matthew Stafford
    print("\n[PLAYER SIMILARITY] Finding QBs similar to Matthew Stafford...")
    stafford_similar = comparator.find_similar_players("Matthew Stafford", n_similar=5, position_only=True)
    
    # Demo: Predict on sample player
    print("\n[DRAFT PREDICTION] Predicting draft position for sample QBs...")
    qbs = df[df['pos'] == 'QB'].head(3)
    for _, qb in qbs.iterrows():
        pred_pick = predictor.predict(qb)
        success_prob = classifier.predict_proba(qb)
        print(f"  {qb['name']:<20} Actual: Pick {int(qb['draft_pick']):3}, "
              f"Predicted: Pick {pred_pick:3}, Success Prob: {success_prob:.1%}")
    
    print("\n" + "="*80)
