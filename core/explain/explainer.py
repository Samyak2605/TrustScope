from typing import Dict, Any

class TrustExplainer:
    """
    Translates mathematical trust signals into human-readable explanations.
    Supports different tones/personas.
    """
    
    def synthesize_explanation(self, trust_report: Dict[str, Any], tone: str = 'technical') -> str:
        score = trust_report['trust_score']
        label = trust_report['trust_label']
        components = trust_report['component_scores']
        
        if tone == 'executive':
            return self._executive_tone(score, label, components)
        elif tone == 'simple':
            return self._simple_tone(score, label, components)
        else:
            return self._technical_tone(score, label, components)

    def _technical_tone(self, score, label, components) -> str:
        expl = f"Trust Level: {label} ({score}/100). "
        reasons = []
        if components['agreement'] < 0.7:
            reasons.append("high ensemble variance (model disagreement)")
        if components['uncertainty'] < 0.7:
            reasons.append("elevated epistemic uncertainty via MC Dropout")
        if components['distribution_similarity'] < 0.05:
            reasons.append("input identified as Out-of-Distribution (OOD)")
            
        if reasons:
            expl += "Reliability inhibited by " + ", ".join(reasons) + "."
        else:
            expl += "All reliability signals are within nominal parameters."
        return expl

    def _executive_tone(self, score, label, components) -> str:
        if label == "SAFE":
            return "This prediction meets all corporate safety standards for automated processing."
        elif label == "REVIEW":
            return "Caution: System confidence is moderate. Recommend verification by an analyst."
        else:
            return "Warning: High risk of error. This case requires immediate human intervention."

    def _simple_tone(self, score, label, components) -> str:
        if label == "SAFE":
            return "We are confident in this result."
        elif label == "REVIEW":
            return "This case is a bit unusual, so a human should double-check it."
        else:
            return "The system is unsure about this because it hasn't seen many cases like it before."
