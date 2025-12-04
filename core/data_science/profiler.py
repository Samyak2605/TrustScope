import numpy as np
import pandas as pd
from scipy.stats import chi2
from sklearn.preprocessing import StandardScaler
from typing import Dict, Any, List

class DataProfiler:
    """
    Handles statistical profiling of features and detects Out-of-Distribution (OOD) inputs.
    
    Why this matters for Trust:
    Model performance is only guaranteed on data that resembles the training distribution.
    If an input is in a 'rare region' or is OOD, the model is essentially guessing.
    Detecting this allows TRUSTSCOPE to lower the trust score before even making a prediction.
    """
    
    def __init__(self):
        self.feature_stats = {}
        self.scaler = StandardScaler()
        self.mean_train = None
        self.inv_cov_train = None
        self.feature_names = None
        self.is_fitted = False

    def fit_distribution(self, df: pd.DataFrame):
        """
        Profiles the training data distribution.
        Computes mean and inverse covariance for Mahalanobis distance.
        """
        self.feature_names = df.columns.tolist()
        df_scaled = self.scaler.fit_transform(df)
        
        self.mean_train = np.mean(df_scaled, axis=0)
        self.inv_cov_train = np.linalg.pinv(np.cov(df_scaled, rowvar=False))
        
        # Profile individual features
        for col in self.feature_names:
            self.feature_stats[col] = {
                'mean': float(df[col].mean()),
                'std': float(df[col].std()),
                'min': float(df[col].min()),
                'max': float(df[col].max()),
                'q1': float(df[col].quantile(0.25)),
                'q3': float(df[col].quantile(0.75))
            }
        
        self.is_fitted = True
        print(f"[DataProfiler] Distribution profiling complete for {len(self.feature_names)} features.")

    def compute_similarity(self, input_data: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculates how similar a new input is to the training distribution.
        Uses Mahalanobis distance to detect multivariate outliers.
        """
        if not self.is_fitted:
            raise ValueError("Profiler must be fitted on training data first.")

        # Convert input dict to vector
        input_vec = np.array([input_data[f] for f in self.feature_names]).reshape(1, -1)
        input_scaled = self.scaler.transform(input_vec)
        
        # Mahalanobis Distance: sqrt((x-mu)' * inv_cov * (x-mu))
        delta = input_scaled - self.mean_train
        m_dist = np.sqrt(np.dot(np.dot(delta, self.inv_cov_train), delta.T))[0][0]
        
        # Calculate p-value based on Chi-Squared distribution
        # High p-value = In-distribution, Low p-value = OOD
        p_val = 1 - chi2.cdf(m_dist**2, df=len(self.feature_names))
        
        # Individual feature drift analysis (Z-score)
        feature_drifts = {}
        for i, col in enumerate(self.feature_names):
            val = input_vec[0][i]
            stats = self.feature_stats[col]
            z_score = abs(val - stats['mean']) / (stats['std'] + 1e-9)
            feature_drifts[col] = {
                'z_score': round(float(z_score), 3),
                'is_extreme': bool(z_score > 3.0)
            }

        return {
            'mahalanobis_distance': round(float(m_dist), 4),
            'distribution_p_value': round(float(p_val), 4),
            'is_ood': bool(p_val < 0.05),
            'feature_z_scores': feature_drifts,
            'description': "Determines multivariate similarity to training corpus."
        }

    def get_summary_stats(self) -> Dict[str, Any]:
        return self.feature_stats
