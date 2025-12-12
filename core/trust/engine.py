import numpy as np
from typing import Dict, Any

class TrustScoreEngine:
    """
    The 'Brain' of TRUSTSCOPE. 
    Synthesizes multiple reliability signals into a single trust decision.
    """
    
    def __init__(self, weights: Dict[str, float] = None):
        # Default weights for different trust components
        self.weights = weights or {
            'uncertainty': 0.4,
            'agreement': 0.3,
            'ood': 0.2,
            'calibration': 0.1
        }

    def compute_trust_score(self, 
                           predictions: Dict[str, float],
                           uncertainty_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates a 0-100 Trust Score.
        """
        # 1. Agreement Signal (0 to 1, higher is better)
        disagreement = uncertainty_report['ensemble_disagreement']['disagreement_variance']
        agreement_score = max(0, 1.0 - (disagreement * 4.0)) # Scale: 0.25 variance = 0 agreement
        
        # 2. Uncertainty Signal (0 to 1, higher is better)
        uncertainty_score = 1.0 - uncertainty_report['total_uncertainty_score']
        
        # 3. OOD Signal (0 to 1, higher is better)
        ood_score = uncertainty_report['data_similarity']['distribution_p_value']
        
        # 4. Consistency Signal (Mean of predictions vs individual)
        # (This is partially covered by ensemble disagreement)
        
        # Weighted Synthesis
        final_score = (
            agreement_score * self.weights['agreement'] + 
            uncertainty_score * self.weights['uncertainty'] + 
            ood_score * self.weights['ood']
        )
        
        # Normalize to 0-100
        trust_percentage = round(float(final_score * 100), 2)
        
        # Category Logic
        if trust_percentage > 80 and ood_score > 0.05:
            label = "SAFE"
            recommendation = "Automated decision recommended."
        elif trust_percentage > 50:
            label = "REVIEW"
            recommendation = "Human-in-the-loop review recommended due to moderate uncertainty."
        else:
            label = "UNSAFE"
            recommendation = "Prediction rejected. Extreme uncertainty or OOD detected. Manual intervention REQUIRED."

        return {
            'trust_score': trust_percentage,
            'trust_label': label,
            'recommendation': recommendation,
            'component_scores': {
                'agreement': round(agreement_score, 4),
                'uncertainty': round(uncertainty_score, 4),
                'distribution_similarity': round(ood_score, 4)
            }
        }
