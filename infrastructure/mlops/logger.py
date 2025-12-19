import json
import logging
import os
import numpy as np
from datetime import datetime
from typing import Dict, Any

class TrustLogger:
    """
    Handles MLOps-style audit logging.
    Every prediction and trust decision is stored with metadata for future auditing.
    """
    
    def __init__(self, log_dir: str = "data/logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        self.audit_file = os.path.join(log_dir, "audit_log.jsonl")
        
        # Also setup standard logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - TRUSTSCOPE - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("TrustScope")

    def log_decision(self, 
                     input_features: Dict[str, float], 
                     prediction_report: Dict[str, Any],
                     trust_report: Dict[str, Any]):
        """
        Logs a single decision to a JSONL audit file.
        """
        def npy_serializer(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return str(obj)

        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "model_version": "v1.0.0-pilot",
            "input": input_features,
            "predictions": {k: v.tolist() if isinstance(v, np.ndarray) else v for k, v in prediction_report.items()},
            "trust": trust_report
        }
        
        with open(self.audit_file, "a") as f:
            f.write(json.dumps(entry, default=npy_serializer) + "\n")
            
        self.logger.info(f"Logged trust decision: {trust_report['trust_label']} (Score: {trust_report['trust_score']})")

    def get_recent_logs(self, limit: int = 10):
        if not os.path.exists(self.audit_file):
            return []
        
        logs = []
        with open(self.audit_file, "r") as f:
            for line in f:
                logs.append(json.loads(line))
        return logs[-limit:]
