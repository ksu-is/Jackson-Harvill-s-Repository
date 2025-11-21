#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ScoutSense UI - Tkinter-based GUI for NFL Draft Prediction and Player Comparison
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os
import glob
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.models import (
    DraftPositionPredictor,
    PlayerSuccessClassifier,
    PlayerComparison
)


class ScoutSenseApp:
    """Main Tkinter application for ScoutSense"""
    
    def __init__(self, root, initial_data_path=None, auto_train=False):
        self.root = root
        self.root.title("ScoutSense - NFL Draft Prediction & Comparison")
        self.root.geometry("1000x700")
        
        # Initialize data and models
        self.df = None
        self.predictor = None
        self.classifier = None
        self.comparator = None
        
        # Setup UI
        self.setup_ui()
        # Attempt to load initial data if provided
        self._auto_train_on_startup = bool(auto_train)
        if initial_data_path:
            try:
                self.load_data_from_path(initial_data_path)
            except Exception:
                # Don't block UI startup if initial load fails
                pass
            else:
                # If auto-train requested, schedule training after mainloop starts
                if self._auto_train_on_startup:
                    # schedule shortly after startup so the UI initializes cleanly
                    self.root.after(100, lambda: self.train_models())
        
    def setup_ui(self):
        """Setup the main UI layout"""
        # Create menu bar
        self.create_menu_bar()
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.tab_home = ttk.Frame(self.notebook)
        self.tab_predictor = ttk.Frame(self.notebook)
        self.tab_comparison = ttk.Frame(self.notebook)
        self.tab_analytics = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_home, text="Home")
        self.notebook.add(self.tab_predictor, text="Draft Predictor")
        self.notebook.add(self.tab_comparison, text="Player Comparison")
        self.notebook.add(self.tab_analytics, text="Analytics")
        
        # Setup each tab
        self.setup_home_tab()
        self.setup_predictor_tab()
        self.setup_comparison_tab()
        self.setup_analytics_tab()
        
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Data", command=self.load_data)
        file_menu.add_command(label="Train Models", command=self.train_models)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def setup_home_tab(self):
        """Setup home tab"""
        frame = ttk.Frame(self.tab_home, padding="20")
        frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(
            frame,
            text="ScoutSense",
            font=("Arial", 28, "bold")
        )
        title_label.pack(pady=20)
        
        # Subtitle
        subtitle_label = ttk.Label(
            frame,
            text="NFL Draft Prediction & Player Comparison Tool",
            font=("Arial", 12)
        )
        subtitle_label.pack(pady=10)
        
        # Description
        description = """
ScoutSense uses machine learning to predict draft positions and analyze player similarities.

Features:
• Draft Position Predictor: Predict where a player will be drafted
• Player Success Classifier: Estimate probability of NFL success
• Player Comparison: Find similar players and compare stats
• Feature Analysis: Understand what drives draft position

Getting Started:
1. Load your draft data (File → Load Data)
2. Train the models (File → Train Models)
3. Use the tools in other tabs to analyze players
        """
        
        desc_label = ttk.Label(
            frame,
            text=description,
            font=("Arial", 10),
            justify=tk.LEFT,
            foreground="#333"
        )
        desc_label.pack(pady=20, anchor="w")
        
        # Status frame
        status_frame = ttk.LabelFrame(frame, text="Status", padding="10")
        status_frame.pack(fill="x", pady=20)
        
        self.status_label = ttk.Label(
            status_frame,
            text="No data loaded",
            foreground="red"
        )
        self.status_label.pack(anchor="w")
        
        # Quick buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill="x", pady=20)
        
        ttk.Button(
            button_frame,
            text="Load Data",
            command=self.load_data
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="Train Models",
            command=self.train_models
        ).pack(side="left", padx=5)
        
    def setup_predictor_tab(self):
        """Setup draft predictor tab"""
        frame = ttk.Frame(self.tab_predictor, padding="20")
        frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(
            frame,
            text="Draft Position Predictor",
            font=("Arial", 16, "bold")
        ).pack(pady=10)
        
        # Player selection frame
        select_frame = ttk.LabelFrame(frame, text="Select Player", padding="10")
        select_frame.pack(fill="x", pady=10)
        
        ttk.Label(select_frame, text="Player Name:").pack(side="left", padx=5)
        
        self.player_var = tk.StringVar()
        self.player_combo = ttk.Combobox(
            select_frame,
            textvariable=self.player_var,
            width=30,
            state="readonly"
        )
        self.player_combo.pack(side="left", padx=5)
        
        ttk.Button(
            select_frame,
            text="Predict",
            command=self.predict_draft_position
        ).pack(side="left", padx=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(frame, text="Prediction Results", padding="10")
        results_frame.pack(fill="both", expand=True, pady=10)
        
        self.predictor_results = tk.Text(
            results_frame,
            height=20,
            width=80,
            state="disabled"
        )
        self.predictor_results.pack(fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            results_frame,
            orient="vertical",
            command=self.predictor_results.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.predictor_results.config(yscrollcommand=scrollbar.set)
        
    def setup_comparison_tab(self):
        """Setup player comparison tab"""
        frame = ttk.Frame(self.tab_comparison, padding="20")
        frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(
            frame,
            text="Player Comparison",
            font=("Arial", 16, "bold")
        ).pack(pady=10)
        
        # Options frame
        options_frame = ttk.LabelFrame(frame, text="Comparison Options", padding="10")
        options_frame.pack(fill="x", pady=10)
        
        ttk.Label(options_frame, text="Player Name:").pack(side="left", padx=5)
        
        self.compare_player_var = tk.StringVar()
        self.compare_player_combo = ttk.Combobox(
            options_frame,
            textvariable=self.compare_player_var,
            width=30,
            state="readonly"
        )
        self.compare_player_combo.pack(side="left", padx=5)
        
        ttk.Label(options_frame, text="Similar Players:").pack(side="left", padx=5)
        
        self.similar_count_var = tk.StringVar(value="5")
        similar_spinbox = ttk.Spinbox(
            options_frame,
            from_=1,
            to=10,
            textvariable=self.similar_count_var,
            width=5
        )
        similar_spinbox.pack(side="left", padx=5)
        
        ttk.Button(
            options_frame,
            text="Compare",
            command=self.find_similar_players
        ).pack(side="left", padx=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(frame, text="Comparison Results", padding="10")
        results_frame.pack(fill="both", expand=True, pady=10)
        
        self.comparison_results = tk.Text(
            results_frame,
            height=20,
            width=80,
            state="disabled"
        )
        self.comparison_results.pack(fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            results_frame,
            orient="vertical",
            command=self.comparison_results.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.comparison_results.config(yscrollcommand=scrollbar.set)
        
    def setup_analytics_tab(self):
        """Setup analytics tab"""
        frame = ttk.Frame(self.tab_analytics, padding="20")
        frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(
            frame,
            text="Feature Importance & Analytics",
            font=("Arial", 16, "bold")
        ).pack(pady=10)
        
        # Options frame
        options_frame = ttk.LabelFrame(frame, text="Options", padding="10")
        options_frame.pack(fill="x", pady=10)
        
        ttk.Label(options_frame, text="Top Features:").pack(side="left", padx=5)
        
        self.top_features_var = tk.StringVar(value="10")
        features_spinbox = ttk.Spinbox(
            options_frame,
            from_=1,
            to=20,
            textvariable=self.top_features_var,
            width=5
        )
        features_spinbox.pack(side="left", padx=5)
        
        ttk.Button(
            options_frame,
            text="Analyze",
            command=self.show_analytics
        ).pack(side="left", padx=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(frame, text="Analysis Results", padding="10")
        results_frame.pack(fill="both", expand=True, pady=10)
        
        self.analytics_results = tk.Text(
            results_frame,
            height=20,
            width=80,
            state="disabled"
        )
        self.analytics_results.pack(fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            results_frame,
            orient="vertical",
            command=self.analytics_results.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.analytics_results.config(yscrollcommand=scrollbar.set)
        
    def load_data(self):
        """Load data file"""
        file_path = filedialog.askopenfilename(
            title="Select Data File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.df = pd.read_csv(file_path)
                self.status_label.config(
                    text=f"Loaded: {Path(file_path).name} ({len(self.df)} rows)",
                    foreground="green"
                )
                self.update_player_combos()
                messagebox.showinfo("Success", f"Data loaded successfully!\nRows: {len(self.df)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data:\n{str(e)}")

    def load_data_from_path(self, file_path):
        """Load data from a given file path (used at startup)."""
        if not file_path:
            raise ValueError("No file path provided")
        file_path = str(file_path)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Data file not found: {file_path}")
        # Use the same loading logic as the interactive loader
        self.df = pd.read_csv(file_path)
        self.status_label.config(
            text=f"Loaded: {Path(file_path).name} ({len(self.df)} rows)",
            foreground="green"
        )
        self.update_player_combos()
                
    def train_models(self):
        """Train all models"""
        if self.df is None:
            messagebox.showwarning("Warning", "Please load data first")
            return
            
        try:
            # Disable buttons during training
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Button):
                    widget.config(state="disabled")
            
            self.root.update()
            
            # Train models
            self.predictor = DraftPositionPredictor()
            self.predictor.train(self.df)
            
            self.classifier = PlayerSuccessClassifier(success_threshold=5)
            self.classifier.train(self.df)
            
            self.comparator = PlayerComparison(self.df)
            
            messagebox.showinfo("Success", "Models trained successfully!")
            
            # Re-enable buttons
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Button):
                    widget.config(state="normal")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Training failed:\n{str(e)}")
            
    def update_player_combos(self):
        """Update player combo boxes with available players"""
        if self.df is None:
            return
            
        if 'name' in self.df.columns:
            player_list = self.df['name'].tolist()
            self.player_combo['values'] = player_list
            self.compare_player_combo['values'] = player_list
            
    def predict_draft_position(self):
        """Predict draft position for selected player"""
        if self.predictor is None:
            messagebox.showwarning("Warning", "Please train models first")
            return
            
        player_name = self.player_var.get()
        if not player_name:
            messagebox.showwarning("Warning", "Please select a player")
            return
            
        try:
            player_data = self.df[self.df['name'] == player_name].iloc[0]
            
            pred_pick = self.predictor.predict(player_data)
            success_prob = self.classifier.predict_proba(player_data)
            actual_pick = int(player_data.get('draft_pick', 'N/A'))
            
            result = f"""
DRAFT POSITION PREDICTION
{'='*50}

Player: {player_name}
Position: {player_data.get('pos', 'N/A')}
College: {player_data.get('college', 'N/A')}

Actual Draft Pick: {actual_pick}
Predicted Draft Pick: {pred_pick}
Difference: {abs(actual_pick - pred_pick)} picks

Success Probability: {success_prob:.1%}
{'='*50}

Interpretation:
- The model predicts this player would be drafted at pick {pred_pick}
- There is a {success_prob:.1%} probability of NFL success
- Success is defined as being drafted in rounds 1-5
            """
            
            self.predictor_results.config(state="normal")
            self.predictor_results.delete("1.0", tk.END)
            self.predictor_results.insert("1.0", result)
            self.predictor_results.config(state="disabled")
            
        except Exception as e:
            messagebox.showerror("Error", f"Prediction failed:\n{str(e)}")
            
    def find_similar_players(self):
        """Find similar players"""
        if self.comparator is None:
            messagebox.showwarning("Warning", "Please train models first")
            return
            
        player_name = self.compare_player_var.get()
        if not player_name:
            messagebox.showwarning("Warning", "Please select a player")
            return
            
        try:
            n_similar = int(self.similar_count_var.get())
            similar = self.comparator.find_similar_players(
                player_name,
                n_similar=n_similar,
                position_only=True
            )
            
            if similar.empty:
                result = "No similar players found"
            else:
                result = "SIMILAR PLAYERS\n" + "="*70 + "\n\n"
                result += similar[['name', 'pos', 'draft_pick', 'college', 'similarity_score']].to_string()
            
            self.comparison_results.config(state="normal")
            self.comparison_results.delete("1.0", tk.END)
            self.comparison_results.insert("1.0", result)
            self.comparison_results.config(state="disabled")
            
        except Exception as e:
            messagebox.showerror("Error", f"Comparison failed:\n{str(e)}")
            
    def show_analytics(self):
        """Show feature importance and analytics"""
        if self.predictor is None:
            messagebox.showwarning("Warning", "Please train models first")
            return
            
        try:
            n_features = int(self.top_features_var.get())
            importances = self.predictor.feature_importance(top_n=n_features)
            
            result = "FEATURE IMPORTANCE ANALYSIS\n"
            result += "="*70 + "\n\n"
            result += "Top factors affecting draft position:\n\n"
            
            for i, (feat, imp) in enumerate(importances.items(), 1):
                bar_length = int(imp * 50)
                bar = "█" * bar_length
                result += f"{i:2}. {feat:<30} {bar} {imp:.4f}\n"
            
            self.analytics_results.config(state="normal")
            self.analytics_results.delete("1.0", tk.END)
            self.analytics_results.insert("1.0", result)
            self.analytics_results.config(state="disabled")
            
        except Exception as e:
            messagebox.showerror("Error", f"Analytics failed:\n{str(e)}")
            
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About ScoutSense",
            "ScoutSense v1.0\n\nNFL Draft Prediction & Comparison Tool\n\n"
            "Uses machine learning to predict draft positions and analyze player similarities."
        )


def main():
    """Main entry point"""
    # Parse optional CLI arg for startup data
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--data', help='Path to CSV file to load at startup', default=None)
    # Boolean optional action is available in modern Python to allow --auto-train / --no-auto-train
    try:
        parser.add_argument('--auto-train', action=argparse.BooleanOptionalAction, default=None,
                            help='Automatically train models at startup if data is loaded (env/CLI/auto-detected)')
    except Exception:
        # Fallback for older argparse implementations (shouldn't happen on Python 3.13)
        parser.add_argument('--auto-train', dest='auto_train', action='store_true')
        parser.add_argument('--no-auto-train', dest='auto_train', action='store_false')

    args, _ = parser.parse_known_args()

    # Determine startup data path: CLI -> ENV -> scoutsense/data/*.csv
    startup_data = None
    if args.data:
        startup_data = args.data
    else:
        env_path = os.getenv('SCOUTSENSE_DATA')
        if env_path:
            startup_data = env_path
        else:
            # Look for CSVs in the package data directory
            data_dir = Path(__file__).parent.parent / 'data'
            if data_dir.exists() and data_dir.is_dir():
                # Prefer a file named 'default_data.csv' if present
                default_file = data_dir / 'default_data.csv'
                if default_file.exists():
                    startup_data = str(default_file)
                else:
                    csvs = sorted(glob.glob(str(data_dir / '*.csv')))
                    if csvs:
                        startup_data = csvs[0]

    # Determine auto-train behavior: CLI -> ENV -> default True
    auto_train = True
    if getattr(args, 'auto_train', None) is not None:
        auto_train = bool(args.auto_train)
    else:
        env_auto = os.getenv('SCOUTSENSE_AUTO_TRAIN')
        if env_auto is not None:
            env_auto = env_auto.strip().lower()
            if env_auto in ('0', 'false', 'no'):
                auto_train = False
            else:
                auto_train = True

    root = tk.Tk()
    app = ScoutSenseApp(root, initial_data_path=startup_data, auto_train=auto_train)
    root.mainloop()


if __name__ == "__main__":
    main()
