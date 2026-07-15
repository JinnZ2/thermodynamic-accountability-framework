# sensitivity_analyzer.py
"""
Quantifies the impact of assumption-laden variables on a predictive model.
Integrates with the Bias Autopsy Lab.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

class SensitivityIntegrator:
    """
    Trains a baseline model (with all variables) and a clean model (assumption
    variables removed) and measures the resulting prediction drift.
    """
    def __init__(self, data: pd.DataFrame, target_col: str,
                 assumption_vars: list, control_vars: list = None):
        """
        data: DataFrame with numeric features and target.
        target_col: name of the dependent variable.
        assumption_vars: list of column names flagged as assumption-laden.
        control_vars: list of other predictors; if None, all other numeric
                      columns not in assumption_vars are used.
        """
        self.data = data.copy()
        self.target_col = target_col
        self.assumption_vars = assumption_vars
        if control_vars is None:
            all_cols = [c for c in data.columns if c != target_col]
            self.control_vars = [c for c in all_cols if c not in assumption_vars]
        else:
            self.control_vars = control_vars
        self.baseline_model = None
        self.clean_model = None

    def _prepare_features(self, var_list):
        """Return numeric features and aligned target, dropping NaNs."""
        X = self.data[var_list].select_dtypes(include=[np.number])
        X = X.dropna()
        y = self.data.loc[X.index, self.target_col]
        return X, y

    def fit_baseline(self):
        """Fit model using all variables (assumption + control)."""
        all_vars = self.assumption_vars + self.control_vars
        X, y = self._prepare_features(all_vars)
        self.baseline_model = LinearRegression().fit(X, y)
        self.baseline_X = X
        self.baseline_y = y
        return self.baseline_model

    def fit_clean(self):
        """Fit model using only control variables (assumptions removed)."""
        X, y = self._prepare_features(self.control_vars)
        self.clean_model = LinearRegression().fit(X, y)
        self.clean_X = X
        self.clean_y = y
        return self.clean_model

    def _common_idx(self):
        """Return index present in both baseline and clean datasets."""
        return self.baseline_X.index.intersection(self.clean_X.index)

    def sensitivity_report(self):
        """Compute drift, MSE, and feature importance shift."""
        if not self.baseline_model or not self.clean_model:
            self.fit_baseline()
            self.fit_clean()

        idx = self._common_idx()
        baseline_pred = self.baseline_model.predict(self.baseline_X.loc[idx])
        clean_pred = self.clean_model.predict(self.clean_X.loc[idx])
        y_true = self.baseline_y.loc[idx]

        mse_baseline = mean_squared_error(y_true, baseline_pred)
        mse_clean = mean_squared_error(y_true, clean_pred)
        drift_abs = np.mean(np.abs(baseline_pred - clean_pred))
        drift_pct = drift_abs / np.mean(np.abs(y_true)) * 100

        # Coefficients for linear model (importance)
        imp_base = dict(zip(self.baseline_model.feature_names_in_,
                            self.baseline_model.coef_))
        imp_clean = dict(zip(self.clean_model.feature_names_in_,
                             self.clean_model.coef_))

        return {
            'baseline_mse': mse_baseline,
            'clean_mse': mse_clean,
            'prediction_drift_mean': drift_abs,
            'drift_percent': drift_pct,
            'feature_importance_shift': {
                'baseline': imp_base,
                'clean': imp_clean
            }
        }

    def plot_prediction_drift(self):
        """Scatter plot of baseline vs clean predictions."""
        if not self.baseline_model or not self.clean_model:
            self.fit_baseline()
            self.fit_clean()

        idx = self._common_idx()
        baseline_pred = self.baseline_model.predict(self.baseline_X.loc[idx])
        clean_pred = self.clean_model.predict(self.clean_X.loc[idx])

        plt.figure(figsize=(6, 5))
        plt.scatter(baseline_pred, clean_pred, alpha=0.6)
        min_val = min(baseline_pred.min(), clean_pred.min())
        max_val = max(baseline_pred.max(), clean_pred.max())
        plt.plot([min_val, max_val], [min_val, max_val], 'r--')
        plt.xlabel("Baseline Prediction (with assumptions)")
        plt.ylabel("Bias-Removed Prediction")
        plt.title("Impact of Removing Assumption Variables")
        plt.tight_layout()
        return plt.gcf()
