import numpy as np
import torch
from typing import Dict, Any

class UncertaintyEstimator:
    """
    Quantifies different types of uncertainty for a given prediction.
    
    1. Ensemble Disagreement (Epistemic): Variance across different model architectures.
    2. Monte Carlo Dropout (Aleatoric/Model): Variance within the NN across multiple stochastic passes.
    3. Distance-based (OOD): Based on feature-space similarity.
    """
    
    def __init__(self, model_manager, profiler):
        self.model_manager = model_manager
        self.profiler = profiler

    def get_ensemble_disagreement(self, X_input: np.ndarray) -> Dict[str, Any]:
        """
        Calculates the variance and range of predictions across the ensemble.
        High disagreement = High Epistemic uncertainty.
        """
        probs = self.model_manager.predict_all(X_input)
        stacked_probs = np.stack([probs['rf'], probs['lr'], probs['nn']])
        
        variance = np.var(stacked_probs, axis=0)
        mean_prob = np.mean(stacked_probs, axis=0)
        
        return {
            'disagreement_variance': round(float(variance[0]), 4),
            'disagreement_mean': round(float(mean_prob[0]), 4),
            'raw_probs': {k: round(float(v[0]), 4) for k, v in probs.items()}
        }

    def get_mc_dropout_uncertainty(self, X_input: np.ndarray, num_samples: int = 50) -> Dict[str, Any]:
        """
        Performs multiple forward passes with dropout enabled to estimate model uncertainty.
        Mathematical intuition: Sampling from the approximate posterior of weights.
        """
        X_tensor = torch.FloatTensor(X_input)
        self.model_manager.nn_model.train() # Enable dropout
        
        samples = []
        with torch.no_grad():
            for _ in range(num_samples):
                samples.append(self.model_manager.nn_model(X_tensor).numpy())
                
        samples = np.array(samples)
        variance = np.var(samples, axis=0)
        mean_prob = np.mean(samples, axis=0)
        
        return {
            'mc_variance': round(float(variance[0]), 4),
            'mc_mean': round(float(mean_prob[0]), 4),
            'description': f"Stochastic variance over {num_samples} passes."
        }

    def estimate_total_uncertainty(self, X_input: np.ndarray, input_dict: Dict[str, float]) -> Dict[str, Any]:
        """
        Aggregates all uncertainty signals.
        """
        ensemble = self.get_ensemble_disagreement(X_input)
        mc_dropout = self.get_mc_dropout_uncertainty(X_input)
        dist_analysis = self.profiler.compute_similarity(input_dict)
        
        # Normalized uncertainty score (0 to 1)
        # Combination of disagreement, MC variance, and OOD-ness
        combined_score = (
            ensemble['disagreement_variance'] * 2.0 + 
            mc_dropout['mc_variance'] * 1.5 + 
            (1.0 - dist_analysis['distribution_p_value']) * 0.5
        )
        normalized_score = min(max(combined_score, 0), 1)
        
        return {
            'ensemble_disagreement': ensemble,
            'mc_dropout': mc_dropout,
            'data_similarity': dist_analysis,
            'total_uncertainty_score': round(float(normalized_score), 4)
        }
