import pandas as pd
import joblib
import numpy as np
import os
import sys

# Add current dir to path
sys.path.append(os.getcwd())

from core.data_science.profiler import DataProfiler
from core.modeling.models import TrustModelManager
from core.uncertainty.estimator import UncertaintyEstimator
from core.trust.engine import TrustScoreEngine
from core.explain.explainer import TrustExplainer

def run_test():
    print("[SmokeTest] Initializing components...")
    
    # 1. Load Profiler
    profiler = joblib.load("data/profiler.joblib")
    
    # 2. Setup Models
    manager = TrustModelManager(input_dim=len(profiler.feature_names))
    manager.load_models()
    
    # 3. Setup Estimators
    uncertainty_estimator = UncertaintyEstimator(manager, profiler)
    trust_engine = TrustScoreEngine()
    explainer = TrustExplainer()
    
    # 4. Create a test sample (In-distribution)
    test_features = pd.read_csv("data/test_features.csv").iloc[0].to_dict()
    x_input = np.array([[test_features[f] for f in profiler.feature_names]])
    
    print("[SmokeTest] Running assessment for In-Distribution sample...")
    raw_preds = manager.predict_all(x_input)
    uncertainty = uncertainty_estimator.estimate_total_uncertainty(x_input, test_features)
    trust = trust_engine.compute_trust_score(raw_preds, uncertainty)
    explanation = explainer.synthesize_explanation(trust)
    
    print(f"Result: {trust['trust_label']} (Score: {trust['trust_score']})")
    print(f"Explanation: {explanation}")
    
    # 5. Create OOD sample (Extreme noise)
    print("\n[SmokeTest] Running assessment for Out-of-Distribution sample...")
    ood_features = {k: v * 10 for k, v in test_features.items()}
    x_ood = np.array([[ood_features[f] for f in profiler.feature_names]])
    
    raw_preds_ood = manager.predict_all(x_ood)
    uncertainty_ood = uncertainty_estimator.estimate_total_uncertainty(x_ood, ood_features)
    trust_ood = trust_engine.compute_trust_score(raw_preds_ood, uncertainty_ood)
    explanation_ood = explainer.synthesize_explanation(trust_ood)
    
    print(f"Result: {trust_ood['trust_label']} (Score: {trust_ood['trust_score']})")
    print(f"Explanation: {explanation_ood}")
    
    if trust_ood['trust_label'] != 'SAFE':
        print("\n[SmokeTest] SUCCESS: OOD detection working.")
    else:
        print("\n[SmokeTest] FAILURE: OOD sample marked as SAFE.")

if __name__ == "__main__":
    run_test()
