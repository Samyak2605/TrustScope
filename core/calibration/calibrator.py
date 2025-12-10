import numpy as np
from sklearn.metrics import brier_score_loss
from typing import Dict, Any, List

class TrustCalibrator:
    """
    Assesses how well model probabilities match reality.
    
    Why this matters for Trust:
    Raw probabilities are often overconfident (e.g., model says 99% but is wrong 20% of the time).
    Calibration allows us to 'deflate' trust when a model is known to be overconfident.
    """
    
    def __init__(self, num_bins: int = 10):
        self.num_bins = num_bins

    def calculate_ece(self, y_true: np.ndarray, y_probs: np.ndarray) -> float:
        """
        Calculates Expected Calibration Error (ECE).
        Weighted average of the difference between accuracy and confidence per bin.
        """
        bin_boundaries = np.linspace(0, 1, self.num_bins + 1)
        ece = 0.0
        
        for i in range(self.num_bins):
            bin_mask = (y_probs > bin_boundaries[i]) & (y_probs <= bin_boundaries[i+1])
            if np.sum(bin_mask) > 0:
                bin_acc = np.mean(y_true[bin_mask])
                bin_conf = np.mean(y_probs[bin_mask])
                ece += np.sum(bin_mask) * np.abs(bin_acc - bin_conf)
                
        return float(ece / len(y_probs))

    def evaluate_calibration(self, y_true: np.ndarray, y_probs: np.ndarray) -> Dict[str, Any]:
        """
        Aggregates calibration metrics.
        """
        ece = self.calculate_ece(y_true, y_probs)
        brier = brier_score_loss(y_true, y_probs)
        
        # Heuristic: If ECE > 0.1, the model is significantly miscalibrated
        calibration_quality = 1.0 - min(ece * 5, 1.0) # Scale it for trust logic
        
        return {
            'ece': round(ece, 4),
            'brier_score': round(float(brier), 4),
            'calibration_trust_factor': round(float(calibration_quality), 4),
            'is_overconfident': ece > 0.1 and np.mean(y_probs) > np.mean(y_true)
        }

    def get_reliability_curve(self, y_true: np.ndarray, y_probs: np.ndarray) -> List[Dict[str, float]]:
        """
        Returns data points for a reliability curve (calibration plot).
        """
        bin_boundaries = np.linspace(0, 1, self.num_bins + 1)
        curve = []
        
        for i in range(self.num_bins):
            bin_mask = (y_probs > bin_boundaries[i]) & (y_probs <= bin_boundaries[i+1])
            if np.sum(bin_mask) > 0:
                curve.append({
                    'bin': i,
                    'confidence': float(np.mean(y_probs[bin_mask])),
                    'accuracy': float(np.mean(y_true[bin_mask])),
                    'count': int(np.sum(bin_mask))
                })
        return curve
