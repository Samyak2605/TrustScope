from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Any

# Internal imports
from core.data_science.profiler import DataProfiler
from core.modeling.models import TrustModelManager
from core.uncertainty.estimator import UncertaintyEstimator
from core.trust.engine import TrustScoreEngine
from core.explain.explainer import TrustExplainer
from infrastructure.mlops.logger import TrustLogger

app = FastAPI(title="TRUSTSCOPE API", description="AI Prediction Reliability & Trust Assessment Platform")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for components
state = {
    "profiler": None,
    "model_manager": None,
    "uncertainty_estimator": None,
    "trust_engine": TrustScoreEngine(),
    "explainer": TrustExplainer(),
    "logger": TrustLogger()
}

class PredictionRequest(BaseModel):
    features: Dict[str, float]

@app.on_event("startup")
def startup_event():
    try:
        # Load pre-trained artifacts
        state["profiler"] = joblib.load("data/profiler.joblib")
        
        # Initialize model manager
        sample_features = state["profiler"].feature_names
        state["model_manager"] = TrustModelManager(input_dim=len(sample_features))
        state["model_manager"].load_models()
        
        # Initialize uncertainty estimator
        state["uncertainty_estimator"] = UncertaintyEstimator(
            state["model_manager"], 
            state["profiler"]
        )
        print("[API] All components loaded successfully.")
    except Exception as e:
        print(f"[API] Startup error: {e}")

def deep_clean(obj):
    """Recursively convert numpy types to Python primitives."""
    if isinstance(obj, dict):
        return {k: deep_clean(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [deep_clean(x) for x in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    else:
        return obj

@app.post("/assess")
async def assess_prediction(request: PredictionRequest):
    if not state["profiler"]:
        raise HTTPException(status_code=503, detail="System not initialized. Run setup script.")

    try:
        features = request.features
        # Convert to numpy for model processing
        feature_names = state["profiler"].feature_names
        x_input = np.array([[features[f] for f in feature_names]])
        
        # 1. Get raw predictions
        raw_preds = state["model_manager"].predict_all(x_input)
        
        # 2. Estimate uncertainty
        uncertainty_report = state["uncertainty_estimator"].estimate_total_uncertainty(x_input, features)
        
        # 3. Compute trust score
        trust_report = state["trust_engine"].compute_trust_score(raw_preds, uncertainty_report)
        
        # 4. Generate explanations
        explanation = state["explainer"].synthesize_explanation(trust_report, tone="technical")
        
        # 5. Log decision
        state["logger"].log_decision(features, raw_preds, trust_report)
        
        response = {
            "prediction": raw_preds,
            "trust": trust_report,
            "explanation": explanation,
            "signals": uncertainty_report
        }
        
        return deep_clean(response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs")
async def get_logs(limit: int = 10):
    return state["logger"].get_recent_logs(limit)

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}
